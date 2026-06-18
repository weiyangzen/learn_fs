# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/powerpc.c

## Purpose
`powerpc.c` provides a PowerPC hash-MMU-only LKDTM test that injects SLB multihit conditions and verifies the machine can recover.

## Important APIs, Types, and Functions
Key functions are `insert_slb_entry()`, `inject_vmalloc_slb_multihit()`, `inject_kmalloc_slb_multihit()`, `insert_dup_slb_entry_0()`, and `lkdtm_PPC_SLB_MULTIHIT()`. It uses PowerPC MMU helpers such as `mk_vsid_data()`, `mk_esid_data()`, `mmu_psize_defs`, `radix_enabled()`, and inline `slbmte/slbmfee/slbmfev` assembly.

## Control Flow
The crashtype checks that radix MMU is not enabled. It then allocates vmalloc and kmalloc memory, inserts duplicate SLB entries for those addresses, touches the memory to trigger the exception, and duplicates bolted SLB entry zero before reading from `PAGE_OFFSET`. Successful execution reaches a recovery log line.

## State and Persistence
It transiently modifies processor SLB entries while preemption is disabled. No persistent kernel data is retained after allocations are freed.

## Dependencies and Integration Points
Compiled only into LKDTM powerpc categories under the corresponding architecture configuration. It depends on ppc64 hash MMU semantics and low-level assembly instructions.

## Risks
If platform SLB multihit recovery is broken, the machine may not survive. Running on radix MMU is unsupported and reported as expected failure.

## Test Signals
Signals are successful recovery from vmalloc, kmalloc, and bolted-entry multihit injections, plus `XFAIL` on radix mode. Any hang, machine check, or panic indicates a recovery regression.
