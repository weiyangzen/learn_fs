# sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/msgque.c

`msgque.c` validates SysV message queue dump and restore behavior for checkpoint/restore. It creates a queue, sends two messages, copies metadata and queued messages without consuming them, destroys the queue, recreates the same queue id through `/proc/sys/kernel/msg_next_id`, restores messages, and verifies the restored contents.

Important APIs are `ftok()`, `msgget()`, `msgsnd()`, `msgrcv()`, `msgctl()`, `MSG_STAT`, `MSG_COPY`, `IPC_CREAT`, `IPC_EXCL`, `IPC_RMID`, and `kselftest.h`. `struct msg1` stores message size, type, and payload. `struct msgque_data` stores the key, queue id, mode, queue byte/count metadata, and copied messages. Helpers are `fill_msgque()`, `dump_queue()`, `check_and_destroy_queue()`, and `restore_queue()`.

`main()` requires root, creates the queue, fills it with two distinct messages, dumps queue state by scanning kernel queue indexes and using `MSG_COPY`, destroys the original after checking messages, writes the saved id to `msg_next_id`, recreates it with the saved key and mode, replays messages, and checks/destroys it again.

Kernel state is the SysV queue id, permissions, qbytes/qnum metadata, and queued messages. User-space persists a heap copy of messages between destroy and restore. Dependencies are root, SysV IPC, `CONFIG_CHECKPOINT_RESTORE`, `MSG_COPY`, and writable proc sysctl. Risks include queue-key/id collisions and the fixed scan of kernel ids 0..255. Pass signals are matching queue id, message count, type, size, payload, and successful cleanup.
