## sources/cloud-native/soci-snapshotter/config/service.go

Purpose: service-level configuration composition for filesystem, pull modes, keychains, resolver, and snapshotter behavior.

Important APIs/types/functions: `ServiceConfig`, `KubeconfigKeychainConfig`, `CRIKeychainConfig`, `SnapshotterConfig`, and `parseServiceConfig`.

Control flow: `parseServiceConfig` defaults CRI image service path to containerd's image service socket when unset.

State and persistence: no direct state; values configure daemon credential sources and snapshotter mounting policy.

Dependencies and integration: daemon startup reads these fields to configure kube/CRI/docker keychains, resolver, filesystem options, and service behavior.

Risks and test signals: only CRI path receives parser validation/defaulting here; other fields rely on consumers. Config tests assert CRI default path.
