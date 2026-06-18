# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc.h

## Purpose

This header defines the aggregate `struct intel_uc` and the operation indirection used by GT code to call uC lifecycle hooks regardless of whether GuC is enabled.

## Important APIs, Types, And Functions

`struct intel_uc_ops` contains optional hooks for sanitize, firmware fetch/cleanup, software init/fini, hardware init/fini, and mapping resume. `struct intel_uc` embeds `intel_gsc_uc`, `intel_guc`, and `intel_huc`, records the last failed GuC load log, and tracks reset/fw-table flags. State-checker macros generate `supports`, `wants`, and `uses` helpers for GuC, HuC, GuC submission, SLPC, RC, and GSC uC. Operation-wrapper macros provide no-op/default-return behavior when a hook is absent.

## Control Flow, Dependencies, Risks, And Test Signals

The header is consumed by GT driver init, reset, PM, debugfs, and the GuC/HuC modules. The comment documents the four-state model: not supported, supported, wanted, and in use, with “in use” committing the driver to microcontroller operation once blobs are found. Risks are state-model drift and wrappers hiding absent operations, especially when off-mode must still perform hardware safety checks. Build coverage, all `enable_guc` combinations, firmware-missing cases, and reset/suspend calls through wrappers are the main signals.
