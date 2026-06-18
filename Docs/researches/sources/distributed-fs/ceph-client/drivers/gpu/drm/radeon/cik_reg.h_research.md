# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_reg.h

## Purpose
`cik_reg.h` defines a focused set of CIK register addresses, bitfields, and helper constants used by Radeon display, debug/watchpoint, interrupt, and SDMA queue code. It is narrower than `cikd.h`, concentrating on display scanout/cursor programming, SQ/TCP watch registers, CPC/HQD/SDMA RLC queue registers, and address-watch control packing.

## Important APIs, types, and definitions
- Display and cursor registers: `CIK_GRPH_CONTROL` with depth, bank, tiling, pipe, and pixel-format helpers; `CIK_CUR_*` cursor address, size, position, hotspot, color, and update registers; `CIK_ALPHA_CONTROL`, `CIK_LB_DATA_FORMAT`, and `CIK_LB_DESKTOP_HEIGHT`.
- Debug/watch registers: `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CMD`, `TCP_WATCH{0..3}_ADDR_{H,L}`, and `TCP_WATCH{0..3}_CNTL`.
- Interrupt and queue registers: `CPC_INT_CNTL`, `CP_HQD_IQ_RPTR`, and `SDMA0_RLC0_*` queue registers, plus `SDMA0_CNTL` and `SDMA1_CNTL`.
- Enumerations define maximum trap/watch resources and address-watch register slots.
- `union TCP_WATCH_CNTL_BITS` packs watchpoint mask, VMID, ATC, mode, and valid fields over a 32-bit register value.

## Control flow and integration points
This header does not execute control flow. Driver code uses these constants to build MMIO register reads/writes, compose display surface configuration, control cursor updates, program address watchpoints, and configure SDMA RLC queue state.

## State and persistence behavior
All state lives in hardware registers. Writes using these definitions persist in display engines, watchpoint logic, or SDMA queue registers until overwritten, reset, or power-gated. The `TCP_WATCH_CNTL_BITS` union is a transient CPU-side representation used to compose or inspect a register value.

## Dependencies and constraints
The file assumes Linux-style integer types (`uint32_t`) and Radeon MMIO accessors in consumers. Several helpers mask and shift user-provided values; callers must still provide values legal for the active ASIC and display mode. TCP watch addresses are documented as dword addresses multiplied by four, a detail callers must preserve.

## Risks and test signals
Incorrect field definitions can corrupt scanout format, cursor updates, debugger watchpoints, or queue setup. Test signals include modeset/cursor tests, KFD or debugger watchpoint validation, SDMA queue bring-up, register readback comparisons, and absence of page faults or display underruns after programming these registers.
