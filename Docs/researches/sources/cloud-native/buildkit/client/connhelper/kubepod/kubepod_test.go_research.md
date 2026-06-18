# sources/cloud-native/buildkit/client/connhelper/kubepod/kubepod_test.go

Purpose: unit tests for Kubernetes pod connection-helper URL parsing and identifier validation.

Important APIs/types/functions: `TestSpecFromURL` covers minimal pod URLs, full context/namespace/container URLs, contexts containing `@`, empty pod names, and unsupported pod/container/namespace names.

Control flow: each URL string is parsed, passed to `SpecFromURL`, then compared to an expected `Spec` or expected error.

State and persistence: no persistent state.

Dependencies/integration points: standard `net/url`, testing, and `testify/require`.

Risks/test signals: test signals prove query extraction and validation boundaries for Kubernetes identifiers. It does not inspect actual kubectl command construction or behavior when optional query values are empty.
