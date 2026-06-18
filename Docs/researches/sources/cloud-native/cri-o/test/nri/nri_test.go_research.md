# sources/cloud-native/cri-o/test/nri/nri_test.go

## Purpose
NRI integration tests for plugin registration, synchronization, pod/container events, and container adjustment/update features.

## Important APIs, Types, And Functions
Tests include `TestPluginRegistration`, `TestPluginSynchronization`, `TestPodEvents`, `TestContainerEvents`, `TestMountInjection`, `TestEnvironmentInjection`, `TestAnnotationInjection`, `TestDeviceInjection`, `TestCpusetAdjustment`, `TestMemsetAdjustment`, `TestCpusetAdjustmentUpdate`, and `TestMemsetAdjustmentUpdate`. Helpers include `testXxxsetAdjustment`, `testXxxsetAdjustmentUpdate`, `skipTestForCondition`, and thread-safe `idgen`.

## Control Flow
Tests skip when CRI-O/NRI socket prerequisites are absent. Registration verifies configure/synchronize event stream. Synchronization starts containers before plugin startup and verifies synced pod/container IDs. Event tests create, start, stop, and remove pods/containers while matching plugin events. Injection tests install create handlers that add mounts, env, annotations, devices, cpuset/memset values, or container updates, then verify behavior from inside containers or plugin state.

## State And Persistence
Creates live pods/containers and temp directories. Mount injection writes a file from inside the container to a host temp dir. ID generator state is process-local and protected by a mutex.

## Dependencies And Integration Points
Depends on containerd NRI API adjustment/update types, runtime helpers, filesystem helper functions, CPU/memory topology helpers, and the test plugin in `plugin.go`.

## Risks And Test Signals
Timing-sensitive with 3 to 5 second event timeouts and host topology dependencies. Strong signal for CRI-O's NRI implementation and adjustment propagation, but failures can be environmental.
