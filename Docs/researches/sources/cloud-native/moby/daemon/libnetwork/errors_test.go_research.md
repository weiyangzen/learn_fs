# Research: sources/cloud-native/moby/daemon/libnetwork/errors_test.go

Purpose: validates that libnetwork error types satisfy expected classification interfaces. Important test is `TestErrorInterfaces`.

Control flow: the test checks `ManagerRedirectError` against `types.MaskableError`, `ErrNoSuchNetwork` against `cerrdefs.IsNotFound`, and `ActiveContainerError` against `cerrdefs.IsPermissionDenied`. It uses type switches and `gotest.tools` error-type comparisons.

State/dependencies: no runtime state is involved. Dependencies include containerd errdefs, libnetwork `types`, and assertion helpers. The test guards API behavior expected by higher-level error handling and API response mapping. Gaps include `NetworkNameError` conflict classification and `ActiveEndpointsError` forbidden classification, although their marker methods are present in the source. It also does not verify error message text.
