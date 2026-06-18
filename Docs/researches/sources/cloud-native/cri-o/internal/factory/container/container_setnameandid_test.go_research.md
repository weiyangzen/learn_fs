# sources/cloud-native/cri-o/internal/factory/container/container_setnameandid_test.go

Purpose: tests container ID generation/reuse and Kubernetes-style container name construction.

Important APIs/types/functions: exercises `container.New`, `SetConfig`, `SetNameAndID`, `ID`, `Name`, and helper `setupContainerWithMetadata`.

Control flow: tests verify generated IDs are 64 characters, generated names contain pod name/namespace/UID, explicit old IDs are reused, empty sandbox metadata is accepted, and calling `SetNameAndID` before config setup fails.

State and persistence behavior: in-memory only; generated IDs use storage `stringid.GenerateNonCryptoID` through implementation.

Dependencies/integration points: Ginkgo/Gomega, CRI API types, and container factory package.

Risks: tests assert substrings rather than exact full name format and do not cover attempt number formatting.

Test signals: focused coverage for identity setup and precondition enforcement.
