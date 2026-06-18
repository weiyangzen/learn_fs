# subset-b-001245 grouped research

Work item: `subset-b-001245`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/edac.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/edac.c

Purpose: implements CXL EDAC/RAS feature registration for memory devices and regions. It exposes CXL 3.2 feature mailbox controls through EDAC device feature callbacks for patrol scrub, DDR5 ECS, sparing, and soft PPR. It also caches recent CXL media/DRAM error records so online repair operations can be limited to errors observed in the current boot.

Important APIs, types, and functions: exported entry points are `devm_cxl_memdev_edac_register()`, `devm_cxl_region_edac_register()`, `cxl_store_rec_gen_media()`, and `cxl_store_rec_dram()`. Patrol scrub state is `struct cxl_patrol_scrub_context`, with readable/writable payloads `cxl_scrub_rd_attrbs` and `cxl_scrub_wr_attrbs`. ECS state is `struct cxl_ecs_context` plus FRU attribute arrays. Repair paths use `struct cxl_mem_sparing_context`, `struct cxl_ppr_context`, `struct cxl_mem_repair_attrbs`, and `struct cxl_mem_err_rec`. Mailbox helpers are `cxl_get_feature()`, `cxl_set_feature()`, and local `cxl_perform_maintenance()`.

Control flow: memdev registration probes feature-table entries by UUID, skips unsupported or non-changeable features with `-EOPNOTSUPP`, fills an array of `struct edac_dev_feature`, and calls `edac_dev_register()`. Region registration currently exposes only patrol scrub and applies writes to every target memdev. Patrol scrub reads current values, enforces changeability and minimum cycle, then writes saved-across-reset feature data. ECS reads whole FRU arrays, edits one FRU config, and writes the full feature payload back. Repair setup reads capability/restriction flags, selects EDAC repair ops, and issues maintenance commands when userspace writes `EDAC_DO_MEM_REPAIR`.

State and persistence behavior: contexts are devm-owned by the memdev or region. Scrub writes use `CXL_SET_FEAT_FLAG_DATA_SAVED_ACROSS_RESET`, so device state may persist across reset. `cxlmd->scrub_cycle` and `scrub_region_id` track last Linux-programmed scrub rate and detect region/device override conflicts. Error record xarrays keep up to 200 general-media and DRAM records and expire records older than 10 days using device timestamps; they are freed by devm teardown.

Dependencies and integration points: depends on CXL feature enumeration from `features.c`, mailbox transport from `mbox.c`, event tracing and event records from `trace.h`, CXL region/DPA locks from `hdm.c`, and EDAC feature ops from `<linux/edac.h>`. Repair safety queries endpoint decoder commit state through `cxl_num_decoders_committed()` and DPA bounds through `cxl_resource_contains_addr()`.

Risks: repair is high-risk because it can target live memory. The code mitigates that with region and DPA read locks, online-memory checks, DPA range checks, and current-boot error-record matching when the device claims in-use repair is safe. ECS setters rewrite a full feature payload based on a fresh read; stale FRU count or malformed feature sizes could affect adjacent FRUs. The scrub region path partially applies settings if a later target mailbox write fails. Error-record xarrays are keyed by physical address/DPA and can overwrite records at the same key.

Test signals: exercise feature-present and feature-absent devices, non-changeable features, CAP_SYS_RAWIO enforcement for mutable sysfs knobs, region scrub across multiple targets, scrub min/max/cycle conversions, ECS threshold/mode/log-type validation, repair while endpoint decoders are committed and uncommitted, PPR record matching from general-media and DRAM events, and devm teardown freeing xarray contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/features.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/features.c

Purpose: provides common CXL feature discovery, get/set feature mailbox transfers, and fwctl-mediated userspace access to non-kernel-exclusive CXL features. It separates kernel-owned RAS features from vendor/user features and records feature metadata in `struct cxl_features_state`.

Important APIs, types, and functions: exported APIs are `to_cxlfs()`, `devm_cxl_setup_features()`, `cxl_get_feature()`, `cxl_set_feature()`, `cxl_feature_info()`, and `devm_cxl_setup_fwctl()`. The exclusive feature UUID table covers patrol scrub, ECS, soft/hard PPR, cacheline/row/bank/rank sparing. Internal discovery uses `cxl_get_supported_features_count()` and `get_supported_features()`. fwctl dispatch is handled by `cxlctl_fw_rpc()`, `cxlctl_validate_hw_command()`, `cxlctl_get_supported_features()`, `cxlctl_get_feature()`, and `cxlctl_set_feature()`.

Control flow: setup first checks mailbox feature capability, allocates a features state, asks the device for the supported feature count, then pages through `GET_SUPPORTED_FEATURES` responses according to mailbox payload size. It validates entry counts and output byte multiples before caching the table. `cxl_get_feature()` and `cxl_set_feature()` split large feature payloads across mailbox-sized transfers using offsets and CXL transfer flags. fwctl registration is skipped when every feature is kernel-exclusive; otherwise fwctl exposes read and validated write RPCs.

State and persistence behavior: `cxlds->cxlfs` points to devm-owned state until `free_cxlfs()` clears it and frees entries. `cxl_set_feature()` forcibly strips caller transfer bits and adds `CXL_SET_FEAT_FLAG_DATA_SAVED_ACROSS_RESET`, so callers that use it request persistent device feature updates. fwctl user contexts are stateless; open and close are no-ops.

Dependencies and integration points: depends on mailbox command execution from `mbox.c`, UAPI payload layouts from `<uapi/fwctl/cxl.h>`, fwctl core registration, and CXL feature UUID definitions. `edac.c` queries `cxl_feature_info()` and uses `cxl_get_feature()`/`cxl_set_feature()` for kernel-exclusive RAS controls. `mbox.c` sets `cxl_mbox->feat_cap` while walking the CEL.

Risks: feature discovery treats malformed output as allocation/discovery failure and may disable all feature support. Pointer arithmetic on `void *` payload buffers is compiler-extension dependent but common in kernel code. fwctl write validation must remain aligned with `effects` semantics; allowing immediate configuration/data/policy/log changes at too-low scope would expose unsafe hardware mutation. The supported-features fwctl response hides mutability of exclusive features but still reports their existence.

Test signals: validate devices with zero, read-only, and read-write feature capabilities; feature lists larger than mailbox payload; malformed `num_entries` or odd byte counts; get/set feature payloads that require multi-packet transfer; fwctl rejection of exclusive UUIDs, background effects, reserved effects, and insufficient scopes; teardown clearing `cxlds->cxlfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/hdm.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/hdm.c

Purpose: implements core Host-managed Device Memory decoder and DPA resource management for CXL ports and endpoints. It maps HDM decoder registers, enumerates decoder devices, supports DVSEC range fallback, programs decoder commits/resets, and tracks endpoint DPA allocations across RAM/PMEM partitions.

Important APIs, types, and functions: global `struct cxl_rwsem cxl_rwsem` provides `region` and `dpa` locks. Exported functions include `cxl_dpa_debug()`, `cxl_dpa_setup()`, `devm_cxl_dpa_reserve()`, `cxl_dpa_size()`, `cxl_dpa_resource_start()`, `cxl_resource_contains_addr()`, `cxl_dpa_free()`, `cxl_dpa_set_part()`, `cxl_dpa_alloc()`, `cxl_port_commit_reap()`, `devm_cxl_switch_port_decoders_setup()`, and `devm_cxl_endpoint_decoders_setup()`. Key internals include `devm_cxl_setup_hdm()`, `init_hdm_decoder()`, `cxl_decoder_commit()`, and `cxl_decoder_reset()`.

Control flow: setup maps HDM component registers when present, parses decoder count/interleave/target capabilities, or falls back to DVSEC range emulation for endpoints. Enumeration allocates endpoint or switch decoder devices, initializes each from hardware registers or DVSEC cached ranges, reserves DPA for committed endpoint decoders, and adds devices to the CXL bus. Region construction later allocates DPA with `cxl_dpa_alloc()`, commits decoders in hardware instance order, and resets/reaps them in reverse order.

State and persistence behavior: DPA state is held in `cxlds->dpa_res` and child partition resources. Endpoint decoders hold `dpa_res`, `skip`, `part`, state, and enable/lock flags. `port->hdm_end` tracks DPA reservation order, while `port->commit_end` tracks committed decoder order. Hardware decoder register programming persists until reset or firmware/device state changes; Linux resource reservations are devm-managed and released on port teardown.

Dependencies and integration points: depends on CXL bus/device helpers, PCI/DVSEC decode information from `pci.c`, mailbox sanitize state from `mbox.c`/`memdev.c`, and region code that consumes decoder commit/reset hooks. Debug output integrates with seq_file. EDAC and memdev poison paths use the same DPA and region locks.

Risks: DPA allocation is order-sensitive and uses `skip` reservations to account for sacrificed lower-partition capacity; incorrect skip release can corrupt the resource tree. Decoder commit must be in hardware order and waits only 20 ms for committed/error status. DVSEC fallback locks emulated decoders because runtime range-register updates are not supported. Resetting a decoder moves endpoint state to manual, so userspace must rebuild configuration.

Test signals: enumerate switch and endpoint ports with real HDM registers, no HDM single-dport passthrough, DVSEC fallback, committed and uncommitted decoder registers, invalid interleave encodings, RAM/PMEM partition allocation with skip, out-of-order allocation/free/commit/reset rejection, sanitize-active commit rejection, and DPA resource debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/hdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/mbox.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/mbox.c

Purpose: implements the core CXL memory-device mailbox command layer, userspace ioctl command validation, command enumeration from the CEL, event-log retrieval/clearing, device identify and partition helpers, sanitize/erase orchestration, poison list retrieval, and mailbox state initialization.

Important APIs, types, and functions: exported APIs include `cxl_internal_send_cmd()`, `cxl_query_cmd()`, `cxl_send_cmd()`, `cxl_enumerate_cmds()`, `cxl_event_trace_record()`, `cxl_mem_get_event_records()`, `cxl_dev_state_identify()`, `cxl_mem_sanitize()`, `cxl_mem_dpa_fetch()`, `cxl_get_dirty_count()`, `cxl_arm_dirty_shutdown()`, `cxl_set_timestamp()`, `cxl_mem_get_poison()`, `cxl_poison_state_init()`, `cxl_mailbox_init()`, `cxl_memdev_state_create()`, and `cxl_mbox_init()`. Important state lives in `struct cxl_mailbox`, `struct cxl_memdev_state`, security/poison substructures, and the static `cxl_mem_commands[]` UAPI command table.

Control flow: internal callers initialize `struct cxl_mbox_cmd` and call `cxl_internal_send_cmd()`, which checks payload limits, invokes the transport callback, translates device return codes, and enforces minimum output sizes. Userspace ioctls are copied in, converted to known or raw mailbox commands, checked against enabled/exclusive bitmaps, payload-size contracts, lockdown/raw-command policy, and opcode-specific payload restrictions, then dispatched and copied out. Command enumeration reads Supported Logs, fetches the CEL, walks opcodes, enables supported UAPI commands, records security/poison feature bits, and derives read/write feature capability.

State and persistence behavior: enabled and exclusive command bitmaps persist in the mailbox for the memdev lifetime. Identify populates total/volatile/persistent capacity, partition alignment, label size, firmware revision, and poison limits. Event log retrieval uses a per-device event buffer protected by `event.log_lock`, traces records, stores repair-relevant records through EDAC hooks, and clears records on the device. Sanitize/secure erase are background-capable device operations but are only started when no endpoint decoders are committed. `raw_allow_all` is a debugfs boolean under the CXL mbox directory.

Dependencies and integration points: depends on PCI CXL transport callbacks, security lockdown, debugfs, tracepoints, EDAC record storage, MCE notifier creation, DPA/region translation, and CXL UAPI definitions. `features.c` and `edac.c` build on `cxl_internal_send_cmd()`. `memdev.c` exposes `cxl_query_cmd()` and `cxl_send_cmd()` through `/dev/cxl/memX`.

Risks: raw mailbox access is intentionally restricted because opcodes can change device memory maps, labels, poison state, or security state. User payload checks are command-specific and must be extended with new unsafe opcodes. Event clearing must batch handles according to mailbox payload size, or stale events may loop. `cxl_mem_get_poison()` protects against endless MORE flags by stopping at `max_errors`.

Test signals: CEL discovery with missing/bogus CEL and forced-enable commands, raw command allow/deny paths under lockdown and debugfs override, exclusive command blocking, variable output truncation, event get/clear loops including overflow, sanitize rejection while decoders are committed, identify with media not ready, partition fetch for aligned and unaligned partitioning, and poison list pagination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/mce.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/mce.c

Purpose: registers a CXL-specific machine-check decode notifier that handles cacheline aliasing for CXL memory. When an MCE reports a usable system physical address, the notifier finds the CXL cache alias and offlines that aliased page in addition to the standard MCE handler's action on the original page.

Important APIs, types, and functions: `devm_cxl_register_mce_notifier()` is the exported setup API. It fills a caller-provided `struct notifier_block` with `cxl_handle_mce()` and priority `MCE_PRIO_UC`, registers it with `mce_register_decode_chain()`, and adds a devm unregister action. `cxl_handle_mce()` uses `struct cxl_memdev_state`, `struct cxl_memdev`, endpoint `struct cxl_port`, and `struct mce`.

Control flow: on notification, the handler rejects null or unusable MCE records, missing endpoints, invalid PFNs, and addresses without a CXL SPA cache alias. For a valid alias, it computes the alias PFN, logs an emergency message, calls `memory_failure(pfn, 0)`, and if offlining succeeds marks the PFN no-speculative with `set_mce_nospec()`. It returns `NOTIFY_OK` only when it handled an alias.

State and persistence behavior: the notifier is devm-lifetime state embedded in `struct cxl_memdev_state`. Runtime effects are persistent at memory-management level: `memory_failure()` can offline the aliased page, and `set_mce_nospec()` updates CPU/kernel state to prevent future speculative access. The file does not maintain its own storage.

Dependencies and integration points: depends on x86 MCE decode chains, memory-failure handling, `pfn_valid()`, CXL endpoint alias lookup via `cxl_port_get_spa_cache_alias()`, and memdev state creation in `mbox.c`. The companion header provides a stub when `CONFIG_CXL_MCE` is disabled.

Risks: incorrect alias lookup would offline the wrong page or miss a poisoned alias. The handler assumes `cxlmd->endpoint` remains usable during notification; teardown ordering depends on notifier devm lifetime. This is architecture/config dependent and silently absent when `CONFIG_CXL_MCE` is disabled.

Test signals: build with and without `CONFIG_CXL_MCE`, inject or simulate MCE records with unusable addresses, non-CXL addresses, invalid PFNs, and valid aliased SPAs, verify `memory_failure()` and `set_mce_nospec()` calls, and exercise notifier unregister during memdev teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/mce.h -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/mce.h

Purpose: declares the CXL MCE notifier registration contract and provides a configuration stub when CXL MCE handling is not compiled. It lets mailbox/memdev setup code call one API independent of `CONFIG_CXL_MCE`.

Important APIs, types, and functions: the only API is `devm_cxl_register_mce_notifier(struct device *dev, struct notifier_block *mce_notifier)`. With `CONFIG_CXL_MCE`, the implementation lives in `mce.c`. Without it, the inline stub returns `-EOPNOTSUPP`.

Control flow: including code can call the helper during device-state creation. A real build registers a notifier and attaches a devm cleanup action; a disabled build receives `-EOPNOTSUPP`, allowing callers to warn or continue without alias-specific MCE handling.

State and persistence behavior: the header has no state. It defines the lifetime expectation that the notifier block is owned by the caller and remains valid until devm teardown.

Dependencies and integration points: depends on `<linux/notifier.h>`. It is included by `mbox.c`, which stores the notifier block in `struct cxl_memdev_state` and treats `-EOPNOTSUPP` as non-fatal.

Risks: callers must not treat every nonzero return as fatal without preserving the `-EOPNOTSUPP` distinction, or CXL memdev creation would fail on builds that intentionally omit MCE support. The header does not validate notifier storage lifetime; that remains a caller responsibility.

Test signals: compile both config variants, verify the disabled stub is inlined and returns `-EOPNOTSUPP`, and verify enabled builds link against `mce.c` and register/unregister through devm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/mce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/memdev.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/memdev.c

Purpose: implements the CXL memory device character device and sysfs surface. It creates `/dev/cxl/memX`, exposes identity/capacity/security/poison/firmware-upload operations, mediates mailbox ioctls, manages exclusive command state, and binds `struct cxl_memdev` lifetime to the CXL bus.

Important APIs, types, and functions: exported APIs include `cxl_memdev_has_poison_cmd()`, `cxl_trigger_poison_list()`, `cxl_inject_poison_locked()`, `cxl_inject_poison()`, `cxl_clear_poison_locked()`, `cxl_clear_poison()`, `cxl_memdev_update_perf()`, `is_cxl_memdev()`, `set_exclusive_cxl_commands()`, `clear_exclusive_cxl_commands()`, `_devm_cxl_dev_state_create()`, `devm_cxl_setup_fw_upload()`, `__devm_cxl_add_memdev()`, `devm_cxl_sanitize_setup_notifier()`, `cxl_memdev_init()`, and `cxl_memdev_exit()`. The central objects are `struct cxl_memdev`, `struct cxl_dev_state`, `struct cxl_memdev_state`, `cdev`, IDA IDs, and the `cxl_memdev_rwsem`.

Control flow: memdev allocation reserves an ID, initializes a bus device and cdev, and publishes it with `cdev_device_add()`. Open pins the device; ioctl takes `cxl_memdev_rwsem`, verifies live classmem state, then delegates query/send commands to `mbox.c`. Sysfs attributes report firmware, payload size, label storage, serial, NUMA node, RAM/PMEM size and QoS, and security state. Poison operations take region and DPA locks, validate DPA range/alignment, issue inject/clear mailbox commands, and trace changes. Firmware upload slices images into mailbox-sized `TRANSFER_FW` commands and activates the next slot.

State and persistence behavior: `cxlmd->cxlds` links the character device to live device state and is nulled during shutdown to block new ioctls. Exclusive command bits persist in the mailbox and are updated under write lock to flush in-flight ioctls. Security sysfs can start sanitize/erase device operations, and firmware upload can persistently activate a new firmware slot. Poison inject/clear mutates device media state and emits trace records. IDA IDs and chrdev major are process lifetime kernel state.

Dependencies and integration points: depends on mailbox APIs, CXL DPA/region helpers, firmware upload core, PCI helpers for parent devices, sysfs/kernfs, CXL bus registration, and tracepoints. PMEM, EDAC, feature-fwctl, and endpoint port setup all consume `struct cxl_memdev` links created here.

Risks: ioctl lifetime relies on `cxl_memdev_rwsem` and shutdown ordering. Firmware transfer must honor 128-byte alignment and mailbox payload limits; partial writes or cancel races need correct abort handling. Debugfs poison injection is compiled away unless `CONFIG_DEBUG_FS` is enabled, but when active it can target mapped regions and logs a warning only once. Security operations must remain blocked while decoders are committed.

Test signals: create/remove many memdevs, open/ioctl during unregister, sysfs visibility with and without NUMA, RAM/PMEM/QoS updates, sanitize/erase visibility and state polling teardown, poison list/inject/clear for aligned and invalid DPAs, firmware upload one-shot and multi-slice images with cancel, exclusive command blocking, and chrdev major init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/memdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/pci.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/pci.c

Purpose: provides PCIe-facing helpers for CXL core. It discovers dports, waits for media readiness, decodes and validates DVSEC range registers, enables MEM/HDM decode, reads CDAT through DOE, calculates link latency/bandwidth, detects decoder reset, maps register blocks, configures GPF timeouts, and counts possible downstream ports.

Important APIs, types, and functions: exported functions include `devm_cxl_add_dport_by_dev()`, `cxl_await_media_ready()`, `cxl_dvsec_rr_decode()`, `cxl_hdm_decode_init()`, `read_cdat_data()`, `cxl_pci_get_latency()`, `cxl_endpoint_decoder_reset_detected()`, `cxl_pci_setup_regs()`, `cxl_pci_get_bandwidth()`, `cxl_gpf_get_dvsec()`, `cxl_gpf_port_setup()`, and `cxl_port_get_possible_dports()`. Internal helpers include `pci_get_port_num()`, `cxl_dvsec_mem_range_valid()`, `cxl_dvsec_mem_range_active()`, `devm_cxl_enable_mem()`, `devm_cxl_enable_hdm()`, and CDAT DOE transfer/checksum helpers.

Control flow: endpoint setup first reads DVSEC capabilities and range registers, waits for MEM INFO VALID and MEM ACTIVE, and caches ranges. HDM init enables MEM directly if HDM is already enabled or DVSEC emulation is active, enables HDM if DVSEC memory was disabled, or validates active DVSEC ranges against locked root decoder CFMWS windows before allowing endpoint decoder use. CDAT reading locates a DOE mailbox, reads table length, streams entries by handle, restores overwritten DWORDs, trims malformed trailing data, validates checksum, and attaches the table to the port.

State and persistence behavior: `media_ready_timeout` is a module parameter. MEM Enable and HDM global enable bits are hardware state with devm cleanup actions to clear them when Linux enabled them. `port->cdat_available`, `port->cdat.table`, and `port->cdat.length` persist for the port lifetime. GPF DVSEC timeout programming writes PCI config-space timeout fields and caches `dport->gpf_dvsec`.

Dependencies and integration points: depends on PCI/PCIe config access, DOE mailbox APIs, AER/CXL PCI headers, CXL register mapping, root decoder topology, HDM setup in `hdm.c`, and performance coordinate consumers in memdev sysfs. Restricted CXL host support uses RCRB component register discovery and dport link capability mapping.

Risks: media-ready polling can delay probe up to the module timeout per range. DVSEC ranges are trusted only if platform root windows cover them; mistakes can expose decode outside firmware-advertised CXL ranges. CDAT parsing is sensitive to malformed DOE lengths and checksum failure. MEM/HDM enable cleanup must not disable firmware-owned decode; the code only registers cleanup when it changed the bit.

Test signals: devices with absent/invalid DVSEC, zero or more than two legacy HDM ranges, media valid/active timeout, HDM already enabled, HDM disabled with and without DVSEC ranges, DVSEC range denied by root decoder, DOE absent and malformed CDAT, bad CDAT checksum, restricted CXL register setup, GPF DVSEC absent/present, and link bandwidth/latency calculations across speeds and widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/pmem.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/pmem.c

Purpose: implements CXL persistent-memory bridge devices that connect the CXL topology to the LIBNVDIMM subsystem. It creates root-level `cxl_nvdimm_bridge` devices for persistent-memory capable CXL roots and per-memdev `cxl_nvdimm` devices that host LIBNVDIMM dimm objects.

Important APIs, types, and functions: exported APIs are `to_cxl_nvdimm_bridge()`, `cxl_find_nvdimm_bridge()`, `__devm_cxl_add_nvdimm_bridge()`, `is_cxl_nvdimm()`, `to_cxl_nvdimm()`, and `devm_cxl_add_nvdimm()`. Device types are `cxl_nvdimm_bridge_type` and `cxl_nvdimm_type`. Allocation helpers are `cxl_nvdimm_bridge_alloc()` and `cxl_nvdimm_alloc()`, with cleanup through `unregister_nvb()` and `cxlmd_release_nvdimm()`.

Control flow: bridge creation is skipped when `CONFIG_CXL_PMEM` is disabled, otherwise it allocates an IDA ID, initializes a CXL bus device below the root port, adds it, verifies that a driver attached, and registers devm cleanup. `cxl_find_nvdimm_bridge()` walks from any descendant port to the root and finds a child with bridge device type. Per-memdev addition locates the bridge, locks the root uport and bridge device to ensure `nvdimm_bus` is registered, allocates a `cxl_nvdimm`, names it `pmem%d`, adds it, and registers cleanup.

State and persistence behavior: bridge IDs are IDA-managed until release. `cxl_nvdimm_bridge` stores its root port and `nvdimm_bus` pointer as bridge-driver state. `cxl_nvdimm` stores a backpointer to `cxlmd`, and `cxlmd` stores `cxl_nvd` and `cxl_nvb` while the bridge is active. The NVDIMM device ID string is derived from the CXL serial and persists for device lifetime, not across hardware identity changes.

Dependencies and integration points: depends on CXL bus type and base attributes, root lookup via `find_cxl_root()`, memdev objects from `memdev.c`, and the external `cxl_pmem`/LIBNVDIMM driver that binds bridge and dimm devices. It provides the object layer used by label-storage and namespace operations outside this file.

Risks: bridge creation intentionally fails if no bridge driver attaches; ordering with `cxl_acpi_probe()` is protected by locks in `devm_cxl_add_nvdimm()`. Reference handling is delicate because memdevs hold a bridge reference until `cxlmd_release_nvdimm()`. Error paths must clear `cxlmd->cxl_nvb` and `cxlmd->cxl_nvd` to avoid dangling links.

Test signals: build with `CONFIG_CXL_PMEM` enabled and disabled, root bridge driver attach failure, finding a bridge from nested ports, per-memdev add before and after `nvdimm_bus` registration, add failure after name/device_add, teardown ordering of memdev and bridge, and stable dimm ID based on serial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/pmu.c -->
## sources/distributed-fs/ceph-client/drivers/cxl/core/pmu.c

Purpose: creates CXL PMU bus devices from discovered PMU register blocks. It is small device-model glue that publishes a PMU child device with association ID, index, type, and register base for a PMU driver to bind.

Important APIs, types, and functions: exported API is `devm_cxl_pmu_add()`. The device type is `cxl_pmu_type`, with release callback `cxl_pmu_release()`. `remove_dev()` unregisters the device through devm cleanup. The allocated object is `struct cxl_pmu`, populated from `struct cxl_pmu_regs`, association ID, index, and `enum cxl_pmu_type`.

Control flow: `devm_cxl_pmu_add()` allocates a zeroed PMU object, copies identifying fields and `regs->pmu` base, initializes a CXL bus device below the parent, marks PM not required, names memdev PMUs as `pmu_mem%d.%d`, adds the device, then registers a devm action to unregister it with the parent. Errors before `device_add()` drop the device reference.

State and persistence behavior: PMU state lives in the child device for its lifetime. The register base is an MMIO pointer discovered elsewhere and only stored here. There is no filesystem persistence or runtime counter management in this file; actual PMU operation belongs to the binding driver.

Dependencies and integration points: depends on CXL bus type, CXL PMU type definitions from `<pmu.h>`/`<cxlmem.h>`, and register discovery code that supplies `struct cxl_pmu_regs`. The device name and type are the handoff contract to the PMU driver.

Risks: the switch currently handles `CXL_PMU_MEMDEV`; adding new PMU types without a naming case would leave `rc` undefined or fail unpredictably. The file assumes the parent owns the register mapping lifetime for `pmu->base`. Because cleanup is devm-attached to the parent, parent teardown must outlive any PMU driver access.

Test signals: create memdev PMUs with multiple association IDs and indices, verify device names and CXL bus type, bind/unbind the PMU driver, parent teardown unregisters children, allocation/name/device_add failure paths release memory, and compile coverage when adding new `enum cxl_pmu_type` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/pmu.c -->
