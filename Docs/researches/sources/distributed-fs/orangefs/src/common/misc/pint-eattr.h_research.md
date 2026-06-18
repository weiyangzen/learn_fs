# sources/distributed-fs/orangefs/src/common/misc/pint-eattr.h

Purpose: Declares the extended-attribute validation and conversion interface used by OrangeFS server paths. It documents the separation between namespace access checks, set/list validation, and known-attribute encode/decode hooks.

Important APIs: `PINT_eattr_list_access()` validates attributes returned by list operations and adds the PVFS system prefix when needed. `PINT_eattr_check_access()` validates request attributes and strips PVFS internal prefixes for storage lookup. `PINT_eattr_namespace_verify()` checks whether a key can be set by users. `PINT_eattr_encode()` and `PINT_eattr_decode()` handle known special attributes such as datafile handle arrays.

Control flow and integration: The header is used by eattr/xattr request handling code before interacting with TROVE keyvals or returning attributes to clients. It includes PVFS internal and type definitions for `PVFS_ds_keyval`.

State and persistence behavior: No state is owned by the header. The declared functions can mutate key/value buffers supplied by callers, so callers must provide writable buffers with valid `buffer_sz` and `read_sz` fields.

Dependencies and risks: API users must account for negative PVFS error returns and for buffer ownership changes during encode. Test signals include compile coverage and request-path tests for namespace rejection, prefix stripping/adding, and cross-endian handle array conversions.
