# Research: sources/cloud-native/buildkit/cmd/buildkitd/devices_nvidia.go

Purpose: conditionally imports the NVIDIA CDI setup package when the `nvidia` build tag is enabled. Its only job is side-effect registration.

Important behavior: the file has build tag `nvidia`, package `main`, and a blank import of `github.com/moby/buildkit/contrib/cdisetup/nvidia`, causing that package's `init` to register its `nvidia.com/gpu` setup with the CDI device manager.

State and dependencies: no local state. Runtime state is created by the imported package's registration and later device setup.

Risks and test signals: build-tag selection controls whether experimental NVIDIA on-demand setup is present in the daemon. There are no direct tests for tag wiring here; `nvidia_test.go` covers a helper in the imported package.
