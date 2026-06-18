# Group Research: group_607_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__fab9d8d19ae1

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_plugin.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_plugin.h

## Purpose
Defines the private illumos overlay encapsulation/decapsulation plugin interface used by kernel modules that implement formats such as VXLAN, NVGRE, or Geneve.

## Main Interfaces
- `OVEP_VERSION`: current plugin ABI version.
- `overlay_plugin_flags_t`: plugin feature flags, currently `OVEP_F_VLAN_TAG`.
- `ovep_encap_info_t`: overlay packet metadata containing virtual network identifier and header size.
- Opaque handles:
  - `overlay_prop_handle_t`
  - `overlay_handle_t`
- Plugin callbacks:
  - `overlay_plugin_init_t`, `overlay_plugin_fini_t`
  - `overlay_plugin_encap_t`, `overlay_plugin_decap_t`
  - `overlay_plugin_socket_t`, `overlay_plugin_sockopt_t`
  - `overlay_plugin_getprop_t`, `overlay_plugin_setprop_t`
  - `overlay_plugin_propinfo_t`
- `overlay_plugin_ops_t`: operation vector installed by a plugin.
- `overlay_plugin_register_t`: registration record with version, name, ops, property names, ID width, flags, and destination requirements.
- Registration API:
  - `overlay_plugin_alloc()`
  - `overlay_plugin_free()`
  - `overlay_plugin_register()`
  - `overlay_plugin_unregister()`
- Property-description helpers:
  - `overlay_prop_set_name()`
  - `overlay_prop_set_prot()`
  - `overlay_prop_set_type()`
  - `overlay_prop_set_default()`
  - `overlay_prop_set_nodefault()`
  - `overlay_prop_set_range_uint32()`
  - `overlay_prop_set_range_str()`

## Dependencies And Relationships
Includes STREAMS message blocks, MAC provider definitions, kernel sockets, and `overlay_common.h`. It is consumed by overlay format modules and the broader overlay device framework.

## Research Notes
The header documents module lifecycle ordering: register before `mod_install()`, unregister on failed install or `_fini()`, and refuse unload while busy. It also states synchronization rules: instances may be called concurrently, `getprop`/`setprop` are MAC-perimeter serialized, and encap/decap may run in interrupt context below `LOCK_LEVEL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_plugin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_target.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_target.h

## Purpose
Defines the `/dev/overlay` varpd ioctl interface for associating userland overlay target resolution services with kernel overlay links, servicing dynamic lookups, injecting/resending packets, listing overlay devices, and manipulating target caches.

## Main Interfaces
- `overlay_target_point_t`: resolved endpoint with Ethernet address, IPv6 address, and port.
- Base ioctl family `OVERLAY_TARG_IOCTL`.
- Device state ioctls:
  - `OVERLAY_TARG_INFO`
  - `OVERLAY_TARG_ASSOCIATE`
  - `OVERLAY_TARG_DISASSOCIATE`
  - `OVERLAY_TARG_DEGRADE`
  - `OVERLAY_TARG_RESTORE`
- Lookup/response packet ioctls:
  - `OVERLAY_TARG_LOOKUP`
  - `OVERLAY_TARG_RESPOND`
  - `OVERLAY_TARG_DROP`
  - `OVERLAY_TARG_INJECT`
  - `OVERLAY_TARG_PKT`
  - `OVERLAY_TARG_RESEND`
- List/cache ioctls:
  - `OVERLAY_TARG_LIST`
  - `OVERLAY_TARG_CACHE_GET`
  - `OVERLAY_TARG_CACHE_SET`
  - `OVERLAY_TARG_CACHE_REMOVE`
  - `OVERLAY_TARG_CACHE_FLUSH`
  - `OVERLAY_TARG_CACHE_ITER`
- Main ioctl payloads:
  - `overlay_targ_info_t`
  - `overlay_targ_associate_t`
  - `overlay_targ_degrade_t`
  - `overlay_targ_id_t`
  - `overlay_targ_lookup_t`
  - `overlay_targ_resp_t`
  - `overlay_targ_pkt_t`
  - `overlay_targ_list_t`
  - `overlay_targ_cache_entry_t`
  - `overlay_targ_cache_t`
  - `overlay_targ_cache_iter_t`
- Kernel 32-bit compatibility structure:
  - `overlay_targ_pkt32_t`

## Dependencies And Relationships
Includes datalink, Ethernet, IPv6, and overlay-common definitions. This is the user/kernel contract used by `varpd` and the overlay target-cache machinery.

## Research Notes
Dynamic lookup is designed around userland threads blocking in `OVERLAY_TARG_LOOKUP` for about one second, then responding through separate ioctls. Cache iteration is bounded by `OVERLAY_TARGET_ITER_MAX` to cap kernel allocation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_target.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/panic.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/panic.h

## Purpose
Defines panic-time buffer sizing, persistent panic-data formats, summary-dump header format, kernel panic globals, and architecture/platform hooks used by the common panic path.

## Main Interfaces
- Sizes and versions:
  - `PANICSTKSIZE`
  - `PANICBUFSIZE`
  - `PANICBUFVERS`
  - `PANICNVNAMELEN`
  - `STACK_BUF_SIZE`
  - `SUMMARY_MAGIC`
- `panic_nv_t`: fixed-length name/value panic datum.
- `panic_data_t`: panic buffer header with version, message offset, image UUID, and variable name/value data.
- `summary_dump_t`: summary dump header with magic and stack-buffer checksum.
- Kernel-only panic name/value macros:
  - `PANICNVGET()`
  - `PANICNVADD()`
  - `PANICNVSET()`
- Kernel panic globals:
  - `panicbuf`
  - `panic_thread`
  - `panic_cpu`
  - `panic_hrtime`
  - `panic_hrestime`
  - `panic_bootstr`, `panic_bootfcn`, `panic_forced`, `halt_on_panic`, `nopanicdebug`, `do_polled_io`, `obpdebug`, `in_sync`, `panic_quiesce`, `panic_dump`, `panic_lbolt64`, `panic_regs`, `panic_reg`, `panic_dip`
- Platform hooks:
  - `panic_saveregs()`
  - `panic_savetrap()`
  - `panic_showtrap()`
  - `panic_stopcpus()`
  - `panic_enter_hw()`
  - `panic_quiesce_hw()`
  - `panic_dump_hw()`
  - `panic_trigger()`

## Dependencies And Relationships
Includes kernel thread, CPU, type, and DDI type headers outside assembly. Panic data is consumed by dump code and debuggers.

## Research Notes
`panic_data_t` stores the panic message and optional register-like name/value data in one fixed buffer. The `pd_msgoff` field doubles as the delimiter between structured `panic_nv_t` entries and the panic message.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/panic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/param.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/param.h

## Purpose
Defines legacy and central system parameters used across kernel and user code: path/name limits, user/group constants, block and page conversion macros, file and process limits, machine-dependent exported parameters, and POSIX configuration defaults.

## Main Interfaces
- TTY and POSIX compatibility constants:
  - `_POSIX_VDISABLE`
  - `_TTY_BUFSIZ`
  - `MAX_INPUT`, `MAX_CANON`, `CANBSIZ`
- User/group constants:
  - `UID_NOBODY`, `GID_NOBODY`, `UID_UNKNOWN`, `GID_UNKNOWN`, `UID_DLADM`, `UID_NETADM`, `GID_NETADM`, `GID_TTY`, `UID_NOACCESS`
  - `MAXUID`, `MAXPROJID`, `MINEPHUID`
- Kernel PID constants:
  - `MAX_TASKID`, `MAX_MAXPID`, `DEFAULT_MAXPID`, `DEFAULT_JUMPPID`
  - famous PID values for sched/init/pageout/fsflush
- Filesystem/path constants:
  - `MAXPATHLEN`
  - `TYPICALMAXPATHLEN`
  - `MAXSYMLINKS`
  - `MAXNAMELEN`
  - `MAXLINKNAMELEN`
  - `MAXLINK`
  - `PIPE_BUF`, `PIPE_MAX`
- Block and storage constants:
  - `NBPSCTR`
  - `UBSIZE`
  - `SCTRSHFT`
  - `MAXBSIZE`
  - `DEV_BSIZE`
  - `DEV_BSHIFT`
  - `MAXFRAG`
- Offset and argument-size limits:
  - `MAXOFF32_T`
  - `MAXOFF_T`
  - `MAXOFFSET_T`
  - `NCARGS32`, `NCARGS64`, `NCARGS`
- Conversion macros:
  - `btodb()`, `dbtob()`
  - `lbtodb()`, `ldbtob()`
  - `mmu_ptob()`, `mmu_btop()`, `mmu_btopr()`
  - `mmu_ptod()`, `ptod()`
  - `ptob()`, `btop()`, `btopr()`
  - `dtop()`, `dtopt()`
  - `kbtop()`, `ptokb()`
- Machine-dependent exported variables/macros in kernel/boot contexts:
  - `PAGESIZE`, `PAGESHIFT`, `PAGEOFFSET`, `PAGEMASK`
  - `MMU_PAGESIZE`, `MMU_PAGESHIFT`, `MMU_PAGEOFFSET`, `MMU_PAGEMASK`
  - `KERNELBASE`, `USERLIMIT`, `USERLIMIT32`, `DEFAULTSTKSZ`, `NCPU`, `NCPU_LOG2`, `NCPU_P2`
- Userland sysconf-backed macros:
  - `HZ`, `TICK`, `PAGESIZE`, `PAGEOFFSET`, `PAGEMASK`, `MAXPID`, `MAXEPHUID`

## Dependencies And Relationships
Includes core type, ISA, null, unistd, and optional `machparam.h` definitions. Many kernel and filesystem headers rely on these constants for ABI-sized buffers and address/page math.

## Research Notes
This is a compatibility-heavy public header. Some values are intentionally historical rather than actual implementation limits, such as `MAX_INPUT`, `MAX_CANON`, and `NOFILE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathconf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathconf.h

## Purpose
Defines the kernel/user structure used to carry POSIX `pathconf()` limits, especially for the historical static NFSv2 pathconf mount kludge.

## Main Interfaces
- Bitset helpers:
  - `_BITS`
  - `_PC_N`
  - `_PC_ISSET()`
  - `_PC_SET()`
  - `_PC_ERROR`
- `struct pathcnf`: link/name/path/pipe/terminal pathconf values plus a mask encoding boolean values or errno state.
- `struct pathcnf32`: 32-bit syscall-compatible layout under `_SYSCALL32`.
- Kernel helpers:
  - `PCSIZ`
  - `PCCMP()`

## Dependencies And Relationships
Includes `sys/unistd.h` for `_PC_*` names and system types. NFS mount code historically stores this data locally for servers that could not answer pathconf via protocol.

## Research Notes
`pc_mask` encodes both boolean pathconf features and whether individual fields should be treated as errors. Kernel-only trailing fields add reference counting and a linked-list pointer without changing `PCSIZ`, the comparable non-kernel prefix.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathname.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathname.h

## Purpose
Defines the kernel `pathname_t` abstraction and VFS pathname lookup/manipulation routines used by system calls, symlink expansion, and vnode-to-path conversion.

## Main Interfaces
- `pathname_t`: underlying buffer pointer, current remaining path pointer, remaining length, and total buffer size.
- Pathname buffer/manipulation routines:
  - `pn_alloc()`
  - `pn_alloc_sz()`
  - `pn_get()`
  - `pn_get_buf()`
  - `pn_set()`
  - `pn_insert()`
  - `pn_getsymlink()`
  - `pn_getcomponent()`
  - `pn_setlast()`
  - `pn_skipslash()`
  - `pn_fixslash()`
  - `pn_addslash()`
  - `pn_free()`
- Lookup routines:
  - `lookupname()`
  - `lookupnameat()`
  - `lookupnameatcred()`
  - `lookuppn()`
  - `lookuppnat()`
  - `lookuppnatcred()`
  - `lookuppnvp()`
  - `traverse()`
- Reverse/path discovery helpers:
  - `vnodetopath()`
  - `dogetcwd()`
  - `dirfindvp()`

## Dependencies And Relationships
Includes vnode, credential, uio, and dirent definitions. This is a central VFS pathname resolution contract.

## Research Notes
The convention is that `pn_buf` remains fixed once assigned; path consumption is represented by advancing `pn_path` and updating `pn_pathlen`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pattr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pattr.h

## Purpose
Defines packet attribute types and payload structures for link-layer address/SAP metadata, hardware checksum offload metadata, large-send offload flagging, and zerocopy metadata.

## Main Interfaces
- Attribute type constants:
  - `PATTR_DSTADDRSAP`
  - `PATTR_SRCADDRSAP`
  - `PATTR_HCKSUM`
  - `PATTR_ZCOPY`
- `pattr_addr_t`: physical address plus group-address flag and address length.
- `pattr_hcksum_t`: checksum start/stuff/end offsets, checksum value union, and checksum/offload flags.
- Checksum flags:
  - `HCK_IPV4_HDRCKSUM`
  - `HCK_IPV4_HDRCKSUM_OK`
  - `HCK_PARTIALCKSUM`
  - `HCK_FULLCKSUM`
  - `HCK_FULLCKSUM_OK`
  - `HCK_FLAGS`
  - `HCK_TX_FLAGS`
- LSO flags:
  - `HW_LSO`
  - `HW_LSO_FLAGS`
- `pattr_zcopy_t`: zerocopy flags wrapper.

## Dependencies And Relationships
No explicit includes in the file; it assumes common fixed-width and kernel typedefs are available from includers. These attributes are used by networking code to attach metadata to packet paths.

## Research Notes
Several flag values are intentionally reused for transmit and receive meanings, for example `HCK_IPV4_HDRCKSUM` versus `HCK_IPV4_HDRCKSUM_OK`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pbio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pbio.h

## Purpose
Defines a small ioctl/event interface for a power-button or platform-button monitor device.

## Main Interfaces
- Ioctl base:
  - `PBIOC`
- Ioctls:
  - `PB_BEGIN_MONITOR`
  - `PB_END_MONITOR`
  - `PB_CREATE_BUTTON_EVENT`
  - `PB_GET_EVENTS`
- Event constant:
  - `PB_BUTTON_PRESS`

## Dependencies And Relationships
Standalone public ioctl header. The test suite can use `PB_CREATE_BUTTON_EVENT` to synthesize events.

## Research Notes
The header only defines numeric ABI constants; it does not define an ioctl payload structure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pccard.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pccard.h

## Purpose
Acts as the master include header for PCMCIA PC Card client drivers.

## Main Interfaces
This file primarily aggregates dependencies rather than defining its own data model. It includes:
- Generic kernel/user headers:
  - `sys/types.h`
  - `sys/param.h`
  - `sys/kmem.h`
- Kernel-only support:
  - `sys/systm.h`
  - `sys/sysmacros.h`
  - `sys/cmn_err.h`
  - `sys/debug.h`
  - `sys/devops.h`
- DDI/module headers:
  - `sys/dditypes.h`
  - `sys/modctl.h`
- PC Card/Card Services headers:
  - `sys/pctypes.h`
  - `sys/cs_types.h`
  - `sys/cis.h`
  - `sys/cis_handlers.h`
  - `sys/cs.h`

## Dependencies And Relationships
All PC Card client drivers include this to obtain Card Information Structure and Card Services types in a consistent order.

## Research Notes
No functions or structures are introduced directly; its role is include normalization for legacy PC Card driver code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pccard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci.h

## Purpose
Defines the public PCI configuration-space register map, class/subclass/programming-interface constants, capability identifiers and register layouts, BAR encodings, Open Firmware PCI address-property structures, and common PCI bus limits.

## Main Interfaces
- Standard configuration offsets:
  - `PCI_CONF_VENID` through `PCI_CONF_BIST`
  - Type 0 offsets for BARs, subsystem IDs, ROM, capabilities, and interrupts
  - Type 1 bridge offsets under `PCI_BCNF_*`
  - Type 2 CardBus offsets under `PCI_CBUS_*`
- Command/status/BIST/header bits:
  - `PCI_COMM_*`
  - `PCI_STAT_*`
  - `PCI_BIST_*`
  - `PCI_HEADER_*`
- PCI class, subclass, and programming interface constants for storage, network, display, multimedia, memory, bridges, communications, peripherals, input, docking, processors, serial bus, wireless, intelligent I/O, satellite, crypto, and signal-processing devices.
- BAR and ROM masks:
  - `PCI_BASE_*`
  - `PCI_BASE_ROM_*`
- Conventional capability list support:
  - `PCI_CAP_ID`
  - `PCI_CAP_NEXT_PTR`
  - `PCI_CAP_ID_*`
  - `PCI_CAP_NEXT_PTR_NULL`
- PM capability offsets and bits:
  - `PCI_PMCAP`
  - `PCI_PMCSR`
  - `PCI_PMDATA`
  - `PCI_PMCAP_*`
  - `PCI_PMCSR_*`
- PCI-X capability, bridge, ECC, command, and attribute definitions.
- SHPC/PCI hotplug register offsets and bit masks.
- MSI/MSI-X offsets, masks, vector-table layout constants, and maximum interrupt counts.
- Slot ID and HyperTransport capability constants.
- Property/address structures:
  - `pci_bus_range_t`
  - `pci_ranges_t`
  - `ppb_ranges_t`
  - `struct pci_phys_spec`
  - `pci_regspec_t`
- OF PCI address-cell masks/helpers:
  - `PCI_REG_*`
  - `PCI_ADDR_*`
  - `PCI_REG_*_G()`
  - `PCI_REG_MAKE_BDFR()`
- ROM data-structure constants and invalid-read constants:
  - `PCI_ROM_*`
  - `PCI_PDS_*`
  - `PCI_EINVAL8`, `PCI_EINVAL16`, `PCI_EINVAL32`, `PCI_EINVAL64`

## Dependencies And Relationships
Includes fixed-width and system types. It is the common public vocabulary used by PCI nexus drivers, device drivers, autoconfiguration, pcitool, PCIe code, and property construction.

## Research Notes
This header is pure ABI/register definition. PCIe-specific extended capability bodies are mostly in `pcie.h`, while this file retains the base PCI and conventional capability namespace.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cap.h

## Purpose
Defines helper APIs and macros for locating, reading, writing, and dumping conventional PCI capabilities and PCIe extended capabilities through a DDI config access handle.

## Main Interfaces
- Extended-capability marker:
  - `PCI_CAP_XCFG_FLAG_SHIFT`
  - `PCI_CAP_XCFG_FLAG`
  - `PCI_CAP_XCFG_SPC()`
- Capability ID masks:
  - `PCI_CAP_XID_MASK`
  - `PCI_CAP_ID_MASK`
- Locate functions:
  - `pci_xcap_locate()`
  - `pci_lcap_locate()`
  - `pci_htcap_locate()`
  - `PCI_CAP_LOCATE()`
- Config access sizes:
  - `pci_cap_config_size_t`
  - `PCI_CAP_CFGSZ_8`
  - `PCI_CAP_CFGSZ_16`
  - `PCI_CAP_CFGSZ_32`
- Access macros:
  - `PCI_CAP_GET8/16/32`
  - `PCI_CAP_PUT8/16/32`
  - `PCI_XCAP_GET8/16/32`
  - `PCI_XCAP_PUT8/16/32`
- Core APIs:
  - `pci_cap_probe()`
  - `pci_cap_get()`
  - `pci_cap_put()`
  - `pci_cap_read()`
- Invalid-read constants:
  - `PCI_CAP_EINVAL8`
  - `PCI_CAP_EINVAL16`
  - `PCI_CAP_EINVAL32`
- Debug macro:
  - `PCI_CAP_DBG`

## Dependencies And Relationships
Uses `ddi_acc_handle_t` from DDI headers supplied by includers. It builds on `pci.h` capability definitions and is used by PCI/PCIe nexus and drivers that need capability-safe access.

## Research Notes
Extended-capability access is encoded by ORing the capability ID with `PCI_CAP_XCFG_FLAG`; the same generic get/put path can then distinguish conventional and extended capability spaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cfgacc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cfgacc.h

## Purpose
Defines a root-complex-relative PCI configuration-space access request format and typed get/put helpers for byte, word, dword, and qword accesses.

## Main Interfaces
- `PCI_GETBDF(b, d, f)`: encodes bus/device/function with special handling when device is zero.
- `pci_cfg_data_t`: union for 8/16/32/64-bit config values.
- `pci_config_size_t`: access sizes `PCI_CFG_SIZE_BYTE`, `WORD`, `DWORD`, `QWORD`.
- `pci_cfgacc_req_t`: request containing root-complex dip, BDF, offset, size, write flag, value, and `ioacc` flag.
- Value access macros:
  - `VAL8()`
  - `VAL16()`
  - `VAL32()`
  - `VAL64()`
- Config access functions:
  - `pci_cfgacc_get8/16/32/64()`
  - `pci_cfgacc_put8/16/32/64()`
  - `pci_cfgacc_acc()`

## Dependencies And Relationships
Includes `sys/dditypes.h` and is excluded for assembly. It provides low-level PCI config-space access plumbing for platform/nexus code.

## Research Notes
The request structure centralizes both read and write operations and carries the root-complex devinfo pointer, making it suitable for indirect configuration access paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_cfgacc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_impl.h

## Purpose
Defines private PCI implementation constants and helpers for x86 configuration mechanisms, PCI resource accounting, minor-number encoding, pcitool minor nodes, capability save sizing, and PCI resource setup/teardown.

## Main Interfaces
- x86 config mechanism constants:
  - `PCI_MECHANISM_UNKNOWN`
  - `PCI_MECHANISM_NONE`
  - `PCI_MECHANISM_1`
  - `PCI_MECHANISM_2`
  - `PCI_CONFADD`, `PCI_PMC`, `PCI_CONFDATA`, `PCI_CONE`
  - `PCI_CADDR1()`
  - `PCI_CSE_PORT`, `PCI_FORW_PORT`, `PCI_CADDR2()`
- `pci_acc_cfblk_t`: bus/device/function access block.
- `struct pci_bus_resource`: per-bus I/O, memory, prefetchable memory, and bus-number resource lists plus bridge/autoconfig metadata.
- Global/resource APIs:
  - `pci_bus_res`
  - `pci_memlist_alloc()`
  - `pci_memlist_free()`
  - `pci_memlist_free_all()`
  - `pci_memlist_insert()`
  - `pci_memlist_remove()`
  - `pci_memlist_find()`
  - `pci_memlist_find_with_startaddr()`
  - `pci_memlist_dump()`
  - `pci_memlist_subsume()`
  - `pci_memlist_merge()`
  - `pci_memlist_dup()`
  - `pci_memlist_count()`
- Minor-number macros:
  - `PCI_MINOR_NUM()`
  - `PCI_MINOR_NUM_TO_PCI_DEVNUM()`
  - `PCI_MINOR_NUM_TO_INSTANCE()`
  - `PCI_DEVCTL_MINOR`
  - `PCI_TOOL_REG_MINOR_NUM`
  - `PCI_TOOL_INTR_MINOR_NUM`
- Soft-state flags:
  - `PCI_SOFT_STATE_CLOSED`
  - `PCI_SOFT_STATE_OPEN`
  - `PCI_SOFT_STATE_OPEN_EXCL`
- Capability save-size constants:
  - `PCI_MSI_MIN_WORDS`
  - `PCI_PCIX_MIN_WORDS`
  - `PCI_PCIE_MIN_WORDS`
  - `PCI_PMCAP_NDWORDS`, `PCI_AGP_NDWORDS`, `PCI_SLOTID_NDWORDS`, `PCI_MSIX_NDWORDS`, HT capability sizes, and `PCI_CAP_SZUNKNOWN`
- Capability traversal macros:
  - `CAP_ID()`
  - `NEXT_CAP()`
- Resource lifecycle:
  - `pci_resource_setup()`
  - `pci_resource_destroy()`

## Dependencies And Relationships
Includes DDI types and memlist support. The x86-specific section is only compiled for `__i386` or `__amd64`.

## Research Notes
This is private nexus/autoconfig support, not a public PCI device-driver interface. It bridges hardware configuration access, resource list management, and driver minor-node conventions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_intr_lib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_intr_lib.h

## Purpose
Declares PCI interrupt helper routines for MSI, MSI-X, INTx, class-to-PIL selection, and interrupt weighting.

## Main Interfaces
- `pci_class_val_t`: class-code/mask/value matching tuple.
- MSI/MSI-X helpers:
  - `pci_msi_get_cap()`
  - `pci_msi_configure()`
  - `pci_msi_unconfigure()`
  - `pci_is_msi_enabled()`
  - `pci_msi_enable_mode()`
  - `pci_msi_disable_mode()`
  - `pci_msi_set_mask()`
  - `pci_msi_clr_mask()`
  - `pci_msi_get_pending()`
  - `pci_msi_get_nintrs()`
  - `pci_msi_set_nintrs()`
  - `pci_msi_get_supported_type()`
  - `pci_msix_init()`
  - `pci_msix_fini()`
  - `pci_msix_dup()`
- INTx helpers:
  - `pci_intx_get_cap()`
  - `pci_intx_set_mask()`
  - `pci_intx_clr_mask()`
  - `pci_intx_get_pending()`
  - `pci_intx_get_ispec()`
- Interrupt policy helpers:
  - `pci_class_to_pil()`
  - `pci_class_to_intr_weight()`

## Dependencies And Relationships
Uses `dev_info_t`, DDI interrupt specs, and MSI-X state types from DDI headers. It is consumed by PCI/PCIe nexus drivers and interrupt allocation code.

## Research Notes
The API separates capability discovery, mode enable/disable, vector programming, masking, pending-state checks, and class-based interrupt prioritization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_intr_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_props.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_props.h

## Purpose
Defines shared PCI node-property construction data and helper functions used to unify boot-time and hotplug PCI node initialization.

## Main Interfaces
- `pci_prop_flags_t`:
  - `PCI_PROP_F_MULT_FUNC`
  - `PCI_PROP_F_PCIE`
  - `PCI_PROP_F_SLOT_VALID`
- `pci_prop_data_t`: captured device identity and classification data, including BDF, revision, header, class/subclass/programming interface, vendor/device/subsystem IDs, PCIe type, slot number, PCIe cap offset, interrupt pin, grant/latency, and status.
- `pci_prop_failure_t`:
  - `PCI_PROP_OK`
  - `PCI_PROP_E_BAD_READ`
  - `PCI_PROP_E_UNKNOWN_HEADER`
  - `PCI_PROP_E_BAD_PCIE_CAP`
  - `PCI_PROP_E_NDI`
  - `PCI_PROP_E_DDI`
- Property setup functions:
  - `pci_prop_data_fill()`
  - `pci_prop_name_node()`
  - `pci_prop_set_common_props()`
  - `pci_prop_set_compatible()`
- Shared class predicates:
  - `pci_prop_class_is_vga()`
  - `pci_prop_class_is_isa()`
  - `pci_prop_class_is_ioapic()`
  - `pci_prop_class_is_pcibridge()`

## Dependencies And Relationships
Includes fixed-width types and DDI types. Used by PCI enumeration paths that need consistent node naming and compatible-property creation.

## Research Notes
The failure enum preserves partial-read semantics: unknown headers and bad PCIe capabilities can still leave useful fields in `pci_prop_data_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_props.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_tools.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_tools.h

## Purpose
Defines the kernel/user ioctl ABI for PCI diagnostic tools that read/write device or nexus registers and inspect or modify interrupt-to-CPU mappings.

## Main Interfaces
- Versioning:
  - `PCITOOL_V1`
  - `PCITOOL_V2`
  - `PCITOOL_VERSION`
- Minor-node suffixes:
  - `PCI_MINOR_REG`
  - `PCI_MINOR_INTR`
- Ioctls:
  - `PCITOOL_DEVICE_GET_REG`
  - `PCITOOL_DEVICE_SET_REG`
  - `PCITOOL_NEXUS_GET_REG`
  - `PCITOOL_NEXUS_SET_REG`
  - `PCITOOL_DEVICE_GET_INTR`
  - `PCITOOL_DEVICE_SET_INTR`
  - `PCITOOL_SYSTEM_INTR_INFO`
- BAR selectors:
  - `PCITOOL_CONFIG`
  - `PCITOOL_BAR0` through `PCITOOL_BAR5`
  - `PCITOOL_ROM`
  - `PCITOOL_BASE`
  - `pcitool_bars_t`
- `pcitool_errno_t`: pcitool-specific status values such as invalid CPU, invalid interrupt, alignment/range errors, ROM disabled/write, I/O error, invalid size, unknown header, and invalid register offset.
- Interrupt payloads:
  - `pcitool_intr_set_t`
  - `pcitool_intr_dev_t`
  - `pcitool_intr_get_t`
  - `PCITOOL_IGET_SIZE()`
  - `pcitool_intr_info_t`
- Interrupt flags and controller types:
  - `PCITOOL_INTR_FLAG_SET_GROUP`
  - `PCITOOL_INTR_FLAG_GET_MSI`
  - `PCITOOL_INTR_FLAG_SET_MSI`
  - `PCITOOL_CTLR_TYPE_*`
- Register access attributes:
  - `PCITOOL_ACC_ATTR_SIZE_*`
  - `PCITOOL_ACC_ATTR_SIZE()`
  - `PCITOOL_ACC_ATTR_ENDN_*`
  - `PCITOOL_ACC_IS_BIG_ENDIAN()`
- `pcitool_reg_t`: register read/write request/result payload.

## Dependencies And Relationships
Includes `sys/modctl.h` for driver-name sizing and relies on `MAXPATHLEN` from common system headers. It is the ABI used by pcitool-style userland utilities and PCI nexus drivers.

## Research Notes
The structures carry both userland and driver ABI versions. Register requests explicitly include access width, endianness, logical target, returned physical address, and status.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pci_tools.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_reg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_reg.h

## Purpose
Defines Intel 82365SL-compatible PCIC/PCMCIA controller register offsets, bit masks, window layout constants, vendor-specific extension registers, interrupt masks, memory/I/O mapping encodings, and CardBus/Yenta socket registers.

## Main Interfaces
- Controller/socket topology:
  - `PCIC_MAX_CONTROLLERS`
  - `PCIC_SOCKETS`
  - `PCIC_MEMWINDOWS`
  - `PCIC_IOWINDOWS`
  - `PCIC_NUMWINDOWS`
  - `PCIC_NUMWINSOCK`
- Index/data register selection:
  - `PCIC_INDEX_REG0`
  - `PCIC_INDEX_REG1`
  - `PCIC_BASE0`
  - `PCIC_BASE1`
  - `PCIC_SOCKET_0`
  - `PCIC_SOCKET_1`
  - `PCIC_DATA_REG0`
  - `PCIC_DATA_REG1`
- Core socket registers:
  - `PCIC_CHIP_REVISION`
  - `PCIC_INTERFACE_STATUS`
  - `PCIC_POWER_CONTROL`
  - `PCIC_CARD_STATUS_CHANGE`
  - `PCIC_MAPPING_ENABLE`
  - `PCIC_INTERRUPT`
  - `PCIC_MANAGEMENT_INT`
  - I/O and memory window registers.
- Vendor-specific registers and bits for Cirrus Logic, Intel 82092AA, Vadem, Ricoh, O2 Micro, Texas Instruments, Toshiba, SMC, and Yenta/CardBus controllers.
- Card status, power, interrupt, change-detect, global-control, and misc-control masks.
- Memory/I/O mapping helpers:
  - `SYSMEM_LOW()`
  - `SYSMEM_HIGH()`
  - `SYSMEM_EXT()`
  - `SYSMEM_WINDOW()`
  - `CARDMEM_LOW()`
  - `CARDMEM_HIGH()`
  - `HIGH_BYTE()`
  - `LOW_BYTE()`
  - `IOMEM_WINDOW()`
  - `IOMEM_SETWIN()`
- Resource range constants:
  - `PCIC_PAGE`
  - `IOMEM_FIRST/LAST/MIN/MAX/GRAN/DECODE`
  - `MEM_FIRST/LAST/MIN/MAX`
  - `MEM_SPEED_MIN/MAX`
- CardBus registers and bit masks:
  - `CB_STATUS_EVENT`
  - `CB_STATUS_MASK`
  - `CB_PRESENT_STATE`
  - `CB_EVENT_FORCE`
  - `CB_CONTROL`
  - `CB_SOCKET_POWER`
  - `CB_*` status, event, power, and voltage bits.

## Dependencies And Relationships
Used by the PCIC driver implementation and paired with `pcic_var.h` soft-state definitions.

## Research Notes
The file covers both classic index/data PCIC register access and CardBus/Yenta memory-mapped socket registers, reflecting support for many legacy controller variants.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_var.h

## Purpose
Defines PCIC driver-private soft state for controllers, sockets, memory/I/O windows, debounce and simulated power management, controller flags, interrupt modes, bus resource layout constants, known chip IDs, and PCIC range-property layout.

## Main Interfaces
- PM simulation constants and state:
  - `PCIC_PM_TIME`
  - `PCIC_PM_DETWIN`
  - `PCIC_PM_METHOD_*`
  - `PCIC_PM_INIT`
  - `PCIC_PM_RUN`
  - `pcic_pm_t`
- Debounce/ready wait constants:
  - `PCIC_REM_DEBOUNCE_CNT`
  - `PCIC_REM_DEBOUNCE_TIME`
  - `PCIC_DEBOUNCE_OK_CNT`
  - `PCIC_READY_WAIT_LOOPS`
  - `PCIC_READY_WAIT_TIME`
- Window structures:
  - `pcs_memwin_t`
  - `pcs_iowin_t`
  - `PCW_MAPPED`, `PCW_ENABLED`, `PCW_ATTRIBUTE`, `PCW_WP`, `PCW_OFFSET`
- Socket state:
  - `pcic_socket_t`
  - `PCS_CARD_PRESENT`
  - `PCS_CARD_IDENTIFIED`
  - `PCS_CARD_ENABLED`
  - `PCS_IRQ_ENABLED`
  - `PCS_CARD_IO`
  - `PCS_CARD_16BIT`
  - `PCS_CARD_ISCARDBUS`
  - `PCS_DEBOUNCING`
  - related socket flags.
- Controller state:
  - `pcic_debounce_state_t`
  - `pcicdev_t`
- Controller flags:
  - `PCF_ATTACHED`
  - `PCF_CALLBACK`
  - `PCF_INTRENAB`
  - `PCF_USE_SMI`
  - `PCF_CBPWRCTL`
  - `PCF_PCIBUS`
  - `PCF_CARDBUS`
  - `PCF_DMA`
  - `PCF_ZV`
  - many variant flags for voltage, IRQ, I/O remap, debounce, and memory-page behavior.
- Interrupt modes and I/O access types:
  - `PCIC_INTR_MODE_ISA`
  - `PCIC_INTR_MODE_PCI`
  - `PCIC_INTR_MODE_PCI_1`
  - `PCIC_INTR_MODE_PCI_S`
  - `PCIC_IO_TYPE_82365SL`
  - `PCIC_IO_TYPE_YENTA`
- Bus resource layout constants for PCI and ISA register properties.
- Chip/vendor IDs and type strings for Intel, Cirrus Logic, Vadem, TI, O2 Micro, ENE, SMC, Ricoh, Toshiba, and generic Yenta devices.
- Card classification and timing helpers:
  - `PCIC_PCI_CLASS()`
  - `PCIC_PCI_PCMCIA`
  - `PCIC_PCI_CARDBUS`
  - `PCIC_MEM_AM`
  - `PCIC_MEM_CM`
  - `mhztons()`
- Event capability defaults:
  - `PCIC_DEFAULT_INT_CAPS`
  - `PCIC_DEFAULT_RPT_CAPS`
  - `PCIC_DEFAULT_CTL_CAPS`
- `pcic_ranges_t`: `ranges` property format.

## Dependencies And Relationships
Depends on `pcic_reg.h`, PCI constants, Card Services event masks, and DDI interrupt/mapping types through includers. It is private to the PCIC driver and controller-specific attach/interrupt paths.

## Research Notes
The soft state tracks both legacy ISA-style and PCI/Yenta-style controllers. Many flags exist to encode chip-specific errata and routing modes rather than abstract PCMCIA behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcic_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie.h

## Purpose
Defines the public PCI Express register, capability, extended capability, AER, ARI, Device 3, TLP, requester ID, completion status, and link-training preset vocabulary.

## Main Interfaces
- PCIe capability register offsets:
  - `PCIE_PCIECAP`
  - `PCIE_DEVCAP`, `PCIE_DEVCTL`, `PCIE_DEVSTS`
  - `PCIE_LINKCAP`, `PCIE_LINKCTL`, `PCIE_LINKSTS`
  - `PCIE_SLOTCAP`, `PCIE_SLOTCTL`, `PCIE_SLOTSTS`
  - `PCIE_ROOTCTL`, `PCIE_ROOTCAP`, `PCIE_ROOTSTS`
  - `PCIE_DEVCAP2/DEVCTL2/DEVSTS2`
  - `PCIE_LINKCAP2/LINKCTL2/LINKSTS2`
  - `PCIE_SLOTCAP2/SLOTCTL2/SLOTSTS2`
- Config size:
  - `PCIE_CONF_HDR_SIZE`
- PCIe capability/device/link/slot/root bits:
  - `PCIE_PCIECAP_*`
  - `PCIE_DEVCAP*`
  - `PCIE_DEVCTL*`
  - `PCIE_DEVSTS*`
  - `PCIE_LINKCAP*`
  - `PCIE_LINKCTL*`
  - `PCIE_LINKSTS*`
  - `PCIE_SLOTCAP*`
  - `PCIE_SLOTCTL*`
  - `PCIE_SLOTSTS*`
  - `PCIE_ROOT*`
- Indicator helpers:
  - `pcie_slotctl_pwr_indicator_get()`
  - `pcie_slotctl_attn_indicator_get()`
  - `pcie_slotctl_attn_indicator_set()`
  - `pcie_slotctl_pwr_indicator_set()`
- Extended capability header and IDs:
  - `PCIE_EXT_CAP`
  - `PCIE_EXT_CAP_*`
  - `PCIE_EXT_CAP_ID_*` including AER, VC, serial number, ACS, ARI, ATS, SR-IOV, PASID, DPC, PTM, DOE, IDE, high-speed physical layer caps, SIOV, and captured data.
- AER offsets and bits:
  - `PCIE_AER_*`
  - uncorrectable/correctable/root/secondary error status, masks, severity, header logs, and source IDs.
- Serial Number and ARI capability offsets/bits.
- Device 3 extended capability:
  - `PCIE_DEVCAP3`
  - `PCIE_DEVCTL3`
  - `PCIE_DEVSTS3`
- TLP definitions:
  - TLP format/type constants
  - combined TLP encodings such as `PCIE_TLP_MRD3`, `PCIE_TLP_CFGWR0`, `PCIE_TLP_CPLD`, `PCIE_TLP_MSI64`
  - `pcie_tlp_hdr_t`
  - `pcie_mem64_t`
  - `pcie_memio32_t`
  - `pcie_cfg_t`
  - `pcie_cpl_t`
  - `pcie_msg_t`
- Requester/completer support:
  - `pcie_req_id_t`
  - `PCIE_REQ_ID_*`
  - `PCIE_CPL_STS_*`
- Message and equalization presets:
  - `PCIE_MSG_CODE_ERR_*`
  - `PCIE_GEN3_RX_PRESET_*`
  - `PCIE_TX_PRESET_*`

## Dependencies And Relationships
Includes `pci.h`, reusing base PCI capability offsets and IDs. Used by PCIe nexus drivers, error handling, link management, hotplug, and device drivers.

## Research Notes
The header is kept current with newer PCIe speeds and capabilities up through 64 GT/s and 128 GT/s identifiers. TLP structures are endian-conditional bitfields, so consumers must compile with `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_impl.h

## Purpose
Defines private PCIe nexus and fabric implementation state: device/bus classification macros, config/capability access shortcuts, fault-management register snapshots, root fault/error-source data, fabric tuning state, per-bus private data, fault queues, scan/error status flags, and PCIe nexus/fabric/link/error-management prototypes.

## Main Interfaces
- Bus-private lookup and classification macros:
  - `PCIE_DIP2BUS()`
  - `PCIE_DIP2UPBUS()`
  - `PCIE_DIP2DOWNBUS()`
  - `PCIE_DIP2PFD()`
  - `PCIE_BUS2DIP()`
  - `PCIE_BUS2DOM()`
  - `PCIE_IS_PCIE()`
  - `PCIE_IS_PCIX()`
  - `PCIE_IS_PCI()`
  - `PCIE_HAS_AER()`
  - `PCIE_IS_ROOT()`
  - `PCIE_IS_RC()`
  - `PCIE_IS_RP()`
  - `PCIE_IS_SWU/SWD/SW()`
  - `PCIE_IS_BDG()`
  - `PCIE_IS_PCIE_BDG()`
- Config/cap access macros:
  - `PCIE_GET()`, `PCIE_PUT()`
  - `PCIE_CAP_GET()`, `PCIE_CAP_PUT()`
  - `PCIE_AER_GET()`, `PCIE_AER_PUT()`
  - `PCIX_CAP_GET()`, `PCIX_CAP_PUT()`
- Hotplug mode enum:
  - `pcie_hp_mode_t`
- Fault/error register snapshot structures:
  - `pf_pci_bdg_err_regs_t`
  - `pf_pci_err_regs_t`
  - `pf_pcix_ecc_regs_t`
  - `pf_pcix_err_regs_t`
  - `pf_pcix_bdg_err_regs_t`
  - `pf_pcie_adv_bdg_err_regs_t`
  - `pf_pcie_adv_rp_err_regs_t`
  - `pf_pcie_adv_err_regs_t`
  - `pf_pcie_rp_err_regs_t`
  - `pf_pcie_err_regs_t`
  - `pf_pcie_slot_regs_t`
- Root fault/source structures:
  - `pf_intr_type_t`
  - `pf_root_eh_src_t`
  - `pf_root_fault_t`
- Link and fabric enums:
  - `pcie_link_width_t`
  - `pcie_link_speed_t`
  - `pcie_link_flags_t`
  - `pcie_lbw_state_t`
  - `pcie_tag_t`
  - `pcie_fabric_flags_t`
- `pcie_fabric_data_t`: hierarchy-wide MPS/tag settings and fabric flags.
- `pcie_bus_t`: core per-node PCIe private state including DIPs, config handle, BDFs, capability offsets, bus ranges, assigned addresses, hotplug state, ARI, link state, link-bandwidth monitoring state, domain, and root-port fabric data.
- Fault queue/data structures:
  - `pf_affected_dev_t`
  - `pf_data_t`
  - `pf_impl_t`
- FM and scan flags:
  - `PF_FM_*`
  - `PF_ADDR_*`
  - `PF_SCAN_*`
  - `PF_ERR_*`
  - `PF_ERR_FATAL_FLAGS`
- Pseudo device types:
  - `PCIE_PCIECAP_DEV_TYPE_RC_PSEUDO`
  - `PCIE_PCIECAP_DEV_TYPE_PCI_PSEUDO`
- Nexus/fabric/link/error APIs:
  - `pcie_init()`, `pcie_uninit()`
  - `pcie_open()`, `pcie_close()`, `pcie_ioctl()`, `pcie_prop_op()`
  - `pcie_fabric_setup()`
  - `pcie_initchild()`, `pcie_uninitchild()`
  - `pcie_init_bus()`, `pcie_fini_bus()`
  - `pcie_fab_init_bus()`, `pcie_fab_fini_bus()`
  - `pcie_rc_init_bus()`, `pcie_rc_fini_bus()`
  - `pcie_enable_errors()`, `pcie_disable_errors()`, `pcie_enable_ce()`
  - `pcie_ari_*()`
  - `pf_*()` scan/handler helpers
  - `pciev_*()` error/domain helpers
  - `pcie_link_bw_*()`
  - `pcie_link_set_target()`
  - `pcie_link_retrain()`

## Dependencies And Relationships
Includes `pcie.h`, `pciev.h`, and taskq internals. This is used by `pciex`, root-complex, bridge, hotplug, and fabric error-management implementation code.

## Research Notes
`pcie_bus_t` is the central nexus-private record. The file distinguishes static device data, last fault data, hotplug state, ARI state, link-management state, bandwidth monitoring state, and fabric-wide tuning data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_pwr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_pwr.h

## Purpose
Defines PCIe nexus power-management state, child power counters, PM capability/flag bits, PPM ioctl request IDs, and common PCIe power-management helper prototypes shared by multiple PCIe-related drivers.

## Main Interfaces
- Counter indexes and count:
  - `PCIE_D3_INDEX`
  - `PCIE_D2_INDEX`
  - `PCIE_D1_INDEX`
  - `PCIE_D0_INDEX`
  - `PCIE_UNKNOWN_INDEX`
  - `PCIE_MAX_PWR_LEVELS`
- PM structures:
  - `pcie_pwr_t`: nexus PM state, lock, PM capability offset/handle, link/function levels, flags, hold count, and child-level counters.
  - `pcie_pwr_child_t`: per-child component counters.
  - `pcie_pm_t`: nexus and parent PM-info wrapper.
- PM-info macros:
  - `PCIE_PMINFO()`
  - `PCIE_NEXUS_PMINFO()`
  - `PCIE_PAR_PMINFO()`
  - `PCIE_CHILD_COUNTERS()`
  - `PCIE_SET_PMINFO()`
  - `PCIE_RESET_PMINFO()`
  - `PCIE_IS_COMPS_COUNTED()`
- Capability bits and helpers:
  - `PCIE_SUPPORTS_D3`
  - `PCIE_SUPPORTS_D2`
  - `PCIE_SUPPORTS_D1`
  - `PCIE_SUPPORTS_D0`
  - `PCIE_L2_CAP`
  - `PCIE_L0s_L1_CAP`
  - `PCIE_DEFAULT_LEVEL_SUPPORTED`
  - `PCIE_LEVEL_SUPPORTED()`
  - `PCIE_SUPPORTS_DEVICE_PM()`
- PM flags:
  - `PCIE_ASPM_ENABLED`
  - `PCIE_SLOT_LOADED`
  - `PCIE_PM_BUSY`
  - `PCIE_NO_CHILD_PM`
- Link PM levels:
  - `PM_LEVEL_L3`
  - `PM_LEVEL_L2`
  - `PM_LEVEL_L1`
  - `PM_LEVEL_L0`
- PPM requests:
  - `PPMREQ`
  - `PPMREQ_PRE_PWR_OFF`
  - `PPMREQ_PRE_PWR_ON`
  - `PPMREQ_POST_PWR_ON`
- Settle time:
  - `PCI_CLK_SETTLE_TIME`
- Power helper prototypes:
  - `pcie_plat_pwr_setup()`
  - `pcie_plat_pwr_teardown()`
  - `pwr_common_setup()`
  - `pwr_common_teardown()`
  - `pcie_bus_power()`
  - `pcie_power()`
  - `pcie_pm_add_child()`
  - `pcie_pm_remove_child()`
  - `pcie_pwr_suspend()`
  - `pcie_pwr_resume()`
  - `pcie_pm_hold()`
  - `pcie_pm_release()`

## Dependencies And Relationships
Uses PM level constants, DDI devinfo internals, PM bus power op types, mutexes, and access handles from includers. The object file is linked into multiple drivers, so lint-only symbol renaming avoids duplicate global warnings.

## Research Notes
The nexus tracks aggregate child power levels with counters, including an unknown bucket. `pcie_pm_hold()`/`pcie_pm_release()` provide a temporary busy hold around operations that should not race power-down.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_pwr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pciev.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pciev.h

## Purpose
Defines PCIe fabric error-event payload and I/O virtualization/domain bookkeeping structures used to track FMA-capable, non-FMA, and root-domain ownership across PCIe devices and bridges.

## Main Interfaces
- `pcie_eh_data_t`: packed error-handling data snapshot containing PCI status, PCI bridge status, PCI-X status/bridge/ECC data, PCIe device/AER/secondary/root-port status, and AER source IDs.
- Domain list structures:
  - `pcie_domains_t`
  - `pcie_req_id_list_t`
  - `pcie_child_domains_t`
- `pcie_domain_t`: per-device domain accounting; leaves cache one domain ID, bridges cache lists of child domain IDs and child BDFs.
- Domain lifecycle/list functions:
  - `pcie_domain_list_add()`
  - `pcie_domain_list_remove()`
  - `pcie_save_domain_id()`
  - `pcie_init_dom()`
  - `pcie_fini_dom()`
- Domain classification macros:
  - `PCIE_ASSIGNED_TO_FMA_DOM()`
  - `PCIE_ASSIGNED_TO_NFMA_DOM()`
  - `PCIE_ASSIGNED_TO_ROOT_DOM()`
  - `PCIE_BDG_HAS_CHILDREN_FMA_DOM()`
  - `PCIE_BDG_HAS_CHILDREN_NFMA_DOM()`
  - `PCIE_BDG_HAS_CHILDREN_ROOT_DOM()`
  - `PCIE_IS_ASSIGNED()`
  - `PCIE_BDG_IS_UNASSIGNED()`
  - `PCIE_IN_DOMAIN()`
- Leaf domain ID macros:
  - `PCIE_DOMAIN_ID_GET()`
  - `PCIE_DOMAIN_ID_SET()`
  - `PCIE_DOMAIN_ID_INCR_REF_COUNT()`
  - `PCIE_DOMAIN_ID_DECR_REF_COUNT()`
- Bridge list macros:
  - `PCIE_DOMAIN_LIST_GET()`
  - `PCIE_DOMAIN_LIST_ADD()`
  - `PCIE_DOMAIN_LIST_REMOVE()`
  - `PCIE_BDF_LIST_GET()`
  - `PCIE_BDF_LIST_ADD()`
  - `PCIE_BDF_LIST_REMOVE()`

## Dependencies And Relationships
Relies on `pcie_req_id_t`, `pcie_bus_t`, and classification helpers supplied by PCIe implementation headers. It is included by `pcie_impl.h` and used by fabric error handling and I/O virtualization domain routing.

## Research Notes
The file explicitly notes that domain-list access is currently lockless and may need revisiting with hotplug. Bridge domain state summarizes leaf children, while leaf devices store only their own assigned domain ID.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pciev.h -->