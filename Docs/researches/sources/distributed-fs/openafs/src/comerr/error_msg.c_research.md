# sources/distributed-fs/openafs/src/comerr/error_msg.c

Purpose: runtime error-code decoder and error-table registry for com_err.

Important APIs and state: `afs_error_message`, `afs_error_message_localize`, `afs_com_right`, `afs_com_right_r`, and `afs_add_to_error_table`. Static `_et_list` stores registered generated tables. In pthread builds, `LOCK_ET_LIST` lazily initializes and uses a mutex via `pthread_once`.

Control flow: negative codes map to selected RX/RPC messages; table number zero maps through `strerror` or legacy volume messages; nonzero table codes split into table base and offset using `ERRCODE_RANGE`, then scan `_et_list` for a matching base. Unknown codes are formatted into a static buffer with table-name text and numeric offset. Localization uses CoreFoundation on Darwin, gettext when available, or plain copy.

Persistence and integration: registry state persists for process lifetime after generated `initialize_*_error_table` functions call `afs_add_to_error_table`. It integrates with `com_err.c`, generated error tables, platform localization, and `et_name` for table names.

Risks and tests: unknown-code and negative-code messages use static buffers, so returned pointers are not thread-safe despite registry locking. `afs_add_to_error_table` prevents duplicate bases but does not validate table contents. Coverage is broad through every generated error-table user.
