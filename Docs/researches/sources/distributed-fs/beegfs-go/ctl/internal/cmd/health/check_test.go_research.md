
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/check_test.go

- Purpose: unit-tests TLS certificate expiration classification used by health checks.
- Important APIs: `TestTLSCertExpirationStatus`, `TestTLSCertExpirationStatusUsesEarliestExpiry`, and `TestTLSCertExpirationStatusNoCerts`.
- Control flow/state: builds synthetic `x509.Certificate` slices around a fixed `2026-01-01` clock and asserts `Healthy`, `Degraded`, or `Critical` plus exact user-facing message text.
- Dependencies/integration: uses `stretchr/testify/assert` and the package-local `tlsCertExpirationStatus`.
- Risks/tests: good boundary coverage at 90 and 30 days, expired durations, no certs, and earliest-chain expiry. It does not cover `checkTLSCertificates` peer extraction or non-TLS transport cases.
