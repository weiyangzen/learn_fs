# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-sdw.c

## Purpose

`rt5682-sdw.c` is the SoundWire bus binding for the Realtek RT5682 ALSA SoC codec. It connects the shared codec component implementation in `rt5682.c` to the Linux SoundWire core by supplying an SDW driver, SDW slave callbacks, SDW stream setup, runtime/system PM glue, and a two-layer regmap arrangement for the codec's normal 16-bit register map over SoundWire indirect access registers.

The file does not implement the common codec controls, DAPM graph, jack state machine, PLL math, or calibration logic itself. Instead it allocates and initializes `struct rt5682_priv`, configures SoundWire-specific register access and port capabilities, then registers `rt5682_soc_component_dev` and the shared AIF DAI ops exported by `rt5682.c`.

## Important APIs, Types, and Functions

- `rt5682_sdw_read()` and `rt5682_sdw_write()` implement indirect 16-bit codec register access through SDW-visible 8-bit registers `0x3000`, `0x3001`, `0x3004`, `0x3005`, and `0x3008`.
- `rt5682_sdw_indirect_regmap` is the logical codec regmap. It is 16-bit register/16-bit value, uses `REGCACHE_MAPLE`, shares `rt5682_reg` defaults, and uses the exported readable/volatile predicates from `rt5682.c`.
- `rt5682_sdw_regmap` is the low-level SDW regmap, 32-bit register/8-bit value, no cache, and only exposes the direct SDW control registers that the indirect access helpers use.
- `rt5682_sdw_hw_params()` converts ALSA PCM params to SDW stream/port config with `snd_sdw_params_to_config()`, adds the codec as an SDW slave to the runtime stream, selects port 1 for playback and port 2 for capture, and programs SDW reference-rate and ADC/DAC oversampling fields.
- `rt5682_sdw_hw_free()`, `rt5682_set_sdw_stream()`, and `rt5682_sdw_shutdown()` manage the SDW stream pointer stored in DAI DMA data.
- `rt5682_sdw_init()` allocates private state, creates the indirect regmap, acquires optional LDO1 GPIO, initializes work and locks, registers the component plus DAIs, and enables runtime PM without initially marking the device active.
- `rt5682_io_init()` performs hardware bring-up after the SDW slave reports attached. It leaves regcache-only mode, validates `RT5682_DEVICE_ID`, runs headphone calibration, applies the patch list and SoundWire PLL/jack register programming, schedules jack detection, and marks `hw_init`/`first_hw_init`.
- `rt5682_read_prop()` describes SDW slave properties: source port bitmap `0x4` for port 2, sink port bitmap `0x2` for port 1, full data ports, simple channel prepare state machines, interrupt masks, invalid initial parity quirk, wake capability, and clock stop timeout.
- `rt5682_clock_config()` maps the current bus data-rate-derived clock to codec SDW control values written to direct SDW registers `0xe0` and `0xf0`.
- `rt5682_interrupt_callback()` schedules the shared jack-detect delayed work on implementation-defined control-port interrupt bit `0x4`, guarded by `disable_irq_lock`.
- `rt5682_update_status()`, `rt5682_bus_config()`, and `rt5682_slave_ops` integrate with SoundWire enumeration and bus reconfiguration.
- `rt5682_dev_suspend()`, `rt5682_dev_system_suspend()`, and `rt5682_dev_resume()` coordinate delayed work cancellation, regcache transitions, SDW interrupt masking, reattach completion waits, and regcache sync.

## Control Flow

Probe starts in `rt5682_sdw_probe()`, which creates the direct SDW regmap and calls `rt5682_sdw_init()`. Initialization intentionally sets both regmaps to cache-only and leaves the runtime PM status suspended until SoundWire enumeration reports the slave as attached. This avoids ASoC runtime PM users racing ahead of actual SDW availability.

When SoundWire core reports status through `rt5682_update_status()`, an unattached transition clears `hw_init`. An attached transition calls `rt5682_io_init()` if initialization is not already complete. `rt5682_io_init()` brings regmaps out of cache-only mode, optionally bypasses the cache for reinitialization, marks PM active for first attach, verifies the device ID with retries, calibrates, then either restores cached state on subsequent attach or performs first-time patch/PLL/jack programming. It schedules `jack_detect_work` after 250 ms and returns the runtime PM reference with autosuspend.

PCM setup for the SDW DAI flows through `rt5682_sdw_hw_params()`. It retrieves the SDW stream runtime previously installed by `.set_stream`, converts PCM params, chooses SDW port number based on stream direction, calls `sdw_stream_add_slave()`, maps sample rates from 8 kHz through 192 kHz plus 11.025/22.05/44.1/88.2/176.4 kHz to SDW reference register values, selects lower oversampling divisors at higher sample rates, and writes playback values to `RT5682_SDW_REF_1_MASK`/DAC OSR or capture values to `RT5682_SDW_REF_2_MASK`/ADC OSR. Freeing the stream removes the slave from the SDW runtime.

System suspend disables implementation-defined interrupts with `sdw_update_no_pm()` under `disable_irq_lock` before delegating to the generic suspend path. Resume either re-enables interrupts immediately when the slave remained attached or waits up to `RT5682_PROBE_TIMEOUT` for `initialization_complete` after an unattach request before syncing the cached codec map.

## State and Persistence Behavior

Persistent driver state lives in `struct rt5682_priv`, especially `slave`, `sdw_regmap`, `regmap`, `hw_init`, `first_hw_init`, `disable_irq`, `params`, and the shared jack/calibration fields. The regcache is important: the logical codec regmap uses maple cache for normal codec registers, while the direct SDW regmap is uncached. During suspend, detach, and pre-enumeration windows, both regmaps are put in cache-only mode and the logical regcache is marked dirty so that resume or reattach can replay state.

No filesystem or firmware persistence is used. Hardware state is reconstructed from register defaults, patch list writes in `rt5682.c`, cached regmap writes, SoundWire bus params, and ASoC/PCM callbacks.

## Dependencies and Integration Points

This file depends on Linux SoundWire core APIs (`sdw_driver`, `sdw_slave_ops`, stream add/remove, bus params, `sdw_update_no_pm()`), regmap, runtime PM, delayed work, and ASoC component/DAI registration. It also depends tightly on shared RT5682 exports from `rt5682.c` and constants/types from `rt5682.h`.

Integration with the shared codec is through `rt5682_soc_component_dev`, `rt5682_aif1_dai_ops`, `rt5682_aif2_dai_ops`, `rt5682_apply_patch_list()`, `rt5682_calibrate()`, `rt5682_get_ldo1()`, `rt5682_jack_detect_handler()`, and the exported regmap metadata. The DAPM routes in `rt5682.c` include SDW-specific endpoints (`SDWRX`, `SDWTX`) and rely on the SDW DAI defined here.

## Risks and Edge Cases

- `rt5682_sdw_read()` and `rt5682_sdw_write()` ignore return values from low-level `regmap_read()`/`regmap_write()`, so indirect register failures can be hidden from callers.
- `rt5682_sdw_hw_params()` calls `sdw_stream_add_slave()` before validating the sample rate. If a later unsupported rate path returns `-EINVAL`, this function does not remove the slave it just added.
- Reattach behavior depends on correct `hw_init`, `first_hw_init`, and `slave->unattach_request` transitions. Incorrect SoundWire status ordering could leave cached codec state stale or synced too early.
- Bus clock configuration supports only a small set of derived rates. Unsupported `params.curr_dr_freq >> 1` values fail bus config.
- Interrupt handling assumes implementation-defined control-port bit `0x4` maps to jack/button events and that `disable_irq_lock` coverage is sufficient against suspend races.
- Jack detection work is shared with the common codec path and can be skipped when the SDW parent is runtime-suspended.

## Test Signals

Useful validation signals include successful SDW probe and slave attach, no timeout waiting for `initialization_complete`, `RT5682_DEVICE_ID` reading as `0x6530`, successful playback and capture stream creation on SDW ports 1 and 2, correct sample-rate register programming for 8 kHz through 192 kHz families, clean suspend/resume with regcache sync, jack insert/remove/button reporting over SoundWire interrupts, and lack of `Invalid clk config`, `Unable to configure port`, or device-ID warnings in dmesg.
