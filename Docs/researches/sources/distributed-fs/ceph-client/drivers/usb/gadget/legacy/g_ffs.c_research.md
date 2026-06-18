# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/g_ffs.c

## Purpose

`g_ffs.c` implements the legacy FunctionFS gadget `g_ffs`. It waits for one or more userspace FunctionFS functions to become ready, then registers a composite gadget containing those userspace functions and optional ECM/RNDIS networking configurations.

## Important APIs, Types, and Functions

Important lifecycle functions are `gfs_init()`, `gfs_exit()`, `functionfs_ready_callback()`, `functionfs_closed_callback()`, `gfs_bind()`, `gfs_unbind()`, `gfs_do_config()`, `eth_bind_config()`, and `bind_rndis_config()`. It allocates `"ffs"` function instances, assigns FunctionFS device names through `ffs_single_dev()` or `ffs_name_dev()`, installs callbacks on `ffs_dev`, and conditionally obtains `"ecm"`, `"geth"`, and `"rndis"` instances.

## Control Flow

Module init normalizes the `functions=` module parameter, allocates per-configuration function arrays, creates one FunctionFS instance per named function, marks it non-configfs, and sets ready/closed/acquire/release callbacks. Each userspace FunctionFS mount calls the ready callback when descriptors are written. When all expected functions are ready, the callback registers the composite driver. If any FunctionFS closes, the close callback increments `missing_funcs` and unregisters the composite driver.

During bind, optional ethernet/RNDIS instances and netdev sharing are prepared, string IDs and OTG descriptors are allocated, and every enabled configuration is added. `gfs_do_config()` optionally adds networking first, then instantiates and adds each FunctionFS function for that configuration. It also clears the next interface array slot to avoid stale interface pointers after changing userspace descriptors.

## State and Persistence Behavior

Global state includes `missing_funcs`, `gfs_registered`, `gfs_single_func`, `fi_ffs`, `f_ffs`, optional network function instances/functions, static strings/descriptors, and OTG descriptor storage. FunctionFS descriptor/interface state is supplied by userspace and lives in `f_fs` data structures. No state is persisted by the kernel file; userspace must remount and rewrite descriptors.

## Dependencies and Integration Points

The file integrates libcomposite, FunctionFS, optional ethernet/RNDIS gether functions, module autoloading through the function registry, USB strings, OTG helpers, and userspace FunctionFS daemons. It is sensitive to `ffs_lock` context, as comments state callbacks and bind/unbind are called under FunctionFS locking.

## Risks and Test Signals

Risks include readiness accounting with multiple functions, composite register/unregister races on close, memory ownership across `f_ffs` matrix entries, stale interface pointers from prior FunctionFS descriptors, and error unwind for optional networking. Tests should run single and multi-function modes, close one FunctionFS while configured, use ECM-only/RNDIS-only/both/generic builds, verify interface arrays after descriptor shape changes, pass custom MACs, and unload while FunctionFS endpoints are mounted.
