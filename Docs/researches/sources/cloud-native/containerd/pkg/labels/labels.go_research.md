# sources/cloud-native/containerd/pkg/labels/labels.go

Purpose: central constants for well-known containerd labels used across content, namespace, and distribution metadata.

Important APIs/types/functions: `LabelUncompressed` marks compressed layer contents with the uncompressed digest. `LabelSharedNamespace` marks namespaces whose contents may be shared. `LabelDistributionSource` records content origin, for example distribution registry and repository source.

Control flow: none; constants only.

State/persistence: labels are persisted as metadata keys wherever containerd stores content or namespace records. This file only defines keys.

Dependencies/integration: imported by content management, namespace sharing, and distribution pull/push paths that need stable label names.

Risks: changing constant values breaks existing metadata compatibility and external tooling. The constants do not validate label values or ownership of subkeys such as distribution source suffixes.

Test signals: no direct tests here; validation tests cover size limits in `validate.go`. Integration tests should assert these labels are emitted and read consistently by content and namespace flows.
