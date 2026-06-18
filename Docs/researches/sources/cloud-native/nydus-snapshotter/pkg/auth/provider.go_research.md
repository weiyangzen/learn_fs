# sources/cloud-native/nydus-snapshotter/pkg/auth/provider.go

Purpose: defines shared provider interfaces, request metadata, renewal capability, and canonical image reference parsing for all auth providers.

Important APIs and functions: `AuthRequest` carries `Ref`, optional `Labels`, and optional `ValidUntil`; `AuthProvider` requires `GetCredentials` and `String`; `RenewableProvider` adds `CanRenew`; `parseReference` returns containerd `reference.Spec` plus distribution host.

Control flow: `parseReference` first normalizes with `distribution.ParseDockerRef`, then parses the normalized string through containerd's `reference.Parse`, extracts the domain with `distribution.Domain`, and rejects missing hosts.

State and persistence: no mutable state; this is interface and helper code.

Dependencies and integration points: all providers use `AuthRequest` and most use `parseReference`. `ValidUntil` is specifically consumed by `KubeletProvider` to bypass cached plugin credentials that expire before the next renewal.

Risks: provider implementations differ on nil-request handling; `LabelsProvider` assumes non-nil. `parseReference` behavior depends on distribution reference normalization, so short refs are canonicalized before host extraction.

Test signals: no dedicated provider test file is listed, but Docker, CRI, kubelet, Kubernetes secret, and renewal tests exercise ref parsing and interface behavior.
