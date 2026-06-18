<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/list_debug.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/list_debug.c

## Purpose
`list_debug.c` provides minimal list corruption checks for nVHE code using Linux `list_head` helpers without depending on the full kernel debug implementation at EL2.

## Important APIs, Types, and Functions
`nvhe_check_data_corruption()` preserves boolean values while satisfying `__must_check`. `NVHE_CHECK_DATA_CORRUPTION()` reports or BUGs depending on `CONFIG_BUG_ON_DATA_CORRUPTION`. `__list_add_valid_or_report()` validates adjacent links and self-insertion before add. `__list_del_entry_valid_or_report()` checks poison pointers and adjacent links before delete.

## Control Flow, State, and Persistence
The functions are pure validation helpers; they persist no state. On corruption they either invoke `BUG()` or `WARN_ON(1)` and return false, allowing list callers to stop the unsafe operation.

## Dependencies and Integration Points
It integrates with nVHE users of Linux list helpers, notably the hyp buddy allocator’s free lists in `page_alloc.c`. It depends only on `linux/list.h`, `linux/bug.h`, and kernel config.

## Risks and Test Signals
Risks include limited diagnostics in EL2, potential fatal BUGs in protected mode when configured, and divergence from upstream `lib/list_debug.c` predicates. Test signals are allocator/list selftests with intentional corruption under warn and bug configurations, plus normal boot allocation paths without false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/list_debug.c -->
