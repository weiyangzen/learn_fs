
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check.go

- Purpose: implements full and quick BeeGFS health checks.
- Important APIs: `Status`, `checkCfg`, `newCheckCmd`, `runHealthCheckCmd`, `checkForFallbacks`, `checkTargets`, `checkForBusyNodes`, `printBusyNodes`, `checkTLSCertificates`, `tlsCertExpirationStatus`, and `QuickChecks`.
- Control flow/state: fetches clients, targets, license, node stats, TLS peer data, and network connections; prints sections for general checks, busy nodes, targets, and connections; optionally watches and ignores failures.
- Dependencies/integration: uses procfs, target/stats/license backends, gRPC peer credentials, Viper display config, and terminal refresh utilities.
- Risks/tests: many remote/local dependencies can make failures environmental; quick checks must stay synchronized with full checks. TLS expiration logic has focused unit coverage in `check_test.go`.
