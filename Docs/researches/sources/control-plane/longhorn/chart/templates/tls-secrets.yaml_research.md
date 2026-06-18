# sources/control-plane/longhorn/chart/templates/tls-secrets.yaml

Purpose: optionally creates TLS secrets for chart-managed UI Ingress.

Important APIs/types/functions: Kubernetes `Secret` type `kubernetes.io/tls`, `.Values.ingress.enabled`, `.Values.ingress.secrets`, secret `name`, `key`, `certificate`, `b64enc`, release namespace, and chart labels.

Control flow: if ingress is enabled, the template iterates over configured secrets and emits one TLS secret per entry, followed by a YAML document separator. Certificate and key values are base64-encoded directly from values.

State and persistence: persistent Kubernetes Secret state stores TLS private keys and certificates. Ingress objects can reference these secrets through `.Values.ingress.tlsSecret`.

Dependencies/integration: depends on `ingress.yaml` when TLS is enabled, and on users supplying correctly paired PEM key/certificate content. It may coexist with cert-manager or external secret management if no inline secrets are provided.

Risks: storing PEM material in Helm values exposes secrets in release history unless mitigated. A mismatch between secret names here and `ingress.tlsSecret` leaves Ingress without the intended certificate. Empty or malformed certificate/key values still render base64 strings but fail controller validation.

Test signals: render with ingress disabled, ingress enabled with no secrets, and one or more secrets. Decode generated data and validate certificate/key pair; verify Ingress TLS uses the expected secret name.
