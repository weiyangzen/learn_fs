# sources/control-plane/external-snapshotter/pkg/webhook/webhook_test.go

Purpose: integration-style test for dynamic TLS certificate reload in the webhook server.

Important APIs/functions: `TestWebhookCertReload` and `generateTestCertKeyPair`.

Control flow: the test creates a temp cert/key pair, starts `StartServer` with a `CertWatcher`-backed TLS config on port `30443`, reads the original certificate from `GetCertificate`, rewrites cert/key files five times, waits for fsnotify processing, and asserts both certificate bytes and RSA private key changed each time.

State and persistence: writes temporary `tls.crt` and `tls.key` files, starts a live local TLS server goroutine, and cleans the temp directory.

Dependencies and integration: uses crypto/x509 RSA certificate generation, fsnotify through `CertWatcher`, TLS config callback behavior, and the actual server startup path.

Risks and test signals: strong signal for simple file rewrite reloads. Risks include fixed port collisions, time-based sleeps causing flakiness, panics from the server goroutine, and no HTTP request/assertion against `/readyz` or `/convert`.
