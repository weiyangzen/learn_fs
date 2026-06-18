<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/types.go -->
# sources/cloud-native/buildkit/frontend/subrequests/types.go

Purpose: provides shared metadata schemas for frontend subrequest discovery and documentation.

Important APIs, types, and functions: `Type` is a string alias with `TypeRPC = "rpc"`. `Named` captures a name, version, and description triple. `Request` describes a subrequest with name, version, type, description, option metadata, and output metadata.

Control flow and state: this file declares data-only structs with JSON tags and no behavior or persistence.

Dependencies and integration: consumed by describe, lint, outline, targets, convertllb, and other frontend subrequest packages. Its JSON field names form part of the external metadata contract returned by `frontend.subrequests.describe`.

Risks and test signals: schema changes are compatibility-sensitive because clients unmarshal these JSON objects. Tests should cover round-trip compatibility for existing fields and absence of required-field enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/types.go -->
