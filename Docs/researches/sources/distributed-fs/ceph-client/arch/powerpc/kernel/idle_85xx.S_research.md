# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_85xx.S

## Purpose
Provides 32-bit e500/85xx idle entry and wakeup restore code for BookE processors, covering both e500mc `wait` idle and older HID0-based DOZE/NAP.

## Important APIs, Types, And Functions
Exports `e500_idle` and `power_save_ppc32_restore`. It uses thread flag `_TLF_NAPPING`, HID0 DOZE/NAP/SLEEP bits, MSR WE/EE, `wrteei`, `wait`, `flush_dcache_L1`, and `powersave_nap`.

## Control Flow
`e500_idle` marks the current thread as napping. On e500mc it hard-enables interrupts and loops on `wait`, relying on a real interrupt to return through the napping fixup. On older e500 it selects DOZE or NAP based on features and `powersave_nap`, flushes L1 data cache before NAP, programs HID0, enables MSR_WE and MSR_EE, and spins. `power_save_ppc32_restore` changes the saved NIP to LR so the interrupted idle function returns normally.

## State And Persistence
State is the thread local napping flag and transient HID0/MSR changes. No separate save arrays are used in this file; architectural state is restored by exception return or remains as configured for the CPU.

## Dependencies And Integration Points
Depends on BookE/e500 exception wakeup handling, CPU feature fixups, `powersave_nap`, `flush_dcache_L1`, and platform assignment of this routine as `ppc_md.power_save`. It integrates with `idle.c` and early 85xx CPU setup.

## Risks And Edge Cases
The main risks are missed wakeups if `_TLF_NAPPING` is not honored, cache coherency problems when entering NAP without the L1 flush, and spurious hypervisor wakeups on e500mc requiring the `wait` loop. HID0 bit selection must match CPU feature fixups.

## Test Signals
Signals include e500/e500mc idle wakeup tests, nap/doze feature builds, `powersave_nap` behavior, timer and doorbell wakeups, L1 flush path execution, and no lost interrupts under idle stress.
