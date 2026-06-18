## sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_unsupported.go

Purpose: non-Linux stub for namespace range user creation.

Important APIs/types/functions: `AddNamespaceRangesUser`.

Control flow: returns `-1, -1` and an unsupported error.

State and persistence: none.

Dependencies and integration points: portable API stub for non-Linux builds.

Risks: callers must handle unsupported platforms.

Test signals: no direct selected tests.
