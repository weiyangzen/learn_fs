# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.h

## Purpose
`vcap_api_debugfs.h` declares the optional debugfs integration for the VCAP API and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled.

## Important APIs
When debugfs is enabled, `vcap_port_debugfs` creates a per-port debugfs file for platform port information and `vcap_debugfs` creates per-VCAP instance debugfs entries. When disabled, `vcap_port_debugfs` compiles to an empty inline and `vcap_debugfs` returns `NULL`.

## Control Flow and State
The header only selects compile-time behavior. It keeps callers simple: platform drivers can call these helpers unconditionally and receive either real debugfs entries or no-op behavior. No state is owned in the header.

## Dependencies and Integration
The enabled declarations depend on Linux `debugfs`, `device`, `net_device`, and `vcap_control`. The implementation lives in `vcap_api_debugfs.c`; callers include this header to avoid directly depending on private internals.

## Risks and Test Signals
The main risk is assuming a non-NULL `struct dentry *` from `vcap_debugfs` when debugfs is disabled or creation fails. Debugfs behavior is covered indirectly by `vcap_api_debugfs_kunit.c` when compiled into the implementation under the VCAP KUnit config.
