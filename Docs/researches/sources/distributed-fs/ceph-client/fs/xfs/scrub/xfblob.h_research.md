<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.h

Purpose: declares the xfile-backed variable-length blob storage interface and convenience helpers for storing XFS names.

Important APIs and types: `struct xfblob` contains the backing xfile and next append offset. `xfblob_cookie` is a `loff_t` offset returned by stores and later used for loads/frees. Public functions create/destroy blob stores, load/store/free blobs, query backing bytes, and truncate all blobs. `xfblob_storename()` stores `xfs_name->name` with `xfs_name->len`; `xfblob_loadname()` loads bytes into `xfs_name->name` and restores the length.

Control flow: callers create a blob store, append payloads to receive cookies, embed those cookies in other scrub records, later load or free blobs by cookie, and finally truncate or destroy the store. The name helpers reduce duplicated casting and length assignment in directory/parent-pointer scrub code.

State and persistence: state is transient and xfile-backed. Cookies are only meaningful for the lifetime of the `xfblob` and after a truncate all previous cookies become stale. The header exposes fields, so callers can inspect but should not mutate allocator state directly.

Dependencies and integration points: depends on `struct xfile`, `struct xfs_name`, and the implementation's header validation. It is commonly paired with `xfarray` records that need stable references to variable-length names.

Risks and test signals: risks include callers treating cookies as durable IDs, reusing cookies after truncate/free, insufficient destination storage in `xfblob_loadname()`, and direct mutation of `last_offset`. Test signals should exercise the generic blob API and name-specific helpers with maximum-length names and stale cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfblob.h -->
