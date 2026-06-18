# sources/distributed-fs/openafs/src/tools/audit/readsysvmq

Purpose: example Perl consumer for OpenAFS fileserver audit logs emitted through the System V message queue audit interface.

Important APIs and control flow: the script requires one argument, the audit log path. It uses `IPC::SysV` `ftok($path, 1)` to derive the queue key, opens the message queue with `msgget($mqkey, S_IRUSR)`, then loops forever calling `msgrcv`. Each received message is unpacked as native long message type plus the remaining text via `unpack("l! a*", $msg)` and printed.

State/dependencies: no persistent state is written. It depends on Perl, `IPC::SysV`, SysV IPC support, and a fileserver started with `-audit-interface sysvmq` plus matching `-auditlog` path.

Risks/test signals: it blocks indefinitely, has no signal handling or queue cleanup, assumes a 2048-byte message payload, and prints raw audit text. Its operational signal is visible audit lines or immediate failure if the path/key/queue is unavailable.
