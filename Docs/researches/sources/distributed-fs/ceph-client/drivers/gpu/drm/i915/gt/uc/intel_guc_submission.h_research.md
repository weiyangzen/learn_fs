# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_submission.h

## Purpose

This header exposes the GuC submission backend contract to the rest of i915 GT/uC code. It declares lifecycle, setup, reset-visible, debug, busyness, virtual-engine heartbeat, and pending-message wait APIs while keeping implementation details in `intel_guc_submission.c`.

## Important APIs, Types, And Functions

The public functions cover early/init/enable/disable/fini, per-engine setup, debug printing, active request dumping, busyness park/unpark, pending-message wait, and work flushing. The inline predicates `intel_guc_submission_is_supported()`, `intel_guc_submission_is_wanted()`, and `intel_guc_submission_is_used()` map `struct intel_guc` booleans and firmware use state into the common uC state model.

## Control Flow

`intel_uc.c` calls these APIs in order: early selection during uC early init, memory initialization before firmware load, engine vfunc setup during engine initialization, enable after GuC firmware/CT communication are running, reset hooks during GT reset, disable/fini during unload or failed init, and debug functions through GuC/UC debugfs.

## State, Dependencies, Risks, And Test Signals

The header depends on `intel_guc.h`, `linux/types.h`, and forward declarations for `drm_printer` and engines. Its main risk is contract drift: callers rely on `is_used()` requiring both a running GuC and selected submission. Build coverage, GuC-enabled boot, debugfs registration, reset/suspend paths, and users of `intel_uc_wait_for_idle()` are the key test signals.
