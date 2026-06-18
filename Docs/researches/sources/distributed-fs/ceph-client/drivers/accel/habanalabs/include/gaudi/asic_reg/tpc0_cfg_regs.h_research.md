# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc0_cfg_regs.h

## Purpose

`tpc0_cfg_regs.h` is an auto-generated register-address map for the Gaudi TPC0 configuration block. It exports `mmTPC0_CFG_*` preprocessor constants that give absolute MMIO addresses for tensor descriptors, kernel launch state, TPC control/status, debug, MBIST, and queue-manager kernel descriptor registers. It contains no functions, types, or runtime logic; the macros are the API.

The address map starts at `0xE06400` for `mmTPC0_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` and ends at `0xE06E3C` for `mmTPC0_CFG_QM_SRF_31`. It is paired with `tpc0_cfg_masks.h`, which describes the bitfields stored at these addresses.

## Important APIs, Types, And Macros

The first contiguous region maps 16 direct kernel tensor descriptors. Each tensor occupies 0x38 bytes: base low/high, padding value, tensor config, and five dimension size/stride pairs. Tensor 0 starts at `0xE06400`; tensor 15 ends at `0xE0677C`. The layout is regular and lets code compute descriptor offsets where appropriate, although this header exposes every address as a distinct macro.

Following the tensor descriptors are direct kernel singleton registers: sync-object message/address at `0xE06780` and `0xE06784`, kernel base address low/high, TID base/size pairs for dimensions 0-4, `KERNEL_CONFIG`, `KERNEL_ID`, and `KERNEL_SRF_0` through `KERNEL_SRF_31` at `0xE067C0` through `0xE0683C`.

The central control/status region includes `ROUND_CSR`, `PROT`, `SEMAPHORE`, vector/scalar flags, LFSR polynomial, `STATUS`, config and shared-memory base registers, `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, icache base address registers, read/write rate-limit registers, `MSS_CONFIG`, TPC interrupt cause/mask, work-queue credits, ARUSER/AWUSER low/high registers, `OPCODE_EXEC`, LUT base address pairs, TSB config, debug-memory registers, in-flight/total counters, IRQ occupancy, and MBIST control/pattern/memory registers.

The final region maps queue-manager supplied kernel state. `mmTPC0_CFG_QM_TENSOR_0_BASE_ADDR_LOW` starts at `0xE06A00`, with the same 16-tensor descriptor stride through tensor 15 ending at `0xE06D7C`. It then maps `QM_SYNC_OBJECT_*`, `QM_KERNEL_BASE_ADDRESS_*`, `QM_TID_*`, `QM_KERNEL_CONFIG`, `QM_KERNEL_ID`, and `QM_SRF_0` through `QM_SRF_31` ending at `0xE06E3C`.

## Control Flow And State

There is no local control flow. The header defines stable addresses for hardware state. Software writes these addresses to configure TPC execution and reads them to observe status, counters, interrupts, and debug/MBIST results. Hardware state persists outside the driver and may be modified by hardware execution, reset, queue-manager activity, or direct MMIO writes.

Typical driver flow uses these addresses with offsets for each TPC instance. Gaudi code writes TPC0 addresses directly for TPC0 and computes per-instance offsets for TPC1-TPC7. For queue-managed launches, driver code writes `QM_KERNEL_BASE_ADDRESS`, icache base, LUT base, sync-object address, command bits, waits on `STATUS`, then writes `TPC_EXECUTE`. Initialization and reset flows program interrupt masks, MSS config, shared-memory base high values, stall bits, and queue-manager stop bits.

## Dependencies And Integration Points

The header depends on no other header besides its include guard. It is included by Gaudi driver code through generated ASIC register headers. The paired field definitions in `tpc0_cfg_masks.h` are required for safe read-modify-write operations.

Integration points include `gaudiP.h`, where `TPC_CFG_OFFSET` is derived from TPC instance base-address differences; `gaudi.c` initialization paths that program TPC interrupt masks, MSS configuration, queue-manager sync-object addresses, and shared-memory base values; TPC kernel launch support that writes QM kernel and icache/LUT registers; reset/stall paths that write `TPC_STALL`; and monitoring/error paths that read `STATUS`, `TPC_INTR_CAUSE`, and work-queue counters.

## Risks And Edge Cases

The constants are a hardware ABI. Any accidental address change, truncation, or local edit can direct writes to the wrong hardware register. That is especially hazardous for `TPC_EXECUTE`, `TPC_STALL`, `TPC_CMD`, interrupt registers, protection/user fields, and MBIST/debug controls.

The map contains reserved-looking gaps, such as between SRF and `ROUND_CSR`, and between some singleton blocks. Tests or register walkers must not assume every 4-byte slot in the aperture is valid. Conversely, repeated regions have strict strides; an incorrect stride can land on the next tensor's base register or a different field.

Because other TPCs are addressed by adding offsets to TPC0 macros, the TPC0 map must remain layout-compatible with sibling generated maps. A mismatch in one instance breaks generic loops that assume `mmTPC1_* - mmTPC0_*` deltas are valid for all repeated registers.

## Test Signals

Compile-time signals include successful resolution of all `mmTPC0_CFG_*` references in Gaudi code. Regeneration tests should diff the address map against the authoritative hardware database and verify the direct and QM tensor descriptor strides.

Runtime signals include correct TPC initialization across all TPC instances, no MMIO access faults during register programming, successful TPC kernel launch using QM descriptor registers, status polling that observes expected idle/ready transitions, interrupt causes read and clear at the expected address, and reset/stall flows affecting only the intended TPC instance.
