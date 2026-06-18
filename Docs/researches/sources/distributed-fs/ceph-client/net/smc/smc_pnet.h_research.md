# sources/distributed-fs/ceph-client/net/smc/smc_pnet.h

Purpose: Declares the SMC PNETID table data structures and exported lookup/lifecycle APIs used by SMC namespace setup, device discovery, and connection establishment.

Important APIs/types/functions: `struct smc_pnettable` contains the per-net PNET entry list and mutex. `struct smc_pnetids_ndev` and `struct smc_pnetids_ndev_entry` track unique PNETIDs observed on UP netdevices with a refcount per PNETID. `smc_pnetid_by_dev_port()` abstracts platform hardware PNET lookup, returning `-ENOENT` when `CONFIG_HAVE_PNETID` is absent. Public functions initialize/exit global and per-net PNET state, find SMC-R/SMC-D resources, apply table entries to new IB/SMCD devices, find alternate RoCE resources, and query PNETID presence.

Control flow: Callers initialize per-net state before PNET lookup, use `smc_pnet_find_roce_resource()` or `smc_pnet_find_ism_resource()` during handshake, and call device-table helpers when IB or SMCD devices appear. The inline hardware lookup selects either architecture support or a no-op fallback at compile time.

State and persistence behavior: The header defines state containers but does not allocate them. State is tied to `struct smc_net` and SMC device objects and is destroyed during namespace/device/module teardown.

Dependencies and integration points: Depends on `include/net/smc.h`, optional `asm/pnet.h`, and forward declarations for SMC IB, SMCD, init-info, and link-group structures. It is the boundary between PNET management and SMC core/handshake code.

Risks and test signals: The main risk is contract drift between table/list fields and implementation locking/refcount expectations. Build with and without `CONFIG_HAVE_PNETID`, exercise namespace init/exit, verify PNETID lookup on platforms without hardware support, and run SMC connection setup tests that require both SMC-R and SMC-D resource discovery.
