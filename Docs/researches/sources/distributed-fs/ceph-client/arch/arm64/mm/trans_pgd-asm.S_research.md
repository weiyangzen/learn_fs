# sources/distributed-fs/ceph-client/arch/arm64/mm/trans_pgd-asm.S

## Purpose
This assembly file defines a temporary EL2 vector table used by transitional page-table flows for hibernate and kexec. It provides just enough hypervisor-stub behavior to set EL2 vectors or perform a soft restart while other unexpected vectors loop or return an error.

## Important APIs, Types, and Functions
The exported symbol is `trans_pgd_stub_vectors`, with end label `__trans_pgd_stub_vectors_end`. Helper macros `invalid_vector` and `el1_sync_vector` generate vector slots. It handles `HVC_SET_VECTORS`, `HVC_SOFT_RESTART`, and returns `HVC_STUB_ERR` for unexpected EL1 synchronous calls.

## Control Flow
Most vector slots branch to themselves forever via `invalid_vector`, making unexpected exceptions obvious and non-returning. The EL1 synchronous vector compares `x0` with `HVC_SET_VECTORS`; on match it writes `x1` to `vbar_el2`, clears `x0`, and `eret`s. It next checks `HVC_SOFT_RESTART`; on match it rearranges arguments and branches to the restart target. Otherwise it places `HVC_STUB_ERR` in `x0` and returns.

## State and Persistence
The vector table is code/data copied by `trans_pgd_copy_el2_vectors()` in `trans_pgd.c`. Its persistent effect is limited to setting `vbar_el2` or transferring control for restart.

## Dependencies and Integration Points
It integrates with kexec and hibernate transitional PGD code and constants from `<asm/kvm_asm.h>`. The table size is checked with an `.org` assertion to fit within `SZ_2K`, matching ARM64 vector table layout.

## Risks
The argument shuffle for soft restart must match callers' ABI. Any vector overflow would corrupt adjacent code, hence the size check. Unexpected exceptions intentionally do not recover, which is appropriate for transitional contexts but makes debugging dependent on where the CPU stalls.

## Test Signals
Hibernate restore and kexec soft restart paths exercise this table. `trans_pgd_copy_el2_vectors()` should copy exactly `ARM64_VECTOR_TABLE_LEN` and cache-maintain it. Failures appear as failed HVC_SET_VECTORS, restart hangs, or vector-size build issues.
