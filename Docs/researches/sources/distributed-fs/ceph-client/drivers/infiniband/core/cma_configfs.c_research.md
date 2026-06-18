<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_configfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_configfs.c

## Purpose

`cma_configfs.c` exposes runtime RDMA CM policy knobs through configfs under the `rdma_cm` subsystem. Users create a configfs group named after an RDMA device, and the file presents per-port attributes for the default RoCE GID mode and default RoCE TOS used by CMA when building RoCE paths.

## Important APIs, types, and functions

Local types are `struct cma_dev_group`, representing a configfs device group with a `ports` subgroup, and `struct cma_dev_port_group`, representing one port directory and its parent device group. `filter_by_name()` matches an `ib_device` by `dev_name()`. `cma_configfs_params_get()` resolves the configfs item to a live `cma_device` using `cma_enum_devices_by_ibdev()` and returns the port group; `cma_configfs_params_put()` drops the device reference.

Attributes are `default_roce_mode` and `default_roce_tos`. The show/store callbacks call `cma_get_default_gid_type()`, `cma_set_default_gid_type()`, `cma_get_default_roce_tos()`, and `cma_set_default_roce_tos()`. Group lifecycle is handled by `make_cma_dev()`, `drop_cma_dev()`, `make_cma_ports()`, `release_cma_dev()`, and `release_cma_ports_group()`. Module hooks are `cma_configfs_init()` and `cma_configfs_exit()`.

## Control flow

Initialization builds and registers the `rdma_cm` configfs subsystem. When a user creates a child group named after a registered RDMA device, `make_cma_dev()` looks up the matching CMA device, allocates a `cma_dev_group`, creates a default `ports` subgroup, and creates one default child group for each physical port. Reads of `default_roce_mode` fetch the current CMA default GID type and stringify it through the GID cache helper. Writes parse a GID type string and ask CMA to validate and install it. Reads and writes of `default_roce_tos` fetch or parse an 8-bit value and update the CMA device.

On group removal, `drop_cma_dev()` removes default child groups and drops the config item, eventually freeing the port array and device group in release callbacks.

## State and persistence

The configfs tree contains only runtime objects. The persistent CMA state being manipulated is in the live `cma_device` arrays allocated by `cma.c`: `default_gid_type[]` and `default_roce_tos[]`. Settings disappear when the RDMA device is removed or the module unloads. The configfs group stores the device name string and generated per-port group objects, not a permanent device pointer, so each attribute access re-resolves and refcounts the current device.

## Dependencies and integration points

This file depends on Linux configfs, RDMA verbs, RDMA CM headers, `core_priv.h` for GID type parsing/stringification, and `cma_priv.h` for CMA device accessors. It is conditionally called from `cma.c` when `CONFIG_INFINIBAND_ADDR_TRANS_CONFIGFS` is enabled. The exported user interface is configfs, usually mounted by userspace management tools that tune RoCE defaults before connections are made.

## Risks

Device lookup is name-based, so users can only configure devices that are currently registered and whose names match exactly. Per-port directories are generated from `phys_port_cnt` and use one-based numbering; any future device with a different start port model would need careful review against the CMA accessor validation. Attribute writes race logically with new connection setup, because they update defaults without a separate policy lock; existing IDs keep their selected GID type while future route resolution uses the new value. The port release callback frees only the port array and depends on configfs release ordering.

## Test signals

Validation should mount configfs, create `rdma_cm/<device>`, observe `ports/<n>/default_roce_mode` and `default_roce_tos`, read valid defaults, write supported RoCE GID modes, reject unsupported or malformed modes, accept `u8` TOS values, reject out-of-range TOS strings, and remove groups cleanly. Device hot removal while configfs entries exist should make later attribute operations fail with `-ENODEV` rather than dereferencing stale state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cma_configfs.c -->
