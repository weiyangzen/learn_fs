# sources/distributed-fs/ceph-client/drivers/media/radio/radio-sf16fmi.c

Purpose: implements direct V4L2 support for MediaForte SF16-FMI/FMP/FMD ISA radio cards, including optional ISA PnP discovery, LM7000 tuner programming, mute, and signal-strength reads.

Important APIs and functions: module lifecycle is `fmi_init`/`fmi_exit`. Tuner programming goes through `fmi_set_freq` and `lm7000_set_freq` with the callback `fmi_set_pins`. V4L2 handlers cover querycap, tuner get/set, frequency get/set, and mute control through `fmi_s_ctrl`. PnP probing is in `isapnp_fmi_probe`.

Control flow: initialization probes ISA PnP first when no `io` parameter is supplied, then falls back to ports `0x284` and `0x384`. It reserves two I/O ports, performs simple presence checks, registers a standalone V4L2 device and mute control, initializes the video device, starts muted at the minimum frequency, and registers the radio node. Frequency changes clamp to 87-108 MHz and round to 800-unit steps before bit-banging LM7000 pins. Signal measurement toggles the STRQ bit, waits 143 ms, reads `io + 1`, and restores output state.

State and persistence: one static `struct fmi` holds V4L2 state, I/O base, mute flag, current frequency, and mutex. PnP attachment is tracked globally in `dev` and `pnp_attached`. Hardware programming is not persistent across unload.

Dependencies and integration points: depends on ISA PnP APIs, I/O port ownership, `lm7000.h`, V4L2 device/control/event helpers, and direct port I/O. Unlike the `radio-isa` conversions, this driver owns its V4L2 registration directly.

Risks: static single-card state limits multi-card support. Error paths after control initialization can miss releasing the reserved I/O region/PnP attachment in one handler-error branch. Signal polling sleeps while holding the device mutex. The hardware presence check is heuristic. Frequency rounding means get-frequency may report the requested cached value rather than exact programmed step.

Test signals: PnP and manual port probe paths, failed-control initialization cleanup, `v4l2-compliance`, mute/unmute port writes, LM7000 tuning across band edges, signal read timing on real hardware, and unload releasing PnP/I/O resources.
