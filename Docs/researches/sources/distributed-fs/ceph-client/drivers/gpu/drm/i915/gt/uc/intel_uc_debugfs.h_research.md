# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.h

## Purpose

This header exposes the aggregate uC debugfs registration hook.

## APIs, Dependencies, Risks, And Test Signals

It forward-declares `struct intel_uc` and `struct dentry` and declares `intel_uc_debugfs_register()`. The small surface keeps debugfs details out of core uC headers. Risk is limited to declaration/definition drift or callers passing a null/invalid GT root. Build coverage and creation of the `uc` debugfs directory with `usage` are the primary signals.
