# Research: subset-b-004990

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/tcp.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/tcp.c

## Purpose
Implements the Linux NVMe over Fabrics TCP host transport. It registers the `tcp` fabrics transport, creates and reconnects controllers, maps blk-mq requests to NVMe/TCP command and data PDUs, owns socket callback integration, supports header/data digests, and optionally negotiates TLS PSKs before the NVMe/TCP initial connection exchange.

## Important APIs, Types, And Functions
Core state lives in `struct nvme_tcp_ctrl`, `struct nvme_tcp_queue`, and `struct nvme_tcp_request`. The important blk-mq hooks are `nvme_tcp_queue_rq()`, `nvme_tcp_commit_rqs()`, `nvme_tcp_timeout()`, `nvme_tcp_poll()`, `nvme_tcp_init_request()`, and hctx init functions. Transport lifecycle is driven by `nvme_tcp_create_ctrl()`, `nvme_tcp_setup_ctrl()`, `nvme_tcp_configure_admin_queue()`, `nvme_tcp_configure_io_queues()`, `nvme_tcp_start_queue()`, teardown helpers, reset/reconnect work, and `nvme_tcp_transport`. Send and receive state machines are centered on `nvme_tcp_try_send()`, `nvme_tcp_try_recv()`, `nvme_tcp_recv_skb()`, `nvme_tcp_recv_pdu()`, `nvme_tcp_recv_data()`, and digest helpers.

## Control Flow
Controller creation parses fabrics options, prevents duplicate connects unless allowed, allocates queues, initializes the common NVMe controller, then configures the admin queue and I/O queues. Queue allocation creates a kernel TCP socket, binds source address/interface when requested, sets TCP options, optionally starts TLS, performs the NVMe/TCP ICReq/ICResp negotiation, and later installs socket callbacks before sending fabrics connect commands. Requests enter from blk-mq, are encoded as command PDUs with transport SGL descriptors, queued through an llist/list pair, and drained by `nvme_tcp_io_work()`. Writes may send inline data, R2T-driven H2C data PDUs, and optional data digests. Reads parse C2H data PDUs into request iterators and complete either via response CQEs or DATA_SUCCESS. Socket state changes and protocol errors trigger reset/reconnect recovery.

## State And Persistence
No media state is persisted here; the file maintains live transport state only. Controller state includes queue arrays, tag sets, address options, reconnect counters, TLS PSK id, and work items. Queue state tracks socket callbacks, CPU affinity, flags for allocated/live/polling, PDU receive offsets, digest CRCs, pending requests, and the current send request. Request state tracks PDU bytes sent, data iterator position, R2T offsets, NVMe status, and digest bytes. Across reconnects, queues and tag sets are torn down and rebuilt while the common NVMe controller state machine moves through CONNECTING, LIVE, RESETTING, and deletion states.

## Dependencies And Integration Points
Integrates with NVMe core/fabrics helpers, blk-mq, kernel sockets/TCP, TLS handshake/keyring APIs, CRC32C, busy-poll, workqueues, memory reclaim controls, and transport registration. It relies on `nvme.h` and `fabrics.h` for command setup, controller state, fabrics connect/register operations, authentication, queue mapping, and namespace request completion.

## Risks
High-risk areas are socket lifetime and callback replacement, because error recovery, teardown, TLS, and reconnect can race with data-ready/write-space callbacks. Send/receive state must handle partial socket I/O, digest mismatch, R2T protocol violations, inline data completion, and CQE lookup failures without double completion. Memory reclaim windows use `memalloc_noreclaim_save()` and `memalloc_noio_save()` to avoid block I/O recursion during send and socket release. TLS secure concatenation has careful PSK revocation and admin-queue restart rules. Global queue CPU accounting is best effort and must be decremented exactly when queues stop.

## Test Signals
Useful coverage includes normal connect/disconnect, reconnect after TCP close, controller reset, duplicate connect rejection, IPv4/IPv6 source binding, host interface binding, header/data digest success and failure, TLS static PSK and secure concatenation, R2T writes larger than inline capsule size, read DATA_SUCCESS completion, blk-mq timeout handling, busy-poll queues, and module unload with live controllers. Kernel signals include absence of request double-completion, lockdep splats on socket locks, stuck socket wmem warnings, and stale TLS key ids after reconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/trace.c

## Purpose
Provides formatter helpers behind the NVMe tracepoints declared in `trace.h`. It decodes admin, NVM, zoned, reservation, and fabrics command dwords into readable trace strings and exports the `nvme_sq` tracepoint symbol.

## Important APIs, Types, And Functions
Public helpers are `nvme_trace_parse_admin_cmd()`, `nvme_trace_parse_nvm_cmd()`, `nvme_trace_parse_fabrics_cmd()`, and `nvme_trace_disk_name()`. Opcode-specific decoders include queue create/delete, identify, get/set features, format NVM, get LBA status, read/write/write-zeroes/zone-append, DSM, zone management send/receive, reservation operations, and fabrics property/connect/auth commands. All helpers write into `struct trace_seq` and use unaligned little-endian accessors for command bytes.

## Control Flow
Tracepoint print code passes opcode, queue id, fabrics command type, and command dwords into the parse helpers. The helpers switch on the opcode or fabrics type, decode recognized fields, terminate the trace sequence string, and fall back to raw hex dumps for unsupported commands. Disk names are conditionally prefixed only when a request has a backing gendisk.

## State And Persistence
The file is stateless. It uses static string tables for zone and reservation action names and writes transient formatted data into trace sequence buffers supplied by ftrace.

## Dependencies And Integration Points
Depends on Linux trace infrastructure, `linux/unaligned.h`, NVMe opcode definitions, and the `TRACE_EVENT` declarations in `trace.h`. It is part of the host trace ABI and is consumed by ftrace/perf tooling when NVMe trace events are enabled.

## Risks
Formatter bugs can mislead debugging without affecting I/O behavior. Field offsets must match NVMe command layouts, especially packed cdw10-cdw15 interpretations for zone, reservation, and fabrics commands. Unsupported new opcodes fall back to raw bytes, so observability can lag protocol support.

## Test Signals
Enable `nvme_setup_cmd` traces for representative admin, I/O, fabrics, zoned, and reservation commands and verify decoded fields against submitted commands. Build testing should catch missing opcode definitions, while trace output should not contain unterminated strings or incorrect endian conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.h -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/trace.h

## Purpose
Declares the NVMe host tracepoint events and connects their print formatting to helper functions in `trace.c`. It captures command submission, request completion, asynchronous events, and submission queue head/tail movement.

## Important APIs, Types, And Functions
Trace events are `nvme_setup_cmd`, `nvme_complete_rq`, `nvme_async_event`, and `nvme_sq`. Helper declarations include `nvme_trace_parse_admin_cmd()`, `nvme_trace_parse_nvm_cmd()`, `nvme_trace_parse_fabrics_cmd()`, and `nvme_trace_disk_name()`. Macros `parse_nvme_cmd()` and `__print_disk_name()` route trace printing based on queue id and opcode. `__assign_disk_name()` copies `gendisk` names into fixed trace entries.

## Control Flow
At command setup, the tracepoint snapshots controller id, queue id, opcode, flags, command id, namespace id, metadata presence, fabrics type, disk name, and cdw10-cdw15 bytes. Completion snapshots result, retries, flags, and status from `nvme_request`. AEN traces capture the result class. SQ traces record queue head and tail. `trace/define_trace.h` materializes the events when included by the trace translation unit.

## State And Persistence
Trace entries are transient ring-buffer records. The header defines the shape of that trace ABI, including fixed field names and string formatting, but does not persist controller state.

## Dependencies And Integration Points
Integrates with Linux tracepoints, block requests, `struct nvme_request`, `struct nvme_command`, `struct nvme_ctrl`, and generated opcode name helpers. It must be included with the correct `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so kernel trace generation can find it.

## Risks
Trace ABI changes can break user-space scripts that parse event fields. The print path must not dereference invalid request or disk data; it snapshots disk names during fast assignment. The parser dispatch assumes queue id zero is admin and nonzero is NVM unless the opcode is fabrics.

## Test Signals
Build with tracing enabled, check generated trace events under tracing events, enable each event, and submit admin, I/O, fabrics, and AEN paths. Validate disk-name handling for namespace and admin requests and confirm `nvme_sq` remains exportable to transport modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/zns.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/zns.c

## Purpose
Implements NVMe Zoned Namespace host support: discovers ZNS limits, configures block queue zoned limits, reports zones to the block layer, and builds zone management send commands.

## Important APIs, Types, And Functions
Key exported helpers are `nvme_query_zone_info()`, `nvme_update_zone_info()`, `nvme_ns_report_zones()`, and `nvme_setup_zone_mgmt_send()`. Internal helpers include `nvme_set_max_append()`, `nvme_zns_alloc_report_buffer()`, and `nvme_zone_parse_entry()`. It works with `struct nvme_zone_info`, ZNS identify data, `struct queue_limits`, and block-layer `struct blk_report_zones_args`.

## Control Flow
Namespace scan calls `nvme_query_zone_info()`, which checks command effects for zone append support, lazily identifies controller ZNS append size, identifies namespace ZNS data, rejects unsupported zone operation characteristics, validates power-of-two zone size, and records max open/active zones. `nvme_update_zone_info()` transfers that data to queue limits. Zone reporting allocates a bounded vmalloc report buffer, issues repeated zone management receive commands starting at zone-aligned sectors, converts each NVMe descriptor to `struct blk_zone`, and advances until the requested count or disk capacity is reached. Zone reset/open/close/etc. requests are encoded by `nvme_setup_zone_mgmt_send()`.

## State And Persistence
Persistent runtime state is stored in `ctrl->max_zone_append`, `ns->head->zsze`, queue limits, and the namespace force-read-only flag. Report buffers and identify data are temporary allocations.

## Dependencies And Integration Points
Depends on NVMe admin identify and sync command submission, NVMe command effects logs, block zoned queue limits, gendisk zone reporting, and helpers converting between LBAs and sectors. It gates writable zoned namespace behavior on zone append command support.

## Risks
Incorrect zone-size validation or sector/LBA conversion would corrupt block-layer zone geometry. Devices without zone append are forced read-only, so command effects log accuracy matters. Report buffer sizing must stay within queue segment and hardware-sector limits. NVMe positive status codes from report commands are normalized to `-EIO`.

## Test Signals
Test ZNS namespaces with and without zone append, invalid non-power-of-two zone sizes, max append limits with and without `zasl`, report-zones over partial and full disk ranges, full-zone write pointer handling, and all block zone management request mappings. Compare `blkzone report` output with raw NVMe zone reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/zns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvmem/Kconfig

## Purpose
Defines the Kconfig menu for the Linux NVMEM framework, optional sysfs interface, layout parsers, and many platform-specific NVMEM provider drivers.

## Important APIs, Types, And Functions
The top-level symbols are `NVMEM` and `NVMEM_SYSFS`, with `NVMEM` implying `NVMEM_LAYOUTS`. This file sources `drivers/nvmem/layouts/Kconfig` and defines provider symbols such as `NVMEM_AN8855_EFUSE`, `NVMEM_APPLE_EFUSES`, `NVMEM_APPLE_SPMI`, `NVMEM_BCM_OCOTP`, `NVMEM_BRCM_NVRAM`, i.MX variants, Ingenic, LAN9662, Layerscape, Qualcomm, Rockchip, STM32, U-Boot environment, and others.

## Control Flow
Kconfig evaluation exposes provider choices only when `NVMEM` is enabled. Each provider constrains itself with architecture, bus, firmware, OF, MFD, or `COMPILE_TEST` dependencies and selects helper libraries such as regmap, CRC, SCM, or generic network utilities when needed.

## State And Persistence
No runtime state. The file controls compile-time inclusion, module availability, and default selections such as Broadcom iProc OCOTP defaulting on its architecture and STM32 OP-TEE helper being enabled when its parent and OP-TEE are enabled.

## Dependencies And Integration Points
Integrates the NVMEM core with platform buses, SoC architecture symbols, MTD, OP-TEE, SPMI, regmap, CRC, and layout parsers. Module names documented in help text map to Makefile objects.

## Risks
Missing dependencies can produce build failures on allyesconfig or unusable drivers on real systems. Overly broad defaults can expose unsafe write-capable OTP drivers; overly narrow dependencies can hide valid compile-test coverage. Layout symbols must remain aligned with `layouts/Makefile`.

## Test Signals
Run Kconfig coverage for defconfig, allmodconfig, and COMPILE_TEST architectures. Check that each selected symbol has a matching object in `drivers/nvmem/Makefile`, expected helper selections, and coherent module names in help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvmem/Makefile

## Purpose
Maps NVMEM Kconfig symbols to built-in or module objects and aggregates multi-object modules for the framework core, layout bus, and individual provider drivers.

## Important APIs, Types, And Functions
Build targets include `nvmem_core.o` from `core.o`, `nvmem_layouts.o` from `layouts.o`, unconditional descent into `layouts/`, and per-provider module aliases such as `nvmem-an8855-efuse.o`, `nvmem-apple-efuses.o`, `apple_nvmem_spmi.o`, `nvmem-bcm-ocotp.o`, `nvmem_brcm_nvram.o`, i.MX modules, and many other SoC drivers.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` lines and then uses `foo-y := file.o` assignments to assemble module names from source files. Layout subdirectory objects are built only when their own Kconfig symbols select them.

## State And Persistence
No runtime state. The file defines build artifacts and therefore module names and object inclusion.

## Dependencies And Integration Points
Must stay synchronized with `drivers/nvmem/Kconfig`, `drivers/nvmem/layouts/Makefile`, and source filenames. It also reflects naming conventions used by module loading and distribution packaging.

## Risks
Mismatched object names break builds or produce unexpected module filenames. Because several object names use hyphen/underscore variants, renames are easy to get wrong. Unconditional `obj-y += layouts/` is safe only because the subdirectory Makefile is symbol-gated.

## Test Signals
Build all listed NVMEM symbols as modules and built-ins, verify `modinfo` names for selected providers, and run `make W=1` to catch stale or missing source mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/an8855-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/an8855-efuse.c

## Purpose
Exposes Airoha AN8855 switch eFuse words as a read-only NVMEM provider backed by the parent MFD regmap.

## Important APIs, Types, And Functions
`an8855_efuse_read()` performs `regmap_bulk_read()` from `AN8855_EFUSE_DATA0 + offset`. `an8855_efuse_probe()` obtains the parent regmap, fills an `nvmem_config` with 50 32-bit cells, 32-bit stride/word size, and registers through `devm_nvmem_register()`.

## Control Flow
The platform driver matches `airoha,an8855-efuse`. Probe fetches the parent regmap, attaches it as provider private data, and registers the NVMEM device. Reads are direct bulk register reads in word units.

## State And Persistence
The only driver state is the regmap pointer stored as `config.priv`. Fuse contents are hardware-persistent and read-only from this provider.

## Dependencies And Integration Points
Depends on a parent device exposing a regmap, platform/OF matching, and the NVMEM provider core. Consumers access calibration cells via standard NVMEM APIs or fixed DT cells.

## Risks
Offsets are treated as byte offsets while bulk count is `bytes / sizeof(u32)`, so NVMEM core alignment via 32-bit stride and word size is important. Missing parent regmap returns `-ENOENT`.

## Test Signals
Probe under an AN8855 MFD parent, read aligned 32-bit cells, verify sysfs or NVMEM consumer output matches hardware documentation, and test failure when no parent regmap exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/an8855-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-efuses.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/apple-efuses.c

## Purpose
Registers memory-mapped Apple SoC eFuses as a root-only, read-only NVMEM provider with legacy fixed OF cell support.

## Important APIs, Types, And Functions
`struct apple_efuses_priv` stores the ioremapped fuse base. `apple_efuses_read()` reads 32-bit words with `readl_relaxed()`. `apple_efuses_probe()` maps the platform resource, sizes the provider from the resource, and registers `apple_efuses_nvmem` with automatic ids.

## Control Flow
OF match on `apple,efuses` triggers probe. Probe allocates private state, maps resource 0, fills config, and calls `devm_nvmem_register()`. Read callbacks iterate word-by-word from the requested offset.

## State And Persistence
Only the MMIO base is kept in driver memory. Fuse data persists in hardware and the provider is read-only and root-only.

## Dependencies And Integration Points
Depends on platform resources, OF match, MMIO accessors, and NVMEM fixed OF cell parsing. Consumers such as PHY or board drivers can retrieve calibration data through NVMEM cells.

## Risks
The read path ignores trailing byte counts smaller than 32 bits, relying on core word-size alignment. Root-only access is important because fuses may contain sensitive identifiers. Relaxed reads assume no special sequencing is needed.

## Test Signals
Boot on matching Apple SoC DT, verify resource size maps to NVMEM size, read fixed cells, confirm unprivileged sysfs restrictions, and check no partial-word reads are attempted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-efuses.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-spmi-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/apple-spmi-nvmem.c

## Purpose
Exposes Apple SPMI PMIC address space as a byte-addressable NVMEM provider using a regmap over SPMI extended transfers.

## Important APIs, Types, And Functions
`apple_spmi_regmap_config` configures 16-bit registers and 8-bit values. `apple_spmi_nvmem_probe()` creates an SPMI regmap and registers an NVMEM device named `spmi_nvmem` with `regmap_bulk_read` and `regmap_bulk_write` as callbacks.

## Control Flow
The SPMI driver matches `apple,spmi-nvmem`. Probe initializes `devm_regmap_init_spmi_ext()`, stores the regmap as private data, and registers a 0xffff-byte, byte-stride NVMEM provider.

## State And Persistence
Runtime state is the regmap. Backing storage is SPMI-attached PMIC NVMEM or register-backed persistent settings, writable through the NVMEM core.

## Dependencies And Integration Points
Depends on SPMI, `REGMAP_SPMI`, the NVMEM provider framework, and Apple PMIC DT bindings. It allows cell consumers to access power or RTC-related persistent settings.

## Risks
The callbacks are cast to NVMEM function types, so their signatures must remain compatible. Exposing write access across the full 16-bit address range can be risky if bindings do not constrain cells. Regmap/SPMI errors propagate directly to consumers.

## Test Signals
Probe on Apple SPMI PMICs, read and write known safe cells, confirm regmap transaction sizes, and test invalid SPMI transfers. DT cell coverage should constrain consumers to documented offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-spmi-nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/bcm-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/bcm-ocotp.c

## Purpose
Implements a Broadcom on-chip OTP controller provider with read and write support for v1 and v2 row layouts, using command/status MMIO sequencing.

## Important APIs, Types, And Functions
`struct otpc_map` describes row width and data register offsets; `struct otpc_priv` stores device, base, map, and config. Helpers program command, address, start bit, and data registers. `poll_cpu_status()`, `enable_ocotp_program()`, and `disable_ocotp_program()` manage command completion and write enable sequence. `bcm_otpc_read()` and `bcm_otpc_write()` are NVMEM callbacks; `bcm_otpc_probe()` maps registers, enables CPU mode, reads `brcm,ocotp-size`, selects v1/v2 geometry, and registers NVMEM.

## Control Flow
Probe gets match data from OF or ACPI, maps the controller, enables CPU access, resets start state, validates the size property, adjusts word size to 8 bytes for v2, and registers. Reads issue one READ command per row and copy row words from configured data registers. Writes first send the magic program-enable sequence, then issue PROGRAM commands row by row, and finally disable programming.

## State And Persistence
The provider stores MMIO base and selected layout. OTP bits are one-time persistent hardware state; writes can permanently blow fuses. The static `bcm_otpc_nvmem_config` is mutated during probe for size, dev, priv, and v2 alignment.

## Dependencies And Integration Points
Integrates with OF/ACPI platform matching, NVMEM provider core, Broadcom iProc hardware, and optional cell consumers. DT must provide `brcm,ocotp-size`.

## Risks
Write support is inherently destructive. The static config is shared across instances and could be unsafe for multiple controllers. `disable_ocotp_program()` return is ignored after successful writes. Row-size handling relies on core alignment and correct byte counts.

## Test Signals
Validate v1 and v2 reads, ACPI and OF matches, missing/zero size property failures, write-enable timeout handling, write-prohibited regions, and post-write readback on sacrificial OTP words. Hardware tests should confirm program mode is disabled after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/bcm-ocotp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/brcm_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/brcm_nvram.c

## Purpose
Exposes Broadcom I/O-mapped NVRAM as an NVMEM provider and dynamically creates cells for `name=value` variables, including MAC address post-processing.

## Important APIs, Types, And Functions
`struct brcm_nvram` stores copied NVRAM data, detected length, padding byte, and generated cell array. `brcm_nvram_copy_data()` maps flash/NVRAM, trims trailing padding, copies data into RAM, and initializes legacy bcm47xx NVRAM access. `brcm_nvram_parse()` validates the `FLSH` header and length. `brcm_nvram_add_cells()` scans variables and builds `nvmem_cell_info` entries. `brcm_nvram_read()` serves reads from the RAM copy and pads beyond actual data.

## Control Flow
Registered at `subsys_initcall_sync`, probe copies the MMIO region, parses the Broadcom header, discovers variable cells after the header, and registers NVMEM. For `et0macaddr`, `et1macaddr`, and `et2macaddr`, cells expose binary `ETH_ALEN` values rather than ASCII strings, with optional index-based address incrementing.

## State And Persistence
Driver state is a RAM snapshot of NVRAM data and generated cell metadata. The underlying NVRAM persists in flash/firmware storage, but this driver is read-only and does not write back changes. Padding byte preserves reads over unused space.

## Dependencies And Integration Points
Depends on platform MMIO, OF matching, NVMEM provider/consumer APIs, Broadcom bcm47xx NVRAM compatibility initialization, and Ethernet address helpers. Child DT nodes may map generated cells.

## Risks
Parsing modifies temporary delimiters inside the copied data and must restore them. Malformed variables without `=` stop cell generation. MAC string parsing can fail if board data uses unexpected formatting. Very large detected NVRAM only warns above 128 KiB.

## Test Signals
Test valid and invalid magic, length larger than mapped resource, padded trailing bytes, cells for ordinary strings and MAC addresses, indexed MAC consumers, and compatibility with existing bcm47xx NVRAM users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/brcm_nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/core.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/core.c

## Purpose
Implements the NVMEM framework core: provider registration, consumer lookup, cell parsing, sysfs access, fixed/layout cell creation, keepout handling, notifier events, and exported read/write helpers.

## Important APIs, Types, And Functions
Internal types are `struct nvmem_cell_entry` and `struct nvmem_cell`. Provider APIs include `nvmem_register()`, `devm_nvmem_register()`, `nvmem_unregister()`, `nvmem_add_one_cell()`, notifier registration, and layout registration. Consumer APIs include `nvmem_device_get()/put()`, `devm_nvmem_device_get()/put()`, `nvmem_cell_get()/put()`, `of_nvmem_cell_get()`, `nvmem_cell_read()/write()`, typed reads, variable-length little-endian reads, device direct reads/writes, and lookup table add/delete.

## Control Flow
Providers register with `nvmem_config`; the core allocates ids, initializes a bus device, obtains optional write-protect GPIO, copies config fields, validates keepouts, adds static and DT cells, registers the device, populates layouts, creates sysfs cell files, and emits notifiers. Consumers first try OF phandle lookup, then platform lookup tables. Cell reads call provider `reg_read`, apply bit shifting, invoke optional post-processing, and return allocated buffers. Writes validate read-only state and bit-cell sizing, merge unaffected bits from hardware when needed, toggle write-protect GPIO around provider writes, and return byte counts.

## State And Persistence
Framework state includes the global NVMEM bus, ida ids, provider refcounts, cell lists, lookup list, blocking notifier chain, optional sysfs attributes, and per-device layout pointer. Hardware persistence is delegated to providers; the core only mediates access and stores metadata.

## Dependencies And Integration Points
Integrates with Linux driver core, sysfs, OF phandles, GPIO descriptors, module refcounts, NVMEM provider/consumer public headers, layout bus helpers, and devres. It is initialized by `subsys_initcall()` so providers and consumers can bind early.

## Risks
Lifetime and locking are central: cells reference provider entries, consumers hold module and kref references, and layout modules may need extra references before generated cells exist. Bit-cell write preparation reads adjacent hardware bits, so volatile or write-once backing stores need caution. Keepout ranges must be sorted and word/stride aligned. Sysfs `force_ro` can change writeability when a provider has `reg_write`.

## Test Signals
Exercise provider registration/unregistration, devm cleanup, OF cell lookup, lookup-table fallback, fixed layout and dynamic layout cells, sysfs raw and cell reads, write-protect GPIO toggling, read-only enforcement, keepout fill behavior, bit-offset cell reads/writes, typed reads, and module unload with live consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-iim.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-iim.c

## Purpose
Provides read-only NVMEM access to the older i.MX IC Identification Module eFuse banks.

## Important APIs, Types, And Functions
`struct imx_iim_drvdata` carries the number of byte registers per SoC. `struct iim_priv` stores MMIO base and clock. `imx_iim_read()` enables the clock, maps byte offsets to IIM bank/register offsets with `IIM_BANK_BASE()`, reads one byte per 32-bit register, and disables the clock. `imx_iim_probe()` registers `imx-iim`.

## Control Flow
OF match selects SoC register count. Probe maps resource 0, gets the clock, fills a read-only byte-addressed config, and registers. Reads walk every requested byte while the clock is enabled.

## State And Persistence
Runtime state is MMIO base and clock handle. eFuse data is persistent hardware state and cannot be modified by this driver.

## Dependencies And Integration Points
Depends on platform MMIO, clocks, OF match data, and NVMEM provider core. Consumers retrieve per-SoC fuse values through NVMEM cells.

## Risks
Every byte read is a separate 32-bit MMIO access; incorrect nregs match data can expose invalid addresses. Clock enable failures propagate. No locking is used, assuming read-only operations and clock framework serialization are sufficient.

## Test Signals
Probe each supported compatible, read first/last cells, verify clock prepare/disable balance, and compare bank/register offset mapping with reference manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-iim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-ele.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-ele.c

## Purpose
Provides read-only NVMEM access to i.MX93/i.MX94/i.MX95 OCOTP fusebox regions where some words are readable through FSB, some belong to ELE, and some have ECC-width quirks.

## Important APIs, Types, And Functions
`enum fuse_type`, `struct ocotp_map_entry`, and `struct ocotp_devtype_data` describe readable, ELE-owned, ECC, and invalid word ranges. `imx_ocotp_fuse_type()` classifies words. `imx_ocotp_reg_read()` reads valid words, zeros invalid/ELE ranges, masks ECC words to 16 bits, and handles unaligned byte ranges through a temporary buffer. `imx_ocotp_fixup_dt_cell_info()` aligns DT cells to 32-bit raw reads and installs `imx_ocotp_cell_pp()` for MAC byte reversal.

## Control Flow
Probe obtains match data, maps the base, configures a read-only `ELE-OCOTP` NVMEM provider with fixed OF cells, and initializes a mutex. Reads clamp to device size, round to word reads, lock the provider, classify each word, read from `reg_off + index * 4` or synthesize zero, then copy the requested byte slice.

## State And Persistence
State is the SoC map, MMIO base, config, and mutex. Fuse values persist in hardware; ELE-owned or invalid ranges are intentionally hidden as zero.

## Dependencies And Integration Points
Depends on i.MX platform devices, OF match data, MMIO access, NVMEM core fixed cells, and Ethernet MAC post-processing conventions shared with other i.MX OCOTP drivers.

## Risks
Range maps must exactly match SoC fuse ownership; exposing ELE-only words or masking the wrong ECC words would return misleading data. The read-only zero-fill policy can make invalid ranges indistinguishable from programmed zero. Static maps require updates for new SoC revisions.

## Test Signals
Read cells across FSB, ELE, ECC, and invalid boundaries on each supported SoC; verify MAC-address post-processing; confirm out-of-range reads clamp cleanly; and compare reported values with firmware tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-ele.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-scu.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-scu.c

## Purpose
Implements i.MX8 SCU-mediated OCOTP access, reading fuses through SCU RPC and writing single words through an ARM SMC call while respecting ECC and hole regions.

## Important APIs, Types, And Functions
`struct ocotp_devtype_data` describes fuse count and special regions. `in_hole()` and `in_ecc()` classify indexes. `imx_sc_misc_otp_fuse_read()` issues SCU MISC OTP read RPCs. `imx_scu_ocotp_read()` reads words into a temporary buffer, zeroes holes, and serializes with `scu_ocotp_mutex`. `imx_scu_ocotp_write()` validates single-word writes, rejects holes, checks ECC words are still zero, and invokes `arm_smccc_smc(IMX_SIP_OTP_WRITE, ...)`.

## Control Flow
Probe gets the SCU IPC handle, selects i.MX8QXP or i.MX8QM data, sizes the provider, and registers writable `imx-scu-ocotp`. Reads round to 32-bit words and call SCU RPC per non-hole word. Writes allow exactly four bytes, optionally pre-read ECC regions to avoid reprogramming, then issue the secure monitor write.

## State And Persistence
Driver state is SCU IPC pointer, SoC region map, and device pointer. The global mutex serializes all SCU OCOTP accesses. Fuse programming is permanent.

## Dependencies And Integration Points
Depends on IMX_SCU firmware RPC, ARM SMCCC, platform OF matching, and NVMEM provider APIs. It uses legacy fixed OF cells and can serve consumers that need SoC IDs or calibration values.

## Risks
Write support can permanently alter OTP. Offset handling treats NVMEM offsets as word indexes despite a byte-sized config, so callers must follow the configured word size and core alignment. ECC-region policy only checks nonzero before programming and cannot fully prevent hardware-specific one-time constraints. Firmware/SMC errors propagate but may not be descriptive.

## Test Signals
Test reads in normal, ECC, and hole regions; writes of wrong sizes; write attempts to holes; ECC write to nonzero words; successful write/readback on disposable fuses; and SCU IPC unavailable deferral/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp.c

## Purpose
Provides NVMEM access to i.MX6/7/8 OCOTP fuse boxes, including read support, controlled one-word write support, SoC-specific timing, banked addressing, and MAC-address post-processing.

## Important APIs, Types, And Functions
`struct ocotp_params` captures register count, bank addressing, timing callback, and control bit masks. `imx_ocotp_wait_for_busy()`, `imx_ocotp_clr_err_if_set()`, `imx_ocotp_read()`, `imx_ocotp_write()`, `imx_ocotp_set_imx6_timing()`, and `imx_ocotp_set_imx7_timing()` implement hardware access. SoC match tables select parameter sets for i.MX6, i.MX7, and i.MX8 variants, including i.MX8MP alternate control bits.

## Control Flow
Probe maps the controller, obtains the clock, selects parameters, configures legacy fixed OF cells, clears any stale error bit, and registers NVMEM. Reads enable the clock, wait for idle, read shadow/fuse words into a rounded temporary buffer, clear the error bit on read-locked sentinel values, and return the requested bytes. Writes require one aligned word, enable the clock, program timing, wait idle, set address and unlock code, write data registers in banked or non-banked order, wait for completion, delay, reload shadow registers, and return the byte count.

## State And Persistence
Runtime state includes MMIO base, clock, SoC parameters, config pointer, and a global mutex. OTP contents are permanent; shadow registers are reloaded after writes to synchronize runtime reads.

## Dependencies And Integration Points
Depends on platform/OF matching, clocks, MMIO access, NVMEM provider core, fixed OF cells, and Ethernet MAC helper conventions. Consumers use cells for IDs, MAC addresses, calibration, and boot configuration.

## Risks
OTP writes are irreversible and require precise timing. Banked i.MX7 writes depend on writing DATA0 last to trigger programming. Read-locked words set error bits that must be cleared or later operations fail. Static config mutation and global mutex are acceptable for usual single-controller systems but are notable for multi-instance scenarios. Some parameter sets lack a write timing callback, so write use must match supported hardware behavior.

## Test Signals
Read across unaligned byte ranges, read locked words, MAC-address cell reversal, write rejection for unaligned or non-word requests, successful sacrificial word programming, shadow reload completion, timing values across clock rates, and all supported compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/internals.h -->
# sources/distributed-fs/ceph-client/drivers/nvmem/internals.h

## Purpose
Defines the private `struct nvmem_device` layout and internal layout-bus hooks shared between the NVMEM core and layout implementation.

## Important APIs, Types, And Functions
`struct nvmem_device` stores owner, driver-core device, stride, word size, id, refcount, size, access flags, type, compatibility sysfs attributes, cell list, DT fixup callback, keepout metadata, provider callbacks, write-protect GPIO, active layout, provider private pointer, and sysfs-cell population state. Internal declarations cover layout bus register/unregister, layout populate, and layout destroy, with OF-disabled stubs.

## Control Flow
The header has no runtime flow. It is included by `core.c` and `layouts.c`; when OF is disabled, layout operations compile to no-ops.

## State And Persistence
Defines in-memory framework state only. Persistence belongs to providers.

## Dependencies And Integration Points
Depends on device model, NVMEM public consumer/provider headers, GPIO descriptors through the core, and OF conditional compilation.

## Risks
Changing this private structure affects core/layout assumptions and lifetime management. The OF stubs must match real function signatures so non-OF builds remain valid.

## Test Signals
Build with and without `CONFIG_OF`, with sysfs enabled and disabled, and run provider registration plus layout population tests to catch structure or stub mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/jz4780-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/jz4780-efuse.c

## Purpose
Registers the Ingenic JZ4780 eFuse block as a read-only NVMEM provider and handles controller read timing through regmap and clock configuration.

## Important APIs, Types, And Functions
`struct jz4780_efuse` stores device, regmap, and clock. `jz4780_efuse_read()` reads in fixed 32-byte chunks by programming address/length/read-enable bits, polling `EFUSTATE_RD_DONE`, bulk-reading data registers, and copying the requested slice. Probe configures regmap, enables the clock with devm cleanup, computes read adjust/strobe fields from bus rate, and registers `jz4780-efuse`.

## Control Flow
Probe maps MMIO, initializes a 32-bit regmap, enables clock, calculates timing constraints, writes read timing fields, and registers a 1024-byte byte-addressed NVMEM device. Reads loop until the caller's byte range is satisfied, aligning each hardware transaction to a 32-byte boundary.

## State And Persistence
State is device, regmap, and clock. Fuse contents are persistent and read-only here.

## Dependencies And Integration Points
Depends on platform/OF matching, regmap MMIO, clock framework, polling helpers, and NVMEM provider core.

## Risks
Timing calculation must fit four-bit fields; unsupported clock rates fail probe. Read timeout returns errors to consumers. The driver reads full chunks for partial requests, so controller side effects must tolerate repeated aligned reads.

## Test Signals
Probe at supported clock rates, verify timing register values, read unaligned ranges spanning chunk boundaries, force timeout paths if possible, and compare exported NVMEM data to factory fuse maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/jz4780-efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lan9662-otpc.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/lan9662-otpc.c

## Purpose
Implements Microchip LAN9662 OTP controller access as a byte-addressable NVMEM provider with read and write support.

## Important APIs, Types, And Functions
`struct lan9662_otp` stores device and MMIO base. Helpers power the OTP block, wait for flags to clear, set byte addresses, execute commands, and read/write individual bytes. `lan9662_otp_read()` and `lan9662_otp_write()` provide NVMEM callbacks over 8192 bytes.

## Control Flow
Probe maps the controller and registers `lan9662-otp`. Reads power up the block, issue a read command per byte, check read-prohibited status, copy data, and power down. Writes power up, skip zero bytes, read current data, OR requested bits into current data, skip no-op writes, program bytes, check write-prohibited/fail bits, and power down.

## State And Persistence
Runtime state is MMIO base and device. OTP contents are permanent; writes only transition bits by ORing new data with existing data.

## Dependencies And Integration Points
Depends on platform/OF matching, MMIO polling, and NVMEM provider core. Consumers can read or program LAN9662 OTP bytes through standard NVMEM APIs.

## Risks
OTP writes are destructive. Power-up return values are ignored in read/write wrapper paths, which can hide power sequencing failures. There is no explicit lock around byte sequences, so concurrent readers/writers could interleave. Byte-wise access is slow but simple.

## Test Signals
Read full and partial ranges, read/write prohibited addresses, write zero no-op behavior, write OR semantics, timeout on busy/go flags, and power state after early errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/lan9662-otpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layerscape-sfp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layerscape-sfp.c

## Purpose
Exposes the OTP region of NXP/Freescale Layerscape Security Fuse Processor blocks as a read-only NVMEM provider.

## Important APIs, Types, And Functions
`struct layerscape_sfp_data` supplies OTP size and register endian format per SoC. `layerscape_sfp_read()` bulk-reads 32-bit words from `LAYERSCAPE_SFP_OTP_OFFSET + offset`. Probe creates an MMIO regmap with SoC endian, sets size, and registers `fsl-sfp`.

## Control Flow
OF match selects `ls1021a` big-endian or `ls1028a` little-endian data. Probe maps registers, initializes regmap bounds to the OTP window, and registers a 32-bit aligned NVMEM device. Reads are direct regmap bulk reads.

## State And Persistence
State is just the regmap. Fuse data persists in SFP hardware and this provider is read-only.

## Dependencies And Integration Points
Depends on platform MMIO, device property match data, regmap endian support, and NVMEM core. Cells expose values such as unique IDs and secure boot information.

## Risks
Wrong endian match data produces byte-swapped fuse values. Bulk read count assumes 32-bit aligned accesses enforced by word size and stride. Size constants must match SoC OTP windows.

## Test Signals
Probe both compatible strings, verify endian-correct known fuse words, test unaligned read rejection by the core, and compare provider size with SFP documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layerscape-sfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts.c

## Purpose
Implements the NVMEM layout bus, allowing DT-described layout parsers to bind below an NVMEM provider and dynamically add cells.

## Important APIs, Types, And Functions
Exports `__nvmem_layout_driver_register()`, `nvmem_layout_driver_unregister()`, and `of_nvmem_layout_get_container()`. Internal flow uses `nvmem_layout_bus_type`, `nvmem_layout_bus_match()`, `nvmem_layout_bus_probe()`, `nvmem_layout_bus_remove()`, `nvmem_layout_create_device()`, `nvmem_layout_bus_populate()`, `nvmem_populate_layout()`, and `nvmem_destroy_layout()`.

## Control Flow
During provider registration, the core calls `nvmem_populate_layout()`. This finds the `nvmem-layout` child, skips nodes without `compatible` and fixed layouts handled elsewhere, creates a single `struct nvmem_layout` device under the provider, marks the DT node populated, and lets a layout driver bind by OF compatible. Driver probe sets `layout->add_cells` and calls `nvmem_layout_register()` in the core.

## State And Persistence
Runtime state is the layout device linked bidirectionally with `nvmem->layout`. Device release drops the DT node reference and frees the layout. DT populated flags prevent duplicate devices.

## Dependencies And Integration Points
Depends on OF, driver core buses, device links sync-state pause/resume, DMA mask setup, MSI OF configuration, and internal NVMEM core structures. Layout drivers in `drivers/nvmem/layouts/` register on this bus.

## Risks
Provider/layer lifetime must be paired: destroying a provider must unregister the layout device and clear OF populated flags. Fixed layouts are intentionally skipped here and parsed in core, so behavior is split. Missing `remove` callbacks reject layout drivers.

## Test Signals
Register providers with no layout, fixed layout, and dynamic layout nodes; bind/unbind layout modules; verify OF_POPULATED_BUS flag clearing on teardown; and test non-OF builds through stubs in `internals.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Kconfig

## Purpose
Defines Kconfig symbols for NVMEM layout parser modules that discover cells from structured data stored inside an NVMEM provider.

## Important APIs, Types, And Functions
`NVMEM_LAYOUTS` is a hidden OF-dependent symbol. Under the layout menu it defines `NVMEM_LAYOUT_SL28_VPD`, `NVMEM_LAYOUT_ONIE_TLV`, and `NVMEM_LAYOUT_U_BOOT_ENV`, selecting CRC helpers and generic network utilities as needed.

## Control Flow
The top-level NVMEM Kconfig sources this file. When layouts are enabled, users can select parser modules; selected symbols control objects in `layouts/Makefile`.

## State And Persistence
No runtime state. It controls compile-time availability and module construction.

## Dependencies And Integration Points
Depends on OF because layouts are discovered from `nvmem-layout` DT nodes. It integrates with CRC8/CRC32 libraries and the U-Boot environment parser.

## Risks
Missing helper selections break module builds; too-broad layout availability could bind to malformed DT descriptions. Symbols must stay aligned with layout driver source files and compatible strings.

## Test Signals
Kconfig allmodconfig coverage, individual module builds, OF-disabled builds where `NVMEM_LAYOUTS` is unavailable, and verification that each selected layout has a matching Makefile object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Makefile

## Purpose
Maps layout Kconfig symbols to parser module objects.

## Important APIs, Types, And Functions
Build mappings are `CONFIG_NVMEM_LAYOUT_SL28_VPD -> sl28vpd.o`, `CONFIG_NVMEM_LAYOUT_ONIE_TLV -> onie-tlv.o`, and `CONFIG_NVMEM_LAYOUT_U_BOOT_ENV -> u-boot-env.o`.

## Control Flow
Kbuild descends into the directory from the parent Makefile, then includes only objects whose symbols are enabled.

## State And Persistence
No runtime state; it determines module/built-in object inclusion.

## Dependencies And Integration Points
Must stay synchronized with `layouts/Kconfig` and layout source files.

## Risks
Stale object names or missing entries cause selected layout drivers not to build. The simple mapping makes regressions easy to spot in allmodconfig.

## Test Signals
Build each layout as module and built-in, run `make M=drivers/nvmem/layouts`, and verify resulting module names match Kconfig expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/onie-tlv.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/onie-tlv.c

## Purpose
Parses ONIE Type-Length-Value EEPROM/NVMEM tables and adds NVMEM cells for recognized TLV fields, including indexed MAC address handling and CRC validation.

## Important APIs, Types, And Functions
`struct onie_tlv_hdr` and `struct onie_tlv` describe the table. `onie_tlv_cell_name()` maps TLV type codes to cell names. `onie_tlv_crc_is_valid()` validates the JAMCRC field. `onie_tlv_parse_table()` reads the header and full table from the backing NVMEM device. `onie_tlv_add_cells()` creates cells with offsets into the table and optional post-processing from `onie_tlv_read_cb()`. The layout driver registers as `onie-tlv-layout`.

## Control Flow
Probe sets `layout->add_cells` and calls `nvmem_layout_register()`. Parsing reads the header, validates magic `TlvInfo` and version 1, bounds total size to 2048 bytes, reads the table, validates the trailing CRC TLV, then iterates data TLVs. Recognized TLV types become cells, with DT child nodes looked up under the layout container. MAC address cells use a post-process callback that adds the requested index.

## State And Persistence
The layout stores no persistent driver state beyond generated core cell entries. The backing ONIE table persists in the provider. The parsed table allocation is devm-managed for the layout device lifetime.

## Dependencies And Integration Points
Depends on the NVMEM layout bus, NVMEM direct reads, OF layout container lookup, CRC32, and Ethernet address helpers. It exposes standardized ONIE fields to ordinary NVMEM consumers.

## Risks
The loop continues without advancing offset for unknown cell names, which can hang on unrecognized TLV types; this is a notable correctness risk in the current code. Bounds checking uses `offset + tlv.len >= data_len`, which may reject or mishandle edge TLVs depending on intended inclusive semantics. CRC validation assumes the final TLV is type 0xfe length 4.

## Test Signals
Parse valid ONIE tables, invalid magic/version, oversized length, bad CRC, missing CRC TLV, unknown TLV types, edge-length TLVs, MAC address indexed consumers, and DT child-node association. A regression test should specifically cover unknown TLVs to detect infinite-loop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/onie-tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/sl28vpd.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/sl28vpd.c

## Purpose
Parses the Kontron SMARC-sAL28 VPD layout and creates cells for serial number and base MAC address after validating header and CRC8.

## Important APIs, Types, And Functions
`struct sl28vpd_header` and `struct sl28vpd_v1` define the layout. `sl28vpd_v1_check_crc()` validates the CRC8 over the v1 structure. `sl28vpd_add_cells()` reads the header, checks magic/version, validates CRC, and adds cells from `sl28vpd_v1_entries`. `sl28vpd_mac_address_pp()` validates and increments MAC addresses by cell index.

## Control Flow
Probe assigns `layout->add_cells` and registers the layout. The add-cells callback reads the header from the backing provider, rejects invalid magic or unsupported versions, validates CRC, gets the layout DT container, and adds two cells: `serial-number` and `base-mac-address`.

## State And Persistence
No private persistent state. Generated cells live in the NVMEM core. VPD contents persist in the underlying provider.

## Dependencies And Integration Points
Depends on the NVMEM layout bus, direct NVMEM reads, OF layout child lookup, CRC8, and Ethernet address helpers. Consumers can reference serial and MAC cells by DT phandle.

## Risks
Only version 1 is supported. MAC post-processing rejects invalid base addresses and negative indexes, so consumers expecting derived MACs depend on correct `#nvmem-cell-cells` indexing. CRC polynomial/table must match board firmware.

## Test Signals
Valid v1 VPD parse, invalid magic, unsupported version, bad CRC, serial cell read, base MAC read, indexed MAC derivation, invalid base MAC rejection, and layout unbind/rebind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/sl28vpd.c -->
