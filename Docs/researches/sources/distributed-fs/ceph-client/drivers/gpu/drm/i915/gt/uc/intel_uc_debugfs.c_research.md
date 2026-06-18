# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_debugfs.c

## Purpose

This file creates the top-level GT `uc` debugfs directory and registers aggregate GuC/HuC/GSC debug views.

## Important APIs And Control Flow

`uc_usage_show()` prints supported/wanted/used booleans for GuC, HuC, and GuC submission using generated state helpers. `intel_uc_debugfs_register()` returns early without a GT root or without GuC support, creates `uc`, stores it in `uc->guc.dbgfs_node`, registers the `usage` file, then delegates to GSC, GuC, and HuC debugfs registration.

## State, Dependencies, Risks, And Test Signals

The only persistent side effect is the debugfs dentry pointer in GuC. Dependencies include Linux debugfs, DRM printers, `intel_gt_debugfs`, and each subcomponent debugfs registrar. Risks include partial debugfs registration if one subcomponent is unsupported and user-visible confusion when GuC unsupported suppresses HuC/GSC entries. Test signals are the `uc/usage` file content across `enable_guc` modes and the presence of nested GuC/HuC/GSC debug files on supported platforms.
