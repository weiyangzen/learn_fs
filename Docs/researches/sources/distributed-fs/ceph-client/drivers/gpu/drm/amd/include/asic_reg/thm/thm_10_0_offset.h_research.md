<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_offset.h

## Purpose
`thm_10_0_offset.h` defines THM 10.0 MMIO register offsets for the `thm_thm_SmuThmDec` address block whose documented base address is `0x59800`. It maps thermal, TMON, SBI, SBRMI, SMBus, and remote temperature-monitor registers to symbolic `mm...` offsets and supplies a matching `..._BASE_IDX` macro for each register.

## Important APIs, Types, And Macros
The header exports constants only. There are no functions, structs, enums, or runtime objects.

Important register groups include:

- Thermal controller and interrupt registers from offsets `0x0000` through `0x000c`, including current temperature, HTC, thermal trip, CTF delay, GPIO PROCHOT control, thermal interrupt enable/control/status.
- TMON0 local data and control registers from `0x000d` through `0x0030`, including `RDIL0..15`, `RDIR0..15`, interrupt data, control, control2, and debug.
- Die/software temperature and thermal configuration registers at `0x0055` through `0x005e`, including `DIE1_TEMP`, `DIE2_TEMP`, `DIE3_TEMP`, `SW_TEMP`, `CG_MULT_THERMAL_CTRL/STATUS`, `CG_THERMAL_RANGE`, `THM_TMON_CONFIG`, `THM_TMON_CONFIG2`, and `THM_TMON0_COEFF`.
- Local thermal controller registers `THM_TCON_LOCAL0` through `LOCAL13` at `0x006e` through `0x007b`, plus `THM_PWRMGT` at `0x007d`.
- SBI/SBTSI/SBRMI registers from `0x0080` through `0x0098`, covering SBI address/data/control/timing, remote temperature, SBRMI command/write/read data, core-enable status, APIC status, and MCE status.
- SMBus and alert registers from `0x0099` through `0x00a7`, including control, block read/write command control, timing control, trigger, UDID, SMUSBI SMBus, and alert.
- Remote TMON window ranges: `THM_TMON0_REMOTE_START/END` through `THM_TMON3_REMOTE_START/END`, spanning `0x0100` through `0x01ff` by range endpoints.

All listed registers use `_BASE_IDX 0`.

## Control Flow
There is no local control flow. Consumer code uses these offsets with THM mask/default headers and AMDGPU MMIO helpers to read temperatures, configure interrupts, handle PROCHOT/thermal trips, program temperature monitor windows, and communicate over SBI/SBRMI/SMBus sideband interfaces.

## State And Persistence Behavior
The header is stateless, but the named registers hold thermal-management state:

- Temperature and status registers reflect live sensor, interrupt, and thermal-trip state.
- Control registers configure thermal thresholds, PROCHOT GPIO behavior, TMON behavior, power management, and interrupt routing.
- SBI, SBRMI, and SMBus registers hold sideband command/data/timing state.
- Remote TMON start/end ranges define monitored remote regions until reprogrammed.

Values persist in hardware until reset or rewritten by BIOS, firmware, SMU, or driver code.

## Dependencies
This header depends on the THM 10.0 register map and should be used with `thm_10_0_default.h` and the matching THM shift/mask header for field-level access. The `mm...` and `_BASE_IDX` macro names must match the AMDGPU register-access conventions.

## Integration Points
The offsets integrate with AMDGPU thermal and power-management code, SMU/PM firmware interactions, register dump tools, and sideband-management paths. They provide the address layer for temperature readings, thermal interrupt programming, SMBus/SBI/SBRMI transactions, and TMON remote monitoring on THM 10.0 ASICs.

## Risks
- Offset errors in thermal-control registers can break over-temperature protection or PROCHOT behavior.
- Misaddressed SMBus/SBI/SBRMI registers can corrupt sideband transactions and make platform-management failures hard to diagnose.
- Remote TMON ranges are represented by start/end offsets rather than every element in the range; code iterating those windows must derive intermediate addresses correctly.
- The base index is uniformly `0`; consumers must not assume multiple THM instances without checking the IP discovery data.
- Combining this offset header with another generation's shift/mask/default header can silently decode or program wrong fields.

## Test Signals
- Thermal sensor tests should read current, die, and software temperature registers and compare them with SMU-reported temperatures.
- Thermal interrupt tests should exercise enable/control/status paths and verify ACK/clear behavior through the companion mask header.
- PROCHOT and thermal-trip validation should confirm the expected registers at the documented offsets are affected.
- SMBus/SBI/SBRMI transaction tests should verify command/data/timing offsets against hardware traces.
- Register dump validation should confirm the THM 10.0 block starts at base `0x59800` and all offsets land on expected registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/thm/thm_10_0_offset.h -->
