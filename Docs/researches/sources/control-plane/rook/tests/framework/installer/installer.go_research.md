# sources/control-plane/rook/tests/framework/installer/installer.go

Purpose: this file contains package-wide installer constants and small helpers shared by Rook integration installers.

Important APIs/types/functions: `LocalBuildTag`, package logger, kubectl argument constants (`createArgs`, `createFromStdinArgs`, `deleteArgs`, `deleteFromStdinArgs`), `SystemNamespace`, `checkError`, and `renderTemplate`.

Control flow: `SystemNamespace` returns the namespace itself on OpenShift and `<namespace>-system` otherwise. `checkError` ignores nil and not-found errors during cleanup but asserts any other error. `renderTemplate` parses and executes a Go text template, panicking on parse or render errors.

State and persistence behavior: no direct persistence. Constants shape applied resource operations and image tags across installer files.

Dependencies and integration points: depends on capnslog, `utils.IsPlatformOpenShift`, testify assertions, Kubernetes API errors, and `text/template`. Used by manifest generation and installer cleanup paths.

Risks: panic-based template rendering is acceptable for tests but abrupt. Cleanup assertion behavior can fail a whole suite after the underlying test passed if teardown encounters unexpected errors. The shared argument slices should not be mutated by callers.

Test signals: platform-specific namespace calculation, not-found cleanup tolerance, and template rendering for object store manifests are the key behaviors to exercise indirectly.
