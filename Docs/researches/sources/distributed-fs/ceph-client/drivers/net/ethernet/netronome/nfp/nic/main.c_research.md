# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.c

Purpose: Defines the NFP core NIC app type and wires generic app lifecycle hooks to NIC-specific vNIC allocation, DCB initialization, and cleanup.

Important APIs/types/functions: `nfp_nic_init()` validates Ethernet table count against max data vNICs. `nfp_nic_vnic_alloc()` calls common NIC allocation then allocates `struct nfp_app_nic_private`. `nfp_nic_vnic_init/clean()` call DCB init/clean. `app_nic` registers callbacks for app selection.

Control flow: App init runs after PF data is available and rejects ETH/vNIC count mismatch. Each vNIC allocation runs common allocation first, then allocates per-vNIC private data. vNIC init attaches optional DCB support; clean releases it; free releases private memory. SR-IOV enable/disable hooks are stubs returning success/no-op.

State and persistence: Per-vNIC `nn->app_priv` owns NIC private state, including DCB state under `CONFIG_DCB`. No persistent storage.

Dependencies/integration: Depends on NFP app framework, PF ETH table discovery, `nfp_app_nic_vnic_alloc()`, and `main.h` DCB helpers.

Risks: If private allocation fails after common vNIC allocation, this function returns `-ENOMEM` without local rollback of the common allocation in this file. ETH table count validation only runs when `pf->eth_tbl` exists. SR-IOV hooks are placeholders.

Test signals: App selection/probe, ETH table count mismatch, vNIC allocation failure injection, DCB init/clean calls with and without `CONFIG_DCB`, and unload freeing `app_priv`.
