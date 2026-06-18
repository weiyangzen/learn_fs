# sources/distributed-fs/ceph-client/include/linux/pstore.h

Purpose: defines the generic persistent storage backend interface used to save crash logs, console output, ftrace records, machine checks, and pmsg data into platform storage and expose them through pstorefs.

Important APIs and types: `enum pstore_type_id` defines ABI-sensitive record types. `struct pstore_record` carries record metadata, data buffer, ECC notice, backend private pointer, and dmesg-specific fields such as count/reason/part/compressed. `struct pstore_info` describes a backend with owner/name, crash dump buffer and raw spinlock, read mutex, frontend flags, max kmsg reason, private data, and callbacks `open`, `close`, `read`, `write`, `write_user`, and `erase`. Frontend flags include dmesg, console, ftrace, and pmsg. `pstore_register()` and `pstore_unregister()` manage backends. Ftrace helpers encode CPU either in IP or timestamp and store/read timestamp bits.

Control flow: a backend registers `pstore_info`; pstore core opens/read/closes it to enumerate records into pstorefs, calls `write()` from crash or frontend paths, optionally writes userspace pmsg data through `write_user()`, and erases records when pstorefs files are removed. Dmesg crash writes use the preallocated backend buffer because allocation may be unsafe after oops/panic.

State and persistence: backend storage is persistent across reboot by design. Runtime state includes preallocated buffers, callback serialization, record IDs, timestamps, ECC notices, and backend private record data freed by the core.

Dependencies and integration points: depends on kmsg dump reasons, pstorefs, console/ftrace/pmsg frontends, module ownership, mutex/spinlock primitives, and platform-specific backends such as EFI, ramoops, block, and zone.

Risks and test signals: risks include ABI record-type renumbering, crash-path allocation or locking, truncating compressed records, wrong erase identification, leaking `record->priv`, and ftrace CPU/timestamp encoding errors. Test panic/oops persistence, pstorefs read/erase, console/ftrace/pmsg frontends, ECC notices, backend unregister, and crash-time write constraints.
