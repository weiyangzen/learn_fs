## sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils_unsupported.go

Purpose: non-Linux stubs for ID-mapped mount utilities.

Important APIs/types/functions: `CreateIDMappedMount` and `CreateUsernsProcess`.

Control flow: both return unsupported errors; process creation returns `-1, nil, error`.

State and persistence: none.

Dependencies and integration points: portable API surface for packages that import idmap.

Risks: callers must handle unsupported errors or gate by platform/capability.

Test signals: no direct selected tests.
