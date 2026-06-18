# sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/kustomization.yaml

Purpose: base Kustomize entry for Nydus snapshotter Kubernetes deployment.

Structure: declares `nydus-snapshotter.yaml` as the only resource with kustomize v1beta1 metadata.

State/dependencies: no runtime state; consumed by `kubectl apply -k` or overlays.

Integration points: overlays for k3s and rke2 reference this base.

Risks/tests: minimal file; drift risk is only resource naming/path. Validation is by Kubernetes/kustomize tooling, not Go tests.
