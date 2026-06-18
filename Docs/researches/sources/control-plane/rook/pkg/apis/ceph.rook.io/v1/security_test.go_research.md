# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security_test.go

Purpose: tests KMS authentication helper predicates for Vault Agent and Kubernetes auth modes.

Important APIs/types/functions: exercises `KeyManagementServiceSpec.IsAgentAuthEnabled` and `KeyManagementServiceSpec.IsK8sAuthEnabled`.

Control flow: each test defines a table of `ConnectionDetails` maps and `TokenSecretName` values. Agent auth cases cover empty config, auth method set to agent with token present, auth method set to token, and auth method set to agent without token. Kubernetes auth cases cover empty config, token-only, Kubernetes auth with token present, unknown auth method, and Kubernetes auth without token.

State and persistence: test-only local KMS specs; no persistence.

Dependencies/integration: uses standard testing only. The tests validate the precedence rule that token secret configuration disables agent/Kubernetes auth helper results.

Risks: tests use literal `"VAULT_AUTH_METHOD"` strings rather than imported constants, so constant drift could break runtime behavior without making the intent obvious. They do not cover provider helpers, TLS helpers, `IsEnabled`, `IsTokenAuthEnabled`, or whitespace trimming.

Test signals: focused coverage for two auth modes and token-secret precedence.
