# subset-b-005600 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_xs.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_xs.c

## Purpose
`xenbus_xs.c` is the kernel-side Xenstore client library used by Xen bus code and the xenbus userspace device. It wraps Xenstore requests, replies, transactions, directory/read/write/remove helpers, and watch registration over `xenbus_comms`.

## Important APIs, types, and functions
Exports include `xenbus_directory`, `xenbus_exists`, `xenbus_read`, `xenbus_write`, `xenbus_rm`, `xenbus_transaction_start`, `xenbus_transaction_end`, `xenbus_scanf`, `xenbus_read_unsigned`, `xenbus_printf`, `xenbus_gather`, `register_xenbus_watch`, `unregister_xenbus_watch`, and `xenbus_dev_request_and_reply`. Internal request handling centers on `struct xb_req_data`, `xs_talkv`, `xs_single`, `xs_send`, `xs_wait_for_reply`, `read_reply`, `xs_request_enter`, and `xs_request_exit`.

## Control flow
Callers build a Xenstore message, queue an `xb_req_data` on `xb_write_list`, wake `xb_waitq`, then block until the response thread marks the request replied or aborted. Public helpers convert higher-level operations into `XS_*` commands. Watch messages arrive through `xs_watch_msg`, are matched by pointer token, queued on `watch_events`, and executed by the `xenwatch` kthread under `xenwatch_mutex`.

## State and persistence
State is runtime-only: suspend-critical counters, monotonic request IDs, registered watch list, pending watch events, per-request wait queues, and outstanding transaction accounting. `xs_state_users` intentionally counts normal requests and non-user transactions so suspend/resume waits until there are no open kernel Xenstore transactions.

## Dependencies and integration points
The file depends on Xenstore wire types, `xenbus_comms`, Xen domain state, reboot notifiers, kthreads, wait queues, rwsems, and spinlocks. It integrates with xenbus device probing, user-facing xenbus file operations, suspend/resume callbacks, and Xenstore watch notifications.

## Risks and test signals
Risks include request lifetime races, shutdown waits when Xenstore is unreachable, token reuse for watches, pending callbacks during unregister, and transaction accounting imbalance around failed start/end. Test signals include concurrent watches, unregister while callback is pending, suspend/resume with active transactions, reboot while waiting for replies, malformed watch bodies, and Xenstore error mapping coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenbus/xenbus_xs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/Makefile

## Purpose
This kbuild file defines the Xen filesystem module composition. It builds `xenfs.o` when `CONFIG_XENFS` is enabled and conditionally adds dom0-only xenstored support and hypervisor-symbol exposure.

## Important APIs, types, and functions
It is declarative kbuild. `xenfs-y` always includes `super.o`; `xenfs-$(CONFIG_XEN_DOM0)` adds `xenstored.o`; `xenfs-$(CONFIG_XEN_SYMS)` adds `xensyms.o`.

## Control flow
Kbuild evaluates config symbols and links the selected objects into the `xenfs` module or built-in object. The final object supplies the `xenfs` filesystem type and optional files under its root.

## State and persistence
No runtime state is stored here. The persistent effect is build graph selection from `.config`.

## Dependencies and integration points
It binds Xen config choices to source files in `drivers/xen/xenfs`. `super.c` references file operations that only exist when the corresponding object is included.

## Risks and test signals
Risks are missing conditional objects when `super.c` exposes optional files, or stale object names. Test signals are `CONFIG_XENFS=y/m`, dom0/non-dom0 builds, `CONFIG_XEN_SYMS` toggles, and module link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/super.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/super.c

## Purpose
`super.c` implements the `xenfs` pseudo-filesystem, a Xen-specific single-superblock filesystem exposing xenbus, capabilities, privcmd, and initial-domain xenstored/hypervisor-symbol helper files.

## Important APIs, types, and functions
Key functions are `xenfs_fill_super`, `xenfs_get_tree`, `xenfs_init_fs_context`, `xenfs_init`, and `xenfs_exit`. It defines `capabilities_read`, `capabilities_file_ops`, and the `xenfs_type` file_system_type.

## Control flow
Module init registers `xenfs` only when running in a Xen domain. Mount uses `get_tree_single`, then `simple_fill_super` creates fixed tree entries. Initial domains get extra `xsd_kva`, `xsd_port`, and optional `xensyms`; other Xen domains get the minimal tree.

## State and persistence
There is no persistent storage. Directory entries and file contents are synthetic and reflect current Xen role. Capabilities reports `control_d` only for the initial domain.

## Dependencies and integration points
The file integrates with VFS fs_context, `simple_fill_super`, Xen domain detection, xenbus file operations, privcmd operations, and optional xenstored/xensyms file operations declared in `xenfs.h`.

## Risks and test signals
Risks include exposing dom0-only files to guests, missing optional object definitions, and registration on non-Xen systems. Test signals include mount/umount in dom0 and guest domains, permissions on `xenbus` and `privcmd`, `capabilities` output, and config matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenfs.h -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenfs.h

## Purpose
`xenfs.h` is the small internal header connecting the xenfs superblock code with optional file-operation implementations.

## Important APIs, types, and functions
It declares `xsd_kva_file_ops`, `xsd_port_file_ops`, and `xensyms_ops`.

## Control flow
The header has no executable flow. `super.c` uses the declarations when creating initial-domain tree descriptors.

## State and persistence
No state is defined. The declarations refer to synthetic runtime files.

## Dependencies and integration points
It depends on `struct file_operations` being visible to including C files and bridges `super.c` to `xenstored.c` and `xensyms.c`.

## Risks and test signals
Risks are config mismatches where declarations are referenced but objects are not linked. Test signals are `CONFIG_XEN_DOM0` and `CONFIG_XEN_SYMS` build combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenstored.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenstored.c

## Purpose
`xenstored.c` exposes dom0 xenstored bootstrap details through xenfs: the shared Xenstore interface address and event channel port.

## Important APIs, types, and functions
It defines `xsd_kva_file_ops` and `xsd_port_file_ops`. Helpers include `xsd_kva_open`, `xsd_kva_mmap`, `xsd_port_open`, `xsd_read`, and `xsd_release`.

## Control flow
Opening `xsd_kva` formats `xen_store_interface` as a string and allows a single-page mmap of that interface via `remap_pfn_range`. Opening `xsd_port` formats `xen_store_evtchn`. Reads use `simple_read_from_buffer`; release frees the per-open string.

## State and persistence
State is per-open `file->private_data` containing a formatted string. The underlying Xenstore page and event channel are kernel runtime Xen state, not filesystem storage.

## Dependencies and integration points
The file depends on Xen page helpers, xenbus globals, VFS file operations, and VM remapping. It integrates with userspace xenstored startup in initial domains.

## Risks and test signals
Risks include unsafe mmap sizes, stale xenstored globals, exposing kernel virtual addresses, and reference/lifetime issues during Xenstore restart. Test signals include read/mmap bounds checks, dom0-only visibility, invalid offsets, and xenstored userspace bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xenstored.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xensyms.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xenfs/xensyms.c

## Purpose
`xensyms.c` implements a seq_file view of Xen hypervisor symbols under xenfs, similar in spirit to `/proc/kallsyms` for the hypervisor.

## Important APIs, types, and functions
The main private type is `struct xensyms`, carrying `struct xen_platform_op`, a symbol-name buffer, and name length. Key functions are `xensyms_next_sym`, `xensyms_start`, `xensyms_next`, `xensyms_show`, `xensyms_open`, and `xensyms_release`; `xensyms_ops` is exported to xenfs.

## Control flow
Open allocates seq private data and an initial name buffer, sets `XENPF_get_symbol`, and wires the Xen guest handle. Iteration sets `symnum`, calls the hypervisor platform op, resizes the buffer if Xen reports a longer symbol, and emits address/type/name lines until `symnum` stops advancing.

## State and persistence
State is per-open seq state. Symbol data comes from the hypervisor at read time and is not cached persistently.

## Dependencies and integration points
It depends on Xen platform hypercalls, guest-handle setup, seq_file, and xenfs. It is only useful when hypervisor symbol access is enabled and permitted.

## Risks and test signals
Risks include buffer resize loops, hypercall errors, symbol table permission differences, and leaking sensitive hypervisor layout information. Test signals include reading from start and nonzero offsets, long symbol names, hypercall failure injection, and `CONFIG_XEN_SYMS` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xenfs/xensyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xlate_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/xen/xlate_mmu.c

## Purpose
`xlate_mmu.c` provides MMU helpers for Xen guests with auto-translated physmaps. It maps foreign GFNs into userspace VMAs, unmaps them, maps ballooned pages for grant tables, and remaps VMA ranges from preallocated pages.

## Important APIs, types, and functions
Exports are `xen_xlate_remap_gfn_array`, `xen_xlate_unmap_gfn_range`, `xen_xlate_map_ballooned_pages`, and `xen_remap_vma_range`. Internal helpers include `xen_for_each_gfn`, `remap_pte_fn`, `setup_hparams`, `unmap_gfn`, `setup_balloon_gfn`, and `remap_pfn_fn`.

## Control flow
Remap validates a PFNMAP/IO VMA, batches up to `XEN_PFN_PER_PAGE` foreign GFNs, calls `XENMEM_add_to_physmap_range`, records per-GFN errors, counts successful mappings, and installs special PTEs when the hypercall itself succeeds. Unmap walks GFNs and calls `XENMEM_remove_from_physmap`. Balloon mapping allocates unpopulated pages, collects GFNs, and vmaps them.

## State and persistence
State is transient: page arrays, per-batch hypercall arrays, mapped counts, and VMA page tables. Mappings persist only as VMA/PTE state until unmapped or process teardown.

## Dependencies and integration points
The file depends on Xen memory hypercalls, balloon allocation, page/PFN/GFN translation, `apply_to_page_range`, and `vmap`. It is used by privcmd/grant-related paths on ARM and other auto-translated guests.

## Risks and test signals
Risks include partial hypercall success, mismatch between Xen PFN and Linux page size, installing PTEs despite per-entry errors, invalid VMA flags, and cleanup after vmap or balloon allocation failures. Test signals include mixed-success GFN arrays, non-page-aligned ranges, unmap idempotence, balloon allocation failure, and privcmd mmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/xlate_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/zorro/Kconfig

## Purpose
This Kconfig fragment controls the optional Zorro device-name database for Amiga Zorro bus support.

## Important APIs, types, and functions
It defines `CONFIG_ZORRO_NAMES`, a boolean depending on `ZORRO`.

## Control flow
At configuration time, enabling the symbol causes kbuild to include `names.o` and generated device-name tables.

## State and persistence
The only persistent state is the selected `.config` value. Runtime names are initialized during boot and the init-only database can be freed afterward.

## Dependencies and integration points
It integrates with the Zorro bus core and the `drivers/zorro/Makefile` rule that generates `devlist.h` from `zorro.ids`.

## Risks and test signals
Risks are hidden name support when users expect descriptive `/proc/iomem` output, or extra image size in constrained configs. Test signals include `CONFIG_ZORRO_NAMES=y/n`, Amiga Zorro boot logs, and generated header builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Makefile -->
# sources/distributed-fs/ceph-client/drivers/zorro/Makefile

## Purpose
This Makefile maps Zorro bus configuration to core bus objects, procfs support, optional device names, and the host generator for `devlist.h`.

## Important APIs, types, and functions
It builds `zorro.o`, `zorro-driver.o`, and `zorro-sysfs.o` for `CONFIG_ZORRO`; `proc.o` for `CONFIG_PROC_FS`; `names.o` for `CONFIG_ZORRO_NAMES`; and host program `gen-devlist`.

## Control flow
Kbuild first builds `gen-devlist`, then generates `devlist.h` from `zorro.ids` before compiling `names.o`.

## State and persistence
No runtime state. `devlist.h` is generated build output and cleaned by `make clean`.

## Dependencies and integration points
The file integrates with kbuild host programs, procfs config, Zorro core objects, and generated name tables.

## Risks and test signals
Risks include missing explicit generated-file dependencies and generator/parser failures on malformed `zorro.ids`. Test signals include clean builds, parallel builds, `CONFIG_PROC_FS=n`, and `CONFIG_ZORRO_NAMES=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/gen-devlist.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/gen-devlist.c

## Purpose
`gen-devlist.c` is a host-side build tool that transforms the Zorro ID database into C macro invocations consumed by `names.c`.

## Important APIs, types, and functions
The program uses `main` and helper `pq` for quote escaping. It emits `MANUF`, `PRODUCT`, and `ENDMANUF` records to `devlist.h`.

## Control flow
It reads `zorro.ids` from stdin, skips blank/comment lines, parses manufacturer lines and tab-indented product lines, validates name lengths, truncates bracketed product descriptions if needed, escapes quotes, and closes the last manufacturer block.

## State and persistence
State is parser-local: current manufacturer ID/name length, mode, line number, and output file handle. Persistent output is generated `devlist.h`.

## Dependencies and integration points
It depends on stdio/string libc and the exact text format of `zorro.ids`. `names.c` includes the generated header multiple times with different macro definitions.

## Risks and test signals
Risks include fixed-size manufacturer buffers, strict whitespace assumptions, overlong names, malformed IDs, and stale generated output. Test signals include generator execution in kbuild, malformed fixture lines, quote escaping, long descriptions, and empty database handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/gen-devlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/names.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/names.c

## Purpose
`names.c` resolves Zorro manufacturer/product IDs into human-readable device names during initialization.

## Important APIs, types, and functions
Key private types are `struct zorro_prod_info` and `struct zorro_manuf_info`. The exported init helper is `zorro_name_device`. It includes generated `devlist.h` three times to create initdata strings, product arrays, and manufacturer arrays.

## Control flow
`zorro_name_device` searches manufacturers by `ZORRO_MANUF(dev->id)`, then products by combined product/EPC value. It leaves the generic name if no manufacturer matches, writes a manufacturer-only fallback if product is unknown, and appends `(#n)` for repeated products.

## State and persistence
The lookup tables and strings are `__initdata` and discarded after boot. `seen` counters track duplicate naming during initialization.

## Dependencies and integration points
It depends on `devlist.h`, Zorro ID macros, and `struct zorro_dev`. It is called from Zorro bus enumeration before device registration/resources are published.

## Risks and test signals
Risks include generated table mismatches, duplicate counter mutation in initdata, and name buffer overflow if generated names exceed expected sizes. Test signals include known/unknown manufacturer/product devices, duplicates, and `CONFIG_ZORRO_NAMES=n` fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/names.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/proc.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/proc.c

## Purpose
`proc.c` provides legacy procfs inspection for Zorro devices under `/proc/bus/zorro`.

## Important APIs, types, and functions
It defines binary per-slot read/lseek operations, seq operations for `/proc/bus/zorro/devices`, `zorro_proc_attach_device`, and `zorro_proc_init`.

## Control flow
At `device_initcall`, Amiga systems with Zorro hardware create `bus/zorro`, a `devices` seq file, and one binary proc entry per autoconfig slot. Per-device reads synthesize an Amiga `ConfigDev` from `struct zorro_dev`.

## State and persistence
Proc entries mirror boot-time `zorro_autocon` state. No data is persisted; reads construct data on demand.

## Dependencies and integration points
The file depends on procfs, Amiga hardware detection, endian conversions, setup/autoconfig globals, and user-copy helpers.

## Risks and test signals
Risks include proc entry creation failures being mostly ignored, bounds mistakes in fixed-size binary reads, and stale data if device registration partially failed. Test signals include `/proc/bus/zorro/devices`, per-slot read offsets, non-Amiga boot, and procfs-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-driver.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro-driver.c

## Purpose
`zorro-driver.c` implements Linux driver-core services for the Zorro bus: device/driver matching, probe/remove dispatch, driver registration, uevents, and bus registration.

## Important APIs, types, and functions
Exports are `zorro_register_driver`, `zorro_unregister_driver`, and `zorro_bus_type`. Internal helpers include `zorro_match_device`, `zorro_device_probe`, `zorro_device_remove`, `zorro_bus_match`, and `zorro_uevent`.

## Control flow
`postcore_initcall` registers the bus. Drivers register with a name, id table, and probe/remove callbacks. The bus match function selects exact IDs or `ZORRO_WILDCARD`; probe rechecks the matching ID and calls the driver probe. Uevents publish ID, slot name/address, and modalias.

## State and persistence
State is managed by the driver core. Zorro devices are boot-discovered and remain in memory; driver binding state is runtime-only.

## Dependencies and integration points
It integrates with the generic device model, module autoload modaliases, `struct zorro_driver`, sysfs attribute groups, and `zorro.c` device registration.

## Risks and test signals
Risks include missing id tables, probe return normalization, modalias formatting mismatches, and remove callbacks assuming resources still exist. Test signals include wildcard and exact matches, module autoload, bind/unbind, and device/driver sysfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro-sysfs.c

## Purpose
`zorro-sysfs.c` exposes Zorro device configuration through sysfs attributes and a binary `config` file.

## Important APIs, types, and functions
It defines readonly attributes `id`, `type`, `serial`, `slotaddr`, `slotsize`, `resource`, and `modalias`, plus binary attribute `config`. The exported group array is `zorro_device_attribute_groups`.

## Control flow
The Zorro bus type attaches these groups to each registered device. Attribute reads format fields from `struct zorro_dev`; binary config reads construct a `struct ConfigDev` and return bytes via `memory_read_from_buffer`.

## State and persistence
No independent state. Sysfs exposes current boot-discovered `zorro_dev` fields.

## Dependencies and integration points
It depends on driver core attributes, endian helpers, Amiga `ConfigDev`, and Zorro resource helpers. It integrates with udev and module matching through `modalias`.

## Risks and test signals
Risks include endian mismatches, resource formatting errors, and binary config offset handling. Test signals include sysfs attribute reads, modalias matching, serial byte order, and partial reads of `config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro.c

## Purpose
`zorro.c` enumerates Amiga Zorro AutoConfig devices, registers them with the Linux device model, manages resources, and tracks unused Zorro II RAM chunks.

## Important APIs, types, and functions
Exports include `zorro_find_device`, `zorro_num_autocon`, `zorro_autocon`, and `zorro_unused_z2ram`. Core helpers are `mark_region`, `zorro_find_parent_resource`, `amiga_zorro_probe`, and `amiga_zorro_init`.

## Control flow
The platform probe allocates a flexible `zorro_bus`, registers the bus device, copies firmware/autoconfig records into `zorro_dev` entries, derives IDs and names, requests resource ranges, sets DMA masks based on Zorro II/III type, registers each device, then marks available/used Zorro II RAM chunks.

## State and persistence
Boot-time state includes the global autoconfig array, per-device resources, and `zorro_unused_z2ram` bitmap. It persists for the running kernel but is not stored on disk.

## Dependencies and integration points
It depends on Amiga hardware setup globals, platform devices, resource management, DMA masks, Zorro name lookup, and driver-core bus registration from `zorro-driver.c`.

## Risks and test signals
Risks include address-space collisions, GVP EPC quirk reads, incorrect DMA masks, resource parent selection, and bitmap mismatch for Zorro II RAM. Test signals include Amiga boot enumeration, resource collision logs, Zorro II RAM consumers, and `zorro_find_device` iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.h -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro.h

## Purpose
`zorro.h` is the private Zorro bus header shared by the bus core, driver core, sysfs, and names code.

## Important APIs, types, and functions
It declares `zorro_bus_type`, `zorro_name_device`, and `zorro_device_attribute_groups`. When `CONFIG_ZORRO_NAMES` is disabled, `zorro_name_device` is an inline no-op.

## Control flow
No executable flow beyond the inline no-op. Including files use the declarations during bus registration and enumeration.

## State and persistence
No state is defined.

## Dependencies and integration points
It ties conditional name support and sysfs attribute groups to the rest of `drivers/zorro`.

## Risks and test signals
Risks are declaration/config mismatches. Test signals are compile-only across `CONFIG_ZORRO_NAMES` and sysfs-enabled device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Kconfig -->
# sources/distributed-fs/ceph-client/fs/9p/Kconfig

## Purpose
This Kconfig fragment exposes Linux 9P filesystem support and optional caching, POSIX ACL, and security-label features.

## Important APIs, types, and functions
Symbols are `CONFIG_9P_FS`, `CONFIG_9P_FSCACHE`, `CONFIG_9P_FS_POSIX_ACL`, and `CONFIG_9P_FS_SECURITY`.

## Control flow
`9P_FS` depends on `NET_9P` and selects `NETFS_SUPPORT`. Optional symbols gate FS-Cache integration, POSIX ACL handlers, and security xattr handlers.

## State and persistence
Only build configuration is persisted in `.config`. Runtime behavior is selected through compiled objects and mount options.

## Dependencies and integration points
It integrates 9p with the net/9p client, netfs library, FS-Cache, generic POSIX ACL helpers, and LSM security xattrs.

## Risks and test signals
Risks include invalid dependency combinations, especially built-in 9p with modular FS-Cache. Test signals include allmodconfig/randconfig, ACL option availability, and security xattr handler builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Makefile -->
# sources/distributed-fs/ceph-client/fs/9p/Makefile

## Purpose
This Makefile builds the 9p filesystem object from VFS, session, fid, inode, xattr, address-space, and optional cache/ACL sources.

## Important APIs, types, and functions
It creates `9p.o` from `vfs_super.o`, `vfs_inode.o`, `vfs_inode_dotl.o`, `vfs_addr.o`, `vfs_file.o`, `vfs_dir.o`, `vfs_dentry.o`, `v9fs.o`, `fid.o`, and `xattr.o`, with optional `cache.o` and `acl.o`.

## Control flow
Kbuild links selected objects according to `CONFIG_9P_FS`, `CONFIG_9P_FSCACHE`, and `CONFIG_9P_FS_POSIX_ACL`.

## State and persistence
No runtime state. The file defines build composition only.

## Dependencies and integration points
It maps Kconfig symbols to implementation files and must stay aligned with declarations in `v9fs_vfs.h`, `cache.h`, `acl.h`, and `xattr.h`.

## Risks and test signals
Risks include missing optional objects or stale object lists. Test signals include module and built-in builds with cache/ACL toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.c -->
# sources/distributed-fs/ceph-client/fs/9p/acl.c

## Purpose
`acl.c` implements POSIX ACL support for 9p, translating Linux ACL operations to 9P2000.L extended attributes and maintaining cached ACLs when client-side access checks are enabled.

## Important APIs, types, and functions
Important functions are `v9fs_get_acl`, `v9fs_iop_get_inode_acl`, `v9fs_iop_get_acl`, `v9fs_iop_set_acl`, `v9fs_acl_chmod`, `v9fs_set_create_acl`, `v9fs_acl_mode`, and `v9fs_put_acl`. Helpers include `v9fs_fid_get_acl`, `v9fs_acl_get`, `__v9fs_get_acl`, and `v9fs_set_acl`.

## Control flow
ACL reads fetch `system.posix_acl_*` xattrs via a fid, decode them with `posix_acl_from_xattr`, and cache results on inode creation. ACL sets validate and encode ACLs, possibly update mode bits, issue xattr writes, and update cached ACL state. Creation helpers derive inherited ACLs from the parent and apply them after remote object creation.

## State and persistence
Kernel state is the inode ACL cache. Persistent ACL values live on the 9p server as xattrs.

## Dependencies and integration points
It depends on xattr helpers, fid lookup, POSIX ACL library, `v9fs_vfs_setattr_dotl`, and 9P2000.L access mode semantics.

## Risks and test signals
Risks include stale cached ACLs, server-side xattr failures, access=client behavior differences, mode/ACL update ordering, and symlink/default ACL edge cases. Test signals include get/set ACL, chmod with ACLs, inherited default ACLs, access modes, and servers without ACL xattr support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.h -->
# sources/distributed-fs/ceph-client/fs/9p/acl.h

## Purpose
`acl.h` provides the conditional ACL interface used by 9p inode and superblock code.

## Important APIs, types, and functions
When `CONFIG_9P_FS_POSIX_ACL` is enabled it declares ACL get/set/chmod/create helpers. Otherwise it supplies NULL operation pointers and no-op inline helpers.

## Control flow
No runtime control flow except inline no-op paths in non-ACL builds.

## State and persistence
No state is owned here. It controls whether ACL state is handled by compiled code.

## Dependencies and integration points
It integrates optional `acl.c` support with inode operation tables and creation/setattr code.

## Risks and test signals
Risks include build breakage from missing stub coverage and behavior differences when ACL support is disabled. Test signals are ACL-enabled/disabled builds and inode operation table initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.c -->
# sources/distributed-fs/ceph-client/fs/9p/cache.c

## Purpose
`cache.c` integrates 9p with FS-Cache for persistent read caching of regular files.

## Important APIs, types, and functions
It implements `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie`.

## Control flow
Session setup builds a volume key from device name and cachetag/aname, sanitizes slashes, and acquires an FS-Cache volume. Inode setup for regular files derives cookie keys from qid path/version, acquires an fscache cookie, and marks the mapping for release callbacks.

## State and persistence
State includes session `fscache` volume pointers and netfs inode cache cookies. Cached file data is persisted by the FS-Cache backend according to its policy; the 9p client stores only references.

## Dependencies and integration points
It depends on FS-Cache, netfs inode state, qid metadata, and mount cache options.

## Risks and test signals
Risks include duplicate volume keys, stale data when qid version is unreliable, non-regular inode cookies, and cache resize/relinquish ordering. Test signals include `cache=fscache`, duplicate cache tags, qid version changes, file truncation, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.h -->
# sources/distributed-fs/ceph-client/fs/9p/cache.h

## Purpose
`cache.h` declares FS-Cache helpers for 9p and supplies stubs when cache support is not compiled.

## Important APIs, types, and functions
It declares `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie` under `CONFIG_9P_FSCACHE`; otherwise `v9fs_cache_inode_get_cookie` is an inline no-op.

## Control flow
No standalone control flow. Call sites can unconditionally call inode cookie setup while cache-disabled builds compile to no-op behavior.

## State and persistence
No state is defined in the header.

## Dependencies and integration points
It connects `v9fs.c`, inode setup, and optional `cache.c` without scattering config conditionals.

## Risks and test signals
Risks are missing stubs for session functions or incorrect conditional call sites. Test signals include cache-enabled/disabled builds and mount option handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.c -->
# sources/distributed-fs/ceph-client/fs/9p/fid.c

## Purpose
`fid.c` manages 9p fid lookup, attachment, cloning, and association with dentries and inodes. Fids are the active protocol handles used by VFS operations.

## Important APIs, types, and functions
Exports include `v9fs_fid_add`, `v9fs_open_fid_add`, `v9fs_fid_find_inode`, and `v9fs_fid_lookup`. Internals include `v9fs_fid_find`, `v9fs_fid_lookup_with_uid`, `build_path_from_dentry`, and `v9fs_is_writeable`.

## Control flow
Lookup first searches dentry fid lists, then open inode fid lists. On miss it tries the parent fid, otherwise attaches a root fid for the selected user and walks from root in `P9_MAXWELEM` batches. It holds `rename_sem` while using dentry names to prevent path changes during multi-component walks.

## State and persistence
Fids are cached in `dentry->d_fsdata` and `inode->i_private` hlist heads. They are runtime protocol references and are clunked when dentries/files/inodes release them.

## Dependencies and integration points
It depends on p9 client attach/walk/reference counting, current fsuid, session access modes, dentry locking, inode locking, and the session `rename_sem`.

## Risks and test signals
Risks include fid leaks, stale fids after unlink/rename, race windows around d_unhashed, incorrect access mode user selection, and path walk under concurrent rename. Test signals include multi-user access modes, rename storms, open-file writeback fid reuse, root attach failures, and deep path walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.h -->
# sources/distributed-fs/ceph-client/fs/9p/fid.h

## Purpose
`fid.h` exposes fid management helpers and cache-mode flag adjustment used by 9p VFS files.

## Important APIs, types, and functions
It declares fid lookup/add functions and defines inline `v9fs_parent_fid`, `clone_fid`, `v9fs_fid_clone`, and `v9fs_fid_add_modes`.

## Control flow
Clone helpers look up and clone protocol fids through a zero-length walk. `v9fs_fid_add_modes` marks fids direct or no-write-cache depending on session cache flags, qid version, direct I/O, sync, and open flags.

## State and persistence
The header mutates fid `mode` bits but stores no independent state.

## Dependencies and integration points
It bridges file/inode/address-space code to fid lookup and cache policy selection.

## Risks and test signals
Risks include incorrect direct-cache decisions for synthetic qid version zero, and clone lifetime mistakes. Test signals include O_DIRECT, directio mount, writeback cache, O_DSYNC, sync mount, and qid.version zero servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/fid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.c -->
# sources/distributed-fs/ceph-client/fs/9p/v9fs.c

## Purpose
`v9fs.c` provides 9p module initialization, mount option parsing, session creation/teardown, sysfs cache listing, and inode-cache setup.

## Important APIs, types, and functions
Important APIs are `v9fs_param_spec`, `v9fs_parse_param`, `v9fs_show_options`, `v9fs_session_init`, `v9fs_session_close`, `v9fs_session_cancel`, and `v9fs_session_begin_cancel`. Module lifecycle is `init_v9fs`/`exit_v9fs`; inode cache helpers manage `v9fs_inode_cache`.

## Control flow
Mount parsing fills `v9fs_context` session/client/transport option structs. Session init creates a p9 client, derives protocol/access flags, applies options, attaches a root fid, optionally acquires an FS-Cache session, and registers the session. Module init creates the inode slab, sysfs `fs/9p`, and registers the filesystem.

## State and persistence
Runtime state includes the global session list, sysfs kobject, inode slab cache, session flags/options, p9 client pointer, and optional fscache volume. No filesystem data is stored locally except optional FS-Cache contents.

## Dependencies and integration points
It depends on fs_context parsing, net/9p transports, p9 client creation/attach/disconnect, netfs inode storage, sysfs, and FS-Cache.

## Risks and test signals
Risks include ignored unknown mount options, transport module ref leaks, access mode fallback surprises, cachetag collisions, session-list locking, and teardown while requests are pending. Test signals include mount option matrix, unsupported transports, protocol versions, sysfs cache listing, failed attach cleanup, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.h -->
# sources/distributed-fs/ceph-client/fs/9p/v9fs.h

## Purpose
`v9fs.h` is the core 9p filesystem header defining session flags, cache modes, session state, inode wrapper state, and helper accessors.

## Important APIs, types, and functions
Key definitions are `enum p9_session_flags`, `enum p9_cache_shortcuts`, `enum p9_cache_bits`, `struct v9fs_session_info`, `struct v9fs_inode`, `V9FS_I`, and `v9fs_inode_cookie`.

## Control flow
The header has no primary control flow. Inline helpers recover the 9p inode wrapper and return an FS-Cache cookie when enabled.

## State and persistence
It defines runtime session state: mount options, access mode, protocol flags, cache mode, default ids, p9 client, session list linkage, rename semaphore, and lock retry timeout. Inode state tracks qid, netfs context, cache validity, and a mutex.

## Dependencies and integration points
It connects 9p VFS code to net/9p client types, transports, netfs, backing-dev support, and FS parser structures.

## Risks and test signals
Risks include flag bit overlap, cache shortcut interpretation, stale cache_validity handling, and assumptions about access mode masks. Test signals include compile coverage and mount/runtime tests for every cache/access/protocol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs_vfs.h -->
# sources/distributed-fs/ceph-client/fs/9p/v9fs_vfs.h

## Purpose
`v9fs_vfs.h` declares the shared VFS operation tables and helper functions used across 9p source files.

## Important APIs, types, and functions
It declares inode/file/dentry/super operation objects, `v9fs_fs_type`, `v9fs_req_ops`, inode allocation and stat conversion helpers, dotl helpers, option parsing/showing, and inline helpers converting inode/dentry/superblock to session state.

## Control flow
No standalone flow. It enables cross-file calls between legacy and dotl implementations, superblock setup, file operations, and address-space operations.

## State and persistence
The header owns no state but exposes operation tables that drive VFS dispatch.

## Dependencies and integration points
It integrates 9p with Linux VFS, netfs, p9 client, xattr/ACL, and filesystem registration.

## Risks and test signals
Risks include signature drift as VFS APIs change and mismatched operation tables across protocol variants. Test signals are full 9p compile coverage and mount/open/stat/create tests for legacy, 9P2000.u, and 9P2000.L.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs_vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_addr.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_addr.c

## Purpose
`vfs_addr.c` implements 9p address-space operations using the netfs library for buffered reads, readahead, dirty folios, writeback, and direct I/O stubs.

## Important APIs, types, and functions
It defines `v9fs_req_ops` and `v9fs_addr_operations`. Core callbacks are `v9fs_init_request`, `v9fs_free_request`, `v9fs_issue_read`, `v9fs_begin_writeback`, and `v9fs_issue_write`.

## Control flow
Netfs initializes each request by selecting a fid from the file or inode, setting request size from client msize/iounit, and storing the fid as private data. Read/write subrequests call `p9_client_read` or `p9_client_write`, report progress/errors to netfs, and release fid refs when the request ends.

## State and persistence
Per-request state is the referenced fid and request size. Persistent data resides on the 9p server; local cached folios are governed by netfs and optional FS-Cache.

## Dependencies and integration points
It depends on netfs APIs, p9 client I/O, fid lookup, page cache, trace/netfs events, and cache policy bits set during open.

## Risks and test signals
Risks include missing writable fid during writeback, short I/O handling, EOF/tail clearing, fid lifetime, and iounit/msize sizing. Test signals include buffered reads/writes, readahead, mmap writeback, writeback with write-only opens, direct I/O, short server reads, and cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dentry.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_dentry.c

## Purpose
`vfs_dentry.c` implements 9p dentry operations, including fid cleanup, cached dentry invalidation, attribute revalidation, and rename unalias locking.

## Important APIs, types, and functions
It defines `v9fs_cached_dentry_operations` and `v9fs_dentry_operations`. Internal functions include `v9fs_cached_dentry_delete`, `v9fs_dentry_release`, `__v9fs_lookup_revalidate`, `v9fs_lookup_revalidate`, and unalias lock/unlock helpers.

## Control flow
Negative cached dentries are discarded. On release, the dentry fid hlist is moved under d_lock and all fids are put. Revalidation refreshes inode attributes when `V9FS_INO_INVALID_ATTR` is set, using dotl or legacy refresh paths, and invalidates the dentry if the server reports ENOENT or type change.

## State and persistence
State is dentry-associated fid lists and inode cache-validity flags. No local persistent data is stored.

## Dependencies and integration points
It depends on VFS dentry operations, fid lookup, inode refresh helpers, and session `rename_sem`.

## Risks and test signals
Risks include fid leaks, RCU lookup limitations, stale positive dentries, and revalidation racing with remove/rename. Test signals include dcache-heavy lookup, negative entries, remote deletion, type changes, rename aliasing, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dir.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_dir.c

## Purpose
`vfs_dir.c` implements directory iteration for legacy 9P stat streams and 9P2000.L dirent streams.

## Important APIs, types, and functions
It defines private `struct p9_rdir`, helpers `dt_type` and `v9fs_alloc_rdir_buf`, readdir implementations `v9fs_dir_readdir` and `v9fs_dir_readdir_dotl`, and file operation tables `v9fs_dir_operations` and `v9fs_dir_operations_dotl`.

## Control flow
Directory open reuses `v9fs_file_open`. Iteration allocates a per-fid buffer, fills it with `p9_client_read` or `p9_client_readdir` when consumed, decodes entries with `p9stat_read` or `p9dirent_read`, emits them to the VFS, and advances `ctx->pos` according to protocol encoding.

## State and persistence
Per-directory fid state includes the reusable `rdir` buffer with head/tail offsets. Directory contents persist only on the remote server.

## Dependencies and integration points
It depends on p9 stat/dirent parsers, p9 client read/readdir, VFS `dir_context`, and shared file open/release.

## Risks and test signals
Risks include corrupt directory records, ctx position handling differences, buffer sizing from msize, and memory retained on fid until release. Test signals include large directories, partial dirent buffers, dotl and legacy servers, seekdir/telldir behavior, and malformed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_file.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_file.c

## Purpose
`vfs_file.c` implements 9p regular file operations: open, read/write dispatch, splice, mmap, fsync, and local/remote file locking.

## Important APIs, types, and functions
Important functions include `v9fs_file_open`, `v9fs_file_read_iter`, `v9fs_file_write_iter`, `v9fs_file_splice_read`, `v9fs_file_fsync`, `v9fs_file_fsync_dotl`, `v9fs_file_lock`, `v9fs_file_lock_dotl`, `v9fs_file_flock_dotl`, and `v9fs_file_mmap_prepare`. Operation tables are `v9fs_file_operations` and `v9fs_file_operations_dotl`.

## Control flow
Open converts Linux flags to legacy or dotl open modes, clones/opens a fid, optionally upgrades write-only writeback opens to read/write, uses fscache cookies, adjusts fid cache flags, and stores the fid on the open inode list. I/O chooses netfs cached or unbuffered paths based on fid mode. Dotl locks synchronize local VFS locks with server lock calls and retry blocked locks.

## State and persistence
State includes open fid references, fid mode cache flags, local lock state, netfs page cache/writeback state, and optional fscache cookie use counts. File contents live on the 9p server.

## Dependencies and integration points
It depends on p9 open/read/write/fsync/lock RPCs, netfs file helpers, VFS locking, mmap VM operations, and shared directory release.

## Risks and test signals
Risks include incorrect cache/direct transitions, write-only writeback fallback, lock rollback mismatches, mmap dirty flushing, and fsync semantics differences between legacy wstat and dotl fsync. Test signals include O_APPEND, O_DIRECT, mmap shared writes, flock/fcntl locks, interrupted blocking locks, fsync, splice, and cache modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_inode.c

## Purpose
`vfs_inode.c` implements legacy and 9P2000.u inode operations, mode/stat conversion, inode allocation/eviction, create/lookup/remove/rename, getattr/setattr, symlink, hardlink, and special-file handling.

## Important APIs, types, and functions
Exports include `v9fs_alloc_inode`, `v9fs_free_inode`, `v9fs_set_netfs_context`, `v9fs_init_inode`, `v9fs_evict_inode`, `v9fs_inode_from_fid`, `v9fs_uflags2omode`, `v9fs_blank_wstat`, `v9fs_stat2inode`, `v9fs_refresh_inode`, `v9fs_vfs_unlink`, `v9fs_vfs_rmdir`, and `v9fs_vfs_rename`.

## Control flow
Stat data is converted into Linux inode fields and qid-indexed through `iget5_locked`. Lookup walks from the parent fid and instantiates cached or new inodes depending on metadata caching. Create clones a parent fid, issues `fcreate`, walks back to get an unopened fid, and instantiates the dentry. Remove uses dotl unlinkat when available, then path-based remove fallback. Rename prefers dotl operations and otherwise uses legacy wstat within `rename_sem`.

## State and persistence
Runtime state includes qid/inode associations, inode cache-validity flags, nlink adjustments, page-cache/netfs state, and dentry fids. Persistent metadata changes are sent to the server through wstat/fcreate/remove.

## Dependencies and integration points
It depends on VFS inode operations, p9 stat/wstat/walk/create/remove RPCs, fid management, netfs, FS-Cache, xattr/ACL hooks for dotl tables, and session protocol flags.

## Risks and test signals
Risks include stale inode reuse by qid/version, type changes, rename races, legacy protocol feature gaps, size truncation cache sync, and special-device extension parsing. Test signals include lookup/create/atomic open, unlink/rmdir, cross-directory rename, symlink/hardlink/mknod on dotu, getattr/setattr under cache modes, and inode eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode_dotl.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_inode_dotl.c

## Purpose
`vfs_inode_dotl.c` implements 9P2000.L-specific inode operations using Linux-like protocol RPCs for open/create, mkdir, mknod, symlink, hardlink, getattr, setattr, and ACL-aware creation.

## Important APIs, types, and functions
Important functions are `v9fs_inode_from_fid_dotl`, `v9fs_open_to_dotl_flags`, `v9fs_vfs_setattr_dotl`, `v9fs_stat2inode_dotl`, `v9fs_refresh_inode_dotl`, and dotl operation helpers for atomic open, mkdir, mknod, symlink, link, and getattr. It exports inode operation tables for directories, files, and symlinks.

## Control flow
Dotl inode lookup uses `p9_client_getattr_dotl` and qid plus generation for inode matching. Creation paths compute inherited gid and ACL-adjusted mode, issue protocol-native create/mkdir/mknod, walk back to an unopened fid, instantiate the inode, and set inherited ACLs. Setattr maps Linux `ATTR_*` bits to dotl valid flags, flushes dirty data, calls `p9_client_setattr`, resizes netfs/fscache state, and updates ACLs on chmod.

## State and persistence
Runtime state includes inode generation, qid, cached ACLs, netfs size state, and fid associations. Persistent data and metadata live on the 9p server.

## Dependencies and integration points
It depends on dotl p9 client RPCs, shared legacy lookup/remove/rename helpers, ACL/xattr code, fid management, FS-Cache, and VFS inode operation tables.

## Risks and test signals
Risks include ACL/mode ordering, fid ownership after atomic open, generation-based inode matching, partial stat masks, setattr time precision, and cache size synchronization. Test signals include 9P2000.L create/open, ACL inheritance, symlink/readlink, hardlink, mknod, setattr truncate/chmod/chown, and metadata caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_inode_dotl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_super.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_super.c

## Purpose
`vfs_super.c` implements 9p superblock setup, mount tree creation, statfs, unmount cancellation, inode dropping, writeback hooks, and fs_context lifecycle.

## Important APIs, types, and functions
Key functions are `v9fs_get_tree`, `v9fs_fill_super`, `v9fs_kill_super`, `v9fs_umount_begin`, `v9fs_statfs`, `v9fs_drop_inode`, `v9fs_write_inode`, `v9fs_write_inode_dotl`, `v9fs_init_fs_context`, and `v9fs_free_fc`. It defines `v9fs_super_ops`, `v9fs_super_ops_dotl`, and `v9fs_fs_type`.

## Control flow
Mount allocates a session, initializes it to get the root fid, gets/sets up a superblock, creates the root inode from the fid, loads ACLs, attaches the root fid to the root dentry, and returns the root. Kill super cancels/disconnects the session after VFS teardown. Fs_context init seeds default mount/client/transport options.

## State and persistence
Superblock state points to `v9fs_session_info`; BDI readahead/io_pages reflect cache mode; POSIX ACL and xattr handler state is set from protocol/config. No local persistent filesystem metadata is kept.

## Dependencies and integration points
It depends on VFS superblock/fs_context APIs, p9 session init/close, fid lookup, inode creation, netfs writeback, statfs dotl RPCs, xattr handlers, and ACL support.

## Risks and test signals
Risks include mount failure cleanup, root fid ownership, unmount while RPCs are pending, statfs fallback, and cache-mode inode dropping behavior. Test signals include successful/failed mounts, forced unmount, statfs on dotl/non-dotl servers, remount-like option display, and memory leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.c -->
# sources/distributed-fs/ceph-client/fs/9p/xattr.c

## Purpose
`xattr.c` implements extended attribute get/set/list support for 9p using 9P2000.L xattrwalk and xattrcreate operations.

## Important APIs, types, and functions
Exports include `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_xattr_set`, `v9fs_fid_xattr_set`, `v9fs_listxattr`, and `v9fs_xattr_handlers`. Internal xattr handler callbacks map VFS namespaces to full xattr names.

## Control flow
Get walks to an xattr fid, handles size-only queries and range errors, reads the xattr value, then clunks the attr fid. Set clones the target fid, creates or replaces the xattr stream, writes the value, and clunks the cloned fid. Listing is implemented as xattr get with an empty name.

## State and persistence
No local xattr state is stored. Values persist on the 9p server. Handler registration is static per superblock.

## Dependencies and integration points
It depends on p9 xattr RPCs, fid cloning/lookup, iov_iter, VFS xattr handlers, and optional security namespace support.

## Risks and test signals
Risks include size overflow, partial write errors, clone/clunk error ordering, server namespace restrictions, and empty-name list semantics. Test signals include get size/value, ERANGE, set/remove/create/replace flags, listxattr, security labels, and server errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.h -->
# sources/distributed-fs/ceph-client/fs/9p/xattr.h

## Purpose
`xattr.h` declares 9p xattr helpers and the xattr handler table used by dotl superblocks and ACL support.

## Important APIs, types, and functions
It declares `v9fs_xattr_handlers`, `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_fid_xattr_set`, `v9fs_xattr_set`, and `v9fs_listxattr`.

## Control flow
No executable flow. It provides cross-file linkage for inode, ACL, and superblock code.

## State and persistence
No state is owned by the header.

## Dependencies and integration points
It integrates `xattr.c` with ACL routines and dotl inode operation tables.

## Risks and test signals
Risks are declaration drift and missing handler availability when xattrs are disabled by mount flags. Test signals include build coverage and xattr-enabled/disabled mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/Kconfig

## Purpose
This top-level filesystem Kconfig file organizes the kernel filesystem configuration menu, core filesystem helpers, pseudo filesystems, miscellaneous filesystems, and network filesystems.

## Important APIs, types, and functions
It defines symbols such as `DCACHE_WORD_ACCESS`, `VALIDATE_FS_PARSER`, `FS_IOMAP`, `FS_STACK`, `BUFFER_HEAD`, `LEGACY_DIRECT_IO`, `FS_DAX`, `FS_POSIX_ACL`, `EXPORTFS`, `FILE_LOCKING`, `MISC_FILESYSTEMS`, and `NETWORK_FILESYSTEMS`, and sources many subsystem Kconfig files including `fs/adfs/Kconfig` and `fs/9p/Kconfig`.

## Control flow
Kconfig conditionals gate submenus by `BLOCK`, `NET`, architecture capabilities, and parent menu choices. Selected symbols drive object inclusion in `fs/Makefile` and preprocessor conditionals throughout the kernel.

## State and persistence
The state is build-time `.config`. There is no runtime code.

## Dependencies and integration points
It integrates filesystem implementations with core kernel services such as netfs, cachefiles, crypto, verity, quota, notify, DAX, ACLs, and network stacks.

## Risks and test signals
Risks include broken dependency chains, unreachable filesystem options, invalid built-in/module combinations, and hidden helper symbols. Test signals include allnoconfig, allyesconfig, allmodconfig, randconfig, blockless configs, and network-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Makefile -->
# sources/distributed-fs/ceph-client/fs/Makefile

## Purpose
This top-level filesystem Makefile maps core VFS objects and configured filesystem subdirectories into the kernel build.

## Important APIs, types, and functions
It uses kbuild `obj-y` and `obj-$(CONFIG_*)` lists. Relevant mappings include core VFS objects, `obj-$(CONFIG_NETFS_SUPPORT) += netfs/`, `obj-$(CONFIG_ADFS_FS) += adfs/`, and `obj-$(CONFIG_9P_FS) += 9p/`.

## Control flow
Kbuild compiles always-on VFS core files first, then conditionally descends into helper and filesystem subdirectories based on `.config`. Ordering comments preserve behavior such as ext4 before ext2.

## State and persistence
No runtime state. It persists build graph decisions for the configured kernel.

## Dependencies and integration points
It connects top-level Kconfig symbols to actual code directories and shared VFS infrastructure.

## Risks and test signals
Risks include wrong ordering, stale config names, omitted helper directories, and module/built-in link problems. Test signals include broad config builds and verifying selected filesystems produce objects/modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/adfs/Kconfig

## Purpose
This Kconfig fragment exposes Acorn Disc Filing System support and optional experimental write support.

## Important APIs, types, and functions
It defines `CONFIG_ADFS_FS` and `CONFIG_ADFS_FS_RW`. `ADFS_FS` depends on `BLOCK` and selects `BUFFER_HEAD`; write support depends on `ADFS_FS`.

## Control flow
At configuration time, enabling `ADFS_FS` includes the adfs module/built-in objects. Enabling `ADFS_FS_RW` allows directory update paths that otherwise return `-EINVAL`.

## State and persistence
Only `.config` state is persisted. Runtime write behavior is gated by compiled config checks.

## Dependencies and integration points
It integrates ADFS with block devices, buffer heads, and the miscellaneous filesystem menu.

## Risks and test signals
Risks include users enabling experimental writes on fragile media and blockless configs exposing ADFS. Test signals include read-only and RW builds, module builds, and write path gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/adfs/Makefile

## Purpose
This Makefile builds the ADFS filesystem object from its directory, file, inode, map, and superblock implementation files.

## Important APIs, types, and functions
It builds `adfs.o` for `CONFIG_ADFS_FS` from `dir.o`, `dir_f.o`, `dir_fplus.o`, `file.o`, `inode.o`, `map.o`, and `super.o`.

## Control flow
Kbuild links all listed objects into the ADFS module or built-in object when configured.

## State and persistence
No runtime state; it defines build composition.

## Dependencies and integration points
It maps the ADFS Kconfig symbol to the implementation files declared through `adfs.h`.

## Risks and test signals
Risks include stale object list entries and missing format-specific directory code. Test signals are module/built-in ADFS builds with read-only and RW configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/adfs.h -->
# sources/distributed-fs/ceph-client/fs/adfs/adfs.h

## Purpose
`adfs.h` is the internal ADFS filesystem header defining in-memory inode/superblock/directory state, directory operation abstraction, object metadata, map helpers, and cross-file declarations.

## Important APIs, types, and functions
Key types are `struct adfs_inode_info`, `struct adfs_sb_info`, `struct adfs_dir`, `struct object_info`, `struct adfs_dir_ops`, and `struct adfs_discmap`. Important helpers include `ADFS_I`, `ADFS_SB`, `adfs_filetype`, `adfs_inode_is_stamped`, `__adfs_block_map`, `adfs_map_discrecord`, and `adfs_disc_size`.

## Control flow
The header establishes polymorphic directory operations through `adfs_dir_ops`, allowing common directory code to call F or F+ implementations. Block mapping translates object indirect addresses and logical block offsets into physical sectors through the disc map.

## State and persistence
It defines runtime inode metadata copied from ADFS objects, superblock mount settings and map pointers, loaded directory buffers, and disc map buffer heads. Persistent state is the on-disk ADFS structures referenced by these fields.

## Dependencies and integration points
It depends on buffer heads, VFS inode/superblock structures, Linux ADFS disk-format headers, and map/inode/file/super source files.

## Risks and test signals
Risks include indirect address arithmetic, endian/packed structure assumptions, max name length handling, and union lifetime during shutdown. Test signals include mounting F and F+ images, filetype suffix option, block map lookup, and inode metadata conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/adfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/adfs/dir.c

## Purpose
`dir.c` provides common ADFS directory handling independent of on-disk directory format: buffer loading, copying, iteration, lookup, name hashing/comparison, and optional update/commit coordination.

## Important APIs, types, and functions
Important functions are `adfs_dir_copyfrom`, `adfs_dir_copyto`, `adfs_dir_relse`, `adfs_dir_read_buffers`, `adfs_object_fixup`, `adfs_dir_update`, `adfs_iterate`, `adfs_dir_lookup_byname`, `adfs_hash`, `adfs_compare`, and `adfs_lookup`. It exports `adfs_dir_operations`, `adfs_dentry_operations`, and `adfs_dir_inode_operations`.

## Control flow
Directory reads load mapped blocks into buffer_heads via `__adfs_block_map`; format-specific ops validate and parse entries. Iteration emits dot, dotdot, then delegates to the active `adfs_dir_ops`. Lookup scans entries case-insensitively. Updates take the global directory write semaphore, call format update/commit, mark buffers dirty, and optionally sync.

## State and persistence
Runtime state is loaded buffer_heads in `struct adfs_dir` and a global `adfs_dir_rwsem`. Directory data persists on disk; write support modifies buffers only when `CONFIG_ADFS_FS_RW` is enabled.

## Dependencies and integration points
It depends on format-specific F/F+ ops, buffer-head I/O, VFS dentry/inode operations, ADFS map lookup, and RISC OS name/filetype rules.

## Risks and test signals
Risks include global lock contention, buffer boundary copy errors, corrupted directory parent IDs, name normalization collisions, and dirty-buffer handling after failed commits. Test signals include directory iteration across block boundaries, case-insensitive lookup, `/` to `.` fixups, filetype suffixes, RW update failures, and fsync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.c -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_f.c

## Purpose
`dir_f.c` implements ADFS E/F format directory parsing, validation, iteration, entry update, and commit logic for fixed-size 2048-byte directories.

## Important APIs, types, and functions
Important helpers are `adfs_readval`, `adfs_writeval`, `adfs_dir_checkbyte`, `adfs_f_validate`, `adfs_f_read`, `adfs_dir2obj`, `adfs_obj2dir`, `__adfs_dir_get`, `adfs_f_setpos`, `adfs_f_getnext`, `adfs_f_iterate`, `adfs_f_update`, and `adfs_f_commit`. It exports `adfs_f_dir_ops`.

## Control flow
Read loads exactly `ADFS_NEWDIR_SIZE`, maps header/tail, validates magic names, sequence numbers, reserved fields, parent ID, and check byte. Iteration walks 77 fixed 26-byte entries until an empty name. Update locates an entry by indirect address, writes metadata fields back, and commit increments sequence numbers and recomputes the check byte.

## State and persistence
Runtime state is the loaded directory buffer and current byte position. Persistent state is fixed-format directory entries, header, tail, and check byte on disk.

## Dependencies and integration points
It depends on `dir_f.h` packed structures, common `adfs_dir_copyfrom/to`, object fixup, and buffer dirty/sync paths in `dir.c`.

## Risks and test signals
Risks include unaligned multi-byte value parsing, checkbyte correctness across multiple buffer heads, fixed entry count limits, and corrupt tail/header handling. Test signals include valid/corrupt F directories, empty entry termination, update/commit verification, and images with parent ID mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.h -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_f.h

## Purpose
`dir_f.h` defines packed on-disk structures and constants for ADFS E/F format directories.

## Important APIs, types, and functions
Definitions include `ADFS_NEWDIR_SIZE`, `ADFS_NUM_DIR_ENTRIES`, `ADFS_F_NAME_LEN`, `struct adfs_dirheader`, `struct adfs_direntry`, `struct adfs_olddirtail`, and `struct adfs_newdirtail`.

## Control flow
No executable flow. `dir_f.c` interprets buffers using these layouts.

## State and persistence
The structures describe persistent disk bytes: header sequence/name, 26-byte directory entries, and old/new tail variants with parent ID, title, sequence, magic name, and check byte.

## Dependencies and integration points
It is included only by the F-format directory implementation and must match the ADFS disk layout exactly.

## Risks and test signals
Risks include packing/alignment changes, field-size mismatches, and old/new tail interpretation errors. Test signals are mounting known F-format images and validating directory checksum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.c -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.c

## Purpose
`dir_fplus.c` implements ADFS F+ large-directory support with variable directory size, separate entry/name tables, validation, iteration, update, and commit logic.

## Important APIs, types, and functions
Important helpers are `adfs_fplus_offset`, `adfs_fplus_validate_header`, `adfs_fplus_validate_tail`, `adfs_fplus_checkbyte`, `adfs_fplus_read`, `adfs_fplus_setpos`, `adfs_fplus_getnext`, `adfs_fplus_iterate`, `adfs_fplus_update`, and `adfs_fplus_commit`. It exports `adfs_fplus_dir_ops`.

## Control flow
Read loads the first block, validates header version/magic/size/name/entry bounds, loads the full directory size, validates tail and check byte, and records parent ID. Iteration uses an entry index, copies each bigdir entry, then copies the variable-length name from the names area. Update locates by indirect address and rewrites metadata fields; commit increments sequence counters and recomputes the check byte.

## State and persistence
Runtime state is buffer_heads plus `bighead`, `bigtail`, and entry index. Persistent state is the F+ header, entry table, names area, tail, and check byte.

## Dependencies and integration points
It depends on `dir_fplus.h`, common ADFS directory buffer helpers, endian conversion, and generic object fixup.

## Risks and test signals
Risks include malformed size fields, entry/name table bounds, checkbyte coverage over multi-block directories, integer overflow in offset computation, and partial update persistence. Test signals include large F+ directories, corrupt headers/tails, long names, update/commit cycles, and ctx position overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.h -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.h

## Purpose
`dir_fplus.h` defines packed on-disk structures and constants for ADFS F+ directories.

## Important APIs, types, and functions
It defines `ADFS_FPLUS_NAME_LEN`, `BIGDIRSTARTNAME`, `BIGDIRENDNAME`, `struct adfs_bigdirheader`, `struct adfs_bigdirentry`, and `struct adfs_bigdirtail`.

## Control flow
No executable flow. `dir_fplus.c` uses the definitions to validate and parse F+ directories.

## State and persistence
The structures represent persistent disk layout: directory header with size/count/name metadata, fixed-size big directory entries pointing into a names area, and an end marker/check byte tail.

## Dependencies and integration points
It is private to the F+ directory implementation and must remain packed/aligned to match disk format.

## Risks and test signals
Risks include endian mistakes, structure alignment changes, maximum name-length mismatches, and magic constant errors. Test signals include F+ image mount/iterate/update tests and corrupt directory validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_fplus.h -->
