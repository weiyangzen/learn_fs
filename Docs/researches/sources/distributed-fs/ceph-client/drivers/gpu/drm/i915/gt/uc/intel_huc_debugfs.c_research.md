# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_debugfs.c

## Purpose

This file registers HuC-specific debugfs reporting under the GT uC debugfs tree. It provides a narrow `huc_info` file that dumps HuC load and authentication state through the common DRM printer.

## Important APIs, Control Flow, And Integration

`huc_info_show()` obtains `struct intel_huc` from `seq_file::private`, returns `-ENODEV` for unsupported HuC, and delegates formatting to `intel_huc_load_status()`. `intel_huc_debugfs_register()` registers a single `intel_gt_debugfs_file` when HuC is supported. It is invoked by `intel_uc_debugfs_register()` after creating the `uc` directory.

## State, Risks, And Test Signals

The file does not own persistent state. It depends on `intel_gt_debugfs`, `drm_print`, and `intel_huc_load_status()`, which may take runtime PM to read registers. Risk is mostly stale or missing status exposure if support predicates diverge. Test signals are presence/absence of `uc/huc_info`, correct unsupported error behavior, and output containing firmware dump plus HuC status register value on supported platforms.
