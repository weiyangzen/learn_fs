# subset-b-000806 research

Grouped research for pSeries PAPR firmware, RTAS, DLPAR, RAS, PLPKS, persistent-memory, PCI, SMP, suspend, secure-VM, and VAS sysfs support. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-sysparm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-sysparm.c

Purpose: Implements kernel and `/dev/papr-sysparm` access to PAPR system parameters through RTAS `ibm,get-system-parameter` and `ibm,set-system-parameter`.

Important APIs/types/functions: Provides `papr_sysparm_buf_alloc()`, `papr_sysparm_buf_free()`, `papr_sysparm_get()`, `papr_sysparm_set()`, ioctl handlers for `PAPR_SYSPARM_IOC_GET` and `PAPR_SYSPARM_IOC_SET`, and a miscdevice named `papr-sysparm`.

Control flow: Kernel callers allocate a `papr_sysparm_buf`, seed its big-endian length/value, and call get or set. The code validates that the encoded length fits the fixed value buffer, copies the buffer into an RTAS work area, retries while firmware reports busy, maps documented RTAS status codes to errno, and copies successful get results back with length clamping. Userspace follows the same path through ioctl marshaling, with write-mode required for set.

State and persistence: The driver itself keeps no persistent parameter cache. State lives in transient heap buffers, RTAS work-area allocations, and userspace I/O blocks. Firmware is the persistent store for settable parameters.

Dependencies and integration points: Depends on RTAS token lookup/calls, `rtas_work_area_alloc()`, PAPR sysparm UAPI structures, miscdevice registration, pseries machine initcalls, and `setup.c` callers such as CMO feature parsing.

Risks: Length and endian handling are security-critical because firmware can return malformed lengths and userspace can provide bogus input lengths. `copy_to_user()` intentionally exports the full maximum output buffer, so clamping only protects kernel interpretation rather than reducing copied bytes. RTAS work-area allocation may sleep.

Test signals: Exercise ioctl get/set with valid and invalid lengths, missing RTAS tokens, unauthorized and unsupported parameters, busy retry paths, read-only fd set rejection, and boot-time CMO sysparm parsing on pseries.

Source read size: 352 lines, 10206 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-sysparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-vpd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-vpd.c

Purpose: Exposes PAPR vital product data retrieval through `/dev/papr-vpd`, returning an fd-backed immutable blob for a requested location code.

Important APIs/types/functions: Defines `struct rtas_ibm_get_vpd_params`, `rtas_ibm_get_vpd()`, VPD sequence begin/end/work callbacks, `papr_vpd_create_handle()`, `papr_vpd_dev_ioctl()`, and miscdevice `papr-vpd`.

Control flow: Userspace submits `PAPR_VPD_IOC_CREATE_HANDLE` with a nul-terminated `papr_location_code`. The driver validates the location code, configures a `papr_rtas_sequence`, serializes RTAS `ibm,get-vpd` calls with `rtas_ibm_get_vpd_lock`, repeatedly fills a 4 KiB work area until sequence completion, and hands the completed data to the common fd/blob reader helpers.

State and persistence: The only long-lived user-visible state is the anonymous file/blob created by `papr_rtas_setup_file_interface()`. RTAS sequence state tracks current sequence number, last status, bytes written, static location code, and work area while the blob is generated.

Dependencies and integration points: Depends on RTAS `ibm,get-vpd`, `papr-rtas-common` blob/handle utilities, RTAS work areas, PAPR VPD UAPI, and pseries machine initcalls.

Risks: Firmware supports only one VPD sequence at a time, so serialization is required. Location-code termination, work-area write bounds, and sequence restart handling are key correctness points. A VPD change can force `-EAGAIN` and retry logic in the common sequence generator.

Test signals: Validate handle creation for valid and unterminated location codes, sequential read/seek/release behavior, RTAS sequence-more-data and sequence-complete paths, VPD-changed retry, missing RTAS token, and concurrent callers under lockdep.

Source read size: 275 lines, 8391 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-vpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_platform_attributes.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_platform_attributes.c

Purpose: Creates `/sys/firmware/papr/energy_scale_info/` entries that expose platform energy and frequency attributes retrieved via `H_GET_ENERGY_SCALE_INFO`.

Important APIs/types/functions: Defines `struct energy_scale_attribute`, `struct h_energy_scale_info_hdr`, `struct papr_attr`, `struct papr_group`, `papr_get_attr()`, sysfs show functions for `desc`, `value`, `value_desc`, `add_attr_group()`, and init function `papr_init()`.

Control flow: Init checks LPAR and energy-scale firmware features, allocates a hcall buffer, retries with larger buffers when firmware reports partial/too-small results, validates header offsets and attribute count, creates the `papr/energy_scale_info` kobjects, and creates one sysfs group per firmware attribute id. Each sysfs read performs a fresh single-attribute hcall because values can change dynamically.

State and persistence: Keeps global kobjects and an array of `papr_group` objects containing sysfs attributes and group names. Attribute values are not cached; firmware is queried on every read.

Dependencies and integration points: Depends on PAPR hypercall wrappers, `firmware_kobj`, pseries initcalls, sysfs/kobject APIs, and firmware feature bits `FW_FEATURE_LPAR` and `FW_FEATURE_ENERGY_SCALE_INFO`.

Risks: Buffer growth arithmetic and returned `array_offset/num_attrs` validation protect against firmware overrun. Cleanup paths must free partially allocated names and attrs. Current allocation growth uses `ESI_HDR_SIZE + (CURR_MAX_ESI_ATTRS * max_esi_attrs)`, which scales in chunks but deserves review because `max_esi_attrs` already begins as an attribute count.

Test signals: Boot on systems with and without energy-scale support, read all sysfs attributes, simulate partial-buffer hcall responses, attributes with empty `value_desc`, invalid firmware offsets, and init failure injection for kobject/sysfs allocation cleanup.

Source read size: 363 lines, 10214 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_platform_attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_scm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_scm.c

Purpose: Implements the PAPR Storage Class Memory platform driver, registering `ibm,pmemory` devices as libnvdimm DIMMs/regions with metadata, health, performance, flush, badblock, and PDSM support.

Important APIs/types/functions: Central type is `struct papr_scm_priv`. Key functions include bind/unbind/query helpers, `papr_scm_pmem_flush()`, `drc_pmem_query_stats()`, PMU callbacks, health query/cache helpers, metadata get/set, PDSM validators/services, `papr_scm_ndctl()`, sysfs attributes, `papr_scm_nvdimm_init()`, MCE notifier `handle_mce_ue()`, and platform driver probe/remove.

Control flow: Probe reads required OF properties, updates NUMA distances, binds the DRC memory through `H_SCM_BIND_MEM`, builds the memory resource, discovers perf-stat buffer size, registers an nvdimm bus, DIMM, and pmem/volatile region, and optionally registers a PMU. ndctl commands dispatch metadata reads/writes or PAPR PDSM packages. Health and perf sysfs files query hypervisor data on demand. Machine-check UE notifications inside a registered SCM region add nvdimm bad ranges.

State and persistence: Per-device state tracks DRC index, block geometry, bound physical address, libnvdimm objects, dirty shutdown counter, cached health bitmap and timestamp, injection mask, stat buffer length, resource, and list membership under `papr_ndr_lock`. Firmware persists SCM contents and metadata.

Dependencies and integration points: Integrates with PAPR SCM hcalls, platform devices from `pmem.c`, libnvdimm/ndctl/PDSM UAPI, perf PMU support, machine-check notifier chains, NUMA mapping, and nvdimm poison notification.

Risks: Long-running hcall retry loops must not abort partial bind/unbind operations. Metadata byte-width endian conversions, PDSM size validation, health-cache locking, resource overflow (`blocks * block_size` comment), and PMU lifetime via `pdev->archdata.priv` are notable risk areas. `pdsm_cmd_desc()` uses `if (cmd >= 0 || cmd < ARRAY_SIZE(...))`, which is logically permissive and should be scrutinized.

Test signals: Hot-add/remove pmem devices, ndctl get/set config, PAPR health and smart-inject PDSMs, hcall busy/partial/error paths, perf stat reads, MCE UE badblock insertion, volatile and persistent regions, module unload, and KASAN/lockdep fault injection around probe cleanup.

Source read size: 1542 lines, 42875 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_scm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci.c

Purpose: Provides pSeries-specific PCI fixups, SR-IOV PE association, legacy I/O region reservation, and host bridge preparation.

Important APIs/types/functions: Implements SR-IOV helpers `pseries_send_map_pe()`, `pseries_associate_pes()`, enable/disable hooks, `pSeries_final_fixup()`, Winbond IDE fixup, `prop_to_pci_speed()`, and `pseries_root_bridge_prepare()`.

Control flow: Final fixup reserves legacy ISA I/O regions, reports EEH state, and installs SR-IOV hooks when enabled. SR-IOV enable creates VF pci_dn data, builds an RTAS PE map from VF BAR/RID values, calls `ibm,open-sriov-map-pe-number`, and records firmware-assigned PE numbers. Root bridge preparation sets deferred controller release and reads `ibm,pcie-link-speed-stats` up the OF parent chain to set bus speeds.

State and persistence: Per-device SR-IOV state is stored in `pci_dn->pe_num_map`; host bridge release data ties `pci_host_bridge` lifetime to `pci_controller`. No persistent storage is maintained by this file.

Dependencies and integration points: Depends on RTAS PCI calls, EEH, pci_dn, pseries MSI domains, Open Firmware PCI properties, and generic PCI SR-IOV resource handling.

Risks: RTAS data buffer usage must be serialized, PE map size must fit `RTAS_DATA_BUF_SIZE`, and VF limit validation combines firmware configurable VFs with a hard cap. Resource fixups for old Winbond hardware can affect legacy systems. Parent OF node reference handling in bridge speed discovery is subtle.

Test signals: SR-IOV enable/disable on pseries, PE number assignment validation, absent RTAS token, VF count boundary tests, PCIe link speed sysfs values, hotplugged root bridges, EEH recovery, and Winbond fixup regression on legacy machines.

Source read size: 293 lines, 8204 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci_dlpar.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci_dlpar.c

Purpose: Handles dynamic add/remove of pSeries PCI host bridges for DLPAR/hotplug flows.

Important APIs/types/functions: Exports `init_phb_dynamic()` and `remove_phb_dynamic()`.

Control flow: Add initializes NUMA node state for the PHB node, allocates a `pci_controller`, sets up RTAS ranges/controller ops, initializes pci_dn data, MSI domains, IOMMU registration, EEH PE structures, scans the PHB, and finishes bus addition. Remove requires an empty root bus, unmaps I/O space, unregisters IOMMU/MSI, removes the bus and host bridge device, and releases I/O and memory resources while relying on deferred controller freeing.

State and persistence: State lives in the dynamically allocated `pci_controller`, PCI bus/device tree objects, MSI domains, IOMMU registration, EEH PE records, and node online state.

Dependencies and integration points: Integrates with PCI core, pseries RTAS PHB setup, pseries MSI, ppc IOMMU, EEH, NUMA node registration, and `pseries_root_bridge_prepare()` deferred release.

Risks: Removal while child devices remain is refused, but lifetime is still delicate because bus removal, host bridge unregister, and deferred controller free must happen in the right order. Error paths in add are sparse because many helper failures are not explicitly unwound.

Test signals: PCI PHB hot-add/hot-remove, remove with active children returning `-EBUSY`, NUMA node creation, EEH device creation, MSI allocation/free, IOMMU registration cleanup, and repeated DLPAR cycles.

Source read size: 129 lines, 3557 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci_dlpar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-secvar.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-secvar.c

Purpose: Adapts PowerVM PLPKS objects into the kernel secure-variable (`secvar`) interface for static and dynamic secure boot key management.

Important APIs/types/functions: Defines secure variable name lists, `get_policy()`, `plpks_get_variable()`, `plpks_set_variable()`, `plpks_get_sb_keymgmt_mode()`, `plpks_secvar_format()`, `plpks_max_size()`, and static/dynamic `secvar_operations`.

Control flow: Init checks PLPKS availability, reads firmware variable `SB_VERSION` to determine static versus dynamic key-management mode, and installs the matching secvar ops. Gets convert UTF-8 names to little-endian UTF-16 PLPKS labels, read OS-owned variables, and report sizes. Sets parse an 8-byte big-endian flags prefix, strip it from payload, choose policy by variable name, and issue a signed update.

State and persistence: No local cache is kept. Secure variables and `SB_VERSION` persist in PLPKS/firmware; secvar ops expose those values to the broader secure-boot stack.

Dependencies and integration points: Depends on `plpks.c` read/signed-update APIs, `asm/secvar.h`, UTF-8/UTF-16 conversion helpers, pseries initcalls, and secure boot variable naming conventions.

Risks: Name conversion length excludes the terminating nul and must match PLPKS label semantics. Write payloads must include signed-update flags and at least one byte of real data. Returning `-EIO` for most read failures hides detail from userspace intentionally, while writes preserve PLPKS-specific errors.

Test signals: Static and dynamic key mode detection, reads of PK/KEK/db/dbx/grubdb/sbat variables, signed updates with invalid flags or short buffers, missing `SB_VERSION`, PLPKS unavailable boot, and secvar format/max-size queries.

Source read size: 224 lines, 6481 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-secvar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-sysfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-sysfs.c

Purpose: Exposes PLPKS configuration values under `/sys/firmware/plpks/config`.

Important APIs/types/functions: Uses `PLPKS_CONFIG_ATTR` to create read-only attributes for version, object limits, total/used space, supported policies, signed update algorithms, and wrapping features. Exports `plpks_config_create_softlink()`.

Control flow: Init checks PLPKS availability, creates `plpks` and `config` kobjects below `firmware_kobj`, and attaches the attribute group. Each sysfs read calls the corresponding `plpks_get_*` accessor. `used_space` refreshes configuration in the core before returning.

State and persistence: Keeps global kobject pointers for the PLPKS root and config directory. All displayed data comes from cached or refreshed PLPKS core configuration.

Dependencies and integration points: Depends on `plpks.c` availability/config accessors, firmware sysfs, pseries subsystem initcall ordering, and consumers that may create symlinks to the config directory.

Risks: Initialization cleanup must release both kobjects on partial failures. Attribute values are only as fresh as the core accessor semantics, so most fields are initialization snapshots except used space.

Test signals: Sysfs presence only when PLPKS is available, read formatting for all attributes, symlink creation success/failure, kobject allocation failure paths, and config value refresh after object writes/removes.

Source read size: 96 lines, 2787 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks.c

Purpose: Provides the core Power LPAR Platform KeyStore implementation: configuration discovery, OS password management, object label/auth construction, read/write/remove/signed-update APIs, wrapping-key operations, and kexec password handoff.

Important APIs/types/functions: Defines `struct plpks_auth`, label structures, cached config globals, `pseries_status_to_err()`, `_plpks_get_config()`, `plpks_is_available()`, config getters, `plpks_signed_update_var()`, `plpks_write_var()`, `plpks_remove_var()`, read wrappers for OS/firmware/bootloader owners, `plpks_gen_wrapping_key()`, `plpks_wrap_object()`, `plpks_unwrap_object()`, `plpks_populate_fdt()`, and `plpks_early_init_devtree()`.

Control flow: Early boot may recover an existing OS password from `/chosen/ibm,plpks-pw` and nop it from the FDT. Arch init checks the firmware feature, fetches and validates PLPKS config with `H_PKS_GET_CONFIG`, then generates or reuses an OS owner password. Object operations build aligned auth and label buffers, call the relevant `H_PKS_*` hcall, map hypervisor status to errno, and for mutating operations wait for object flush confirmation.

State and persistence: Static globals cache the OS password and config values (`version`, sizes, policies, wrapping flags, used space). PLPKS objects persist in hypervisor storage. Kexec persistence is handled by embedding the password into the next FDT and clearing it early on the next boot.

Dependencies and integration points: Used by secvar, SED, sysfs, secure-boot wrapping, kexec, FDT code, memblock, PAPR hcall wrappers, and firmware feature detection.

Risks: Password buffers and auth/label structures must satisfy hypervisor alignment and page-boundary constraints. Long-busy signed updates and object flush polling can time out. Wrapping/unwrap output length arithmetic assumes wrapped objects are at least the fixed overhead. `plpks_is_available()` refreshes config on every call, which has side effects on cached fields.

Test signals: PLPKS available/unavailable boot, kexec password carryover, read/write/remove OS variables, signed update policies, object flush timeout, config validation failures, wrapping-key generation idempotency, wrap/unwrap round trips, and sensitive-buffer leak checks.

Source read size: 1379 lines, 38660 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks_sed_ops.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks_sed_ops.c

Purpose: Implements SED Opal boot PIN key read/write operations backed by PLPKS.

Important APIs/types/functions: Defines `struct plpks_sed_object_data`, constants for SED component/key/authority/range, `plpks_init_var()`, `sed_read_key()`, and `sed_write_key()`.

Control flow: First use lazily checks PLPKS availability. Reads initialize a PLPKS common variable, read the object into the fixed SED data format, convert the big-endian key length, copy the key out, nul-terminate it, and return the length. Writes populate the SED object metadata and key, remove any existing variable, then write the replacement variable.

State and persistence: Local booleans cache whether PLPKS was initialized and available. SED key material persists as a common PLPKS object under component `sed-opal`.

Dependencies and integration points: Depends on PLPKS core APIs and the SED Opal key interface declared in `linux/sed-opal-key.h`.

Risks: `sed_read_key()` bounds the copied key by `var.datalen`, not the fixed key array or caller buffer size, so callers must provide sufficient space. `sed_write_key()` copies `keylen` into a 32-byte array without local clamping, making caller validation critical. Name mangling for `opal-boot-pin` sets `var->name` to `/default/pri` but leaves `namelen` as the original key length, which deserves review.

Test signals: Read/write boot PIN with PLPKS unavailable, key lengths at 0/32/over-limit, replacement write after remove, default label mapping, endian round trips, and SED Opal unlock integration.

Source read size: 131 lines, 3546 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/plpks_sed_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pmem.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pmem.c

Purpose: Handles DLPAR hot-add/hot-remove of pSeries persistent memory device-tree nodes and initial population of persistent-memory platform devices.

Important APIs/types/functions: Uses global `pmem_node`, helpers `pmem_drc_add_node()`, `pmem_drc_remove_node()`, exported `dlpar_hp_pmem()`, OF match table `drc_pmem_match`, and init `pseries_pmem_init()`.

Control flow: Init finds the `ibm,persistent-memory` parent on POWER8+ and probes child `ibm,pmemory` devices through OF platform code. Hotplug events validate DRC-index event format, take the device hotplug lock, acquire or release the DRC, configure connectors, attach/detach OF nodes, and rely on OF reconfig notifiers to create or tear down platform devices consumed by `papr_scm.c`.

State and persistence: Keeps a referenced global pointer to the persistent-memory parent node. Device state is represented in the dynamic OF tree and DRC ownership in firmware.

Dependencies and integration points: Integrates with pseries DLPAR RTAS helpers, OF dynamic attach/detach, platform bus probing, memory hotplug build config, and the PAPR SCM platform driver.

Risks: Failed attach after configure must release the DRC and free connector nodes carefully. Failed release after detach attempts to reattach the node. Hotplug during early boot is handled by rediscovering `pmem_node`, but lifetime/reference handling remains important.

Test signals: Initial discovery, pmem hot-add/hot-remove, unsupported event id/action, missing parent node, configure-connector failure, attach/detach rollback, and interaction with `papr_scm_probe/remove`.

Source read size: 167 lines, 4357 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/power.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/power.c

Purpose: Provides the pSeries `auto_poweron` sysfs control used to choose normal RTAS power-off versus UPS auto-restart power-off.

Important APIs/types/functions: Defines global `rtas_poweron_auto`, sysfs show/store helpers, `auto_poweron_attr`, and init routines for PM and non-PM builds.

Control flow: Init creates or extends the `power` kobject with `auto_poweron`. Reads print the current global value. Writes parse an unsigned long and accept only `0` or `1`; `setup.c` later uses this flag in `pseries_power_off()`.

State and persistence: The flag is a runtime global and is not persisted across boot. Firmware behavior changes only at power-off call time.

Dependencies and integration points: Integrates with generic power sysfs, pseries initcalls, and RTAS power-off handling in `setup.c`.

Risks: The store path uses `sscanf()` and accepts trailing data after a valid 0/1. When `CONFIG_PM` is enabled it assumes `power_kobj` is already available from generic PM code.

Test signals: Sysfs read/write, invalid values, PM and non-PM build coverage, power-off path with and without `ibm,power-off-ups`, and permissions on the attribute.

Source read size: 72 lines, 1598 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries.h

Purpose: Declares shared pSeries platform interfaces used across setup, RAS, DLPAR, PCI, memory, CPU hotplug, security mitigation, RNG, and CMO code.

Important APIs/types/functions: Declares event-source IRQ setup, machine-check/system-reset handlers, SMP init and stopped-state constants, kexec CPU down, PCI fixups/MSI/controller ops, DLPAR helpers, memory/pmem/cpu hotplug hooks with stubs, CMO accessors, security mitigation setup, HBLKRM reading, RNG init, and SPAPR IOMMU grouping.

Control flow: Header-only inline behavior supplies no-op or `-EOPNOTSUPP` stubs when optional configs are absent and exposes CMO globals through accessors.

State and persistence: Does not own state; it names globals such as `rtas_poweron_auto`, CMO PSP/page-size values, and `pseries_security_flavor`.

Dependencies and integration points: Included throughout `arch/powerpc/platforms/pseries`. It mediates compile-time dependencies for SMP, memory hotplug, CPU hotplug, hash MMU, and SPAPR IOMMU features.

Risks: Prototypes here are cross-file contracts; changing signatures or stub semantics can break optional configuration builds. CMO accessors expose mutable globals initialized in `setup.c`.

Test signals: Build matrix across SMP/non-SMP, MEMORY_HOTPLUG, HOTPLUG_CPU, HASH_MMU, and SPAPR_TCE_IOMMU; runtime DLPAR and PCI paths that depend on declarations.

Source read size: 131 lines, 3627 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries_energy.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries_energy.c

Purpose: Exposes pSeries `H_BEST_ENERGY` CPU activation/deactivation hints through CPU sysfs files.

Important APIs/types/functions: Implements `cpu_to_drc_index()`, `drc_index_to_cpu()`, `get_best_energy_list()`, `get_best_energy_data()`, sysfs show wrappers, `pseries_energy_init()`, and cleanup.

Control flow: Init requires `FW_FEATURE_BEST_ENERGY`, creates root CPU hint-list files, and creates per-CPU hint files. Reads convert between logical CPUs and DRC indexes using either `ibm,drc-info` or legacy `ibm,drc-indexes`, call `H_BEST_ENERGY` in list or per-CPU mode, and format online/offline activation or deactivation candidates.

State and persistence: Maintains only `sysfs_entries` to guard cleanup. Hint data comes live from hypervisor.

Dependencies and integration points: Depends on CPU sysfs, OF CPU DRC properties, PAPR hcalls, CPU online state, module init/exit, and firmware feature detection.

Risks: DRC parsing has legacy and modern formats and must handle references correctly. The `ibm,drc-info` loops use early exits on non-CPU DRC types. CPU device pointers are assumed present for possible CPUs during sysfs creation and removal.

Test signals: Systems with both DRC property formats, online/offline CPU hint lists, per-CPU hint values, unsupported hcall, CPU hotplug interactions, module unload cleanup, and malformed OF DRC properties.

Source read size: 368 lines, 8828 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries_energy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ras.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ras.c

Purpose: Implements pSeries RAS interrupt handling, EPOW/power event parsing, hotplug event dispatch, RTAS hardware error logging, and FWNMI machine-check recovery.

Important APIs/types/functions: Defines RTAS log buffer/lock, `struct pseries_mc_errorlog`, RAS IRQ init functions, `ras_hotplug_interrupt()`, `ras_epow_interrupt()`, `ras_error_interrupt()`, FWNMI helpers, `pSeries_system_reset_exception()`, `mce_handle_error()`, `pSeries_machine_check_log_err()`, `pSeries_machine_check_exception()`, and `pseries_machine_check_realmode()`.

Control flow: Init registers event-source IRQs for hotplug, internal errors, and EPOW. IRQ handlers call RTAS `check-exception` into a shared buffer under spinlock, log or queue events, and power off for fatal cases. FWNMI paths validate firmware save pointers, copy RTAS logs into per-CPU PACA buffers, translate RTAS MCE sections into generic machine-check events, perform limited real-mode recovery for ERAT/SLB, and later decide whether to recover, signal, die, or panic.

State and persistence: Global state includes the shared RTAS log buffer, `ras_check_exception_token`, EPOW event count, FWNMI token globals from setup, and per-CPU PACA MCE buffers allocated elsewhere.

Dependencies and integration points: Integrates with RTAS, pseries error log parsing, DLPAR workqueues, poweroff/reboot paths, machine-check core, SLB/ERAT flushing, SMP NMI IPI handling, and `setup.c` machine callbacks.

Risks: The shared log buffer is interrupt-context state guarded by a spinlock; hotplug handler assumes a hotplug section exists before dereferencing. FWNMI recovery must release `ibm,nmi-interlock` promptly without losing logs. Machine-check recovery decisions are architecture-critical.

Test signals: Inject RTAS hotplug/EPOW/internal-error events, fatal versus recoverable hardware errors, FWNMI system reset and MCE paths, user/kernel synchronous UE handling, SLB/ERAT recovery, malformed/corrupt save areas, and panic/poweroff behavior.

Source read size: 882 lines, 24802 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/reconfig.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/reconfig.c

Purpose: Provides the legacy `/proc/powerpc/ofdt` write interface for dynamic Open Firmware device-tree node and property reconfiguration.

Important APIs/types/functions: Implements node add/remove helpers, property list parsing/allocation/freeing, command handlers for `add_node`, `remove_node`, `add_property`, `remove_property`, `update_property`, `ofdt_write()`, and proc registration.

Control flow: A privileged write is blocked under device-tree lockdown, copied from userspace as a nul-terminated command buffer, split into command and payload, parsed into paths/phandles/properties, and applied using OF attach/detach/add/remove/update APIs. Updating `slb-size` or `ibm,slb-size` also calls `slb_set_size()`.

State and persistence: Mutates the live dynamic OF tree. Allocated `struct property` objects are attached to nodes on success or freed on failure. No separate persistent state exists.

Dependencies and integration points: Depends on OF dynamic APIs, security lockdown, procfs, usercopy, `pseries_of_derive_parent()`, and MMU SLB sizing.

Risks: The binary/text hybrid property parser is fragile and legacy. Some handlers leak node references on early returns. Property removal passes `of_find_property()` results directly and must handle absent properties through OF core behavior. Lockdown is essential because this mutates hardware description.

Test signals: Proc command tests for add/remove/update paths, malformed property buffers, lockdown enforcement, child-node busy removal, SLB-size update, reference leak detection, and OF reconfig notifier effects.

Source read size: 414 lines, 10664 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/reconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rng.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rng.c

Purpose: Installs pSeries firmware random seed support via the `H_RANDOM` hypercall when an `ibm,random` device-tree node exists.

Important APIs/types/functions: Implements `pseries_get_random_long()` and `pseries_rng_init()`.

Control flow: Init searches for compatible node `ibm,random`; if present, it assigns `ppc_md.get_random_seed`. Calls to that hook invoke `H_RANDOM`, return the first hypercall result word on success, and report failure otherwise.

State and persistence: Only mutates the machine descriptor hook. Random values are not cached.

Dependencies and integration points: Depends on OF compatible nodes, PAPR hcall wrappers, arch random seed plumbing, and pseries setup calling `pseries_rng_init()`.

Risks: Availability is inferred from device tree, not from probing the hcall at init. Runtime hcall failures simply return no seed.

Test signals: Boot with and without `ibm,random`, successful and failing `H_RANDOM`, random seed consumers, and OF node reference cleanup.

Source read size: 37 lines, 818 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.c

Purpose: Implements RTAS firmware-assisted dump operations for PowerVM, bridging generic fadump core logic with RTAS `ibm,configure-kernel-dump` structures and firmware-provided dump data.

Important APIs/types/functions: Uses static `fdm` and `fdm_active`, and implements `rtas_fadump_init_mem_struct()`, register/unregister/invalidate/process/region-show/trigger/max-region ops, CPU register parsing helpers, `rtas_fadump_build_cpu_notes()`, and `rtas_fadump_dt_scan()`.

Control flow: Device-tree scan detects fadump support and active dumps, captures firmware section sizes, and installs `fadump_ops`. Registration builds a dump memory structure with CPU state, HPTE, boot memory, and optional parameter sections, then calls RTAS with busy-delay handling. Capture kernel processing validates completed sections, parses firmware `REGSAVE` CPU register data into ELF notes, overlays exact crash CPU registers from the fadump header, and updates the vmcore header.

State and persistence: `fdm` is the registration structure for future crashes; `fdm_active` points to firmware-preserved active dump metadata from the flattened device tree. Generic `fw_dump` carries reservation, boot-memory, CPU-note, and active/registered state.

Dependencies and integration points: Depends on generic fadump internals, RTAS calls, OF flat tree properties, memblock/crash dump plumbing, ELF note generation, and `rtas-fadump.h` layout definitions.

Risks: Section counts and exact structure size must match firmware expectations. Active-dump pointer address handling is subtle. CPU register parser trusts firmware sentinels and can run off if malformed. Busy-delay loops currently have TODOs for upper time limits.

Test signals: Fadump register/unregister/invalidate, active dump capture boot, malformed or incomplete sections, CPU note generation for multiple CPUs, parameter-area preservation, non-contiguous reserved memory error, and RTAS busy/error status mapping.

Source read size: 649 lines, 19570 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.h

Purpose: Defines RTAS fadump constants, dump section layouts, register-save layouts, and utility macros shared by the RTAS fadump implementation.

Important APIs/types/functions: Provides section type constants, `RTAS_FADUMP_MIN_BOOT_MEM`, `MAX_SECTIONS`, `RTAS_FADUMP_MAX_BOOT_MEM_REGS`, `struct rtas_fadump_section`, `struct rtas_fadump_section_header`, `struct rtas_fadump_mem_struct`, register save header/entry structs, `RTAS_FADUMP_SKIP_TO_NEXT_CPU`, and CPU id mask.

Control flow: Header-only control flow is limited to the skip macro, which advances a register-entry pointer until `CPUEND` and then to the next CPU block.

State and persistence: Describes firmware-persistent dump memory structures and register-save data; it owns no runtime state.

Dependencies and integration points: Consumed by `rtas-fadump.c` and generic fadump code interacting with PAPR/RTAS firmware dump formats.

Risks: Structure packing, endian fields, and maximum section counts are firmware ABI. The skip macro assumes a valid `CPUEND` sentinel and has no bounds checking.

Test signals: Build-time layout checks, fadump registration structure inspection, active dump parsing, unknown/new section compatibility, and corrupted register-save data tests.

Source read size: 121 lines, 3930 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-work-area.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-work-area.c

Purpose: Provides RTAS-addressable temporary work-area allocation with an early-boot fallback and a bounded runtime gen_pool/mempool allocator.

Important APIs/types/functions: Defines allocation constants, global `rwa_state`, early static work area, `__rtas_work_area_alloc()`, `rtas_work_area_free()`, `rtas_work_area_allocator_init()`, and `rtas_work_area_reserve_arena()`.

Control flow: Early callers get a single aligned static 4 KiB buffer. Early boot reserves a low-memory arena if relevant RTAS functions exist. Later arch init creates a gen_pool over that arena plus a descriptor mempool, marks the allocator available, and regular allocations queue under a mutex then wait on a waitqueue for first-fit aligned space. Frees return space and wake waiters.

State and persistence: Runtime state includes the reserved arena pointer, gen_pool, descriptor mempool, availability flag, mutex, waitqueue, and early in-use flag.

Dependencies and integration points: Used by PAPR sysparm, VPD, and other RTAS call wrappers needing firmware-accessible buffers. Depends on memblock, genalloc, mempool, RTAS token discovery, and pseries init ordering.

Risks: Requests larger than `RTAS_WORK_AREA_MAX_ALLOC_SZ` warn but could block indefinitely if bypassing wrapper checks. Early work area supports only one in-flight allocation. Allocation fairness relies on serializing waiters with the mutex.

Test signals: Early sysparm calls before allocator init, concurrent runtime allocations of mixed sizes, allocation/free wakeups, exhausted pool behavior, RTAS work-area physical address validity, and warning paths for oversize or double-free early use.

Source read size: 210 lines, 6524 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-work-area.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/setup.c

Purpose: Main pSeries platform setup file: machine probing, early architecture initialization, interrupt/controller setup, PCI discovery, FWNMI setup, LPAR idle/accounting, security mitigations, CMO parsing, power-off, and machine descriptor registration.

Important APIs/types/functions: Defines globals such as `shared_processor`, CMO values, `fwnmi_active`, `ibm_nmi_interlock_token`, and `pseries_security_flavor`. Key functions include `fwnmi_init()`, `pseries_init_irq()`, DTL allocation, LPAR idle, relocation-on-exception controls, PCI PHB discovery and SR-IOV fixups, `pseries_setup_security_mitigations()`, `pSeries_setup_arch()`, `pseries_init()`, `pseries_power_off()`, `pSeries_probe()`, and `define_machine(pseries)`.

Control flow: Probe validates CHRP/pSeries compatibility, installs power-off, and runs early pseries init. Setup initializes SMP/hotplug, FWNMI buffers, security mitigations, PCI flags/tokens/notifiers, NVRAM, VPA/shared-processor behavior, idle/PMC hooks, SR-IOV hooks, root bridge prepare, and RNG. The machine descriptor wires RTAS and RAS handlers into generic powerpc callbacks.

State and persistence: Maintains machine-wide feature globals, CMO parameters from sysparm, FWNMI per-CPU buffer pointers, DTL cache, relocation-on-exception state, and machine descriptor hooks.

Dependencies and integration points: Integrates almost every pSeries subsystem: RTAS, hcalls, OF, PCI/MSI/IOMMU, XICS/XIVE, VPA/DTL, security feature framework, fadump/RAS, CMO, RNG, kexec, PM, NVRAM, and powerpc machine descriptors.

Risks: Init ordering is critical because callbacks are installed before later subsystems use them. FWNMI buffers must be below RMA. Security mitigation defaults must be reset before migration-sensitive hcall updates. CMO string parsing mutates a sysparm buffer and must stay within firmware length bounds. Power-off intentionally never returns.

Test signals: Boot on LPAR and non-LPAR pSeries, radix/hash MMU, XIVE/XICS fallback, FWNMI MCE/system reset, migration security-feature refresh, SR-IOV firmware BAR parsing, CMO sysparm parsing, shared processor accounting, kexec/kdump endian exception paths, and power-off UPS flag behavior.

Source read size: 1165 lines, 33429 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/smp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/smp.c

Purpose: Provides pSeries SMP operations for CPU startup, per-CPU interrupt setup, VPA setup, IPI routing, and NMI IPI support.

Important APIs/types/functions: Defines `of_spin_mask`, `smp_query_cpu_stopped()`, `smp_startup_cpu()`, `smp_setup_cpu()`, `smp_pSeries_kick_cpu()`, `pseries_smp_prepare_cpu()`, `dbell_or_ic_cause_ipi()`, `pseries_cause_nmi_ipi()`, `pSeries_smp_probe()`, `pseries_smp_ops`, and `smp_init_pseries()`.

Control flow: Early init installs pSeries SMP ops and marks CPUs already spinning in OF hold loops when stopped-state query is unavailable. CPU kick starts a CPU through RTAS `start-cpu` unless it is already spinning, then sets PACA `cpu_start`. Probe initializes XIVE or XICS SMP support and may replace controller IPIs with doorbell-or-controller IPIs when hardware, SMT, hypervisor, and secure-guest conditions make that useful.

State and persistence: Tracks OF-spinning CPUs in `of_spin_mask` and stores the original interrupt-controller IPI function in `ic_cause_ipi`. Per-CPU setup initializes XIVE/XICS and VPA state.

Dependencies and integration points: Depends on RTAS CPU calls, PACA startup flags, XICS/XIVE, doorbells, VPA, KVM guest detection, secure guest checks, and generic powerpc SMP ops.

Risks: CPU startup differs for OF-started, stopped, kexec, and missing-token cases. Doorbell optimization must avoid slow or unsupported KVM emulation and secure-guest instruction visibility problems. NMI IPI uses hypervisor system-reset signaling and must tolerate failure.

Test signals: Secondary CPU boot, CPU hotplug, kexec CPU states, XIVE and XICS systems, SMT doorbell IPI delivery, KVM and secure guest behavior, RTAS query/start failures, and NMI IPI all-others paths.

Source read size: 282 lines, 7137 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/suspend.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/suspend.c

Purpose: Exposes pSeries partition hibernation/suspend-to-memory coordination through `/sys/power/hibernate` and platform suspend ops.

Important APIs/types/functions: Defines `pseries_suspend_begin()`, `pseries_suspend_enter()`, sysfs `store_hibernate()`/`show_hibernate()`, `suspend_subsys`, `pseries_suspend_ops`, sysfs registration helper, and `pseries_suspend_init()`.

Control flow: Init on LPAR creates a custom `power` bus root with a `hibernate` attribute and installs suspend ops. Writing a stream id requires `CAP_SYS_ADMIN`, polls `H_VASI_STATE` until firmware reports suspending rather than enabled, invokes `pm_suspend(PM_SUSPEND_MEM)`, and on success runs `post_mobility_fixup()`. Enter calls `rtas_ibm_suspend_me()`.

State and persistence: Keeps a static device for the suspend sysfs bus. Hibernation stream state lives in firmware and post-resume device-tree fixups update runtime state.

Dependencies and integration points: Depends on PAPR VASI hcall, RTAS suspend-me, generic PM suspend core, pseries mobility fixups, firmware LPAR feature detection, and capability checks.

Risks: The sysfs bus name overlaps conceptually with generic power sysfs. `simple_strtoul()` parsing accepts trailing junk. Polling `-EAGAIN` sleeps indefinitely until firmware changes state. Correct post-mobility fixup is essential after resume.

Test signals: Sysfs hibernate read/write permissions, valid/invalid stream ids, VASI enabled/suspending/error states, suspend/resume on LPAR, post-mobility device-tree update, and non-LPAR init no-op.

Source read size: 190 lines, 4407 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/svm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/svm.c

Purpose: Implements pSeries secure guest memory-sharing hooks for SWIOTLB, generic set-memory encrypted/decrypted calls, and dispatch trace log page sharing.

Important APIs/types/functions: Provides early init `init_svm()`, `set_memory_encrypted()`, `set_memory_decrypted()`, `dtl_cache_ctor()`, and DTL shared-page tracking helpers.

Control flow: Early init checks `is_secure_guest()`, forces SWIOTLB use for DMA, marks SWIOTLB usable for any address, and shares the SWIOTLB buffer with the host. Encryption/decryption hooks validate page alignment and call ultravisor unshare/share operations when confidential-computing memory encryption is active. DTL cache construction shares each dispatch log page once.

State and persistence: Maintains a fixed array of shared DTL pages and a count. SWIOTLB flags are global runtime state. Memory sharing state is maintained by the ultravisor.

Dependencies and integration points: Depends on secure guest detection, confidential-computing attributes, ultravisor page share/unshare calls, SWIOTLB, DTL allocation from `setup.c`, and machine early init ordering.

Risks: DTL page tracking has no explicit locking and assumes construction context serialization. `dtl_nr_pages` overflow only warns after storing. Encryption hooks silently no-op outside encrypted guests, so callers must not infer security transitions there.

Test signals: Secure guest boot DMA with SWIOTLB forced, set_memory encrypted/decrypted alignment checks, ultravisor share/unshare calls, DTL allocation across all CPUs, and non-secure guest no-op behavior.

Source read size: 95 lines, 2335 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas-sysfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas-sysfs.c

Purpose: Builds pSeries VAS sysfs hierarchy for GZIP default and QoS capability credit accounting and QoS credit updates.

Important APIs/types/functions: Defines `struct vas_caps_entry`, `struct vas_sysfs_entry`, read/store helpers, capability kobj types, `sysfs_add_vas_caps()`, miscdevice `vas`, and `sysfs_pseries_vas_init()`.

Control flow: Init registers `/dev/vas`, creates `vas0` below the misc device, and creates a `gzip` directory when GZIP capability bits are present. Each capability added later allocates a `vas_caps_entry`, chooses default or QoS kobject type based on descriptor, and creates `default_capabilities` or `qos_capabilities`. Reads report atomic total/used credits. QoS writes parse a new total and call `vas_reconfig_capabilties()` to close/reopen windows as needed.

State and persistence: Global kobject pointers track the VAS root and gzip directory. Each capability kobject owns a heap `vas_caps_entry` pointing at live capability state maintained by the VAS core.

Dependencies and integration points: Depends on VAS core types/functions in `vas.h`, miscdevice sysfs, kobject lifetime, atomic credit counters, and management-console DLPAR QoS notifications.

Risks: `vas_caps_kobj_name()` returns `"Unknown"` without initializing a kobject for unexpected descriptors; caller currently avoids `kobject_add()` when parent is NULL but still leaks the allocated entry. QoS store maps all reconfiguration failures to `-EINVAL`, hiding detail.

Test signals: Sysfs hierarchy for default and QoS capabilities, read credit counters while windows open/close, QoS credit update via drmgr path, unsupported descriptors, kobject release cleanup, and `CONFIG_SYSFS=n` stubs.

Source read size: 281 lines, 7410 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/vas-sysfs.c -->
