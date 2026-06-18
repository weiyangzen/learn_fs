# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_features.h

## Purpose
This header defines software feature bits and model-specific feature masks for supported Mali Midgard/Bifrost GPUs.

## Important APIs, Types, and Functions
`enum panfrost_hw_feature` lists feature flags such as jobchain disambiguation, XAFFINITY, flush reduction, protected mode, AArch64 MMU, TLS hashing, IDVS group size, and cache-clean safety. `hw_features_*` macros map GPU families to bitmasks. `panfrost_has_hw_feature` tests the runtime bitmap.

## Control Flow
There is no runtime flow beyond the inline bitmap test. `panfrost_gpu_init_features` consumes the masks when it matches a GPU model and populates `pfdev->features.hw_features`.

## State and Persistence Behavior
The header defines compile-time masks. Runtime feature state lives in `struct panfrost_features` in the device object.

## Dependencies and Integration Points
It depends on bitops and `panfrost_device.h`. GPU init, MMU selection, job submission, quirks, flush reduction, and reset logic use these feature predicates.

## Risks
Incorrect model masks can enable unsupported hardware paths or miss required workarounds. Feature names are driver-internal and must stay aligned with register/programming assumptions, not just marketing GPU names.

## Test Signals
Validate feature bitmaps in boot logs for each GPU model, exercise AArch64 MMU and flush-reduction paths only on advertised hardware, and compare userspace feature queries against expected model data.
