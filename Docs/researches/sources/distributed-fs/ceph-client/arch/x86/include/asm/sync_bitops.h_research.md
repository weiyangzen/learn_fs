<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_bitops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_bitops.h

Purpose: provides fully synchronized x86 bit operations for users that require locked atomic bit manipulation. Important APIs include `sync_set_bit()`, `sync_clear_bit()`, `sync_change_bit()`, `sync_test_and_set_bit()`, `sync_test_and_clear_bit()`, `sync_test_and_change_bit()`, and `sync_test_bit()`.

Control flow: wrappers emit locked `bts/btr/btc` operations or equivalent atomic bitops, returning previous bit values where needed. State is the target bitmap word. Dependencies include x86 atomic instruction semantics and generic bitops expectations.

Risks include overusing heavier synchronized operations in hot paths, wrong memory-order assumptions, and bit-number/address constraints. Test signals include atomic bitop selftests, SMP races, lock bitmap users, and compiler constraint builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_bitops.h -->
