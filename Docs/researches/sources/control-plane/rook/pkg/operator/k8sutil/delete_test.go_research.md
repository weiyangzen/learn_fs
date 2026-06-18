# sources/control-plane/rook/pkg/operator/k8sutil/delete_test.go

Purpose: validates the generic `DeleteResource` state machine with stubbed delete and verify functions.

Important APIs/types/functions: `TestDeleteResource`.

Control flow: the test configures delete to return generic errors, NotFound, or nil, then checks MustDelete behavior, idempotent missing-resource behavior, no-wait behavior, timeout behavior with `ErrorOnTimeout` true and false, successful verification after retries, and override of retry count/interval from `DeleteOptions`.

State and persistence behavior: no Kubernetes objects are created. Local counters model resource existence and package variable `unitTestRetryIntervalRecord` records selected retry interval.

Dependencies/integration: uses Kubernetes API NotFound errors, schema group resource, time durations, and testify.

Risks: no test for nil `DeleteOptions`/`WaitOptions`, verify returning transient API errors followed by NotFound, or context cancellation because `DeleteResource` has no context parameter.

Test signals: strong coverage for the helper's intended deletion and wait contract.
