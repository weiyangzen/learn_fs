# sources/cloud-native/cri-o/server/naming.go

Purpose: creates and reserves Kubernetes-style infra container names for pod sandboxes.

Important APIs and functions: `makeSandboxContainerName` joins `k8s`, `POD`, pod name, namespace, UID, and attempt with underscores. `ReserveSandboxContainerIDAndName` validates config/metadata, generates a non-cryptographic storage ID, and reserves the generated name through `ReserveContainerName`.

Control flow: validation happens before ID generation; reservation errors propagate to the caller.

State and persistence: mutates the server's container-name reservation index. The generated ID is used as the reservation owner.

Dependencies and integration: depends on Kubernetes CRI sandbox metadata, CRI-O `oci.InfraContainerName`, and storage `stringid.GenerateNonCryptoID`. Called during `RunPodSandbox` before storage creation.

Risks: duplicate metadata fields produce duplicate names and reservation failure; callers must release reserved names on later sandbox-creation failure.

Test signals: `naming_test.go` covers successful reservation, nil config, missing metadata, and duplicate-name reservation failure.
