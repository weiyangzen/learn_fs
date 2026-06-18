# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/nid.h

## Purpose
`nid.h` is the Northern Islands/Cayman-era register and packet-definition header for the Radeon DRM driver. It does not implement behavior directly; it names memory-mapped register offsets, bit fields, packet builders, command opcodes, async-DMA packet formats, and ASIC limits used by the NI, Cayman, Trinity/Aruba, UVD, display AUX, VM, memory-controller, power-management, and command-processor code.

## Important APIs, Types, And Functions
The file exports preprocessor constants rather than C functions or structs. Important groups are Cayman resource caps (`CAYMAN_MAX_*`), golden address configurations, SRBM/GRBM status and soft-reset bits, VM L1/L2/context/protection-fault registers, MC aperture and DRAM timing registers, HDP flush/coherency registers, shader/texture/color/depth backend disable masks, SCLK/MCLK/SMC power-management registers, CAC weight and throttle fields, PCIe link fields, UVD ring/status registers, PM4 `PACKET0`, `PACKET2`, `PACKET3` helpers and PACKET3 opcodes, and async DMA ring/IB/fence/trap/copy/write packet helpers.

## Control Flow
There is no runtime control flow in the header. Its macros encode control flow for other modules by making hardware state machines addressable: reset code polls `SRBM_STATUS`/`GRBM_STATUS` bits, VM code invalidates TLB/L2 through `VM_L2_CNTL2`, ring emitters build PM4 packets with `PACKET*`, DMA emitters build DMA words with `DMA_PACKET`/`DMA_IB_PACKET`, and DPM code programs PLL, voltage, CAC, and memory-timing fields.

## State, Persistence, And Dependencies
The persistent state controlled through this header lives in GPU registers and command streams, not in the header itself. Register writes alter hardware-visible state such as VM contexts, ring pointers, memory timing, clocks, PCIe link configuration, UVD state, and reset bits. The header depends on shared Radeon packet constants such as `RADEON_PACKET_TYPE0`, `RADEON_PACKET_TYPE3`, and `REG_SET`, plus the driver convention that register offsets are byte offsets.

## Integration Points
The definitions are consumed throughout the Radeon ASIC files for Northern Islands and related hardware, including interrupt/reset paths, ring setup, VM fault handling, power management, UVD setup, DisplayPort AUX transactions, and DMA command emission. The PM4/DMA packet helpers are an ABI boundary with GPU firmware and hardware parsers: callers must pass exactly the field widths expected by the command processor.

## Risks
Because this is a raw hardware contract, wrong masks, shifts, or offsets can cause hangs, memory corruption, failed reset, incorrect VM fault handling, or broken power management. Several macro names are generic (`ENABLE`, `RESET`, `BYPASS`, `INDEX`) and depend on include ordering and local context. Field builders generally do not mask every input, so callers must range-check values. Duplicate concepts such as soft reset bits in SRBM and GRBM need careful selection for the target block. The header is also architecture-sensitive because packet words and register offsets must match the hardware documentation exactly.

## Test Signals
Useful signals are successful NI/Cayman bring-up, ring tests, IB tests, DMA copy/fill tests, VM fault decode and TLB invalidate tests, UVD ring tests, DisplayPort AUX reads/writes, suspend/resume reset tests, and DPM clock/voltage transitions. Static checks should watch for macro redefinition warnings and ensure packet-builder users mask or bound user-derived fields.
