# sources/control-plane/rook/tests/framework/utils/env.go

Purpose: this file provides test-environment helpers for platform naming, retry counts, OpenShift detection, and default environment variable reads.

Important APIs/types/functions: `TestEnvName`, `TestRetryNumber`, `IsPlatformOpenShift`, and `GetEnvVarWithDefault`.

Control flow: `TestEnvName` reads `TEST_ENV_NAME` with default `localhost`. `TestRetryNumber` reads `RETRY_MAX` with default `55` and panics if conversion to integer fails. `IsPlatformOpenShift` is true only when `TestEnvName()` equals `openshift`.

State and persistence behavior: no persistence. Values influence package-level retry loop initialization and platform-specific command/manifest behavior.

Dependencies and integration points: used by `k8s_helper.go`, installer namespace/OpenShift paths, log collection naming, and test wait loops.

Risks: invalid `RETRY_MAX` panics at runtime. OpenShift detection is string-exact and depends on CI naming conventions. Since `RetryLoop` is initialized at package load, later changes to `RETRY_MAX` will not affect it.

Test signals: environment override tests should verify retry parsing, default values, and OpenShift command selection.
