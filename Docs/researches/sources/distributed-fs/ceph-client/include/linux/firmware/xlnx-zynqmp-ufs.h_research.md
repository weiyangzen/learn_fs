# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-zynqmp-ufs.h

## Purpose
This header exposes small AMD/Xilinx firmware helpers for UFS/MPHY bring-up on ZynqMP-family firmware platforms.

## APIs, types, and control flow
The real API, enabled through reachable `CONFIG_ZYNQMP_FIRMWARE`, includes readiness probes for MPHY TX/RX configuration and SRAM initialization, a call to set SRAM bypass, and a call to fetch UFS calibration values. Each writes results through caller-provided `bool *` or `u32 *` output pointers. Disabled stubs uniformly return `-ENODEV`.

## State and dependencies
No local state is defined. State is firmware and hardware init state, observed or mutated through the PM firmware channel. Dependencies are minimal but the header is included by `xlnx-zynqmp.h` and UFS platform drivers.

## Integration, risks, and tests
UFS host initialization can use these calls to decide when MPHY/SRAM setup is ready and to program calibration. Risks include assuming output values are initialized on error, polling indefinitely, calling bypass at the wrong phase, and missing firmware availability checks. Tests should cover disabled stubs, timeout behavior around readiness polling, calibration output validation, and probe deferral or failure handling when firmware reports not-ready states.
