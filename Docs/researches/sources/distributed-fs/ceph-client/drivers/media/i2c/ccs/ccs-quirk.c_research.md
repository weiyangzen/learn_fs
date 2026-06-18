# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-quirk.c

## Purpose
`ccs-quirk.c` provides sensor-specific workarounds for known SMIA/CCS modules that do not behave fully according to generic CCS limits or recommended register programming.

## Important APIs, Types, and Functions
The file exports quirk objects `smiapp_jt8ew9_quirk`, `smiapp_imx125es_quirk`, `smiapp_jt8ev1_quirk`, and `smiapp_tcm8500md_quirk`. Helper `ccs_write_addr_8s()` writes arrays of `struct ccs_reg_8`. Quirk callbacks include limit replacement, post-power-on register sequences, pre-stream-on, post-stream-off, and init hooks.

## Control Flow
`ccs_identify_module()` selects a matching quirk from `ccs_module_idents[]`. During probe and runtime, `ccs-core.c` calls `limits`, `post_poweron`, `pre_streamon`, `post_streamoff`, and `init` through `ccs_call_quirk()`. JT8EW9 adjusts frame skip and analog gain limits and writes Toshiba-recommended registers after power-on. IMX125ES writes a small power-on register sequence. JT8EV1 adjusts limits, writes multiple recommendation registers, applies extra registers for 9.6 MHz external clock, clears/restores one register around streaming, and sets PLL lane-speed flags. TCM8500MD raises the minimum PLL input clock limit.

## State and Persistence Behavior
Quirks mutate per-device cached limits, `frame_skip`, and PLL fields, and write volatile sensor registers after each power-on or stream transition. They do not persist state outside the device.

## Dependencies and Integration Points
The file depends on `ccs.h`, `ccs-limits.h`, CCI register writes through `ccs_write_addr()`, and core identity matching. It integrates with probe, runtime power-on, stream start/stop, and PLL setup.

## Risks and Edge Cases
Hard-coded manufacturer-specific register sequences are sensor revision and clock sensitive. JT8EV1 only has extra programming for 9.6 MHz external clock and warns for other rates. Limit quirks must run after the generic limit cache is populated and before controls/PLL decisions rely on those limits. Failed quirk writes abort power-on or streaming.

## Test Signals
Test each matched module ID, especially JT8EW9 revisions below 0x0300, JT8EV1 at 9.6 MHz and other clocks, analog gain ranges after limit replacement, stream start/stop register side effects, and probe failure logging when a quirk write fails.
