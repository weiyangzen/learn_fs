# sources/control-plane/rook/pkg/operator/k8sutil/delete.go

Purpose: generic deletion helper logic shared by Kubernetes resource-specific delete wrappers.

Important APIs/types/functions: `BaseKubernetesDeleteOptions`, `DeleteOptions`, test variable `unitTestRetryIntervalRecord`, and `DeleteResource`.

Control flow: `BaseKubernetesDeleteOptions` returns foreground deletion with zero grace period. `DeleteResource` invokes caller-supplied delete, handles NotFound as success unless `MustDelete`, returns errors for other delete failures, optionally waits by repeatedly invoking caller-supplied verify until it returns NotFound, and either returns or logs timeout depending on `ErrorOnTimeout`. Retry count/interval come from opts with defaults supplied by the resource wrapper.

State and persistence behavior: no direct Kubernetes access; persistence is through injected delete/verify closures. Records retry interval in a package variable for tests.

Dependencies/integration: used by `DeleteConfigMap` and other delete helpers. Depends on Kubernetes API error classification and `WaitOptions` from elsewhere in k8sutil.

Risks: callers must provide a verify function where NotFound means deleted; other errors do not break early and are reported only at timeout. Passing nil `opts` would panic because fields are accessed directly. Logs use seconds formatting, losing sub-second precision in messages.

Test signals: `delete_test.go` covers delete errors, NotFound with/without MustDelete, no-wait default, wait timeout with and without error, successful wait after retries, and explicit retry option overrides.
