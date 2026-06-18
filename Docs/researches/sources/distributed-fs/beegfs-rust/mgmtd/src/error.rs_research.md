<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/error.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/error.rs

Purpose: defines a small typed error enum for recurring database/business validation failures with stable wording.

Important APIs/types/functions: `TypedError` has `ValueNotFound { name, value }` and `ValueExists { name, value }` variants with `thiserror` display implementations. Constructors `value_exists()` and `value_not_found()` accept `ToString` inputs.

Control flow: no control flow beyond constructor formatting. Callers wrap variants in `anyhow` or `bail!` so errors can be propagated through gRPC and service layers.

State and persistence: stateless.

Dependencies and integration points: used by entity, target, buddy group, and storage pool validation to produce consistent "not found" and "already exists" errors.

Risks: only two error categories exist; most logic still uses free-form `anyhow` messages, so callers should not assume all validation failures are typed.

Test signals: no direct tests. Existing DB tests indirectly check these paths by asserting operations fail, but not exact messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/error.rs -->
