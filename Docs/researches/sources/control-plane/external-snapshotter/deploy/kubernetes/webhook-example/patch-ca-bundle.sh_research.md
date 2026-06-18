# sources/control-plane/external-snapshotter/deploy/kubernetes/webhook-example/patch-ca-bundle.sh

## Purpose
Patches the webhook example manifest or live configuration with the generated CA bundle.

Source size: 12 lines, 406 bytes.

## Important APIs, Types, and Functions
- External commands/helpers: `kubectl`.

## Control Flow
- Reads CA certificate material, base64-encodes or injects it, and patches the webhook configuration.
- Updates the `caBundle` field so the Kubernetes API server trusts the conversion webhook service.

## State and Persistence
- Mutates webhook configuration YAML or Kubernetes API state depending on invocation.
- No controller state is stored locally beyond generated cert files.

## Dependencies and Integration Points
- kubectl/sed/base64 tooling, generated CA certificate, webhook example manifest.

## Risks and Edge Cases
- Incorrect CA bundle breaks CRD conversion requests.
- Patching assumptions can drift if webhook YAML structure changes.

## Test Signals
- API-server conversion through the webhook and successful `kubectl apply` of CRDs validate the patch.
