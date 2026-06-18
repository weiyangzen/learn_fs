# sources/cloud-native/cri-o/server/naming_test.go

Purpose: Ginkgo tests for sandbox infra container name reservation.

Important APIs and functions: exercises `sut.ReserveSandboxContainerIDAndName` with valid metadata, nil config, missing metadata, and duplicate metadata.

Control flow: the duplicate test reserves once, then retries with the same metadata and expects an error.

State and persistence: mutates the in-memory name reservation store in the test server and cleans it up via framework teardown.

Dependencies and integration: CRI-O server test framework, Ginkgo/Gomega, and CRI sandbox metadata types.

Risks: does not assert exact generated name format, only that a name is non-empty or reservation fails.

Test signals: protects validation and duplicate-reservation behavior used by sandbox creation cleanup logic.
