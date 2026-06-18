<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/abi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/abi_test.c

## Purpose
Validates the user_events ioctl ABI for enablement bits, persistent events, bit-size validation, multi-format events, fork COW updates, and clone shared-VM updates.

## Important APIs, Types, and Functions
DIAG_IOCSREG, DIAG_IOCSUNREG, DIAG_IOCSDEL, struct user_reg/user_unreg, reg_enable*, reg_disable, find_multi_event_dir, event_exists/change_event/delete.

## Control Flow
Fixture mounts/checks tracefs, registers events through /sys/kernel/tracing/user_events_data, toggles enable files, verifies userspace status bits, tests invalid flags/sizes, locates multi-format event directories by format content, and checks fork/clone propagation.

## State and Persistence
Creates and deletes tracefs event directories under user_events/user_events_multi; manipulates in-process enable words and may mount tracefs temporarily.

## Dependencies and Integration Points
Requires root, tracefs, CONFIG_USER_EVENTS, linux/user_events.h, glob/stat/ioctl support, and user_events_selftests.h.

## Risks and Edge Cases
Persistent-event and multi-format cleanup can lag, so wait loops are used; tests depend on exact tracefs paths and kernel ABI errno behavior.

## Test Signals
Pass is all kselftest fixture cases completing with expected ioctl results and enable-bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/abi_test.c -->
