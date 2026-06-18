# sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/config

This config fragment records kernel options needed by the IPC checkpoint/restore message-queue test. It requests `CONFIG_EXPERT=y` and `CONFIG_CHECKPOINT_RESTORE=y`.

There is no executable control flow. The file is consumed by kselftest config tooling and aligns with `msgque.c`, which writes `/proc/sys/kernel/msg_next_id` to recreate a SysV message queue with a chosen id.

Dependencies and integration points are kernel Kconfig aggregation, SysV IPC support supplied elsewhere, and checkpoint/restore support. The main risk is minimal coverage: this fragment does not itself request every SysV IPC option. A useful validation signal is a running kernel that exposes writable `msg_next_id` for root and supports `MSG_COPY`.
