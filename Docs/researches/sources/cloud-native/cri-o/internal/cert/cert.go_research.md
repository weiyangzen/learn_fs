# sources/cloud-native/cri-o/internal/cert/cert.go

## Purpose
TLS certificate configuration and hot-reload support for CRI-O metrics/streaming endpoints.

## Important APIs, Types, and Functions
Config holds tls.Config under RWMutex plus cert/key/CA paths, min TLS version, ciphers. NewCertConfig loads certs, creates fsnotify watcher, reloads on file events, closes on doneChan. GetConfigForClient returns current config. reload validates key pair dates and optional client CA mTLS. GenerateSelfSignedCertKey creates cert/key if both absent.

## Control Flow
Initial load must succeed; watcher goroutines monitor cert/key/CA files and swap tls.Config atomically on successful reload while retaining previous config on errors. Self-signed generation only occurs when both cert and key are missing.

## State and Persistence
Persists generated cert/key files with 0700 dirs and 0600 files; in-memory tls.Config is protected by mutex.

## Dependencies
Depends on crypto/tls/x509, fsnotify, client-go cert.GenerateSelfSignedCertKey, filesystem, internal log.

## Integration Points
Integrated with CRI-O TLS-enabled metrics/streaming server via GetConfigForClient callback.

## Risks and Edge Cases
Fatal on watcher.Add failures inside goroutine; CA AppendCertsFromPEM return is not checked; if only one of cert/key missing generation does nothing; reload on every fs event can duplicate work.

## Test Signals
Signals are successful config load, cert date logs, fsnotify reload logs, and TLS client/server behavior; direct tests not in subset.
