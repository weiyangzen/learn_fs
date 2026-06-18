# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/commiter_helpers_test.go

Purpose: unit tests helper functions in `commiter.go`.

Important APIs and flow: `TestWithRetry` and `TestWithRetryImmediate` validate retry counts and final error behavior. `TestValidateRef` and `TestValidateRefAddsTag` assert Docker reference normalization and digested reference rejection. `TestGetDistributionSourceLabel` and invalid cases verify containerd distribution-source label construction. `TestMountList` checks thread-safe append behavior at the API level. `TestMakeDesc` and marshal-error cases validate JSON descriptor generation.

State and persistence: pure in-memory except for no-op descriptor data. No containerd or registry operations are invoked.

Dependencies and integration: validates behavior critical to manifest push and retry control. Uses OCI descriptors and distribution/reference parsing.

Risks and test signals: good coverage of deterministic helpers. It does not test concurrent `MountList.Add`, real retry side effects, or descriptor media type preservation beyond simple inputs.
