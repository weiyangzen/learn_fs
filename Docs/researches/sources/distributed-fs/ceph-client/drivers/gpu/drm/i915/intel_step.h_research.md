# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.h

Purpose: Defines the normalized stepping data structure and public stepping helpers.

Important APIs/types: `struct intel_step_info` has `graphics_step` and `media_step`, where graphics represents the compute tile on Xe HPC. Exports `intel_step_init()` and `intel_step_name()`.

Control flow: None in the header beyond declarations. The comment establishes the numeric convention that GMD step conversion relies on: four numeric steps per letter.

State/persistence: No state. It describes the shape of `RUNTIME_INFO(i915)->step` values written by the implementation.

Dependencies/integration: Includes Linux types and `drm/intel/step.h` for `enum intel_step`. Consumed by platform init and code that prints or compares hardware stepping.

Risks: Any enum-layout change in `drm/intel/step.h` that violates the four-steps-per-letter assumption would break GMD conversion.

Test signals: Build-time type checking and runtime unknown-revision warnings from `intel_step.c`.
