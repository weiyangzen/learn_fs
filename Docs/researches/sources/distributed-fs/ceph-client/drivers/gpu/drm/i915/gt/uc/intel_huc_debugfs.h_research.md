# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.h

## Purpose

This header exposes HuC debugfs registration to the UC debugfs aggregator.

## APIs, Dependencies, Risks, And Test Signals

It forward-declares `struct intel_huc` and `struct dentry` and declares `intel_huc_debugfs_register()`. The dependency surface is intentionally small to avoid pulling debugfs internals into other uC headers. Contract risk is limited to signature drift with `intel_huc_debugfs.c` and callers. Build coverage and the presence of `uc/huc_info` when HuC is supported are sufficient signals.
