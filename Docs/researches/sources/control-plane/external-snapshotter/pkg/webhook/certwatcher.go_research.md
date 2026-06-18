# sources/control-plane/external-snapshotter/pkg/webhook/certwatcher.go

Purpose: watches TLS certificate and key files for changes and exposes the currently loaded certificate to the HTTPS webhook server.

Important APIs/types/functions: `CertWatcher`, `NewCertWatcher`, `GetCertificate`, `Start`, `Watch`, `ReadCertificate`, `handleEvent`, and fsnotify event helpers.

Control flow: construction loads the initial key pair and creates an fsnotify watcher. `Start` registers both file paths, starts `Watch` in a goroutine, blocks until context cancellation, then closes the watcher. Watch events for write/create/remove trigger a certificate reload; remove events also attempt to re-add the watch.

State and persistence: holds the current `tls.Certificate` in memory behind a mutex. Persistent state is the certificate/key files on disk, which are read but not written.

Dependencies and integration: adapted from controller-runtime internals; integrates `fsnotify`, `crypto/tls`, klog, and `http.Server` TLS `GetCertificate` callbacks.

Risks and test signals: risks include reload failure leaving the previous certificate active, watching removed files directly rather than parent directories, races around rotation patterns, and logging without surfacing errors to readiness. The webhook reload test exercises repeated file rewrites and `GetCertificate` changes.
