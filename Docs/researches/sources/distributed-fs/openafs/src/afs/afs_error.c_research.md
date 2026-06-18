# sources/distributed-fs/openafs/src/afs/afs_error.c

Purpose: Normalizes AFS, unified-AFS, volume, network, and request-state errors into OS-facing errno-style values for vnode and pioctl callers. It also initializes and copies per-request error state used by `afs_Analyze` and higher-level operations.

Important APIs and functions: `init_et_to_sys_error` populates a 512-entry table from unified-AFS error constants (`UAE*`) to local errno values. `et_to_sys_error` maps an error-table value back to system errno when possible. `afs_FinalizeReq` initializes a `struct vrequest` error state. `afs_CopyError` transfers server skip/error arrays and aggregate flags between requests. `afs_CheckCode` is the central finalizer that traces raw errors and applies request-context overrides.

Control flow: `afs_CheckCode` first logs non-zero codes, translates unified error-table values, and returns immediately if no initialized request is supplied. Initialized request flags take precedence over raw code: network errors become `ETIMEDOUT`, access errors become `EACCES`, volume errors map to `ENODEV`, `EWOULDBLOCK`, or `EIO`, and selected server codes (`VNOVNODE`, `VDISKFULL`, `VOVERQUOTA`, `VNOSERVICE`) map to OS errors. Otherwise the raw/translated code is returned.

State and persistence: The only module state is the static `et2sys` mapping table, populated at initialization. `struct vrequest` carries transient per-operation state: skipserver/lasterror arrays, busy count, idle/token/access/volume/network/perm-write flags, and `initd`. No durable state is written.

Dependencies and integration points: Depends on generated/defined unified-AFS error constants, errno availability, OpenAFS volume error constants, stats/tracing, and `struct vrequest` semantics. `afs_CheckCode` is used broadly by platform vnode ops, VNOPS implementations, pioctl handling, background stores, Linux exporter paths, and cache-bypass reads.

Risks: `init_et_to_sys_error` assumes every referenced `UAE* - ERROR_TABLE_BASE_uae` index fits within 512 entries; new constants outside that range would write out of bounds unless guarded. `afs_CheckCode` intentionally hides raw errors when request flags are set, which can reduce diagnostic specificity. Some mappings are platform-conditional (`EDQUOT`) or historical (`VNOSERVICE` as timeout), so cross-platform behavior can differ.

Test signals: Verify every populated unified-AFS mapping, unmapped in-range values, and out-of-range passthrough. Exercise `afs_CheckCode` with no request, uninitialized request, network/access/volume flags, quota/full/no-service/vnovnode codes, and combined flags to confirm precedence. Callers that wait on background stores should check both raw and checkcode values.
