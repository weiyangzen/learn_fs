# sources/distributed-fs/ceph-client/drivers/edac/debugfs.c

## Purpose
This file provides EDAC debugfs support. It creates the top-level `debugfs` directory for EDAC, exposes generic memory-controller fake-error injection controls, and exports helper wrappers for EDAC drivers that need debugfs files or directories.

## Important APIs, Types, And Functions
The top-level state is the static `struct dentry *edac_debugfs`. `edac_debugfs_init()` creates `/sys/kernel/debug/edac`, and `edac_debugfs_exit()` removes it recursively. `edac_create_debugfs_nodes()` creates per-memory-controller injection controls.

`edac_fake_inject_write()` is the write handler for `fake_inject`; it chooses CE or UE from `mci->fake_inject_ue`, defaults count to one if `fake_inject_count` is zero, and calls `edac_mc_handle_error()` with user-selected layer indexes. Exported wrappers include `edac_debugfs_create_dir()`, `edac_debugfs_create_dir_at()`, `edac_debugfs_create_file()`, `edac_debugfs_create_x8()`, `edac_debugfs_create_x16()`, and `edac_debugfs_create_x32()`.

## Control Flow
At EDAC core initialization, `edac_debugfs_init()` creates the root. When a memory controller is added to sysfs, `edac_create_debugfs_nodes()` creates a child directory named after `mci->dev.kobj.name`, creates `fake_inject_<layer-name>` files for each MC hierarchy layer, creates `fake_inject_ue` and `fake_inject_count`, and creates the write-only `fake_inject` trigger file. On removal, callers remove `mci->debugfs`, and final EDAC shutdown removes the top-level tree.

## State And Persistence
Debugfs files directly modify fields embedded in `struct mem_ctl_info`: `fake_inject_layer[]`, `fake_inject_ue`, and `fake_inject_count`. No state is persisted across device removal or module unload. Fake injection increments normal EDAC counters and emits normal EDAC logs/traces, but it does not exercise hardware-specific decoding.

## Dependencies And Integration Points
The file depends on debugfs, simple file operations, `edac_module.h`, `to_mci()`, `edac_layer_name[]`, and `edac_mc_handle_error()`. Several hardware drivers use the exported debugfs wrappers for driver-specific injection controls.

## Risks
Fake injection is for EDAC core handling only; it can create misleading confidence if treated as hardware decode coverage. Layer values are user-controlled and rely on `edac_mc_handle_error()` sanity checks for out-of-range positions. Helper wrappers fall back to the top-level EDAC debugfs directory if a parent is not provided.

## Test Signals
Signals include existence of per-MC fake injection files under debugfs, CE/UE counter increments after writing `fake_inject`, correct layer-name files for each topology, and full cleanup after MC removal and EDAC debugfs exit.
