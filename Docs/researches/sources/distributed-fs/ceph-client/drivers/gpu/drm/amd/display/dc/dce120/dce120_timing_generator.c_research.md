## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c

Purpose: DCE12/SOC15 timing-generator implementation. It ports DCE110 behavior to SOC15 register access helpers, adds DCE12 timing constraints, and provides a DCE120-specific `timing_generator_funcs` table.

Important APIs: `dce120_timing_generator_construct` plus static callbacks for timing validation, CRTC enable, blanking/color programming, DRR, scanout position, advanced request, test patterns, vertical interrupts, GSL/reset, CRC configure/read, and enable-state queries. It reuses shared DCE110 functions for BIOS timing programming, disable, counter moving, and two-pixels-per-container logic.

Control flow: register writes go through `CRTC_REG_UPDATE*`/`CRTC_REG_SET*` macros over SOC15 offsets. Timing validation first calls DCE110 validation, then checks DCE12 minimum vblank and sync widths. Program timing chooses VBIOS or direct blanking. CRC and test-pattern flows mirror DCE110 with SOC15 accessors.

State and dependencies: state is `dce110_timing_generator` plus SOC15 offsets, DCE12 min constraints, and hardware registers. Dependencies include DCE12 offset/sh-mask headers, `soc15_hw_ip.h`, `vega10_ip_offset.h`, and shared DCE110 timing definitions. Risks include macro definitions for `_4` and `_5` passing `3` as the field count, mixed reuse of DCE110 functions that may read non-SOC15 register addresses, TODOs around reset sources, and direct static-screen side effects in DRR. Test signals are DCE12 modesets, SOC15 register access validation, timing-bound rejection, DRR, sync/reset, test patterns, vertical interrupts, and CRC.
