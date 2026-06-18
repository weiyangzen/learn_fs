# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm.c

## Purpose

`mdt_hsm.c` implements the MDT-facing HSM RPC handlers and the small on-disk HSM attribute update helper. It is the bridge between client/copytool RPC capsules and the MDT HSM coordinator code in the neighboring `mdt_hsm_cdt_*` files. It handles copytool progress, copytool registration, HSM state get/set, HSM data-version updates, current-action queries, and submission of archive/restore/remove/cancel requests.

The file is intentionally a request validation and translation layer. It checks protocol buffers, initializes credentials, enforces RBAC/capability requirements, locks the target object where on-disk xattrs are read or modified, converts user-visible HSM actions/states to coordinator actions, and delegates scheduling/state changes to coordinator helpers.

## Important APIs, Types, and Functions

- `mdt_hsm_attr_set()` packs `struct md_hsm` into a `struct hsm_attrs` xattr buffer and writes `XATTR_NAME_HSM` through `mo_xattr_set()`.
- `mdt_hsm_is_admin()` initializes a ucred from the request body and returns true only when the caller has `CAP_SYS_ADMIN` and `uc_rbac_hsm_ops`.
- `mdt_hsm_progress()` handles `MDS_HSM_PROGRESS`, converts network errno values, checks HSM admin rights, and calls `mdt_hsm_update_request_state()`.
- `mdt_hsm_ct_register()` and `mdt_hsm_ct_unregister()` register/unregister copytool agents by export client UUID. Registration supports both old single archive-mask clients and newer archive-id arrays.
- `mdt_hsm_state_get()` returns `struct hsm_user_state` for a file by reading `MA_HSM` under a protected lookup lock.
- `mdt_hsm_state_set()` updates HSM flags and optional archive id after mask validation, RBAC checks, privilege checks for non-user flags, and coherent-state validation.
- `mdt_hsm_data_version()` stores the nonzero client-supplied data version in the HSM xattr archive-version field.
- `mdt_hsm_action()` queries coordinator state with `mdt_hsm_get_action()` and translates internal `HSMA_*`/`ARS_*` values into user `HUA_*`/`HPS_*` current-action output.
- `mdt_hsm_request()` validates a `struct hsm_request`, deduplicates requested FIDs, builds a bounded `struct hsm_action_list`, maps user actions to `HSMA_*`, and calls `mdt_hsm_add_actions()`.

## Control Flow

All RPC handlers begin by validating that required capsule fields and the MDT body are present. Handlers that need authorization call `tsi2mdt_info()` and then initialize ucred state either directly or through `mdt_hsm_is_admin()`. Each handler ends by calling `mdt_thread_info_fini()` on initialized MDT thread info.

Copytool progress first reads `RMF_MDS_HSM_PROGRESS`, converts the embedded errno from network representation with `lustre_errno_ntoh()`, logs status and completion details, requires HSM admin privileges, then forwards the progress record to the coordinator. Copytool registration requires HSM admin privileges and reads the archive field. For old clients without `archive_id_array` support, the field must be one `__u32` mask and registration goes to `mdt_hsm_agent_register_mask()`. For newer clients, the payload must be an integral array of `__u32`; a single zero means no archive filter, otherwise the array is passed to `mdt_hsm_agent_register()`. Unregister simply authorizes and calls `mdt_hsm_agent_unregister()`.

State get initializes credentials, takes a child lookup lock in PR mode, requests `MA_HSM` through `mdt_attr_get_complex()`, then copies `mh_flags` and `mh_arch_id` into the server `hsm_user_state` reply. State set takes a child lock with LOOKUP and XATTR bits in PW mode, validates set/clear masks against `HSM_FLAGS_MASK`, restricts non-root callers to `HSM_USER_MASK`, reads current HSM state, applies requested set/clear masks, optionally changes archive id, checks flag coherence, writes the updated HSM xattr with `mdt_hsm_attr_set()`, then unlocks and releases credentials.

Data-version updates follow a similar lock/read/write sequence but only change `mh_arch_ver`. They reject a zero `mbo_version`, because zero is not a meaningful archive data version. Current-action queries do not lock or read the object xattr; they call the coordinator for the FID from the body and translate internal action/status enums into the wire reply.

HSM request submission validates item count, item array length, and opaque data length before credential setup. It rejects callers without `uc_rbac_hsm_ops`, maps `HUA_ARCHIVE`, `HUA_RESTORE`, `HUA_REMOVE`, and `HUA_CANCEL` into coordinator actions, and explicitly rejects `HUA_RELEASE`. The handler computes one action-list allocation containing the filesystem name and one item slot per requested item plus per-item opaque data. Allocation is capped at `MDT_HSM_ALLOC_MAX` to prevent a single RPC from forcing an unbounded kernel allocation. The loop skips duplicate FIDs already present in the action list, copies extents and opaque data into each `hsm_action_item`, and submits the final list to `mdt_hsm_add_actions()`.

## State and Persistence Behavior

The only direct persistent metadata written by this file is `XATTR_NAME_HSM` on MDT objects. `mdt_hsm_attr_set()` serializes in-memory `struct md_hsm` into the on-disk `struct hsm_attrs` format through `lustre_hsm2buf()` and writes it to the child metadata object. `mdt_hsm_state_set()` persists HSM flags and archive id. `mdt_hsm_data_version()` persists the archive data version. State get and action query are read-only.

Coordinator state is not stored directly here. Progress updates, action-list submission, action lookup, and agent registration are delegated to HSM coordinator functions, which may update coordinator memory and logs. Copytool identity is keyed by `exp_client_uuid`. Request action lists are temporary kernel allocations freed before the handler exits.

The file relies on MDT locking for consistency around the HSM xattr. State get uses a protected read lock. State set and data-version update use write locks with XATTR bits so concurrent xattr readers/writers and metadata operations observe coherent state. Credential state is transient and explicitly entered/exited around authorization checks.

## Dependencies and Integration Points

The file depends on `mdt_internal.h`, the MDT request/session helpers, `req_capsule` field accessors, ucred/RBAC helpers, LDLM locking through `mdt_object_lock()` and `mdt_object_unlock()`, metadata attribute reads through `mdt_attr_get_complex()`, xattr writes through `mo_xattr_set()`, HSM serialization helpers `lustre_hsm2buf()` and `lustre_buf2hsm()` via the attribute path, and coordinator APIs such as `mdt_hsm_update_request_state()`, `mdt_hsm_agent_register()`, `mdt_hsm_agent_unregister()`, `mdt_hsm_get_action()`, and `mdt_hsm_add_actions()`.

It is wired into `mdt_handler.c` through the MDS HSM opcodes: `MDS_HSM_PROGRESS`, `MDS_HSM_CT_REGISTER`, `MDS_HSM_CT_UNREGISTER`, `MDS_HSM_STATE_GET`, `MDS_HSM_STATE_SET`, `MDS_HSM_ACTION`, `MDS_HSM_REQUEST`, and `MDS_HSM_DATA_VERSION`. It also integrates with client feature negotiation through `exp_connect_archive_id_array()` for archive-id-array compatibility.

## Risks and Edge Cases

- Authorization is split between `CAP_SYS_ADMIN`, `uc_rbac_hsm_ops`, and per-handler RBAC-only checks. Future changes must preserve the distinction between copytool/admin operations and ordinary HSM state operations.
- `mdt_hsm_state_set()` depends on coherent flag combinations. Missing a new HSM flag in `HSM_FLAGS_MASK`, `HSM_USER_MASK`, or the consistency checks could allow invalid on-disk HSM state.
- Archive-id compatibility is client-version dependent. Old clients are limited by `LL_HSM_ORIGIN_MAX_ARCHIVE`, while new clients can send arrays. Bad size checks would corrupt registration semantics.
- `mdt_hsm_request()` multiplies item count by item/data sizes to compute `hal_size`. The allocation cap limits damage, but integer overflow or future structure-size changes should be considered when modifying this path.
- Duplicate FIDs are removed with a linear scan over the partially built action list, so very large but still under-cap requests are quadratic in item count.
- `HUA_RELEASE` is deliberately rejected. Any later attempt to re-enable release must coordinate with layout/HSM released-file handling elsewhere in MDT.
- State get assumes `MA_HSM` read success provides meaningful flags; files without HSM xattrs depend on the lower attribute helper's default handling.

## Test Signals

Tests should cover HSM admin authorization, RBAC-only denial, malformed or missing capsule fields, old and new copytool registration payloads, single zero archive-array compatibility, unregister by client UUID, progress with retry/fatal/completed flags, and network-to-host errno conversion. State tests should cover set/clear masks outside `HSM_FLAGS_MASK`, non-root attempts to change non-user flags, archive-id setting without `HS_EXISTS`, old-client archive-id maximum enforcement, invalid flag combinations such as DIRTY without EXISTS or RELEASED with DIRTY, xattr write failure propagation, and successful readback through state get.

Request tests should cover zero item count, item/data length mismatch, unsupported release action, unknown action, duplicate FID suppression, allocation cap/ENOMEM behavior, opaque data copying, and coordinator failure propagation. Data-version tests should cover zero-version rejection, successful xattr update, and lock/unlock behavior under injected errors. Current-action tests should validate translation of every known `HSMA_*` action and `ARS_*` status plus unknown-action fallback logging.
