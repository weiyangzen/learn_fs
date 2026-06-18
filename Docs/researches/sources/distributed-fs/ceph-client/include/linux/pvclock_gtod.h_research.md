# sources/distributed-fs/ceph-client/include/linux/pvclock_gtod.h

Purpose: declares notifier registration for paravirtual clock users that need to track system time-of-day updates.

Important APIs and types: `pvclock_gtod_register_notifier()` and `pvclock_gtod_unregister_notifier()` manage a `notifier_block`. Notifier actions indicate whether system time was stepped.

Control flow: a paravirtual clock provider registers a notifier, receives callbacks when system time is updated, and updates guest-visible time synchronization data; it unregisters during teardown.

State and persistence: state is the notifier chain and registered blocks in memory. Guest time synchronization state is maintained by notifier users.

Dependencies and integration points: depends on Linux notifier infrastructure and timekeeping update paths. Integrates KVM/paravirtual clock code with host time changes.

Risks and test signals: risks include notifier leaks, callback ordering, handling stepped vs slewed time incorrectly, and teardown races. Test register/unregister, host time step events, concurrent callbacks during module removal, and guest time monotonicity.
