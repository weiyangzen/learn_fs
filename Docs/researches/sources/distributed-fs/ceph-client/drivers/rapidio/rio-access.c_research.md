# sources/distributed-fs/ceph-client/drivers/rapidio/rio-access.c

Purpose: provides exported RapidIO configuration-space access wrappers for local and remote devices plus a doorbell send wrapper. It is the common alignment and dispatch layer between RapidIO core/clients and mport-specific operations.

Important APIs, types, and functions: macro families `RIO_LOP_READ`, `RIO_LOP_WRITE`, `RIO_OP_READ`, and `RIO_OP_WRITE` generate `__rio_local_read_config_{8,16,32}`, `__rio_local_write_config_{8,16,32}`, `rio_mport_read_config_{8,16,32}`, and `rio_mport_write_config_{8,16,32}`. `rio_mport_send_doorbell()` invokes the mport `dsend` operation. All generated accessors are exported GPL symbols.

Control flow: each generated accessor first checks access alignment (`RIO_16_BAD`, `RIO_32_BAD`; 8-bit always allowed), then calls the appropriate `struct rio_ops` method on the mport: local `lcread`/`lcwrite` or remote `cread`/`cwrite`. Read wrappers receive a 32-bit temporary from the low-level op and truncate it to the requested type. Write wrappers pass the typed value and access length through. The doorbell helper passes `mport->id`, destination ID, and payload to `mport->ops->dsend`.

State and persistence: no local state. The only persistent effects are hardware/configuration changes made by lower-level mport operations.

Dependencies and integration: depends on `struct rio_mport` and `struct rio_ops` from RapidIO headers. Tsi721 supplies the low-level ops; `rio_mport_cdev` uses these wrappers for user-space maintenance IO; enumeration and drivers can use them for config-space access.

Risks: the wrappers do not validate operation pointers or mport lifetime; callers must use registered, live mports. They enforce alignment but not offset range, except where lower-level drivers do. Type truncation for 8/16-bit reads depends on low-level ops returning data in the expected lower bits.

Test signals: alignment error checks for 16/32-bit offsets, successful local and remote config accesses through a mock or real mport, 8/16/32-bit truncation behavior, error propagation from low-level ops, and doorbell dispatch with expected destination and payload.
