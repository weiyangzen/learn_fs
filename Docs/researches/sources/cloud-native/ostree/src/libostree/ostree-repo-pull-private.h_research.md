# sources/cloud-native/ostree/src/libostree/ostree-repo-pull-private.h

Purpose: declares private pull-state types and verification helper prototypes shared by OSTree pull implementation files.

Important APIs/types/functions: defines `OstreeFetcherSecurityState` and the large `OtPullData` struct. Declares `_signapi_init_for_remote`, `_sign_verify_for_remote`, `_verify_unwritten_commit`, and `_process_gpg_verify_result`.

Control flow: `OtPullData` is the shared mutable state machine for pull operations: remote identity, fetcher/mirrorlists/local caches, main context/cancellable/progress, HTTP options, phases, verification settings, summary metadata, ref maps, static delta state, object request/pending sets, counters, timestamp/depth limits, import flags, signapi verifier arrays, queued object scans, and async error handling.

State and persistence: the struct itself is transient pull runtime state, but it coordinates persistent writes to the target repo, object imports, verification caches, and summary/ref decisions in other files. `verified_commits` and `signapi_verified_commits` avoid duplicate verification.

Dependencies/integration: includes fetcher utilities, remote/private repo headers, and is consumed by `ostree-repo-pull.c`, `ostree-repo-pull-verify.c`, and related static delta/fetch code. Verification helpers declared here are implemented in `ostree-repo-pull-verify.c`.

Risks: the struct is broad and mutable, so field initialization and cleanup must stay synchronized with pull code. Counters and pending sets drive async completion and progress; mistakes can deadlock or prematurely complete pulls. Security fields (`gpg_verify`, `signapi_*`, `trusted_http_direct`, `disable_verify_bindings`) must be interpreted consistently across fetch and verify stages.

Test signals: pull shell tests, signed pull tests, mirrorlist tests, and pre-signed pull tests exercise subsets of this state. Field-level changes need broad pull regression coverage.
