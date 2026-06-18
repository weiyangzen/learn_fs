# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/t4vf_defs.h

## Purpose
Defines the VF-visible Chelsio register map and slice-to-module mapping constants used by the VF driver to address SGE, MPS, PL, CIM, and mailbox data registers. It provides the address constants used by mailbox, readiness, interrupt, and doorbell code.

## Important APIs, Types, And Functions
The file exposes base addresses (`T4VF_SGE_BASE_ADDR`, `T4VF_MPS_BASE_ADDR`, `T4VF_PL_BASE_ADDR`, `T4VF_MBDATA_BASE_ADDR`, `T6VF_MBDATA_BASE_ADDR`, `T4VF_CIM_BASE_ADDR`), register-map bounds, per-module VF register offsets (`SGE_VF_KDOORBELL`, `SGE_VF_GTS`, `PL_VF_WHOAMI`, `CIM_VF_EXT_MAILBOX_CTRL`, etc.), the `T4VF_MOD_MAP()` macro, and `NUM_CIM_VF_MAILBOX_DATA_INSTANCES`.

## Control Flow
There is no runtime control flow. These constants are compiled into hardware access paths. `sge.c` uses SGE VF doorbell/GTS offsets for queue updates; `t4vf_hw.c` uses PL `WHOAMI` for readiness and CIM mailbox registers for firmware command exchange. The compile-time `#error` enforces that the VF mailbox base matches the PF CIM mailbox data convention.

## State And Persistence
No state is stored here. The definitions describe the fixed or PF-programmed VF register aperture through which runtime driver state is synchronized with the adapter.

## Dependencies And Integration Points
The header depends on `../cxgb4/t4_regs.h` for PF register constants and is included by `sge.c` and `t4vf_hw.c`. It integrates directly with the hardware/firmware ABI: wrong values affect register reads, mailbox writes, queue doorbells, and interrupt rearming.

## Risks
Register-map constants are high-risk because errors produce silent device misprogramming. T6 mailbox data moved from `T4VF_MBDATA_BASE_ADDR` to `T6VF_MBDATA_BASE_ADDR`, so chip-version selection in users must stay aligned. The trailing include guard comment appears misspelled, but the actual guard macro is consistent and functional.

## Test Signals
Probe readiness via `PL_VF_WHOAMI`, successful mailbox commands, queue doorbell operation, and interrupt rearming are practical integration tests. Build-time enforcement of mailbox-base equivalence provides a static signal for T4/T5 register compatibility.
