# Research: sources/cloud-native/moby/daemon/cluster/executor/container/errors.go

## sources/cloud-native/moby/daemon/cluster/executor/container/errors.go

Purpose: defines package-level sentinel errors used by the container executor. The exported values are `ErrImageRequired`, `ErrContainerDestroyed`, and `ErrContainerUnhealthy`.

APIs are simple `errors.New` variables. They integrate with `newContainerConfig` for missing images, `controller.Start` when a destroy event arrives before readiness, and `controller.Start`/`Wait`/`checkHealth` when healthchecks report unhealthy. `exitError.Unwrap` can expose the underlying health error to callers using `errors.Is`.

There is no persistent state. The risk is compatibility: callers and tests may match these sentinels, so changing text or replacing variables would alter behavior. Test signal is indirect through `health_test.go`, which expects `ErrContainerUnhealthy`, and through controller lifecycle paths that propagate these values.
