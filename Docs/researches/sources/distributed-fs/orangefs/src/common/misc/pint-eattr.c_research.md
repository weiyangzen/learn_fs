# sources/distributed-fs/orangefs/src/common/misc/pint-eattr.c

Purpose: Implements extended-attribute namespace validation and special encoding/decoding for OrangeFS attributes, especially PVFS internal attributes exposed through `system.pvfs2.*` names. It protects set/list/get behavior from unsupported namespaces and normalizes internal key names.

Important APIs and functions: Public functions are `PINT_eattr_check_access()`, `PINT_eattr_namespace_verify()`, `PINT_eattr_system_verify()`, `PINT_eattr_list_access()`, `PINT_eattr_encode()`, and `PINT_eattr_decode()`. Internal check tables define accepted access namespaces, settable namespaces, system ACL checks, list-prefix handling, and encode/decode handlers. `PINT_handle_array` plus generated endecode helpers support endian-safe datafile handle arrays.

Control flow: All checks use `PINT_eattr_verify()`, which walks an ordered `PINT_eattr_check` array, matches namespace/key prefixes, returns configured error codes, or invokes a handler. Get/access strips `system.pvfs2.` before TROVE lookup. Set namespace verification rejects `system.pvfs2.` writes, accepts POSIX-like namespaces, and validates ACL sizes for supported system ACL names. List handling adds `system.pvfs2.` to internal keys that lack a standard namespace. Encoding recognizes `DATAFILE_HANDLES_KEYSTR`, replaces raw handle arrays with encoded buffers, and decoding reverses the public `system.pvfs2.dh` form.

State and persistence behavior: The module mutates caller-provided `PVFS_ds_keyval` buffers in place and may free/replace `val->buffer` during encode. Persistent xattr state is owned by TROVE; this module controls the names and byte layout used before storage or after retrieval.

Dependencies and integration points: Uses PVFS request limits, internal key strings, ACL structures, generated endecode functions, PVFS error codes, and memory allocation. It integrates with server eattr operations, xattr utilities, and tools such as viewdist that read datafile handle arrays.

Risks and test signals: `PINT_eattr_strip_prefix()` uses `sscanf()` into a fixed-size temporary buffer and assumes key buffer string termination. `PINT_eattr_add_pvfs_prefix()` relies on caller-provided buffer capacity and uses `sprintf()`. Decode frees `harray.handles` only on size error, so generated decode ownership must be verified. Tests should cover every namespace branch, malformed/non-terminated keys, ACL sizes, list prefix capacity errors, endian round trips for datafile handles, and set rejection for `system.pvfs2.*`.
