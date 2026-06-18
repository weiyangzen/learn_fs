# sources/control-plane/external-snapshotter/pkg/webhook/config.go

Purpose: defines minimal TLS configuration input and a helper to create a static `tls.Config` from certificate files.

Important APIs/types/functions: `Config` with `CertFile` and `KeyFile`, and `configTLS`.

Control flow: `configTLS` loads the X.509 key pair from disk and returns a TLS config with the certificate installed; load failures call `klog.Fatal`.

State and persistence: reads certificate files and stores loaded certificate material in memory.

Dependencies and integration: depends on `crypto/tls` and klog. It can be used by webhook startup code when dynamic `CertWatcher` is not driving `GetCertificate`.

Risks and test signals: fatal exit makes this unsuitable for recoverable library use; static certificates will not reload. Dynamic reload behavior is tested in `webhook_test.go`, but this helper itself has no direct tests.
