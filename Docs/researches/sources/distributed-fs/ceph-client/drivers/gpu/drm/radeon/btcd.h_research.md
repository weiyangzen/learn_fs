# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/btcd.h

## Purpose
This header defines BTC-family power-management, memory-controller, clock-gating, and PCIe register offsets and bitfields used by Radeon DPM code. It is a register map fragment for Barts/Turks/Caicos rather than an executable module.

## Important APIs, Types, and Functions
The file exposes macros for `GENERAL_PWRMGT`, `TARGET_AND_CURRENT_PROFILE_INDEX`, `CG_BIF_REQ_AND_RSP`, `SCLK_PSKIP_CNTL`, `CG_ULV_CONTROL`, `CG_ULV_PARAMETER`, memory arbitration registers such as `MC_ARB_DRAM_TIMING`, `MC_ARB_RFSH_RATE`, and `MC_ARB_BURST_TIME`, memory sequencer timing and LP registers, clock-gating handshake register `MC_SEQ_CG`, display reset selector `LB_SYNC_RESET_SEL`, and PCIe link control register `PCIE_LC_SPEED_CNTL`.

Bitfield helpers follow the common Radeon style: value constructors like `POWERMODE0(x)`, masks like `POWERMODE0_MASK`, and shifts like `POWERMODE0_SHIFT`. They cover global DPM enable bits, AC/DC state, voltage control, Gen2 PCIe enablement, client clock-gating handshakes, memory power-mode fields, memory burst states, GDDR5 detection, and PCIe speed/voltage override fields.

## Control Flow
There is no runtime flow in this header. Its macros are consumed by `btc_dpm.c` and related DPM code to read-modify-write registers, extract current DPM profile indices, mirror normal memory timing into low-power timing registers, program ULV timing, manage clock-gating request/response bits, and control dynamic PCIe Gen2 transitions.

## State and Persistence Behavior
The header stores no C state. The registers it names are persistent hardware state while the device is powered: DPM enablement, thermal protection, voltage management, memory timing, refresh/burst timing, clock-gating handshakes, low-power memory sequencer copies, and PCIe link-speed configuration.

## Dependencies and Integration Points
The macros are used with Radeon register accessors such as `RREG32`, `WREG32`, `WREG32_P`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`. They integrate tightly with BTC DPM, RV770/Cypress helper code, ATOMBIOS timing data, and SMC-managed power-state transitions.

## Risks
Incorrect offsets or masks would cause writes to the wrong hardware registers or preserve the wrong bits during read-modify-write operations. Some fields are reused in tight transition sequences, such as PCIe Gen2 enable/disable and memory LP timing setup, where a bad bit definition can produce hangs or link instability. Because these are preprocessor macros, type checking and range checking are minimal.

## Test Signals
Signals are primarily build coverage plus hardware runtime validation: DPM enable/disable, current profile index reads, ULV entry/exit, dynamic memory clock switching, clock-gating enable/disable, thermal protection toggles, and PCIe Gen2 link transitions on BTC boards.
