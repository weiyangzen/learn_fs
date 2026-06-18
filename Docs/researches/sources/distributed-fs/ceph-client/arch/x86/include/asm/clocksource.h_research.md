
# sources/distributed-fs/ceph-client/arch/x86/include/asm/clocksource.h

Purpose: x86 vDSO clocksource usage tracking.

Important APIs and control flow: declares `vclocks_used`. `vclock_was_used()` reads the bitmask with `READ_ONCE()` and tests a vclock bit. `vclocks_set_used()` ORs in a bit and writes it back with `WRITE_ONCE()`.

State, dependencies, and risks: state is a global bitmask describing which vDSO clock modes have been used. Dependencies include vDSO clocksource identifiers and one-copy access primitives. Risks include non-atomic read-modify-write lost updates if called concurrently in unexpected contexts, and stale vclock accounting. Test signals include vDSO time tests and clocksource switching tests.
