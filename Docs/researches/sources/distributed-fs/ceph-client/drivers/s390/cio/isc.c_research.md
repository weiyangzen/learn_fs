# sources/distributed-fs/ceph-client/drivers/s390/cio/isc.c

Purpose: reference-counts s390 I/O interruption subclass enablement.

Important APIs/types/functions: exports `isc_register()` and `isc_unregister()`. Global `isc_refs[MAX_ISC + 1]` and `isc_ref_lock` protect per-ISC user counts. First registration sets control register bit 6, `31 - isc`; last unregister clears it.

Control flow: register validates range, increments under spinlock, and enables the mask only for the first user. Unregister validates range and nonzero count, disables the mask for the last user, and decrements.

State and persistence behavior: state is in-memory reference counts and system control-register mask bits. Hardware mask state follows runtime registrations and is not persisted.

Dependencies and integration points: used by EADM, QDIO adapter interrupts, and other s390 I/O facilities. Depends on `asm/isc.h`, `system_ctl_set_bit()`, and `system_ctl_clear_bit()`.

Risks and test signals: unregister misuse warns and leaves state unchanged. Tests should cover multiple users of one ISC, first/last transitions, invalid ISC warnings, and absence of interrupt-context callers per the API contract.
