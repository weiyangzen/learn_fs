# sources/distributed-fs/ceph-client/include/uapi/drm/amdxdna_accel.h

## Purpose
Defines the AMD XDNA accelerator DRM UAPI for NPU hardware contexts, BOs, command execution, telemetry, resource queries, and power/preemption state.

## Important APIs, Types, And Functions
Exports invalid-handle constants, QoS priorities, device and ioctl enums, `amdxdna_qos_info`, hardware-context create/destroy/config payloads, CU configuration arrays, BO type/create/info/sync structures, command submit payloads, AIE status/version/metadata structs, clock/sensor/context/power/firmware/resource telemetry structs, `amdxdna_drm_get_info`, array-query structures, state-setting structures, and `DRM_IOCTL_AMDXDNA_*`.

## Control Flow
Ioctl workflows are declarative: create BOs, create a hardware context with QoS and UMQ/log buffers, configure CUs or debug buffers, submit commands or dependencies/signals, query metadata/telemetry/arrays, set power or preemption state, and destroy resources.

## State, Persistence, And Dependencies
Persistent kernel state includes hardware contexts, command queues, syncobjs, BO handles, device heap allocations, context telemetry counters, async errors, power mode, and preemption attributes. It depends on `<linux/stddef.h>` and `drm.h`.

## Integration Points
Used by AMD XDNA kernel driver, NPU runtime/shim layers, XRT-style management tools, DRM syncobj infrastructure, dma-buf-backed BO flows, and telemetry consumers.

## Risks
Variable-length arrays and user pointers need strict size validation. Many fields are MBZ and should reject nonzero values for forward compatibility. Command handle arrays, QoS hints, and device memory BO accounting are security and robustness sensitive. Power/preemption setters affect global device behavior.

## Test Signals
Ioctl ABI size tests, create/config/destroy context lifecycle tests, BO mmap/sync/import tests, command completion syncobj tests, telemetry buffer sizing tests, MBZ rejection tests, power mode permission tests, and async error query tests.
