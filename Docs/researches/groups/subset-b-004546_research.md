# subset-b-004546 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.c

## Purpose
`macsec_fs.c` builds the mlx5 MACsec flow-steering implementation for Ethernet and RoCE traffic. It creates TX/RX crypto and validation tables, installs per-SA encrypt/decrypt rules, manages packet reformat and metadata actions, tracks MACsec security-association IDs, exposes counter reads, and publishes notifier events so RoCE MACsec rules can be synchronized with SA lifetime.

## Important APIs, types, and functions
The public entry points are `mlx5_macsec_fs_init()`, `mlx5_macsec_fs_cleanup()`, `mlx5_macsec_fs_add_rule()`, `mlx5_macsec_fs_del_rule()`, `mlx5_macsec_fs_get_stats_fill()`, `mlx5_macsec_fs_get_stats()`, `mlx5_macsec_fs_get_fs_id_from_hashtable()`, and exported RoCE helpers `mlx5_macsec_add_roce_rule()`, `mlx5_macsec_del_roce_rule()`, `mlx5_macsec_add_roce_sa_rules()`, and `mlx5_macsec_del_roce_sa_rules()`. Core state is split across `struct mlx5_macsec_fs`, `struct mlx5_macsec_tx`, `struct mlx5_macsec_rx`, `struct mlx5_macsec_tables`, `struct mlx5_macsec_device`, and `struct mlx5_fs_id`. `union mlx5_macsec_rule` stores the caller-owned TX or RX rule handle. The file uses `rhashtable` for SCI and RX fs-id lookups, `xarray` for per-netdev SA IDs, and `ida` for TX fs-id allocation.

## Control flow
Initialization allocates the top-level object, initializes SCI and fs-id rhashtables, creates TX/RX counter containers, initializes the TX ID allocator, and initializes the MACsec notifier head on `mdev`. Flow tables are created lazily on first rule add through `macsec_fs_tx_ft_get()` or `macsec_fs_rx_ft_get()` and destroyed when the corresponding table refcount returns to zero.

TX rule creation allocates the TX tables if needed, builds an ADD_MACSEC packet reformat buffer from `struct macsec_context`, allocates a packet reformat object, allocates a 1-16 interface fs-id, matches WQE metadata register A, sets MACsec crypto object parameters, and forwards encrypted traffic to a check table. The check table allows packets with a clean ASO status and counts drops on the default miss rule. RX rule creation programs metadata register B with a MACsec marker plus fs-id, adds decrypt rules for SCI-present traffic and, for end-station SCIs, source-MAC-based no-SCI traffic, then forwards to the RX check table where the SecTAG is removed and clean packets continue to the next priority or to RoCE dispatch.

RoCE integration creates extra RDMA TX/RX MACsec flow tables when capabilities permit. TX RoCE rules match source IP and write MACsec TX metadata before jumping to the regular MACsec crypto table. RX RoCE rules match destination IP and metadata copied from register B to register C, allowing only packets whose SA metadata matches the expected fs-id.

## State and persistence behavior
All state is in kernel memory and hardware flow-steering objects. There is no disk persistence. Hardware state includes flow tables, groups, rules, counters, modify-header objects, packet reformat objects, and MACsec crypto actions. Software state tracks per-device TX/RX fs-id entries; TX maps SCI to fs-id for datapath lookups, while RX maps fs-id to SCI/SA ownership. Refcounts prevent duplicate RX fs-id objects and release flow tables only after the last SA rule is deleted.

## Dependencies and integration points
The file depends on Linux MACsec types, mlx5 flow steering, packet reformat, modify-header, counters, rhashtable, xarray, IDA, RoCE GID notification lists, and capability helpers such as `mlx5_is_macsec_roce_supported()`. It is consumed by the mlx5 MACsec accelerator path and by RoCE code that adds or removes IP-based MACsec rules as GIDs appear and disappear.

## Risks and edge cases
The highest-risk areas are unwind paths after partial flow-table creation, fs-id refcount symmetry, and RoCE rule cleanup after a partial add failure. TX fs-id allocation supports only 16 interfaces, so exhaustion is a functional limit. RX no-SCI matching depends on the SCI default port convention and source MAC extraction. Counter and table cleanup assumes callers delete all SA rules before final cleanup; otherwise the code logs nonzero table refcounts and leaves objects rather than tearing down live hardware state.

## Test signals
Useful tests include MACsec TX/RX offload add/delete for SCI-present and no-SCI SAs, VLAN MACsec TX reformat offset, interface-count exhaustion, repeated add/delete on the same RX fs-id, stats counter reads for pass/drop paths, RoCE GID add/delete synchronization, hardware capability-disabled RoCE paths, module unload with no leaked table refcounts, and fault injection around flow-table, flow-rule, modify-header, packet-reformat, counter, xarray, and rhashtable allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.h

## Purpose
`macsec_fs.h` declares the public interface and metadata encoding contract for mlx5 MACsec flow steering. It is compiled only when `CONFIG_MLX5_MACSEC` is enabled and lets MACsec and RoCE code create/delete SA rules, query counters, and translate between SCI and mlx5 steering IDs.

## Important APIs, types, and functions
The header defines RX metadata helpers `MLX5_MACSEC_METADATA_MARKER()` and `MLX5_MACSEC_RX_METADAT_HANDLE()`, TX WQE metadata helpers `mlx5_macsec_fs_set_tx_fs_id()` and `MLX5_MACSEC_TX_METADATA()`, and the `MLX5_MACSEC_NUM_OF_SUPPORTED_INTERFACES` limit. Important types are opaque `struct mlx5_macsec_fs`, opaque `union mlx5_macsec_rule`, `struct mlx5_macsec_rule_attrs`, `struct mlx5_macsec_stats`, and `enum mlx5_macsec_action`. Public functions include initialization, cleanup, rule add/delete, stats fill/get, and SCI-to-fs-id lookup.

## Control flow
The header has no runtime control flow. It establishes the call contract used by the mlx5 MACsec accelerator: callers initialize a steering object, pass MACsec context plus `mlx5_macsec_rule_attrs` to add encrypt or decrypt rules, retain the returned rule handle, and later delete it with the same action and SA fs-id context.

## State and persistence behavior
No state is stored in the header. The macros define in-packet or WQE metadata layout: RX uses bits 31-30 as a MACsec marker and bits 15-0 as an SA handle; TX uses the mlx5 Ethernet WQE flow-table metadata field with a MACsec bit and a small fs-id. These encodings are persistent hardware/software ABI within the driver.

## Dependencies and integration points
The header depends on mlx5 driver types, Linux MACsec `sci_t`, and MACsec configuration guards. It is included by `macsec_fs.c` and higher-level MACsec/RoCE offload code that needs opaque rule handles and metadata helpers.

## Risks and edge cases
Metadata macro changes must remain consistent with flow rules in `macsec_fs.c` and TX WQE producers. The RX max define is misspelled as `MLX5_MACEC_RX_FS_ID_MAX`, so renaming would require broad caller checks. The TX fs-id field supports only 16 interfaces, and callers must not assume arbitrary SA counts fit into TX metadata.

## Test signals
Build coverage under `CONFIG_MLX5_MACSEC=y/m` and disabled configurations is essential. Runtime signals come from successful MACsec TX/RX offload, correct metadata marker recognition on RX, correct SCI lookup for TX RoCE rules, and stats retrieval through the declared APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mlx5.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mlx5.h

## Purpose
`lib/mlx5.h` is a small internal umbrella header for shared mlx5 core-library helpers. It declares reserved GID and core-dump helpers, provides safe uplink-netdev get/put wrappers, and exposes inline accessors for Socket-Direct state on `struct mlx5_core_dev`.

## Important APIs, types, and functions
Declared APIs include `mlx5_init_reserved_gids()`, `mlx5_cleanup_reserved_gids()`, reserved GID allocate/free helpers, and `mlx5_crdump_enable()`, `mlx5_crdump_disable()`, `mlx5_crdump_collect()`. Inline helpers `mlx5_uplink_netdev_get()` and `mlx5_uplink_netdev_put()` protect `mdev->mlx5e_res.uplink_netdev` with `uplink_netdev_lock` and netdev reftracking. `mlx5_get_sd()` and `mlx5_set_sd()` read/write the device's Socket-Direct pointer.

## Control flow
The header has no standalone flow. Callers use the uplink getter before dereferencing a possibly changing netdev, then release with the matching put. Socket-Direct setup code stores an allocated `struct mlx5_sd` with `mlx5_set_sd()` and other subsystems query it with `mlx5_get_sd()`.

## State and persistence behavior
No persistent state is created here. The inline helpers manipulate references to state stored inside `struct mlx5_core_dev`: the uplink netdev pointer and the `dev->sd` Socket-Direct pointer. The reserved GID and crdump declarations refer to state maintained in their implementation files.

## Dependencies and integration points
This header depends on `mlx5_core.h`, Linux netdevice reference APIs, and mlx5e resource fields. It is used by Socket-Direct (`sd.c`), crash dump, reserved GID management, and callers that need a stable uplink netdev reference.

## Risks and edge cases
The uplink getter calls `netdev_hold()` on the current pointer without an explicit NULL guard in this header, so callers depend on netdev ref helpers tolerating the current state or on the uplink being initialized. Socket-Direct accessors are trivial and rely on callers for locking and lifetime. Prototype drift for reserved GID or crdump helpers would affect multiple core subsystems.

## Test signals
Build coverage is the direct signal. Runtime signals include uplink netdev notifier replay without use-after-free, balanced netdev hold/put accounting, Socket-Direct initialization/cleanup setting and clearing `dev->sd`, and successful crash dump/reserved GID paths in the implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mlx5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.c

## Purpose
`mpfs.c` manages the mlx5 Multi-Physical Function Steering L2 table for MAC-address based receive steering. It keeps a software hash of requested unicast MAC addresses, programs hardware L2 table entries when enabled, reference-counts duplicate requests, and supports global enable/disable replay of all tracked entries.

## Important APIs, types, and functions
Public functions are `mlx5_mpfs_init()`, `mlx5_mpfs_cleanup()`, exported `mlx5_mpfs_add_mac()`, exported `mlx5_mpfs_del_mac()`, `mlx5_mpfs_enable()`, and `mlx5_mpfs_disable()`. Internal helpers `set_l2table_entry_cmd()` and `del_l2table_entry_cmd()` issue firmware commands. `struct mlx5_mpfs` stores the L2 hash, mutex, enabled flag, table size, and bitmap. `struct l2table_node` extends `struct l2addr_node` with hardware index and refcount.

## Control flow
Initialization runs only for eswitch managers with an L2 table larger than one entry. It allocates the state object and a bitmap sized from `log_max_l2_table`. Adding a MAC locks the table, finds an existing hash node or allocates a new one, allocates a hardware index when enabled, sends `SET_L2_TABLE_ENTRY`, and records index/refcount. Deletion decrements the refcount, and only on the final release sends `DELETE_L2_TABLE_ENTRY`, frees the bitmap bit, and removes the hash node. Enable replays all hashed MACs into hardware; disable removes all programmed indexes while retaining software hash entries.

## State and persistence behavior
State is volatile driver memory plus hardware L2 table entries. Software hash entries persist across `mlx5_mpfs_disable()` so addresses can be restored by `mlx5_mpfs_enable()`. Cleanup expects the hash to be empty and warns otherwise, then frees the bitmap and object.

## Dependencies and integration points
The file depends on mlx5 firmware command helpers, eswitch-manager capability checks, Ethernet address helpers, bitmap allocation, and hash helpers from `mpfs.h`. It is initialized in `main.c` during once-only mlx5 core initialization and used by upper mlx5 Ethernet/eswitch code that needs shared L2 table programming.

## Risks and edge cases
Enable replay can partially program entries and return an error without rolling back entries already reprogrammed during that pass. Delete ignores firmware delete errors, which favors cleanup progress but can hide hardware-table inconsistency. Index bitmap exhaustion returns `-ENOSPC`. Refcount imbalance causes leaked hardware entries or `-ENOENT` on delete. Cleanup warning indicates callers did not delete all MACs before teardown.

## Test signals
Tests should cover add/delete/refcount for duplicate MACs, ENOSPC when the bitmap is full, disable then enable replay, firmware command failure injection during add and enable, cleanup with empty hash, non-eswitch-manager no-op behavior, and concurrent add/delete serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.h

## Purpose
`mpfs.h` defines the internal MAC-address hash helpers and public MPFS lifecycle hooks for mlx5 L2 table steering. It also provides no-op stubs when `CONFIG_MLX5_MPFS` is disabled.

## Important APIs, types, and functions
The header defines `MLX5_L2_ADDR_HASH_SIZE`, `MLX5_L2_ADDR_HASH()`, `struct l2addr_node`, iteration macros `mlx5_mpfs_foreach()` and `for_each_l2hash_node()`, and allocation/search/delete macros `l2addr_hash_find()`, `l2addr_hash_add()`, and `l2addr_hash_del()`. Public MPFS functions are declared or stubbed: `mlx5_mpfs_init()`, `mlx5_mpfs_cleanup()`, `mlx5_mpfs_enable()`, and `mlx5_mpfs_disable()`.

## Control flow
This header contributes macro-expanded control flow for hash users. Hash lookup uses the last MAC byte as a bucket and scans with `hlist_for_each_entry()`. Hash add allocates a typed node, copies the address, and inserts at the bucket head. Delete removes the hlist node and frees the containing object.

## State and persistence behavior
No state is owned by the header. It defines the layout convention used by MPFS nodes: any typed node must embed `struct l2addr_node node`. Hashing by the last MAC byte is simple and stable but not cryptographic or balanced for adversarial input.

## Dependencies and integration points
The header depends on Linux Ethernet address helpers, hlist, allocation helpers, and mlx5 device declarations. It is consumed by `mpfs.c` and can support other mlx5 L2-address hash users that embed the same node shape.

## Risks and edge cases
The hash macros are type-sensitive and assume the caller's struct has a member named `node`. They perform allocation/free directly, so callers must avoid double free and must serialize access externally. A single-byte hash can cluster addresses with common low bytes. Stubbed builds return success for init/enable and do nothing for cleanup/disable, so callers must tolerate MPFS absence.

## Test signals
Build both `CONFIG_MLX5_MPFS` enabled and disabled. Runtime coverage comes through MPFS add/delete/replay tests, hash collision behavior, cleanup with all nodes removed, and static analysis for macro users that embed the expected member names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/mpfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.c

## Purpose
`nv_param.c` exposes selected mlx5 nonvolatile firmware configuration items as devlink permanent parameters. It reads and writes the MNVDA register for global PCI, per-host-PF PCI, software offload, software offload capability, and software accelerate configuration classes, then maps them to devlink SR-IOV, VF count, CQE compression, and SW parser checksum mode settings.

## Important APIs, types, and functions
Public functions are `mlx5_nv_param_register_dl_params()` and `mlx5_nv_param_unregister_dl_params()`. Low-level helpers are `mlx5_nv_param_read()`, `mlx5_nv_param_write()`, and class-specific read wrappers for SW offload, SW accelerate, global PCI config/capability, and per-host-PF PCI config. Devlink callbacks include get/set/validate for `ENABLE_SRIOV`, `TOTAL_VFS`, driver parameter `cqe_compress_type`, and driver parameter `swp_l4_csum_mode`. Local bitfield structs describe MNVDA configuration item headers and payloads.

## Control flow
Registration is PF-only and registers a static array of devlink parameters. Each get callback prepares an MNVDA header with type class, parameter index, header length, and sometimes access mode, reads the register, decodes fields, and fills `ctx->val`. Set callbacks usually read the existing NV item first, update a specific field, and write the whole item back. Validation callbacks reject unsupported strings and, for `l4_only`, read capability bits before allowing the value. SR-IOV setters first force global configuration into per-PF VF-count mode, then update per-PF enable or VF total fields.

## State and persistence behavior
Writes through `mlx5_nv_param_write()` mutate nonvolatile device configuration via the MNVDA register using write access mode. Values are devlink `CMODE_PERMANENT`, so effects may require reload or reset depending on firmware. The file itself keeps no dynamic state.

## Dependencies and integration points
The file depends on mlx5 register access, generated IFC field macros, devlink parameter APIs, extack reporting, and PF detection. It integrates with mlx5 devlink setup/teardown and with firmware configuration storage for SR-IOV and offload defaults.

## Risks and edge cases
The SR-IOV enable setter appears to compute `data` before clearing/re-reading `mnvda`, then sets `pf_total_vf_en` after the per-PF read without refreshing `data`; that is a fragile pointer-to-stack-buffer pattern and should be reviewed. Similar care is needed wherever `mnvda` is memset after `data` is assigned. Invalid firmware values are surfaced as `-EOPNOTSUPP` or `-EINVAL`. Permanent NV writes can change device behavior after reboot, so validation and extack messages are important. Global versus per-PF SR-IOV support is intentionally restricted to per-PF-capable devices.

## Test signals
Test devlink param registration on PF and non-PF devices, get/set/validate for all four parameters, unsupported capability handling, invalid strings, max VF validation, MNVDA read/write failure injection, persistence across reload or reboot where available, and SR-IOV per-PF behavior on devices with and without `per_pf_total_vf_supported`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.h

## Purpose
`nv_param.h` declares the mlx5 NV-parameter devlink registration interface. It is a narrow header used by devlink/core initialization code to add or remove permanent firmware-backed devlink parameters.

## Important APIs, types, and functions
The header exposes `mlx5_nv_param_register_dl_params(struct devlink *devlink)` and `mlx5_nv_param_unregister_dl_params(struct devlink *devlink)`. It includes the mlx5 driver definitions and local devlink declarations needed for those prototypes.

## Control flow
There is no runtime flow in this header. Callers register NV-backed parameters during device/devlink setup and unregister them during teardown. The implementation decides at runtime whether the device is a PF and no-ops for other function types.

## State and persistence behavior
The header stores no state. The declared implementation exposes persistent firmware settings through devlink permanent parameters, so callers must pair registration and unregistration with devlink lifetime.

## Dependencies and integration points
It depends on Linux mlx5 driver types and the local `devlink.h`. It integrates `nv_param.c` with the mlx5 devlink parameter registration path.

## Risks and edge cases
The main risk is lifecycle mismatch: registering parameters after devlink exposure or failing to unregister before devlink destruction can create stale devlink callbacks. Build coverage must keep prototypes consistent with implementation.

## Test signals
Build coverage and devlink parameter enumeration on mlx5 PFs are the direct signals. Non-PF devices should not expose these parameters, and unload/reload should not leave duplicate or stale devlink params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.c

## Purpose
`pci_vsc.c` implements access to mlx5 PCI vendor-specific capability gateway registers. It finds the VSC capability, serializes gateway access with PCI config locking and a firmware semaphore, switches address spaces, reads blocks through the gateway, and supports semaphore-space locking for firmware/reset coordination.

## Important APIs, types, and functions
Public functions are `mlx5_pci_vsc_init()`, `mlx5_vsc_gw_lock()`, `mlx5_vsc_gw_unlock()`, `mlx5_vsc_gw_set_space()`, `mlx5_vsc_gw_read_block_fast()`, and `mlx5_vsc_sem_set_space()`. Internal helpers handle bit extraction/merge, config dword read/write, flag polling (`mlx5_vsc_wait_on_flag()`), single gateway reads/writes, and fast reads that return the next address.

## Control flow
Initialization is PF-only and records the offset of `PCI_CAP_ID_VNDR` in `dev->vsc_addr`. Gateway locking takes the PCI config access lock, polls the VSC semaphore, reads a counter, writes it back to claim ownership, and verifies the lock value. Unlock writes `MLX5_VSC_UNLOCK` and releases PCI config access. Setting a gateway space writes the target space into the VSC control register, validates status bits, and optionally returns the space size from the address register. Block reads iterate from address zero to requested length using the device-provided next address and periodically call `cond_resched()`.

## State and persistence behavior
The file stores only `dev->vsc_addr` and transient hardware semaphore state. Gateway operations mutate PCI config-space VSC registers and, for semaphore spaces, device firmware semaphore words. There is no disk persistence.

## Dependencies and integration points
It depends on Linux PCI config access APIs, mlx5 logging, `pci_channel_offline()`, and VSC definitions in `pci_vsc.h`. It is initialized from `main.c` after BAR mapping and used by diagnostics, firmware reset, or crash dump paths that need gateway access.

## Risks and edge cases
Failure to unlock after a successful lock can block other gateway users. The retry loops cap at 2048 iterations and may return `-EBUSY` on slow devices. Access is rejected if the VSC capability was not found. Fast block reads return the byte offset reached on failure, not a negative errno, so callers must interpret partial progress correctly. PCI channel offline returns `-EACCES`.

## Test signals
Test PF VSC discovery, non-PF no-op discovery, lock/unlock balance, set-space success and invalid-space failure, block-read partial failure handling, PCI offline behavior, semaphore-space lock/unlock, and long block reads that exercise `cond_resched()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.h

## Purpose
`pci_vsc.h` declares the mlx5 PCI vendor-specific capability gateway API and small enum constants for gateway lock state and scan CR-space selection.

## Important APIs, types, and functions
It defines `enum mlx5_vsc_state` with `MLX5_VSC_UNLOCK` and `MLX5_VSC_LOCK`, defines `MLX5_VSC_SPACE_SCAN_CRSPACE`, declares VSC init, gateway lock/unlock, set-space, fast block-read, and semaphore-space functions, and provides inline `mlx5_vsc_accessible()` to test `dev->vsc_addr`.

## Control flow
The header has no standalone runtime flow. Callers first check accessibility or call APIs that do so, then lock the gateway, select a space, perform reads/writes through implementation functions, and unlock.

## State and persistence behavior
No state is stored here. The inline accessibility check reads the VSC capability offset saved in `struct mlx5_core_dev`.

## Dependencies and integration points
It depends on `struct mlx5_core_dev` being visible through including context. It is used by PCI setup, diagnostic, crash dump, and firmware-control code that needs VSC gateway access.

## Risks and edge cases
Callers must pair lock/unlock and avoid gateway operations when `mlx5_vsc_accessible()` is false. The API exposes only block-read and semaphore-space helpers, so direct write users are intentionally limited to implementation internals.

## Test signals
Build coverage and runtime VSC access tests through `pci_vsc.c` are sufficient. Static analysis should verify all successful locks have matching unlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/pci_vsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.c

## Purpose
`port_tun.c` manages port-level tunnel entropy calculation settings for mlx5 tunnel offloads. It coordinates VXLAN/L3-tunnel rules that need entropy calculation enabled with NVGRE rules that may require entropy disabled, using refcounts and firmware PCMR register updates.

## Important APIs, types, and functions
Public functions are `mlx5_init_port_tun_entropy()`, `mlx5_tun_entropy_refcount_inc()`, and `mlx5_tun_entropy_refcount_dec()`. Internal helpers query PCMR state (`mlx5_query_port_tun_entropy()`), set global tunnel entropy calculation, set GRE-specific entropy calculation, and choose the correct control path in `mlx5_set_entropy()`.

## Control flow
Initialization records the device, initializes a mutex, queries support/current enablement, and defaults to enabled when the firmware lacks explicit support. Refcount increment accepts VXLAN/L3 tunnel entries only if entropy is currently enabled, increasing `num_enabling_entries`. For NVGRE, the first disabling entry tries to disable entropy, preferably through GRE-specific control when supported, and subsequent entries only bump the disabling count. Refcount decrement reverses those counts and re-enables entropy when the last NVGRE entry is removed.

## State and persistence behavior
State is kept in `struct mlx5_tun_entropy`: enabling and disabling entry counts, cached enabled flag, mutex, and device pointer. Hardware state is the PCMR port-check register. There is no disk persistence, but firmware register state may affect all tunnel offload users on the port.

## Dependencies and integration points
The file depends on mlx5 port check register access, `MLX5_REFORMAT_TYPE_*` constants, and mlx5 logging. It integrates with flow/reformat code that calls the refcount helpers when tunnel reformat rules are installed or removed.

## Risks and edge cases
The decrement path only treats VXLAN as enabling, while increment also accepts `L2_TO_L3_TUNNEL`; callers using L3 tunnel must ensure symmetry or this can under/over-count. Global entropy disable fails if enabling entries exist. External firmware or other software changing forced entropy state can trigger `-EOPNOTSUPP`. Missing refcount decrements can leave entropy disabled after NVGRE rules are removed.

## Test signals
Test initialization with and without PCMR support, VXLAN/L3 increment success while enabled, NVGRE first-rule disable and last-rule re-enable, mixed VXLAN plus NVGRE conflict, GRE-specific capability path, global force-capability path, and refcount symmetry under add/delete stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.h

## Purpose
`port_tun.h` declares the tunnel entropy state object and refcount API used by mlx5 tunnel reformat/offload code.

## Important APIs, types, and functions
`struct mlx5_tun_entropy` stores the mlx5 device pointer, enabling and disabling entry counters, cached enabled state, and a mutex. The header declares initialization plus increment/decrement functions keyed by reformat type.

## Control flow
The header has no runtime flow. Callers initialize one entropy object for a device or port context, call `mlx5_tun_entropy_refcount_inc()` before installing an entropy-sensitive tunnel rule, and call `mlx5_tun_entropy_refcount_dec()` when removing it.

## State and persistence behavior
State is volatile and contained in `struct mlx5_tun_entropy`. The structure mirrors hardware PCMR entropy state only through implementation code; callers should not mutate fields directly.

## Dependencies and integration points
It depends on mlx5 driver definitions and Linux mutex support through included headers. It is consumed by tunnel offload and packet reformat code paths that need to coordinate port-wide entropy behavior.

## Risks and edge cases
Because the struct is exposed, direct field modification by callers could break locking/refcount invariants. The API relies on balanced inc/dec by reformat type.

## Test signals
Build coverage and runtime tunnel rule add/delete tests through `port_tun.c` validate this header. Static analysis can check that callers use the public helpers rather than modifying counters directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.c

## Purpose
`sd.c` implements mlx5 Socket-Direct multi-PF grouping. It discovers devices that firmware marks as one Socket-Direct group, elects a primary PF, disconnects secondary PFs from direct network steering, creates alias access from secondaries to the primary TX flow table, exposes debugfs group details, and redirects auxiliary-device access from secondaries to primary devices when needed.

## Important APIs, types, and functions
Public APIs are `mlx5_sd_init()`, `mlx5_sd_cleanup()`, channel-index helpers, peer lookup, and auxiliary-device get/put helpers. `struct mlx5_sd` stores group ID, host bus count, devcom component, debugfs dentry, up/down state, primary flag, and a union of primary or secondary fields. Internal helpers query MPIR/NIC vport SD group, test capability support, register with devcom, set/unset primary and secondary hardware state, create/destroy alias flow tables, and print/debug group members.

## Control flow
Initialization first filters to non-embedded PFs, reads SD group metadata, checks capability support, allocates `struct mlx5_sd`, and registers a devcom component keyed by group ID and network namespace. Once the devcom component size equals `host_buses`, the group is marked ready, the lowest PCI bus is elected primary, and peer pointers are filled. The first device that observes a ready down group creates a primary egress flow table, grants other-vHCA access with a random key, creates alias objects on secondaries, sets secondary TX root to the alias object, enables silent L2 mode on secondaries, creates debugfs files, and marks the group up. Cleanup reverses this sequence under the devcom component lock and clears peer pointers before unregistering.

## State and persistence behavior
State is volatile: `dev->sd`, devcom membership, flow table aliases, silent-mode settings, TX root steering, debugfs entries, and device references. Hardware state is restored during cleanup by resetting TX roots, destroying aliases, destroying the primary flow table, and disabling silent mode.

## Dependencies and integration points
The file depends on devcom grouping, flow steering commands, vport SD group query, MPIR register query, debugfs, random key generation, auxiliary devices, and mlx5 alias-object commands declared in `mlx5_core.h`. It is initialized during core once-only setup and affects channel mapping, auxiliary-device routing, and multi-PF netdev composition.

## Risks and edge cases
Group bring-up is sensitive to lock ordering and partial failure rollback. The code documents auxiliary-device lock ordering to avoid ABBA. Only groups up to `MLX5_SD_MAX_GROUP_SZ` are supported. Capability mismatch skips combining rather than failing probe. A secondary removal while an auxiliary device is being redirected requires the recheck after dropping devcom lock and taking `device_lock()`.

## Test signals
Test two-PF Socket-Direct systems, unsupported capability skip, primary election by PCI bus number, devcom readiness when all peers register, cleanup on removal of primary or secondary, debugfs contents, alias-object failure rollback, silent-mode restoration, channel-index mapping, and auxiliary-device redirect races during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.h

## Purpose
`sd.h` declares the mlx5 Socket-Direct public helper API and iteration macros used by core and Ethernet code to address devices within a combined multi-PF group.

## Important APIs, types, and functions
It defines `MLX5_SD_MAX_GROUP_SZ` as 2 and forward-declares `struct mlx5_sd`. Public helpers include primary peer lookup, channel-index-to-device/vector mapping, channel-index-to-device lookup, auxiliary-device get/put redirection, and init/cleanup. Iteration macros cover all group devices, all devices up to a target, secondaries only, and secondaries up to a target.

## Control flow
The header has no standalone runtime flow. Its macros repeatedly call `mlx5_sd_primary_get_peer()` and stop when no peer or a specified target is reached. Callers use these macros to apply setup/teardown across primary and secondary devices in group order.

## State and persistence behavior
No state is stored in the header. It defines group-size and iteration semantics over state owned by `sd.c` and stored in `dev->sd`.

## Dependencies and integration points
It integrates Socket-Direct support with channel allocation, auxiliary-device routing, and core setup/cleanup. It assumes `struct mlx5_core_dev` and `struct auxiliary_device` are visible to includers.

## Risks and edge cases
The maximum group size is a software limit; firmware groups larger than two are intentionally unsupported. Iteration macros evaluate peer lookup each loop and rely on stable group state under the caller's locking.

## Test signals
Build coverage plus Socket-Direct runtime tests through `sd.c` validate the header. Unit-style checks can verify channel index modulo/division mapping and macro iteration boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sf.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sf.h

## Purpose
`sf.h` provides inline helpers for mlx5 SubFunction capability and numbering. It abstracts compile-time `CONFIG_MLX5_SF` support and firmware capability fields for callers that need SF start IDs and limits.

## Important APIs, types, and functions
`mlx5_sf_start_function_id()` returns `sf_base_id`. When `CONFIG_MLX5_SF` is enabled, `mlx5_sf_supported()` returns the firmware `sf` capability and `mlx5_sf_max_functions()` returns `max_num_sf` or `1 << log_max_sf`. When disabled, support is always false and max functions is zero.

## Control flow
The helpers are pure inline queries with no side effects. Callers branch on support before creating or managing SF resources.

## State and persistence behavior
No state is stored. Values come from cached HCA capabilities in `struct mlx5_core_dev`.

## Dependencies and integration points
The header depends on Linux mlx5 driver capability macros. It is used by SF management and any code that sizes SF-related resources or IDs.

## Risks and edge cases
Callers must check support before trusting the base ID or maximum count. The fallback from `max_num_sf` to `log_max_sf` assumes firmware provides one of those encodings. Disabled builds compile out SF behavior through zero/false helpers.

## Test signals
Build with `CONFIG_MLX5_SF` enabled and disabled, verify max-function calculations on firmware exposing `max_num_sf` and legacy `log_max_sf`, and ensure callers skip SF setup when support is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.c

## Purpose
`smfs.c` is a thin adapter between mlx5 flow-steering objects and the software managed flow steering/direct-rules (`mlx5dr`) API. It converts `struct mlx5_flow_spec` masks and values into `mlx5dr_match_parameters` and wraps matcher, table, action, and rule creation/destruction.

## Important APIs, types, and functions
Public wrappers include `mlx5_smfs_matcher_create()`, `mlx5_smfs_matcher_destroy()`, `mlx5_smfs_table_get_from_fs_ft()`, `mlx5_smfs_action_create_dest_table()`, `mlx5_smfs_action_create_flow_counter()`, `mlx5_smfs_action_destroy()`, `mlx5_smfs_rule_create()`, and `mlx5_smfs_rule_destroy()`.

## Control flow
Matcher creation points the match mask buffer at `spec->match_criteria` with `DR_SZ_MATCH_PARAM` and calls `mlx5dr_matcher_create()`. Rule creation points the value buffer at `spec->match_value`, passes the action array and flow source through to `mlx5dr_rule_create()`, and returns the created direct-rule object. Destroy paths directly call the matching `mlx5dr_*_destroy()` functions.

## State and persistence behavior
The wrapper owns no state. State is created in the mlx5dr layer as matchers, actions, and rules, and the caller is responsible for lifetimes through the returned handles.

## Dependencies and integration points
It depends on `steering/sws/mlx5dr.h`, `dr_types.h`, and mlx5 flow-spec layout. It integrates regular mlx5 flow table abstractions with SMFS/direct-rule acceleration paths.

## Risks and edge cases
Because match buffers point into caller-provided `struct mlx5_flow_spec`, callers must keep the spec valid for the creation call and ensure criteria/value are initialized. The wrappers do not add validation around null pointers, action counts, or flow-source values; the underlying mlx5dr API must reject invalid input.

## Test signals
Build coverage plus SMFS rule insertion tests with destination table and counter actions are the main signals. Failure injection around matcher/action/rule creation should verify caller cleanup, since this file has no internal rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.h

## Purpose
`smfs.h` declares the mlx5 SMFS wrapper API for creating direct-rule matchers, actions, and rules from ordinary mlx5 flow-steering structures.

## Important APIs, types, and functions
The header exposes matcher create/destroy, conversion from `struct mlx5_flow_table` to `struct mlx5dr_table`, destination-table action creation, flow-counter action creation, action destroy, rule create, and rule destroy. It includes the mlx5dr public and direct-rule type headers.

## Control flow
No standalone flow exists. Callers obtain a direct-rule table from an FS table, create matchers/actions, create rules with match specs, and destroy objects in reverse order.

## State and persistence behavior
No state is owned by the header. Object lifetime is external and handled by the implementation plus underlying mlx5dr code.

## Dependencies and integration points
The header ties mlx5 flow steering to software managed flow steering. It depends on direct-rule types and the flow spec/table types visible through included mlx5dr headers.

## Risks and edge cases
The API returns raw pointers and does not encode ownership in types. Callers must destroy only objects they created and must keep table/matcher/action lifetimes ordered correctly.

## Test signals
Build coverage and SMFS rule lifecycle tests validate the declarations. Static analysis can catch missing destroy calls in users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/st.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/st.c

## Purpose
`st.c` manages PCIe TPH steering-tag indexes for mlx5 memory keys. It enables TPH, maps CPU/memory-type steering tags into device ST indexes, reference-counts shared tags, and supports direct mode when the PCIe TPH table is not present.

## Important APIs, types, and functions
Public APIs are `mlx5_st_create()`, `mlx5_st_destroy()`, exported `mlx5_st_alloc_index()`, and exported `mlx5_st_dealloc_index()`. `struct mlx5_st` stores a mutex, xarray allocation limit, xarray of index data, and direct-mode flag. `struct mlx5_st_idx_data` stores a refcount and PCIe TPH tag.

## Control flow
Creation checks the mlx5 `mkey_pcie_tph` capability, reuses the parent device ST object for SFs, verifies PCIe TPH support, detects direct mode when the ST table location is none, enables TPH in device-specific mode, and initializes xarray state. In table mode, index zero is reserved for non-TPH cases and the xarray allocates from 1 to table size minus one. Allocation asks PCIe for the CPU steering tag, returns the tag directly in direct mode, otherwise reuses an existing xarray entry with the same tag or allocates a new index and programs it into PCI config space. Deallocation decrements the refcount and erases the xarray entry on last use.

## State and persistence behavior
State is volatile in `dev->st` plus PCIe TPH configuration. Table entries are left programmed on deallocation because no mkey will reference them after the xarray entry is removed. Destroy disables TPH for non-SF devices and warns if indexes remain allocated.

## Dependencies and integration points
The file depends on `CONFIG_PCIE_TPH`, PCIe TPH helpers, xarray, refcounting, mlx5 capabilities, and SF parent-device sharing. It is created during `mlx5_init_once()` and destroyed during once-only cleanup.

## Risks and edge cases
SF devices share the parent ST object and must not disable or free it. Refcount imbalance leaves xarray entries and triggers destroy warnings. PCIe TPH programming failures require xarray and allocation rollback. Direct mode bypasses xarray and deallocation is a no-op, so callers must tolerate different index meanings by mode.

## Test signals
Test devices without mlx5 TPH capability, without PCIe TPH capability, direct mode, table mode, duplicate CPU tag reuse/refcounting, allocation limit exhaustion, PCIe set-entry failure rollback, SF parent sharing, and destroy warnings for leaked indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/tout.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/tout.c

## Purpose
`tout.c` centralizes mlx5 driver timeout values. It initializes software defaults, updates command/init timeouts from the device initialization segment, and updates many reset/teardown/reclaim timeouts from the firmware DTOR register when supported.

## Important APIs, types, and functions
Public functions are `mlx5_tout_init()`, `mlx5_tout_cleanup()`, `mlx5_tout_query_iseg()`, `mlx5_tout_query_dtor()`, and `_mlx5_tout_ms()`. `struct mlx5_timeouts` stores an array indexed by `enum mlx5_timeouts_types`. Helpers convert firmware multiplier/value fields to milliseconds and test whether timeout registers are supported.

## Control flow
Initialization allocates the timeout object and fills all slots from `tout_def_sw_val`. `mlx5_tout_query_iseg()` reads big-endian `cmd_q_init_to` and `cmd_exec_to` fields from the initialization segment when supported and updates FW init and command timeouts. `mlx5_tout_query_dtor()` reads `MLX5_REG_DTOR` and uses macros to convert and install firmware-provided values, adding dependent extra time for reset and PCI sync where needed. If timeout support is absent, DTOR query returns success without changes.

## State and persistence behavior
State is per-device in `dev->timeouts` and is volatile. Firmware-provided values override software defaults for the running driver instance only. Cleanup frees the object.

## Dependencies and integration points
The file depends on initialization-segment MMIO, mlx5 register access, generated DTOR field macros, integer power helpers, and timeout enums from `tout.h`. `main.c` uses these values throughout firmware wait, command, health, reset, and teardown flows.

## Risks and edge cases
Incorrect conversion of multiplier fields can make waits too short or too long. `tout_is_supported()` uses `cmd_q_init_to` as the support sentinel, so devices with zero there keep defaults. Callers assume `dev->timeouts` was initialized before `_mlx5_tout_ms()` is used. Firmware DTOR zero fields intentionally do not override defaults.

## Test signals
Test default values after init, ISEG timeout override, DTOR override with milliseconds/seconds/minutes/hours multipliers, unsupported register fallback, cleanup, and main lifecycle waits using the updated values. Fault injection for `mlx5_core_access_reg()` should preserve defaults and return the firmware error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/tout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/tout.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/tout.h

## Purpose
`tout.h` defines the canonical mlx5 timeout identifiers and declares the timeout initialization/query/access API. It gives other driver files a stable macro, `mlx5_tout_ms(dev, TYPE)`, for retrieving per-device millisecond values.

## Important APIs, types, and functions
`enum mlx5_timeouts_types` covers pre-init wait/warn/recovery values, init-segment command/init values, and DTOR-provided PCI toggle, health poll, crash dump, reset, flush, PCI sync, teardown, FSM reactivate, page reclaim, VF page reclaim, and reset unload values. Declared functions manage lifecycle and queries, while `mlx5_tout_ms()` maps symbolic names to enum constants.

## Control flow
The header has no runtime flow. Callers initialize timeouts during mdev setup, query firmware sources during function enable, and retrieve values through the macro in wait loops and subsystem setup.

## State and persistence behavior
The header stores no state. It defines indexes into `struct mlx5_timeouts` owned by `tout.c`.

## Dependencies and integration points
It depends on `struct mlx5_core_dev` and is included by core lifecycle, command, health, reset, and page allocation code needing timeouts.

## Risks and edge cases
Adding an enum value requires updating the default table in `tout.c`. The macro concatenates names, so caller spelling must match enum naming exactly. Using the accessor before initialization would dereference an uninitialized `dev->timeouts`.

## Test signals
Build coverage catches enum/table mismatch only partly; runtime tests should verify every enum has a nonzero or intentional default and that main lifecycle paths call timeout init before access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/tout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.c

## Purpose
`vxlan.c` manages the hardware VXLAN UDP destination-port table for mlx5 Ethernet offloads. It creates a per-device VXLAN object, programs firmware add/delete commands for UDP ports, tracks configured ports in an RCU hash table, and resets to the default IANA port.

## Important APIs, types, and functions
Public APIs are `mlx5_vxlan_create()`, `mlx5_vxlan_destroy()`, `mlx5_vxlan_add_port()`, `mlx5_vxlan_del_port()`, `mlx5_vxlan_lookup_port()`, and `mlx5_vxlan_reset_to_default()`. `struct mlx5_vxlan` stores the core device, hash table, and mutex. `struct mlx5_vxlan_port` stores hash linkage and UDP port. Firmware helpers issue `ADD_VXLAN_UDP_DPORT` and `DELETE_VXLAN_UDP_DPORT`.

## Control flow
Creation returns `-EOPNOTSUPP` encoded in the pointer when VXLAN stateless offload is unsupported or the function is not a PF. Otherwise it allocates the object, initializes the mutex/hash, and adds the default IANA VXLAN port. Add allocates a software node, sends the firmware add command first, then inserts into the RCU hash under the mutex. Delete locks, finds the port, removes it from the RCU hash, waits for readers with `synchronize_rcu()`, sends the firmware delete command, frees the node, and returns `-ENOENT` if the port is unexpectedly absent. Reset iterates configured ports and removes every port except the IANA default.

## State and persistence behavior
State is volatile software hash entries plus hardware UDP destination-port table entries. Destroy deletes the default port, warns if the hash is not empty, and frees the object. Unsupported state is represented by an error pointer, and all public helpers tolerate that through `mlx5_vxlan_allowed()`.

## Dependencies and integration points
The file depends on Linux VXLAN constants, RCU hash APIs, mutexes, mlx5 command execution, and PF/offload capability checks. It is created/destroyed by the core lifecycle in `main.c` and used by tunnel offload code that needs hardware recognition of VXLAN ports.

## Risks and edge cases
`mlx5_vxlan_add_port()` does not check for an existing port before programming hardware, so callers should avoid duplicates. Delete ignores the return from the firmware delete command and always returns the software lookup status. Creation does not roll back object allocation if adding the default port fails. RCU lookup returns false for unsupported/error-pointer objects.

## Test signals
Test supported PF creation, unsupported VF/capability error pointers, default port programming, add/delete/lookup for custom ports, reset-to-default, duplicate add behavior, firmware command failure injection, destroy with no extra ports, and concurrent RCU lookup during deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.h

## Purpose
`vxlan.h` declares the mlx5 VXLAN UDP-port table API and provides capability/stub helpers around optional `CONFIG_VXLAN` support.

## Important APIs, types, and functions
It forward-declares `struct mlx5_vxlan` and `struct mlx5_vxlan_port`, defines `mlx5_vxlan_max_udp_ports()` from firmware capability with a default of 4, defines `mlx5_vxlan_allowed()` for non-error pointers, and declares or stubs create/destroy/add/delete/lookup/reset functions depending on `CONFIG_VXLAN`.

## Control flow
The header has no standalone flow. Callers create a VXLAN context, guard operations with `mlx5_vxlan_allowed()` or rely on helper no-ops, add/delete ports as tunnel sockets are configured, and reset or destroy during teardown.

## State and persistence behavior
No state is stored here. The allowed helper interprets unsupported state encoded by `mlx5_vxlan_create()` as an error pointer or NULL.

## Dependencies and integration points
It depends on mlx5 driver definitions and optional VXLAN kernel support. It is included by core lifecycle and tunnel offload code.

## Risks and edge cases
Disabled `CONFIG_VXLAN` builds return `-EOPNOTSUPP` and false lookups; callers must not treat VXLAN offload as mandatory. `mlx5_vxlan_max_udp_ports()` supplies a default when capability reports zero, so tests should verify this matches firmware expectations.

## Test signals
Build with `CONFIG_VXLAN` enabled and disabled. Runtime tests should verify max-port capability reporting, allowed/error-pointer behavior, and no-op stubs in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/main.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/main.c

## Purpose
`main.c` is the primary mlx5 core PCI driver and device lifecycle implementation. It registers the PCI driver, probes/removes devices, initializes software and PCI resources, enables firmware/HCA functions, configures capabilities, loads and unloads runtime subsystems, handles devlink registration, PCI error recovery, suspend/resume, shutdown, and VF-to-PF core-device lookup.

## Important APIs, types, and functions
Major entry points include module init/exit `mlx5_init()`/`mlx5_cleanup()`, PCI callbacks `probe_one()`, `remove_one()`, `shutdown()`, `mlx5_suspend()`, `mlx5_resume()`, AER handlers, `mlx5_mdev_init()`/`mlx5_mdev_uninit()`, `mlx5_init_one()`/`mlx5_uninit_one()`, `mlx5_load_one()`/`mlx5_unload_one()`, light-probe variants, recovery helpers, and exported VF accessors. Capability code includes `mlx5_core_get_caps()`, `set_hca_cap()`, handlers for general, general2, atomic, ODP, RoCE, and port-selection caps, plus `mlx5_core_enable_hca()`/`mlx5_core_disable_hca()`.

## Control flow
Module init verifies parameters, registers debugfs, initializes mlx5e and SF driver support, then registers the PCI driver. Probe allocates devlink/core device state, assigns PF/VF type, initializes mdev software, enables PCI and maps BAR/ISEG, initializes shared devlink, then runs full device initialization. Full init sets up firmware command access, enables HCA, allocates startup pages, queries timeouts/capabilities, initializes once-only software objects, registers devlink parameters, loads runtime subsystems, marks the interface up, registers auxiliary devices, enables crash dump and hwmon, and saves PCI state.

Runtime load allocates BFREGs, starts event/pagealloc machinery, creates IRQ/EQ tables, loads clock/tracer/fw-reset/hyperv/resource-dump/FPGA/flow-steering/EC/LAG/SR-IOV/SF/devlink trap pieces in a strict order. Unload reverses that order. Uninit unregisters user-visible devices, unloads if up, unregisters devlink params, cleans once-only subsystems, tears down the HCA, unregisters devlink, then PCI close and mdev uninit happen in remove.

PCI error handling enters error state, unloads, disables PCI, waits for slot reset vitality, then reloads and marks health reporter healthy on resume. Shutdown tries firmware fast/force teardown before falling back to normal unload.

## State and persistence behavior
State spans `struct mlx5_core_dev`, devlink, PCI config, BAR mappings, firmware command state, health pollers, capability caches, notifier heads, debugfs, auxiliary devices, IRQ/EQ resources, flow steering, eswitch/SR-IOV/SF/LAG/FPGA/tracer resources, and interface state bits. Persistent hardware state includes PCI enable/master/PTM/atomic settings, HCA capabilities set in firmware, startup pages, and NV/firmware state affected by subordinate modules. Software state is carefully unwound through labeled error paths.

## Dependencies and integration points
The file integrates nearly every mlx5 subsystem: command, health, page allocation, events, IRQ/EQ, flow steering, eswitch, SR-IOV, SF, devlink, devcom, MPFS, VXLAN/Geneve, clock, FPGA, LAG, ECPF, fw reset, hwmon, crash dump, PCI VSC, and mlx5e. It depends heavily on Linux PCI, devlink, module, DMA, debugfs, workqueue, and AER APIs.

## Risks and edge cases
Lifecycle ordering is the dominant risk. A missing rollback in probe/load or wrong unload order can leak IRQs, flow tables, devlink params, health work, or PCI resources. Firmware wait loops must honor removal via `MLX5_BREAK_FW_WAIT`. Capability setting depends on current/max cap caches and devlink driver-init params. Light probe deliberately initializes only a subset and must transition cleanly to full reload. Shutdown fast teardown intentionally enters error state and frees IRQs without full software cleanup.

## Test signals
Test module load/unload, probe/remove on PF/VF/SF-capable hardware, interface load/unload/reload, devlink reload and parameter registration, light probe, PCI AER reset recovery, suspend/resume, shutdown/kexec, SR-IOV enable/disable, firmware init timeout paths, capability negotiation with RoCE on/off, fault injection at each labeled init/load step, and lockdep for devlink and interface-state locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mcg.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mcg.c

## Purpose
`mcg.c` provides simple exported firmware-command wrappers to attach and detach queue pairs from InfiniBand multicast groups on mlx5 devices.

## Important APIs, types, and functions
The file exports `mlx5_core_attach_mcg()` and `mlx5_core_detach_mcg()`. Both take `struct mlx5_core_dev *`, an InfiniBand multicast GID (`union ib_gid *mgid`), and a QP number. They fill the corresponding firmware command input layout and execute the command.

## Control flow
Attach zeroes the command input, sets opcode `MLX5_CMD_OP_ATTACH_TO_MCG`, sets `qpn`, copies the multicast GID into the command payload, and calls `mlx5_cmd_exec_in()`. Detach follows the same pattern with opcode `MLX5_CMD_OP_DETACH_FROM_MCG`.

## State and persistence behavior
The file stores no software state. Successful commands mutate firmware multicast group membership for the specified QP until detached or the HCA is reset/teardown.

## Dependencies and integration points
It depends on RDMA `ib_verbs.h`, mlx5 command execution, and generated command layouts. It is used by RDMA/core mlx5 consumers that need multicast group membership management.

## Risks and edge cases
There is no local validation of QP number or GID; firmware enforces validity. Attach/detach imbalance can leave multicast membership active or cause detach failures. Command errors are returned directly to callers.

## Test signals
RDMA multicast join/leave tests, invalid QPN/GID command failures, repeated attach/detach, and unload/reset cleanup of multicast memberships provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_core.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_core.h

## Purpose
`mlx5_core.h` is the central internal header for the mlx5 core driver. It defines logging helpers, common constants, shared command attribute structs, utility inlines, and prototypes for core lifecycle, capability, port, event, devlink, SR-IOV, scheduling, firmware, alias-object, and recovery functions used across the driver.

## Important APIs, types, and functions
Key content includes `mlx5_core_dbg/err/warn/info` logging macros, `mlx5_printk()`, `ACCESS_KEY_LEN`, `FT_ID_FT_TYPE_OFFSET`, alias/other-VHCA access structs, port/link/eeprom structs, `mlx5_flexible_inlen()`, core capability/query prototypes, command lifecycle prototypes, HCA enable/disable, health/recovery hooks, SR-IOV APIs, event APIs, auxiliary device APIs, load/unload/init prototypes, port configuration/query APIs, firmware flash/version APIs, devlink rescan helpers, SF helpers, same-hardware checks, alias-object command prototypes, EC VF vport helpers, max EQ cap helper, and PCIe congestion support helper.

## Control flow
The header has no primary runtime flow, but its inline helpers implement small control decisions: overflow-safe flexible input length calculation, devlink-rescan locking, coredev SF checks, EC VF vport mapping, maximum EQ capability fallback, and PCIe congestion event support gating.

## State and persistence behavior
No state is owned by the header. It defines how other files access and mutate state in `struct mlx5_core_dev`, cached capability arrays, PCI device fields, devlink, and firmware objects.

## Dependencies and integration points
It pulls in Linux kernel, firmware, mlx5 CQ/FS/driver, and devcom definitions. Almost every mlx5 core source file depends on it. It is also the declaration point for cross-file contracts implemented in `main.c`, port files, command files, fw reset, devlink, and alias-object handling.

## Risks and edge cases
Because this is a broad internal contract, prototype or macro changes can have large blast radius. Logging macros dereference `dev->device`, so early init code must ensure it is set. Flexible input length returns `-ENOMEM` for overflow, so callers must treat it as a negative error length. Inline capability helpers must match firmware capability layout evolution.

## Test signals
Full mlx5 build coverage is the direct signal. Runtime validation comes from lifecycle, port configuration, devlink, SR-IOV, SF, alias-object, recovery, and capability tests that exercise the declared functions. Static analysis should focus on flexible-length error handling and lifecycle lock contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_irq.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_irq.h

## Purpose
`mlx5_irq.h` declares the mlx5 IRQ table, IRQ pool, vector request/release, notifier, affinity, and MSI-X vector-count APIs used by EQ, completion, SF, and SR-IOV code.

## Important APIs, types, and functions
The header defines `MLX5_COMP_EQS_PER_SF`, forward-declares IRQ and pool types, and declares table lifecycle (`mlx5_irq_table_init/create/destroy/cleanup/free_irqs`), pool/vector accessors, MSI-X vector-count helpers, control/completion IRQ request/release, notifier attach/detach, IRQ affinity mask/index/number getters, and SF affinity request helpers. When `CONFIG_MLX5_SF` is disabled, affinity helpers return `-EOPNOTSUPP` or fall back to normal release.

## Control flow
The header itself has only stub control flow for non-SF builds. Runtime users initialize the IRQ table, create vectors during device load, request vectors for EQs or completion queues, attach notifier blocks, and release vectors during unload.

## State and persistence behavior
No state is stored in the header. IRQ state is owned by implementation files and connected to `struct mlx5_core_dev` and `struct mlx5_irq_table`.

## Dependencies and integration points
It depends on mlx5 driver types, Linux notifier blocks, CPU masks, IRQ affinity descriptors, and optional SF support. It integrates IRQ allocation with EQ creation, SF scheduling, SR-IOV MSI-X configuration, and netdev/RDMA completion paths.

## Risks and edge cases
Callers must balance vector requests/releases and notifier attach/detach. Disabled SF builds return error pointers for affinity requests, so callers need robust fallback. MSI-X count changes for VFs must coordinate with PCI/SR-IOV state.

## Test signals
Test IRQ table init/create/destroy across probe/unload, control IRQ request/release, completion vector allocation, notifier delivery and detach, CPU affinity behavior, SF affinity on enabled builds, non-SF stubs, and SR-IOV MSI-X vector-count get/set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mr.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mr.c

## Purpose
`mr.c` implements exported mlx5 core memory-registration command wrappers for memory keys, protection signature vectors, and the special terminate-scatter-list memory key.

## Important APIs, types, and functions
Exports include `mlx5_core_create_mkey()`, `mlx5_core_destroy_mkey()`, `mlx5_core_query_mkey()`, `mlx5_core_create_psv()`, `mlx5_core_destroy_psv()`, and `mlx5_core_get_terminate_scatter_list_mkey()`. Internal helper `mlx5_get_psv()` extracts PSV indexes from command output slots.

## Control flow
Mkey creation sets the create opcode in the caller-provided input, executes the command, reads the returned mkey index, combines it with the low key byte from the input entry, and returns the complete mkey. Destroy and query convert the full mkey to firmware index and execute the relevant command. PSV creation validates `npsvs <= MLX5_MAX_PSVS`, creates the requested count for a PD, and copies returned PSV indexes. The terminate scatter-list helper returns the legacy constant unless firmware advertises a special mkey and the query succeeds.

## State and persistence behavior
The file stores no state. Successful commands create or destroy firmware objects tied to the HCA. Query fills caller-provided output. The special terminate mkey is read from firmware and returned as big-endian for consumers.

## Dependencies and integration points
It depends on mlx5 command execution, generated command layouts, mkey index conversion helpers, QP constants, and exported symbols for RDMA/Ethernet upper layers. It is used by memory registration, signature offload, and transport paths.

## Risks and edge cases
Caller-provided create input must be correctly sized and initialized beyond the opcode. Mkey low bits are taken from the input entry, so incorrect input produces wrong keys. PSV index extraction supports up to four returned indexes and rejects larger requests. Command failures are returned without partial software cleanup because object ownership remains in firmware/caller contracts.

## Test signals
Test mkey create/query/destroy, invalid PSV count, PSV create/destroy for 1-4 vectors, terminate-scatter-list capability present/absent, firmware command failure injection, and upper-layer memory registration teardown on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mr.c -->
