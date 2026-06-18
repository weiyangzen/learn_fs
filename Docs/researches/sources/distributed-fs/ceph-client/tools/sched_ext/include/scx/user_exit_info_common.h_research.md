# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/user_exit_info_common.h

Purpose: shared BPF/user-space definition of sched_ext exit info sizes and payload shape.

Important APIs/types: `enum uei_sizes` defines `UEI_REASON_LEN` 128, `UEI_MSG_LEN` 1024, and `UEI_DUMP_DFL_LEN` 32768. `struct user_exit_info` contains `kind`, `exit_code`, `reason[]`, and `msg[]`.

Control flow: none.

State and persistence: defines the shared memory layout used in BPF `.data` maps and user-space skeleton views.

Dependencies and integration: optionally includes `../vmlinux.h` for LSP mode. Included by both BPF and user-space UEI headers.

Risks: changing field order or sizes is an ABI change for skeleton-shared data. `s64` must be available from BPF or user-space typedef context.

Test signals: compile both BPF and C users, inspect skeleton layout, and verify exit info fields retain expected sizes.
