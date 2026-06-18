# sources/control-plane/ceph-csi/e2e/errors.go

Purpose: centralizes retryability and kubectl stderr parsing helpers used by the e2e suite to distinguish transient API errors from terminal failures and to recognize idempotent CLI errors.

Important APIs/types/functions: `isRetryableAPIError(err)` recognizes Kubernetes internal/timeout/server-timeout/too-many-requests errors, EOF/reset/refused network errors, suggested client delays, and known transient strings. `getStdErr(errString)` extracts the `stderr:` section from the formatted kubectl error wrapper. `isAlreadyExistsCLIError(err)`, `isNotFoundCLIError(err)`, and `isNoSuchResourceCLIError(err)` classify kubectl stderr lines while ignoring blanks and warnings.

Control flow: API retryability first checks structured Kubernetes and network predicates, then falls back to string matches such as `etcdserver: request timed out`, `unable to upgrade connection`, `transport is closing`, missing content type, and pod host assignment. CLI helpers require a non-empty extracted stderr region and then scan each line, accepting only the expected error type aside from blank/warning lines.

State and persistence: no persistent state; helpers are pure string/error classifiers.

Dependencies and integration points: uses `k8s.io/apimachinery/pkg/api/errors`, `k8s.io/apimachinery/pkg/util/net`, and `strings`. Deployment, namespace, storage, and kubectl retry helpers consume these predicates to decide whether to poll again, ignore idempotent errors, or fail.

Risks: `getStdErr()` depends on exact formatting from Kubernetes e2e kubectl utilities. CLI classification is all-or-nothing across multi-resource stderr, so mixed NotFound/AlreadyExists output is rejected. Warning filtering is substring-based and could ignore meaningful lines containing `Warning`. String retryability can hide real persistent infrastructure problems until timeout.

Test signals: unit tests cover stderr extraction and AlreadyExists detection for representative kubectl output. Broader signals are reduced flakes in e2e polling loops and correct handling of idempotent create/delete operations.
