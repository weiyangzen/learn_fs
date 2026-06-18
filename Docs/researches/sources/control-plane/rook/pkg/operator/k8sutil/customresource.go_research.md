# sources/control-plane/rook/pkg/operator/k8sutil/customresource.go

Purpose: defines a simple metadata struct for Kubernetes custom resources.

Important APIs/types/functions: `CustomResource` with fields `Name`, `Plural`, `Group`, `Version`, `Kind`, and `APIVersion`.

Control flow: none. The struct is a data container.

State and persistence behavior: none by itself. Instances can describe CRD/API metadata for other code paths.

Dependencies/integration: no imports. Package comment says Kubernetes operator kit.

Risks: no validation methods are attached, so callers must ensure fields are complete and consistent.

Test signals: no direct tests in this subset; behavior is structural only.
