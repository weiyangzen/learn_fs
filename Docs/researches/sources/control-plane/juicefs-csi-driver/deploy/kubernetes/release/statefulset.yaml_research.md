<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/statefulset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/statefulset.yaml

## Purpose
Release overlay patch that removes the webhook certificate volume and mount from the controller StatefulSet.

## Important APIs, Types, and Resources
Targets `apps/v1` StatefulSet `juicefs-csi-controller`; deletes `volumeMounts[name=webhook-certs]` from `juicefs-plugin` and `volumes[name=webhook-certs]` from the pod spec.

## Control Flow
When the release overlay builds, this patch is applied after base resources are loaded and before inline deletion of webhook objects. The release controller runs without webhook TLS material.

## State and Persistence
No source-level state. Persisted effect is the rendered StatefulSet template lacking the certificate mount and volume.

## Dependencies and Integration Points
Depends on Kustomize strategic merge `$patch: delete` and base names. Integrates with default release mode where admission webhooks are not installed.

## Risks
If webhook flags remain enabled while cert volumes are deleted, the controller would fail webhook serving. Name drift can make the delete ineffective and leave unused secret mounts.

## Test Signals
Build the release overlay and verify no `webhook-certs` volume/mount remains; run controller startup and non-webhook provisioning tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/release/statefulset.yaml -->
