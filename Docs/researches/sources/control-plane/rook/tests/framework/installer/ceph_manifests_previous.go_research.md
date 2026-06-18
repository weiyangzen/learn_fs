# sources/control-plane/rook/tests/framework/installer/ceph_manifests_previous.go

Purpose: this adapter provides manifest generation for the prior Rook release used by upgrade tests, currently `v1.19.5`.

Important APIs/types/functions: constant `Version1_19`; struct `CephManifestsPreviousVersion` with `settings` and `latest`; methods satisfying `CephManifests`.

Control flow: base manifests such as CRDs, CSI operator, operator, common, common-external, and toolbox are read from GitHub for the target version and then patched for namespaces/settings. Most generated custom resources delegate to the current `CephManifestsMaster`. `GetObjectStore` explicitly panics if Swift/Keystone is requested for the previous version.

State and persistence behavior: no direct mutation. It returns YAML from remote release manifests and current generator wrappers that later become Kubernetes state.

Dependencies and integration points: depends on `TestCephSettings.readManifestFromGitHub`, `replaceOperatorSettings`, OpenShift selection, current manifest generator compatibility, and GitHub raw availability.

Risks: delegating most resource generators to the current implementation may produce resources unsupported by the prior release unless explicitly overridden. Remote GitHub reads add network flake and mutable availability risk. The Swift/Keystone panic is intentional but can fail upgrade tests abruptly if a caller does not gate scenarios by version.

Test signals: upgrade tests should verify previous-release installation, manifest fetch success, namespace substitution, and compatibility of delegated resources before upgrading to the local build.
