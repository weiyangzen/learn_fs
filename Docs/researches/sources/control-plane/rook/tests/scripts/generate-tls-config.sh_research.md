<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/generate-tls-config.sh -->
# sources/control-plane/rook/tests/scripts/generate-tls-config.sh

Purpose: helper for generating a simple CA, server certificate, and key for Vault or other in-cluster TLS test services.

Important APIs and control flow: it accepts output directory, service, namespace, and optional IP. If IP is omitted, it uses `127.0.0.1`. It writes OpenSSL config files, generates a CA key/cert, generates a service key/CSR with DNS SANs for service and namespace forms plus IP SAN, signs the CSR, and exports `CSR_NAME`.

State, persistence, and integration: writes certificate/key artifacts into the requested directory for later Secret creation. Dependencies include `openssl`, shell, and consumers such as `deploy-validate-vault.sh`. Risks include short-lived local private keys, minimal CA handling, and fixed SAN assumptions. Test signals are successful OpenSSL commands and downstream TLS clients connecting to the generated certs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/generate-tls-config.sh -->
