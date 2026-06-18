# sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/create-cert.sh

## Purpose
Creates example TLS material for the snapshot conversion webhook deployment.

Source size: 128 lines, 3579 bytes.

## Important APIs, Types, and Functions
- Shell functions: `usage`.
- External commands/helpers: `base64`, `kubectl`, `mktemp`, `openssl`.

## Control Flow
- Generates a CA and serving certificate/key with OpenSSL for the webhook service DNS names.
- Creates or updates Kubernetes TLS/CA secrets expected by the webhook example.
- Feeds the generated CA to the webhook example patching flow.

## State and Persistence
- Creates local certificate files and Kubernetes Secret state for the example namespace.
- Certificate validity and SANs determine API-server trust.

## Dependencies and Integration Points
- openssl, kubectl, Kubernetes cluster access, webhook example namespace/service naming.

## Risks and Edge Cases
- Example certificates are for development/demo use and must not be reused as production PKI.
- Service DNS names, namespace, and CA bundle must match the webhook manifest.

## Test Signals
- Successful webhook TLS handshake and API conversion calls validate the output.
