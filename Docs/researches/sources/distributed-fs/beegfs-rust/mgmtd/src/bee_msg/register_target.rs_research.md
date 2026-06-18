<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/register_target.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/register_target.rs

**Purpose:** Registers or re-registers storage targets with registration-token validation.

**Important APIs/types/functions:** Implements `HandleWithResponse` for `RegisterTarget`, response `RegisterTargetResp`; uses `try_resolve_num_id`, `db::target::insert_storage`, and direct SQL token updates.

**Control flow:** Fails during pre-shutdown, decodes `reg_token` as UTF-8, resolves existing storage target if present, validates or fills stored registration token, otherwise checks `registration_disable` and inserts a new storage target. Logs new vs existing registration and returns the target ID.

**State and persistence behavior:** Inserts storage target rows and persists registration tokens. Existing targets may have a missing token filled on first compatible registration.

**Dependencies and integration points:** Used by storage services registering targets before mapping them to nodes. Integrates with DB entity resolution and registration-disable policy.

**Risks:** Token mismatch rejects registration. UTF-8 decoding failure rejects the message. New registrations are blocked when registration is disabled, but existing re-registration remains allowed.

**Test signals:** Register new target, re-register with same token, fill missing token, reject mismatched token, reject new target with registration disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/register_target.rs -->
