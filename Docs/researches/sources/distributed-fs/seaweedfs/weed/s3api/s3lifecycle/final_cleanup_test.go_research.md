# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/final_cleanup_test.go

Purpose: gap-filling tests for small lifecycle helpers before broader integration work.

Important tests: `TestActionKind_StringUnspecifiedDefault` pins unknown/default action kind rendering to `"unspecified"`. `TestHashExtended_DirectFromLifecyclePackage` verifies nil/empty extended maps hash to empty bytes, non-empty maps hash to bytes, and multi-key maps hash stably regardless of insertion order.

Control flow/state: tests pure helpers; no persistence. The hash test forces the sort path by using multiple keys.

Dependencies/integration: uses testify and calls `HashExtended`, whose output is used by identity-CAS lifecycle delete requests. Action kind strings feed metrics labels and operator-readable logs.

Risks: this file is named as cleanup rather than function-specific, so future maintainers may overlook it when changing `ActionKind.String` or `HashExtended`. It intentionally supplements broader tests in other packages.

Test signals: small but valuable coverage for default branches and deterministic CAS witness hashing.
