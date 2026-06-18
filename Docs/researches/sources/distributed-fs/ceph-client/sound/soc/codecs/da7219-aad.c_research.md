# sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.c

## Purpose

`da7219-aad.c` implements the DA7219 accessory auto-detect block for the main DA7219 ASoC codec driver. It owns headset/headphone/line-out detection, four-button headset reporting, mic-bias preparation for 4-pole jacks, headphone impedance testing for non-headset plugs, DT/ACPI firmware property conversion for AAD tuning, IRQ handling, and AAD suspend/resume integration.

## Important APIs, Types, and Functions

- `da7219_aad_jack_det()` is the public bridge from the codec component `.set_jack` callback. It stores the `snd_soc_jack`, sends an initial empty jack report, resets `jack_inserted`, and enables or disables `DA7219_ACCDET_EN_MASK`.
- `da7219_aad_probe()` allocates `struct da7219_aad_priv`, attaches it to `struct da7219_priv`, and fills missing AAD platform data from the firmware child node `da7219_aad`.
- `da7219_aad_init()` binds the component pointer, applies platform data to AAD registers, creates a single-thread `da7219-aad` workqueue, initializes button/headphone-test/ground-switch work items, requests a threaded IRQ, and unmasks AAD IRQs.
- `da7219_aad_exit()` masks AAD IRQs, frees the IRQ, cancels all queued work, and destroys the workqueue.
- `da7219_aad_irq_thread()` is the central threaded interrupt handler. It reads and acknowledges `ACCDET_IRQ_EVENT_A/B`, interprets jack insertion/removal/detect-complete/button events, queues slower work, maintains `jack_inserted`, and emits `snd_soc_jack_report()` updates.
- `da7219_aad_btn_det_work()` prepares headphone outputs and mic bias, optionally pulses mic bias to wake headset microphones, then enables button-detection timing with `btn_cfg`.
- `da7219_aad_hptest_work()` performs a destructive but restored headphone load test using the tone generator, DACs, mixout path, HP amps, charge pump, PLL/MCLK, and regmap cache synchronization. It reports `SND_JACK_HEADPHONE` or `SND_JACK_LINEOUT`.
- `da7219_aad_suspend()` and `da7219_aad_resume()` disable or restore AAD when the parent codec is not a wake source, including mic-bias restoration for an inserted 4-pole jack.
- Firmware parsing helpers translate `dlg,*` properties into `sound/da7219-aad.h` enum values and register fields.

## Control Flow

The normal jack flow starts when `da7219_aad_jack_det()` enables ACCDET. A hardware IRQ wakes `da7219_aad_irq_thread()`, which bulk-reads event registers, reads `ACCDET_STATUS_A`, schedules ground-switch enable work on jack insertion, then writes the event bytes back to clear latched interrupts. On detect complete, it cancels the pending ground-switch work, disables the ground switch, and branches by `JACK_TYPE_STS`: 4-pole jacks immediately report `SND_JACK_HEADSET` and queue `btn_det_work`; non-headset plugs queue `hptest_work` to decide headphone versus line-out. Button press and release bits are translated to `SND_JACK_BTN_0` through `SND_JACK_BTN_3`. Removal cancels all delayed or pending work, undrives HP outputs, disables button detection and mic bias, clears the ground switch, resets `jack_inserted`, and reports a zero state for the full AAD mask.

The headphone-test path locks DAPM, `ctrl_lock`, and `pll_lock`, then temporarily changes many audio-path registers with regcache bypass enabled so the previous cached settings can be restored. If MCLK is absent it uses an internal oscillator frequency and additional settle delays; if MCLK exists but PLL is bypassed it temporarily enables the PLL. After tone generation and comparator readout, it syncs individual register regions from cache back to hardware, restores gain ramp and PLL state, disables any prepared MCLK, unlocks, and reports only if `jack_inserted` is still true.

## State and Persistence

Persistent runtime state lives in `struct da7219_aad_priv`: IRQ number, component pointer, jack pointer, workqueue and work items, platform-tuned mic-bias pulse settings, button timing, ground-switch delay, `jack_inserted`, and `micbias_resume_enable`. It also modifies parent `struct da7219_priv` state through `micbias_on_event`, `regmap`, `mclk`, `pll_lock`, and `ctrl_lock`. Hardware state is mainly DA7219 ACCDET registers plus hidden vendor/unlock registers `0xF0`, `0x75`, and `0xFB`. The driver relies on regmap cache to restore user-visible audio controls after HP test, and on DAPM pin state to persist mic-bias power intent.

## Dependencies and Integration Points

The file depends on the main DA7219 codec private structure and exported `da7219_set_pll()`. It integrates with ALSA ASoC jack reporting, DAPM, regmap, Linux workqueues, threaded IRQs, device properties/fwnodes, I2C client data, clocks, and PM wake IRQ support. Public platform enums and pdata come from `<sound/da7219-aad.h>` and `<sound/da7219.h>`, while local register definitions come from `da7219-aad.h` and `da7219.h`.

## Risks and Edge Cases

- `da7219_aad_init()` returns immediately if `request_threaded_irq()` fails, but the workqueue was already created; a failure path leak is possible unless caller teardown handles an only partially initialized AAD block.
- The IRQ handler uses raw register addresses `0xFB`, `0xF0`, and `0x75`; these hidden-page writes are hard to audit against datasheet revisions and can break silently if register paging semantics change.
- `delay = gnd_switch_delay * (internal_osc ? 2 : 1) - 2` can become small or negative if future configuration changes produce low delays.
- HP test temporarily rewrites many live audio-path registers. Locking protects DAPM, controls, and PLL, but concurrent low-level register writes outside those locks could still race the cache-restore sequence.
- Mic-bias status polling only warns on timeout and continues enabling button detection, so marginal hardware may produce incorrect button events.
- The IRQ handler calls `snd_soc_jack_report()` even with a zero `mask` in some paths; harmless but useful to watch for redundant reports.

## Test Signals

Useful validation includes jack insertion/removal tests for 3-pole and 4-pole accessories, line-out versus headphone impedance classification, button A/B/C/D press and release reporting, suspend/resume with an inserted headset, wake-source versus non-wake-source suspend behavior, IRQ storm or spurious IRQ handling, and register-cache restoration after HP test while user controls have non-default values. Kernel logs to watch include failed IRQ/event reads, mic-bias timeout warnings, SRM/PLL messages from the parent codec, and missing or incorrect `SND_JACK_*` input events.
