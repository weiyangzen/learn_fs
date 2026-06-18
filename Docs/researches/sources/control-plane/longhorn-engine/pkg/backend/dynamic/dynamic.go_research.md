<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/dynamic/dynamic.go -->
## sources/control-plane/longhorn-engine/pkg/backend/dynamic/dynamic.go

Purpose: dynamic backend factory dispatcher that chooses a concrete backend implementation from an address scheme.

Important APIs/types/functions: `Factory` holds a map of scheme to `types.BackendFactory`. `New` wraps the map. `Create` splits `address` on `://`, looks up the scheme, strips it, and delegates creation with volume name, protocol, shared timeouts, upgrade flag, and expected size.

Control flow and state: stateless beyond the factories map. Invalid or unknown schemes return an error.

Dependencies and integration points: depends on `types.BackendFactory`; used by controller startup/add-replica paths to support `tcp://`, `file://`, and other backend schemes through one factory.

Risks: address parsing is intentionally simple; malformed addresses or schemes containing `://` are rejected. The factories map is not copied, so external mutation can affect dispatch.

Test signals: backend creation tests should cover known schemes, unknown schemes, and malformed addresses.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/dynamic/dynamic.go -->
