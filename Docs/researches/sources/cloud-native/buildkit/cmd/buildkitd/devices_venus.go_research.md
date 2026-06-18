# Research: sources/cloud-native/buildkit/cmd/buildkitd/devices_venus.go

Purpose: conditionally imports the Venus CDI setup package when the `venus` build tag is enabled. Its behavior is side-effect registration for Docker Desktop GPU support.

Important behavior: the file has build tag `venus`, package `main`, and a blank import of `github.com/moby/buildkit/contrib/cdisetup/venus`, causing package init to register the `docker.com/gpu` setup.

State and dependencies: no local state. The imported package may later inspect devices and write CDI specs when invoked through the CDI manager.

Risks and test signals: feature availability depends entirely on build tags. There are no direct tests for this import wiring.
