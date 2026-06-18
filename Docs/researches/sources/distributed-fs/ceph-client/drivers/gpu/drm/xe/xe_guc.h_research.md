# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc.h

## Purpose

`xe_guc.h` is the public GuC interface for the Xe driver. It exposes lifecycle, upload, reset, communication, self-configuration, IRQ, diagnostic, and helper APIs plus version-comparison macros and engine-class conversion helpers.

## Important APIs, Types, and Functions

- Version macros: `MAKE_GUC_VER()`, `MAKE_GUC_VER_STRUCT()`, `MAKE_GUC_VER_ARGS()`, `GUC_SUBMIT_VER()`, `GUC_FIRMWARE_VER()`, and `GUC_FIRMWARE_VER_AT_LEAST()`.
- Lifecycle/upload APIs mirror `xe_guc.c`: init, post-hwconfig, post-load, reset, upload, min-load, communication enable, suspend/resume, sanitize, stop/start, reset prepare/wait, and wedging.
- Command APIs: `xe_guc_auth_huc()`, `xe_guc_mmio_send*()`, `xe_guc_self_cfg32/64()`, and notification/IRQ helpers.
- Inline helpers convert engine classes to GuC classes and derive `xe_gt`, `xe_device`, and `drm_device` from `struct xe_guc`.

## Control Flow

The header defines the orderable API surface used by GT/uC initialization code: early communication init precedes MMIO messages; noalloc/init/post-hwconfig prepare memory and subsystems; upload starts firmware; communication enable starts CT; post-load enables opt-ins and submission. Inline version checks gate feature setup across implementation files.

## State and Persistence Behavior

No state is owned here. The helpers expose state in `struct xe_guc`, especially firmware version arrays, GT backpointers, and the `uc.guc` placement inside `struct xe_gt`.

## Dependencies and Integration Points

It includes `xe_gt.h`, `xe_guc_types.h`, hardware engine types, and local macro helpers. It is consumed by ADS, CT, capture, HuC auth, submission, reset, debug, and power-management modules.

## Risks and Edge Cases

`xe_engine_class_to_guc_class()` returns `-1` as a `u16` on invalid input after warning, so callers must not treat invalid classes as usable. Version macros rely on 8-bit components and compile-time argument selection; misuse with too many or too few arguments intentionally build-fails.

## Test Signals

Build coverage catches prototype drift. Unit tests should verify class mapping, invalid class warnings, version macro packing, `GUC_FIRMWARE_VER_AT_LEAST()` thresholds, and caller ordering assumptions in init/upload paths.
