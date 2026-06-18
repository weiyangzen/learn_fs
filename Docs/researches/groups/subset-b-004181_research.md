# subset-b-004181 research

Grouped research report for the requested media radio driver files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-miropcm20.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-miropcm20.c

Purpose: implements V4L2 radio support for the ISA Miro PCM20 tuner, relying on the ALSA `snd-miro` ACI interface for tuner and RDS hardware access. It exposes a `/dev/radioX` device with frequency, tuner, mute, stereo/mono, and RDS controls.

Important APIs and functions: module entry/exit are `pcm20_init` and `pcm20_cleanup`. V4L2 operations include `vidioc_querycap`, `vidioc_g_tuner`, `vidioc_s_tuner`, `vidioc_g_frequency`, `vidioc_s_frequency`, event subscription, and control status logging. RDS transport helpers are `rds_waitread`, `rds_rawwrite`, `rds_write`, `rds_readcycle`, `rds_ack`, and `rds_cmd`. `pcm20_setfreq` programs tuner frequency through `snd_aci_cmd`. `pcm20_thread` polls RDS status and updates V4L2 RDS controls.

Control flow: initialization obtains the global ACI object with `snd_aci_get_aci`, registers a standalone `v4l2_device`, creates mute and RDS controls, sets mono/stereo mode, tunes the default frequency, and registers a radio video device. Opening the first file handle starts a kernel thread that polls the RDS decoder every two seconds. Frequency changes clamp to 87-108 MHz, reset RDS, and write ACI tune bytes. The RDS thread queries availability, clears controls after repeated no-RDS intervals, and updates PS name, radio text, PTY, TA, TP, and music/speech controls when valid data appears.

State and persistence: state is process-global in `pcm20_card`, including cached frequency, audio mode, V4L2 objects, ACI pointer, mutex, RDS controls, and optional polling thread. Hardware state lives in the PCM20/ACI device until changed; no settings persist across unload.

Dependencies and integration points: depends on `sound/aci.h`, low-level `inb/outb`, V4L2 device/ioctl/control/event APIs, and the `snd-miro` ALSA driver being loaded first. Userspace consumes radio tuning through V4L2 ioctls and RDS metadata through controls/events.

Risks: the module uses one static device instance, so it is not multi-card capable. RDS reads are timing-sensitive and include a magic microsecond delay. `rds_cmd` sometimes returns `-1` instead of a standard errno. The RDS thread updates controls from a polling context and depends on first-open/last-close lifetime. Tuner stereo detection is known to be affected by mute state.

Test signals: build with Miro/ACI dependencies, module load ordering with `snd-miro`, `v4l2-compliance` for tuner and control ioctls, frequency clamp tests, first-open/last-close thread lifetime, mute/mono commands on hardware, and real RDS station tests observing control events and no-RDS clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-miropcm20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-mr800.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-mr800.c

Purpose: implements a V4L2 USB radio driver for the AverMedia MR 800. The hardware provides tuning/control over USB while analog audio is handled outside this driver by a sound input path.

Important APIs and functions: USB entry points are `usb_amradio_probe`, `usb_amradio_disconnect`, suspend/resume callbacks, and the `module_usb_driver` registration. Device commands go through `amradio_send_cmd`; helpers include `amradio_set_mute`, `amradio_set_freq`, `amradio_set_stereo`, `amradio_get_stat`, `vidioc_s_hw_freq_seek`, and `usb_amradio_init`. V4L2 controls expose `V4L2_CID_AUDIO_MUTE`.

Control flow: probe allocates `struct amradio_device` and an 8-byte command buffer, registers a `v4l2_device`, creates the mute control, initializes mutex and video device metadata, stores USB interface data, sets a default frequency, initializes mute/stereo/frequency state, then registers `/dev/radioX`. V4L2 ioctls call command helpers under the video-device lock. Hardware seek programs search level, restarts from the cached current frequency, issues up/down search, polls the ready flag for up to 30 seconds, reads the found frequency, stops search, and reprograms the cached frequency.

State and persistence: per-device state tracks USB device/interface, V4L2 device/video device/control handler, shared transfer buffer, cached frequency, stereo preference, mute flag, and a mutex. State is volatile and freed by the V4L2 release callback after disconnect and last reference.

Dependencies and integration points: depends on USB bulk endpoints, HID-class USB ID matching, V4L2 radio ioctls, V4L2 controls/events, and analog audio routing outside the driver. Userspace sees hardware frequency seek support and a mute control.

Risks: endpoint numbers are hard-coded (`sndintpipe` 2 and receive pipe `0x81`) and not validated during probe. `vidioc_g_frequency` rejects calls unless `f->type` is already `V4L2_TUNER_RADIO`, which is stricter than many drivers. Seek uses a static 8-byte buffer and blocking polling; nonblocking callers are rejected. Suspend stores "was unmuted" by temporarily setting `muted` false after muting, which is subtle. Frequency conversion comments note occasional out-of-range search results.

Test signals: USB probe/disconnect while file handles are open, `v4l2-compliance`, mute/stereo/frequency command tracing, hardware seek success/timeout/interruption, suspend/resume restoring frequency and mute state, and fault injection for partial bulk transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-mr800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-raremono.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-raremono.c

Purpose: provides V4L2 support for Thanko's Raremono, a USB AM/FM/SW receiver using a si4734 behind firmware that presents the same USB IDs as the Si470x reference design.

Important APIs and functions: USB lifecycle is `usb_raremono_probe` and `usb_raremono_disconnect`. `raremono_cmd_main` sends the firmware frequency/band command over HID control messages. V4L2 ioctls include querycap, tuner get/set, frequency get/set, and frequency-band enumeration.

Control flow: probe allocates device state and a 64-byte buffer, performs a distinguishing GET_REPORT against the shared Si470x USB ID, rejects real Si470x devices, registers V4L2 state, initializes a video device, tunes FM 95.160 MHz, and registers the radio node. Frequency setting chooses FM, AM, or shortwave based on requested V4L2 frequency gaps, clamps to the selected band, converts to kHz or 10 kHz units for FM, and sends a 3-byte HID report. Tuner status reads a signal report and scales signal from returned bytes.

State and persistence: `struct raremono_device` stores USB/V4L2 objects, mutex, shared HID buffer, current band, and current frequency in kHz. No state is persistent beyond the device session.

Dependencies and integration points: uses USB control transfers with HID report requests, V4L2 frequency-band APIs, unaligned big-endian helpers for the device-ID probe, and a V4L2 video device with the radio/tuner capabilities. It intentionally shares ID space with `radio-si470x-usb.c` and cooperates via runtime device identification.

Risks: the firmware hides many si4734 features, so the driver exposes only basic tuning and signal strength. The band selection heuristic depends on gaps between AM/SW/FM ranges. There is no explicit mute, seek, RDS, or power management. Signal reporting uses an opaque vendor report with long timeout. If both Raremono and Si470x matching logic drift, one driver can bind the wrong product.

Test signals: binding tests against both Raremono and Si470x reference devices, `VIDIOC_ENUM_FREQ_BANDS` for all three bands, AM/SW/FM frequency clamp behavior, signal read failures, disconnect during ioctl, and `v4l2-compliance` for basic tuner ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-raremono.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-rtrack2.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-rtrack2.c

Purpose: implements the AIMSlab RadioTrack II ISA card using the shared `radio-isa` framework. It supplies board-specific port programming for frequency, mute, and signal detection.

Important APIs and functions: module entry/exit are `rtrack2_init` and `rtrack2_exit`, registering an `isa_driver`. Board hooks are `rtrack2_alloc`, `rtrack2_s_frequency`, `rtrack2_g_signal`, and `rtrack2_s_mute_volume`, collected in `radio_isa_ops`.

Control flow: the shared framework probes configured or known ports `0x20f` and `0x30f`, allocates a `radio_isa_card`, and exposes standard V4L2 radio operations. Setting frequency converts V4L2 units to the card's serial programming value, sends a reset/preamble sequence, clocks ten zero bits, then clocks 15 frequency bits using `zero` and `one` port waveforms. Mute writes the mute value to the base I/O port, and signal reads bit 1 where set means no signal.

State and persistence: per-card state is the generic `radio_isa_card` allocated by the framework. Frequency, mute, and stereo bookkeeping are primarily framework state; hardware registers are programmed through ISA I/O and do not persist across unload.

Dependencies and integration points: depends on `radio-isa.h`, ISA driver registration, request-region ownership via the framework, low-level `outb_p/inb`, and V4L2 ioctls implemented by the shared radio-ISA layer.

Risks: hardware timing is implicit in `outb_p`; faster or virtualized systems may not match original bus timing. Only two I/O addresses are supported. Signal polarity is board-specific. There is no explicit hardware detection beyond what the framework and port list provide.

Test signals: `v4l2-compliance` on real RadioTrack II hardware, probe at both possible ports, frequency-programming validation across the FM band, mute state retention through frequency changes, and signal bit behavior with/without antenna input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-rtrack2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmi.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmi.c

Purpose: implements direct V4L2 support for MediaForte SF16-FMI/FMP/FMD ISA radio cards, including optional ISA PnP discovery, LM7000 tuner programming, mute, and signal-strength reads.

Important APIs and functions: module lifecycle is `fmi_init`/`fmi_exit`. Tuner programming goes through `fmi_set_freq` and `lm7000_set_freq` with the callback `fmi_set_pins`. V4L2 handlers cover querycap, tuner get/set, frequency get/set, and mute control through `fmi_s_ctrl`. PnP probing is in `isapnp_fmi_probe`.

Control flow: initialization probes ISA PnP first when no `io` parameter is supplied, then falls back to ports `0x284` and `0x384`. It reserves two I/O ports, performs simple presence checks, registers a standalone V4L2 device and mute control, initializes the video device, starts muted at the minimum frequency, and registers the radio node. Frequency changes clamp to 87-108 MHz and round to 800-unit steps before bit-banging LM7000 pins. Signal measurement toggles the STRQ bit, waits 143 ms, reads `io + 1`, and restores output state.

State and persistence: one static `struct fmi` holds V4L2 state, I/O base, mute flag, current frequency, and mutex. PnP attachment is tracked globally in `dev` and `pnp_attached`. Hardware programming is not persistent across unload.

Dependencies and integration points: depends on ISA PnP APIs, I/O port ownership, `lm7000.h`, V4L2 device/control/event helpers, and direct port I/O. Unlike the `radio-isa` conversions, this driver owns its V4L2 registration directly.

Risks: static single-card state limits multi-card support. Error paths after control initialization can miss releasing the reserved I/O region/PnP attachment in one handler-error branch. Signal polling sleeps while holding the device mutex. The hardware presence check is heuristic. Frequency rounding means get-frequency may report the requested cached value rather than exact programmed step.

Test signals: PnP and manual port probe paths, failed-control initialization cleanup, `v4l2-compliance`, mute/unmute port writes, LM7000 tuning across band edges, signal read timing on real hardware, and unload releasing PnP/I/O resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmr2.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmr2.c

Purpose: supports MediaForte SF16-FMR2 and SF16-FMD2 radio cards by adapting their ISA/PnP I/O pins to the common `snd_tea575x` tuner helper and, when present, controlling the TC9154A/PT2254A audio attenuator.

Important APIs and functions: module lifecycle is `fmr2_init`/`fmr2_exit`, registering both PnP and ISA drivers. Core setup is `fmr2_probe`; removal is `fmr2_remove`. TEA575x operations are `fmr2_tea575x_set_pins`, `fmr2_tea575x_get_pins`, and `fmr2_tea575x_set_direction`. Audio controls use `tc9154a_set_attenuation`, `fmr2_s_ctrl`, and `fmr2_tea_ext_init`.

Control flow: PnP probe allocates an FMD2 instance using the PnP port, while ISA matching probes the hardwired FMR2 port `0x384`. `fmr2_probe` rejects duplicate ports, reserves I/O, registers a V4L2 device, configures the embedded `snd_tea575x`, and calls `snd_tea575x_init`. The TEA helper drives tuning and standard radio ioctls, calling back into the port pin functions. Extra volume/balance controls are added only for FMR2 cards that report a volume-control presence bit.

State and persistence: each card has a dynamically allocated `struct fmr2` containing I/O base, V4L2 device, embedded TEA575x state, optional volume/balance controls, and an FMD2 flag. Global arrays track up to two cards and which bus drivers registered.

Dependencies and integration points: depends on ISA and PnP bus APIs, `media/drv-intf/tea575x.h`, V4L2 device/control support through the TEA helper, direct port I/O, and microsecond delays for the volume shift register.

Risks: if `snd_tea575x_init` fails, `fmr2_probe` releases the I/O region but leaves the V4L2 device registered, which looks like a cleanup bug. The global `num_fmr2_cards` is incremented on probe but never decremented on remove. Volume attenuation mapping uses inverted absolute values around a max of 68 and is easy to regress. `set_direction` is a no-op because hardware direction is fixed/implicit.

Test signals: PnP FMD2 and ISA FMR2 probe/remove cycles, duplicate-port rejection, TEA575x detection failure cleanup, `v4l2-compliance` through the TEA helper, frequency and stereo tuning, optional volume/balance controls on hardware with the attenuator, and unload/reload checking global card count behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark.c

Purpose: implements USB V4L2 tuning support for the Griffin radioSHARK, using the common `snd_tea575x` tuner helper and optional LED class devices. Audio is provided separately by USB audio.

Important APIs and functions: USB lifecycle is `usb_shark_probe`, `usb_shark_disconnect`, `usb_shark_release`, and optional suspend/resume. TEA575x operations are `shark_write_val` and `shark_read_val`. LED helpers include `shark_led_work`, brightness setters, `shark_register_leds`, `shark_unregister_leds`, and `shark_resume_leds`.

Control flow: probe validates expected interrupt endpoints, allocates device state and a 6-byte transfer buffer, assigns a unique V4L2 name, registers LED devices, registers the V4L2 device, populates the embedded `snd_tea575x`, and calls `snd_tea575x_init`. Tuning writes a 32-bit TEA shift-register value over USB interrupt OUT and caches it to avoid redundant transfers. Reads request status with command `0x80`, read interrupt IN status, update cached value, and infer stereo because the hardware does not expose the stereo pin. Disconnect exits the TEA helper under its mutex, unregisters LEDs, and drops the V4L2 reference.

State and persistence: `struct shark_device` stores USB/V4L2 objects, embedded TEA575x state, optional LED work/state/name arrays, a transfer buffer, and the last TEA value. State is volatile and released via the V4L2 device release hook.

Dependencies and integration points: depends on USB interrupt endpoints, `media/drv-intf/tea575x.h`, optional `LEDS_CLASS`, workqueues, and V4L2 device registration performed by the TEA helper. It matches radioSHARK by USB IDs plus `bcdDevice` 0x0001.

Risks: LED registration happens before `v4l2_device_register`, so LED names use the preassigned V4L2 name and need careful cleanup if partial registration fails. `shark_unregister_leds` unregisters all templates even if registration failed partway. Read fallback returns `last_val` after USB errors, which may hide stale hardware state. Stereo is inferred, not measured. `cannot_mute` is set because hardware tuning path lacks mute support.

Test signals: endpoint validation, TEA575x initialization, tuning and status reads over USB, radioSHARK versus radioSHARK2 matching by `bcdDevice`, LED brightness/pulse sysfs behavior, suspend/resume retuning and LED restoration, and disconnect while LED work or tuner ioctls are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark2.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark2.c

Purpose: implements USB V4L2 support for the Griffin radioSHARK2, using the local `radio_tea5777` helper for AM/FM tuning and optional LED class devices. Audio is handled by USB audio outside this driver.

Important APIs and functions: USB lifecycle is `usb_shark_probe`, `usb_shark_disconnect`, `usb_shark_release`, and optional PM callbacks. TEA5777 operations are `shark_write_reg` and `shark_read_reg` in `radio_tea5777_ops`. LED handling mirrors the original shark driver through `shark_led_work`, brightness setters, and register/unregister helpers.

Control flow: probe validates interrupt endpoints, allocates device state and a 7-byte buffer, creates a V4L2 device name, registers LEDs, registers the V4L2 device, sets up the embedded `radio_tea5777` with AM support and the `write_before_read` quirk, then calls `radio_tea5777_init` to register the radio video device. Register writes send command `0x81` plus the six TEA5777 bytes; reads send request `0x82`, read three status bytes, and return them to the helper. Resume retunes through `radio_tea5777_set_freq` and reapplies LED state.

State and persistence: `struct shark_device` contains USB/V4L2 objects, the embedded TEA5777 helper state, optional LED work/state/name arrays, and a transfer buffer. All state is volatile and freed via V4L2 device release after disconnect.

Dependencies and integration points: depends on USB interrupt pipes, `radio-tea5777.h`, optional LED class support, workqueues, and the TEA5777 helper's V4L2 controls/ioctls. USB ID matching distinguishes radioSHARK2 with `bcdDevice` 0x0010.

Risks: LED partial-registration cleanup has the same all-slots unregister pattern as `radio-shark.c`. The read path assembles only three bytes and depends on exact firmware report layout. The `write_before_read` quirk means read status can force a pending write, so lock ordering with the helper mutex matters. Debug logging can expose raw register traffic but is module-parameter gated.

Test signals: probe against radioSHARK2 and rejection of radioSHARK, TEA5777 AM/FM tuning, hardware seek through the helper, USB read/write error injection, LED sysfs behavior, suspend/resume retuning, and disconnect during pending LED work or V4L2 access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-si476x.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-si476x.c

Purpose: implements the V4L2 radio interface for Silicon Labs Si4761/Si4764/Si4768 AM/FM receiver MFD cells. It translates V4L2 tuner, frequency, seek, RDS, and custom Si476x controls into commands and regmap properties owned by the `si476x-core` MFD driver.

Important APIs and functions: platform lifecycle is `si476x_radio_probe` and `si476x_radio_remove`. V4L2 handlers include `si476x_radio_querycap`, tuner get/set, band enumeration, frequency get/set, hardware seek, RDS `read`, `poll`, open/release, and optional advanced-debug register access. Control handlers are `si476x_radio_s_ctrl` and `si476x_radio_g_volatile_ctrl`. Function-mode orchestration is handled by `si476x_radio_init_vtable`, `si476x_radio_change_func`, `si476x_radio_do_post_powerup_init`, and `si476x_radio_pretune`. Debugfs readers expose ACF, RDS block count, AGC, and RSQ reports.

Control flow: probe obtains the parent core with `i2c_mfd_cell_to_core`, registers V4L2 state, configures video capabilities based on whether the chip is a secondary tuner, creates standard/custom controls, registers the radio device, and creates debugfs files. The first open powers the core up, syncs regmap regions, initializes the operation vtable for the current AM/FM function, pretunes, then applies controls. Last release powers down. Frequency setting chooses AM or FM by the gap midpoint, validates chip capability, switches core function when needed, converts V4L2 frequency units to chip units, and sends tune commands. Hardware seek validates or reads seek bounds, switches AM/FM mode, writes seek properties, and starts seek. RDS reads block on the core RDS FIFO and copy FIFO bytes to userspace.

State and persistence: `struct si476x_radio` holds V4L2 objects, control handler, core pointer, current operation vtable, debugfs root, and cached audio mode. Persistent-like settings are cached in the parent core regmap and resynchronized after power/function changes; runtime RDS bytes live in the core kfifo and waitqueue.

Dependencies and integration points: tightly depends on `media/drv-intf/si476x.h`, `linux/mfd/si476x-core.h`, regmap/regcache, parent core locking, V4L2 controls/events/read/poll, kfifo-backed RDS in the core, and debugfs. It is not a standalone I2C driver; it is a platform child of the Si476x MFD.

Risks: several debugfs blob readers check `ops->rds_blckcnt` before calling unrelated `agc_status`/`rsq_status`, likely a copy-paste guard bug that can hide supported operations. RDS control changes in AM mode temporarily use regcache cache-only and require later sync. Open failure paths must power down and release V4L2 file handles correctly. Secondary tuners lack RDS/read capabilities and AM restrictions must be maintained. Frequency band constants use floating expressions for AM range initialization, which is unusual in kernel code snapshots.

Test signals: platform MFD probe/remove, first-open/last-close power transitions, AM/FM mode switching, secondary-tuner capability differences, regmap property synchronization after power cycles, V4L2 custom controls, RDS FIFO read/poll and wakeups, hardware seek bounds/spacing, debugfs binary reports, and lockdep around core locks plus control setup outside the lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-si476x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5764.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5764.c

Purpose: implements an I2C V4L2 radio driver for the NXP TEA5764 FM tuner, originally used in Motorola EZX phones. It supports FM tuning, mono/stereo selection, mute, signal reporting, and chip power up/down.

Important APIs and functions: I2C lifecycle is `tea5764_i2c_probe` and `tea5764_i2c_remove`. Register helpers are `tea5764_i2c_read` and `tea5764_i2c_write`. Power/tuning helpers include `tea5764_power_up`, `tea5764_power_down`, `tea5764_set_freq`, `tea5764_get_freq`, `tea5764_tune`, `tea5764_set_audout_mode`, and `tea5764_mute`. V4L2 handlers cover tuner/frequency operations and mute control.

Control flow: probe registers a V4L2 device and mute control, reads the full register map, verifies chip and manufacturer IDs, initializes the video device, sets stereo, mutes, powers down, then registers the radio node. Setting a nonzero frequency clamps to 87.5-108 MHz, powers up, converts V4L2 units to Hz-like chip input, programs PLL fields, and writes registers. Setting frequency zero is a legacy non-compliant power-down path that returns `-EINVAL`. Tuner get reads registers, reports stereo state, signal level, AFC, and current audio mode.

State and persistence: `struct tea5764_device` stores V4L2 objects, control handler, I2C client, video device, cached register image, and mutex. The cached register image mirrors hardware after reads/writes but is not persisted across unload. `use_xtal` and `radio_nr` are module parameters.

Dependencies and integration points: depends on I2C transfers, V4L2 device/ioctl/control/event APIs, endian conversion for packed register structures, and the board instantiating an I2C client named `radio-tea5764`.

Risks: register structures use packed layout and cast a register buffer to `u16 *`, so endian/unaligned assumptions need care. The zero-frequency power-down behavior is explicitly non-compliant but preserved for compatibility. I2C write errors in helpers such as mute/tune are often logged or ignored rather than propagated through all call chains. The driver has TODOs for platform IRQs and RDS support.

Test signals: I2C probe ID validation, endian-correct register dumps, frequency set/get across band limits, zero-frequency power-down compatibility, mute and mono/stereo controls, signal/AFC reporting on hardware, remove-time power-down, and `v4l2-compliance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5764.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.c

Purpose: provides a reusable V4L2 helper for Philips TEA5777 AM/FM tuner chips. Bus-specific drivers supply 6-byte write and 3-byte read register callbacks while this file implements V4L2 frequency, tuner, seek, mute, and band behavior.

Important APIs and functions: exported functions are `radio_tea5777_init`, `radio_tea5777_exit`, and `radio_tea5777_set_freq`. Core helpers include `tea5777_freq_to_v4l2_freq`, `radio_tea5777_update_read_reg`, V4L2 ioctl handlers, hardware seek implementation, and `tea575x_s_ctrl` for mute. Static band descriptors cover FM and AM.

Control flow: initialization builds the default write register, tunes 90.5 MHz FM, initializes the embedded video device and mutex, creates a mute control, applies control defaults, and registers a radio node. Frequency setting selects AM for low frequencies when `has_am` is set, otherwise FM, converts V4L2 units to chip PLL values including IF offsets, writes the callback register, invalidates cached read status, and stores the rounded actual frequency. Tuner get reads status, reports mono/stereo and signal, then invalidates read status for freshness. Hardware seek optionally programs bounded limits by writing bottom/top frequencies with `PROGBLIM`, starts a search, polls read status until station found, band limit, timeout, or signal interruption, then clears search and restores original frequency on failure.

State and persistence: state lives in caller-owned `struct radio_tea5777`: current band/frequency/audmode, seek range cache, read and write register cache, quirk flags, V4L2 objects, callbacks, card/bus strings, and mutex. No persistent storage exists; register state is restored by reprogramming.

Dependencies and integration points: depends on V4L2 device/dev/fh/ioctl/control/event APIs and bus-specific implementations of `radio_tea5777_ops`. `radio-shark2.c` is a direct consumer in this subset.

Risks: the file retains `tea575x_*` names for TEA5777 operations, which can confuse maintainers. In AM setup it clears `TEA5777_W_AM_AGCRF_MASK` twice, likely intending one clear for AGCIF. Seek is blocking and uses `schedule_timeout_interruptible`, so nonblocking callers are rejected. The helper assumes caller has initialized card/bus strings and stable callbacks. `write_before_read` can trigger writes during status reads.

Test signals: unit-like callback fakes for register values, FM/AM frequency conversion round trips, mono/stereo changes, mute bit writes, bounded seek success/failure/timeout, write-before-read behavior with radioSHARK2, V4L2 compliance, and module unload freeing controls after video unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.h -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.h

Purpose: declares the bus-independent TEA5777 helper interface and state structure used by radio drivers that provide raw register transport.

Important APIs and types: `struct radio_tea5777_ops` contains `write_reg` and `read_reg` callbacks for the TEA5777 6-byte write and 3-byte read registers. `struct radio_tea5777` embeds V4L2 file/video/control state, current band/frequency/audmode, seek limits, read/write register caches, quirk flags, callback pointer, private data, and card/bus strings. Exported functions are `radio_tea5777_init`, `radio_tea5777_exit`, and `radio_tea5777_set_freq`.

Control flow: consumers allocate a containing device structure, fill `v4l2_dev`, `ops`, `private_data`, capability flags such as `has_am` and `write_before_read`, and identity strings, then call `radio_tea5777_init`. The helper registers the V4L2 radio node and later uses callbacks to program hardware. Consumers call `radio_tea5777_exit` during teardown.

State and persistence: all helper state is caller-owned and mutable at runtime. Cached register values and seek bounds are volatile and represent the last helper view of hardware.

Dependencies and integration points: includes V4L2 core headers and Linux radio frequency definitions. It is consumed by `radio-shark2.c` in this subset and can be reused by other bus wrappers.

Risks: the header exposes the full mutable helper structure rather than an opaque handle, so consumers can accidentally corrupt invariants. Fixed `card[32]` and `bus_info[32]` buffers require careful string copying. The defined `TEA575X_FMIF` and `TEA575X_AMIF` names are legacy/misleading for TEA5777.

Test signals: compile coverage for consumers, structure initialization by `radio-shark2.c`, callback invocation ordering, string truncation behavior, and helper init/exit under probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5777.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-terratec.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-terratec.c

Purpose: implements board-specific support for the TerraTec ActiveRadio ISA card using the shared `radio-isa` V4L2 framework.

Important APIs and functions: module lifecycle is `terratec_init` and `terratec_exit`. Hooks are `terratec_alloc`, `terratec_s_mute_volume`, `terratec_s_frequency`, and `terratec_g_signal`, collected in `terratec_ops`.

Control flow: the radio-ISA framework probes the single supported port `0x590`, reserves two I/O bytes, registers the radio device, and calls this file's hooks for operations. Frequency setting converts V4L2 units to a legacy tuner value with 10.7 MHz IF adjustment, fills a 25-bit buffer by repeated subtraction, and clocks bits through write-enable/data/clock port toggles. Volume/mute writes an 8-bit digital volume pattern to `io + 1`; mute forces volume zero. Signal reads bit 1 at the base port, where set means no signal.

State and persistence: per-card state is the generic `radio_isa_card`; this file has only module parameters and static driver metadata. Hardware state is volatile and set through ISA I/O.

Dependencies and integration points: depends on `radio-isa.h`, ISA registration, direct I/O, and V4L2 behavior supplied by the shared framework. It advertises stereo and maximum volume 10.

Risks: only one I/O port is supported despite historical uncertainty. Frequency conversion is opaque and comment-marked as poorly understood. Volume programming writes only data bits without explicit visible clocking in this driver, relying on card behavior. There is no RDS support despite hardware notes mentioning SAA6588.

Test signals: probe at 0x590, `v4l2-compliance`, frequency tuning at low/mid/high FM values, mute/volume behavior on speaker output, signal bit readings, and unload releasing the requested region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-terratec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-timb.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-timb.c

Purpose: implements a platform V4L2 radio wrapper for Timberdale FPGA designs. It delegates actual tuner and DSP behavior to I2C V4L2 subdevices described by platform data.

Important APIs and functions: platform lifecycle is `timbradio_probe` and `timbradio_remove`. V4L2 ioctl wrappers are `timbradio_vidioc_querycap`, tuner get/set, and frequency get/set, all forwarding to `sd_tuner` except querycap. File operations use standard V4L2 fh open/release/poll/ioctl paths.

Control flow: probe requires `timb_radio_platform_data`, allocates managed `struct timbradio`, copies platform data, initializes a mutex and video device, registers a standalone V4L2 device, creates tuner and DSP I2C subdevices on the configured adapter, assigns the DSP control handler to the parent V4L2 device, registers the radio video node, and stores driver data. Ioctls route tuner/frequency calls to the tuner subdevice via `v4l2_subdev_call`.

State and persistence: state is device-managed memory containing copied platform data, tuner/DSP subdevice pointers, video/V4L2 objects, and mutex. Persistence depends on child devices; this wrapper does not cache frequency or tuner state.

Dependencies and integration points: depends on platform data from `linux/platform_data/media/timb_radio.h`, I2C adapters, V4L2 subdevice registration helpers, and child tuner/DSP drivers. It integrates the DSP controls into the parent radio node by reusing `sd_dsp->ctrl_handler`.

Risks: `i2c_get_adapter` return values are not checked or released, which can leak adapter references or fail unclearly. Probe registers the V4L2 device with NULL parent rather than `&pdev->dev`. There is no explicit cleanup of child subdevices beyond `v4l2_device_unregister`. Missing platform data is fatal.

Test signals: platform-device instantiation with valid/invalid platform data, missing I2C adapter behavior, tuner/DSP subdevice creation, forwarded tuner/frequency ioctls, DSP controls on the parent node, remove cleanup, and `v4l2-compliance` with the actual subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-timb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-trust.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-trust.c

Purpose: implements support for the Trust FM Radio ISA card through the shared `radio-isa` framework, including bit-banged I2C programming of the tuner and audio processor.

Important APIs and functions: module lifecycle is `trust_init`/`trust_exit`. Board hooks include `trust_alloc`, `trust_initialize`, `trust_s_mute_volume`, `trust_s_frequency`, `trust_s_stereo`, `trust_g_signal`, and `trust_s_ctrl`. `write_i2c` implements a simple variadic bit-banged I2C write over the ISA port.

Control flow: the framework probes configured or known ports `0x350` and `0x358`, allocates `struct trust`, and registers a V4L2 radio node. Initialization sets output latch defaults, configures TDA7318 speaker attenuation/input gain, and adds bass/treble controls. Frequency setting converts V4L2 frequency to 10 kHz plus 10.7 MHz IF and writes a five-byte TSA6060T sequence. Mute/volume changes update a latch bit and write TDA7318 volume. Stereo changes update another latch bit. Signal reads the port 100 times and reports no signal if bit 0 was ever seen set.

State and persistence: `struct trust` embeds `radio_isa_card` and keeps the current output latch byte `ioval`. The shared framework tracks frequency, mute, stereo, and controls. Hardware state is volatile.

Dependencies and integration points: depends on `radio-isa.h`, direct port I/O, V4L2 controls supplied by the framework, and the TDA7318/TSA6060T serial protocols implemented by bit-banged writes.

Risks: `write_i2c` does not sample or enforce ACKs; it just clocks an acknowledge bit. Signal detection ORs repeated reads, so transient noise can force no-signal. Bass/treble table mapping is non-linear and hardware-specific. Variadic I2C writes are easy to misuse if byte count and arguments diverge.

Test signals: probe both jumper-selected ports, initialization programming on a logic analyzer, volume/mute/stereo/bass/treble controls, frequency conversion against known stations, signal reporting stability, and `v4l2-compliance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-trust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-typhoon.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-typhoon.c

Purpose: supports Typhoon/EcoRadio ISA cards through the shared `radio-isa` framework, implementing the card's non-linear frequency programming and coarse speaker-volume mute behavior.

Important APIs and functions: module lifecycle is `typhoon_init` and `typhoon_exit`. Board hooks are `typhoon_alloc`, `typhoon_s_frequency`, and `typhoon_s_mute_volume` in `typhoon_ops`.

Control flow: initialization validates the `mutefreq` module parameter in kHz, then registers an ISA driver for ports `0x316` and `0x336`. Frequency setting approximates the hardware transfer curve with a third-order polynomial and writes the resulting bits to offsets `io + 4`, `io + 6`, and `io + 8`. Mute/volume maps a 16-bit framework volume to two hardware bits. When volume reaches zero, the driver marks the card muted and tunes to a configured noise frequency; when volume becomes nonzero, it retunes to the cached station.

State and persistence: `struct typhoon` embeds the generic ISA card and a `muted` flag. The framework stores cached frequency and volume. Hardware state is transient and controlled only through port writes.

Dependencies and integration points: depends on `radio-isa.h`, ISA bus registration, direct port I/O, and V4L2 behavior from the framework. It advertises stereo and maximum volume 3, though hardware notes say stereo behavior is uncertain.

Risks: muting by detuning can produce noise rather than silence and can surprise users watching frequency-sensitive hardware. The polynomial tuning approximation is empirical. The line output has no mute/volume support despite V4L2 controls. The I/O region size is 8 while writes use `io + 8`, which is at the first byte beyond an 8-byte region if size semantics are exclusive.

Test signals: module parameter validation, requested-region coverage for all offsets, frequency tuning accuracy across band, mute/unmute retuning to `mutefreq` and back, volume step mapping, and `v4l2-compliance` on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-typhoon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-zoltrix.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/radio-zoltrix.c

Purpose: implements the Zoltrix Radio Plus ISA card using the shared `radio-isa` framework, including custom frequency programming, volume/mute, stereo forcing, signal, and rx-subchannel detection.

Important APIs and functions: module lifecycle is `zoltrix_init`/`zoltrix_exit`. Board hooks are `zoltrix_alloc`, `zoltrix_s_mute_volume`, `zoltrix_s_frequency`, `zoltrix_g_rxsubchans`, `zoltrix_g_signal`, and `zoltrix_s_stereo`.

Control flow: the framework probes ports `0x20c` and `0x30c`. Volume/mute writes zero twice and reads a confirmation port when muted, or writes `vol - 1`, sleeps, and reads another port when unmuted. Frequency setting rejects zero, computes an encoded value from V4L2 frequency, merges it and stereo mode into a 64-bit bitmask, sends a reset/prepare sequence, clocks 45 bits through port patterns with microsecond delays, sends a termination sequence, then reapplies cached mute/volume. Stereo changes retune the current frequency to update the programmed bit. Signal and stereo-detect reads compare two samples after volume writes.

State and persistence: `struct zoltrix` embeds the framework card and tracks current volume and mute state for reapplication after frequency changes. Framework state holds frequency and stereo. Hardware state is volatile.

Dependencies and integration points: depends on `radio-isa.h`, direct port I/O, delays, and V4L2 behavior from the shared radio-ISA layer. It is explicitly for the original Zoltrix Radio Plus, not later 108/Windows variants.

Risks: signal/stereo detection is documented as inconsistent and relies on magic values (`0xcf`, `0xdf`, `0xef`). Frequency programming is bitmask-heavy and timing-sensitive. Retuning to apply stereo can fail if cached frequency is invalid. Low volume behavior is known to be non-linear.

Test signals: probe at both ports, full-band tuning compared with real stations, mute/volume reapplication after tuning, stereo force and detection behavior, signal stability, zero-frequency rejection, and `v4l2-compliance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-zoltrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/saa7706h.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/saa7706h.c

Purpose: implements a V4L2 I2C subdevice driver for the Philips SAA7706H car radio DSP. It exposes a mute control and programs a fixed DSP/clock/audio register sequence for unmute.

Important APIs and functions: I2C lifecycle is `saa7706h_probe` and `saa7706h_remove`. Register access helpers are `saa7706h_i2c_send`, `saa7706h_i2c_transfer`, `saa7706h_set_reg24`, `saa7706h_set_reg16`, and `saa7706h_get_reg16`, with `_err` variants for chained programming. Audio state changes are `saa7706h_mute`, `saa7706h_unmute`, and `saa7706h_s_ctrl`.

Control flow: probe checks adapter functionality, allocates state, initializes a V4L2 I2C subdevice, creates `V4L2_CID_AUDIO_MUTE`, reads DSP1 ROM version, warns if it differs from the supported value, and starts muted. Unmute first resets DSP1/DSP2 with PLL settings, sleeps 1 ms, clears reset, then writes a long fixed series of 16-bit and 24-bit registers for clock generation, input sensitivity, DSP pointers, volume/attenuation, and routing. Chained writes stop after the first error. Mute resets both DSPs and marks state muted.

State and persistence: `struct saa7706h_state` holds the V4L2 subdevice, control handler, and muted flag. Hardware register programming persists only while powered and is reissued on unmute.

Dependencies and integration points: depends on I2C, V4L2 subdevice/control APIs, and parent media drivers that instantiate and use the subdevice. The ops table is empty because control handling is the main exported behavior.

Risks: the functionality check asks for SMBus byte data, but the driver actually uses raw I2C master send/transfer. The unmute sequence is a large set of magic constants with minimal documentation. Probe failure manually unregisters/free state and must match subdevice init expectations. Only mute is exposed; other DSP capabilities are fixed.

Test signals: I2C transfer failure injection through the chained unmute sequence, ROM version warning, mute/unmute control behavior, parent subdevice registration, remove-time mute, and hardware audio path validation after the fixed programming sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/saa7706h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Kconfig

Purpose: defines Kconfig options for the Silicon Labs Si470x FM radio receiver support split into common, USB, and I2C modules.

Important APIs and symbols: `RADIO_SI470X` is the common tristate depending on `VIDEO_DEV`. `USB_SI470X` depends on `USB && RADIO_SI470X` and builds USB support. `I2C_SI470X` depends on `I2C && RADIO_SI470X` and builds I2C support.

Control flow: selecting the common symbol enables shared Si470x V4L2 code. Selecting a bus symbol causes the Makefile to build the corresponding bus transport module. Help text lists known USB products and recommends `SND_USB_AUDIO` when USB devices are used for audio rather than only RDS.

State and persistence: no runtime state. These symbols persist in kernel build configuration and determine which modules are available.

Dependencies and integration points: integrates with the media radio Kconfig tree, V4L2 core, USB, I2C, and ALSA USB audio recommendations in documentation. The module names in help text match the Makefile objects.

Risks: the common module alone is not useful without a bus-specific frontend. USB help text can become stale as IDs are added. There is no explicit select for sound support because audio is separate and optional.

Test signals: `menuconfig` visibility, allmodconfig and randconfig coverage, module name/help consistency with the Makefile, and configurations with common-only, USB, I2C, and both bus drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Makefile

Purpose: maps Si470x Kconfig symbols to kbuild object files.

Important APIs and entries: `obj-$(CONFIG_RADIO_SI470X)` builds `radio-si470x-common.o`, `obj-$(CONFIG_USB_SI470X)` builds `radio-si470x-usb.o`, and `obj-$(CONFIG_I2C_SI470X)` builds `radio-si470x-i2c.o`.

Control flow: kbuild compiles the common helper as its own module and bus-specific USB/I2C modules separately according to selected tristates. Bus modules depend on exported symbols from the common module.

State and persistence: no runtime state. Build output is determined by `.config`.

Dependencies and integration points: depends on Kconfig symbols from the same directory and source file names. The common file exports `si470x_ctrl_ops`, `si470x_viddev_template`, `si470x_set_freq`, `si470x_start`, and `si470x_stop` for bus modules.

Risks: adding a new bus transport requires both Kconfig and Makefile updates. If common and bus symbols are built with incompatible module/link settings, unresolved export issues would appear at build time.

Test signals: per-symbol builds for common, USB, I2C, and combined configurations; module dependency generation; and `make M=drivers/media/radio/si470x`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-common.c

Purpose: implements bus-independent V4L2 behavior for Silicon Labs Si470x FM radio receivers. USB and I2C frontends provide register read/write and open/release/querycap callbacks; this file handles tuning, seek, RDS read/poll, volume/mute controls, and common ioctl tables.

Important APIs and functions: exported symbols are `si470x_ctrl_ops`, `si470x_viddev_template`, `si470x_set_freq`, `si470x_start`, and `si470x_stop`. Internal helpers include `si470x_set_band`, `si470x_set_chan`, `si470x_get_step`, `si470x_get_freq`, `si470x_set_seek`, and `si470x_rds_on`. File ops implement RDS `read`, `poll`, delegated `open`, and delegated `release`. V4L2 handlers cover tuner/frequency/seek/band enumeration and controls.

Control flow: bus drivers initialize `struct si470x_device` callbacks and copy `si470x_viddev_template`. Starting the radio programs `POWERCFG`, enables RDS/STC interrupts and de-emphasis, programs band/spacing/volume in `SYSCONFIG2`, then restores the channel. Frequency setting clamps within current band and converts to channel number based on spacing. If a requested frequency is outside the current band, the common ioctl switches to the 76-108 MHz band before tuning. Hardware seek optionally switches to an exact requested band, starts seek bits, waits for completion, clears seek, and reports timeout as `-ENODATA`. RDS read/poll lazily enables RDS and drains 3-byte V4L2 RDS blocks from the circular buffer filled by bus interrupt handlers.

State and persistence: common state lives in `struct si470x_device`: register cache, current band, circular RDS buffer indices, waitqueue, completion, and bus callbacks. It is volatile and owned by the USB/I2C device.

Dependencies and integration points: depends on `radio-si470x.h`, V4L2 core/control/event APIs, completion/waitqueue primitives, and bus-specific register operations. It integrates with USB/I2C files through exported symbols and function pointers.

Risks: RDS buffer read/copy is not explicitly locked despite comments/history about avoiding sleeping under locks; concurrent producer/consumer races rely on simple indices. `copy_to_user` failure breaks without returning `-EFAULT` if some paths are hit. Seek band selection requires exact low/high matches when bounds are supplied. `FREQ_MUL` is defined using a floating literal in the header snapshot, which is unusual.

Test signals: common V4L2 compliance through both USB and I2C drivers, frequency step/band conversion tests for 50/100/200 kHz, tune and seek completion timeouts, RDS read/poll blocking and wraparound, volume/mute controls updating cached registers, and module symbol dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-i2c.c

Purpose: implements the I2C transport and interrupt handling for Si470x FM radio receivers, wiring the common Si470x V4L2 logic to raw I2C register transfers and GPIO reset.

Important APIs and functions: I2C lifecycle is `si470x_i2c_probe`, `si470x_i2c_remove`, and optional PM suspend/resume. Register callbacks are `si470x_get_register`, `si470x_set_register`, and `si470x_get_all_registers`. File callbacks are `si470x_fops_open` and `si470x_fops_release`. Interrupt processing is `si470x_i2c_interrupt`.

Control flow: probe allocates managed state, initializes callbacks, registers V4L2 and controls, copies the common video template, optionally asserts reset GPIO, powers up the chip, reads all registers and firmware version, sets an initial 87.5 MHz frequency, allocates an RDS buffer, requests a threaded falling-edge IRQ, registers the video device, and stores client data. Opening the first handle starts the common radio path and enables RDS/STC interrupt bits/GPIO2 interrupt output. The IRQ reads `STATUSRSSI`, completes tune/seek waiters on STC, checks RDS enable and readiness, reads the RDS register window, converts four RDS blocks to 3-byte V4L2 block records with error flags, updates the circular buffer, and wakes readers.

State and persistence: uses `struct si470x_device` with I2C client, reset GPIO, register cache, buffer indices, completion, mutex, and V4L2 objects. Device state is volatile; reset GPIO is driven low on remove.

Dependencies and integration points: depends on I2C block transfers, GPIO descriptor API, threaded IRQs, V4L2 core/controls, and exported common Si470x helpers. Device-tree matching supports `silabs,si470x`.

Risks: `devm_request_threaded_irq` is called even if `client->irq` is zero, which depends on board data providing a valid interrupt. `si470x_set_register` writes the full writable register window even when one register changes. Buffer producer updates are not locked against read-side consumers. Suspend only sets DISABLE and resume only ENABLEs without fully restoring common start configuration.

Test signals: probe with and without reset GPIO, firmware warning, valid/invalid IRQ board data, RDS interrupt block decoding and overflow, tune/seek completion via STC, suspend/resume retaining usability, remove lowering reset GPIO, and `v4l2-compliance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-usb.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-usb.c

Purpose: implements the USB HID transport, RDS interrupt URB handling, LED status, and probe/disconnect paths for USB Si470x FM radio receivers.

Important APIs and functions: USB lifecycle is `si470x_usb_driver_probe`, `si470x_usb_driver_disconnect`, suspend/resume callbacks, and `si470x_usb_release`. HID helpers are `si470x_get_report`, `si470x_set_report`, register callbacks, `si470x_get_all_registers`, `si470x_set_led_state`, and `si470x_get_scratch_page_versions`. RDS interrupt processing is `si470x_int_in_callback`. `si470x_start_usb` starts the interrupt URB and common radio configuration.

Control flow: probe allocates state and USB buffers, finds an interrupt IN endpoint, allocates an URB, disambiguates the shared Raremono/Si470x USB ID by reading device ID, registers V4L2 state and controls, reads chip and scratch versions, sets LED connect state, allocates the RDS buffer, starts the interrupt URB and common radio, tunes 87.5 MHz, and registers the video node. HID register access uses class GET_REPORT/SET_REPORT on endpoint 0. The interrupt callback handles STC completion, decodes RDS register reports into 3-byte V4L2 RDS blocks when synchronized, updates the circular buffer, wakes readers, and resubmits while running. Disconnect marks V4L2 disconnected, unregisters video, kills URB, clears interface data, and releases via V4L2 refcount.

State and persistence: `struct si470x_device` includes USB device/interface, HID control buffer, interrupt buffer/endpoint/URB/running flag, version bytes, common register cache, RDS buffer indices, completion, lock, and V4L2 objects. Runtime state is freed in `si470x_usb_release`.

Dependencies and integration points: depends on USB HID class reports, interrupt URBs, V4L2 common Si470x exports, V4L2 controls/events/read, unaligned endian helpers, and USB audio for actual sound on most devices. USB IDs include multiple known products and share one ID with Raremono, handled by runtime detection.

Risks: `int_in_running` is a plain int updated across URB callback, suspend, and disconnect with minimal synchronization. The callback comments question whether mutex locking is needed around shared state. Probe starts the radio before registering the video device. RDS buffer overflow drops oldest data silently. Suspend/resume support is noted as historically problematic but present.

Test signals: HID report read/write failures, shared-ID detection against Raremono, interrupt endpoint validation, URB resubmit behavior under errors, RDS synchronization/error flags, LED reports, suspend/resume with active readers, disconnect races, and V4L2 compliance including read/poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-usb.c -->
