# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/exception.S

## Purpose
This LoongArch guest assembly implements TLB refill and general exception entry code for KVM selftests.

## Important APIs, Types, and Functions
`handle_tlb_refill` loads page-table entries through `lddir`/`ldpte` and executes `tlbfill`. `handle_exception` saves general-purpose registers and key CSRs into an `ex_regs` stack frame, calls `route_exception`, restores state, and returns with `ertn`. Macros `save_gprs` and `restore_gprs` handle GPR preservation.

## Control Flow
Both entry points are 4K aligned. TLB refill temporarily saves `t0`, walks PGD state from CSR, fills TLB, restores, and returns. General exception switches to the exception stack from `KS1`, saves registers/ERA/ESTAT/BADV/PRMD, calls C, restores ERA/PRMD and GPRs, then resumes.

## State, Dependencies, and Integration
State is per-exception stack contents and LoongArch CSRs. It integrates with `loongarch_vcpu_setup()`, which programs `TLBRENTRY`, `EENTRY`, page-walk CSRs, and exception stack CSR.

## Risks and Test Signals
The saved frame layout must match C structs and CSR setup. Bad page-walk configuration or stack CSR state causes guest traps, unexpected ucalls, or hangs.
