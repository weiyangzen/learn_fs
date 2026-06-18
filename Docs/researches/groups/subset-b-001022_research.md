# Research: subset-b-001022

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-core.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-core.c

## Purpose
Implements ACPI APEI Error Injection (EINJ) support. It discovers the EINJ table, builds an APEI instruction interpreter for EINJ actions, exposes debugfs controls under the APEI debugfs tree, and exports injection helpers used by other subsystems such as CXL.

## Important APIs, Types, And Functions
Key exported entry points are `einj_get_available_error_type()`, `einj_error_inject()`, `einj_cxl_rch_error_inject()`, `einj_is_cxl_error_type()`, and `einj_validate_error_type()`. Internal data structures model ACPI 5 address parameters (`struct set_error_type_with_address`), ACPI 6.5 EINJv2 component syndrome arrays, vendor extensions, and legacy unpublished v4 parameters. `einj_ins_type[]` maps ACPI EINJ opcodes to the common APEI executor.

## Control Flow
`einj_init()` creates a faux device whose probe reads and validates the ACPI EINJ table, queries supported error types, collects and reserves register resources, pre-maps GARs, maps the parameter block, and creates debugfs files. A debugfs write to `error_type` validates one error bit, and writing `error_inject` calls `einj_error_inject()`. Injection executes optional begin, sets the error type or address parameter block, runs firmware execute, polls busy/status with timeout, obtains the trigger table, executes trigger actions unless `notrigger` is set, and runs optional end.

## State And Persistence
Global state includes the table pointer, resource set, mapped parameter block, supported type masks, EINJv2 syndrome data, debugfs values, and vendor blobs. `einj_mutex` serializes firmware interpreter use. There is no disk persistence, but debugfs values persist in memory until module removal.

## Dependencies And Integration Points
Depends on ACPI table access, APEI executor/resource helpers, debugfs, faux devices, memory resource ownership, fixups for ACPI 5 and EINJv2, and architecture helpers such as `arch_is_platform_page()`. CXL uses exported symbols for CXL protocol and RCH injection paths.

## Risks
Primary risks are malformed firmware tables, unsafe target address masks, resource conflicts with RAM/MMIO, vendor extension size errors, firmware timeouts, and debugfs-triggered injection misuse. CXL RCH injection deliberately bypasses normal memory-MMIO rejection after separate validation.

## Test Signals
Useful signals include EINJ table validation logs, `available_error_type` output, debugfs parameter file behavior, rejected invalid type/flag combinations, timeout paths, successful trigger-table resource collection, CXL injection callers, and cleanup/unmap behavior on module remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-cxl.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-cxl.c

## Purpose
Provides CXL-facing wrappers around EINJ so CXL core can list and inject CXL cache/memory protocol errors through ACPI firmware.

## Important APIs, Types, And Functions
Exports `einj_cxl_available_error_type_show()`, `einj_cxl_inject_rch_error()`, `einj_cxl_inject_error()`, and `einj_cxl_is_initialized()` in the `CXL` namespace. `cxl_dport_get_sbdf()` converts a downstream port PCI device to the segment:bus:device:function encoding required by ACPI EINJ.

## Control Flow
The show helper queries EINJ available types and prints only CXL masks. RCH injection validates the type and calls `einj_cxl_rch_error_inject()` with memory-address flags and the RCRB base. Non-RCH injection validates the type, derives SBDF from the PCI host bridge and device function, then calls `einj_error_inject()` with the PCIe SBDF flag.

## State And Persistence
This file holds only a static string table. Initialization state comes from `einj_initialized` in `einj-core.c`.

## Dependencies And Integration Points
Integrates CXL core with APEI EINJ exports, PCI host bridge/domain numbering, `seq_file`, and `cxl/einj.h`.

## Risks
Incorrect SBDF encoding or missing host bridge information rejects injection. The CXL RCH path passes an MMIO RCRB base through a special EINJ path, so validation must remain coupled to CXL-specific callers.

## Test Signals
Check CXL debugfs/sysfs consumers for listed CXL types, invalid non-CXL type rejection, host bridge domain handling, RCH RCRB injection call parameters, and namespace symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-cxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/erst-dbg.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/erst-dbg.c

## Purpose
Implements `/dev/erst_dbg`, a misc-device test and debugging interface for ACPI ERST persistent error records.

## Important APIs, Types, And Functions
File operations are `erst_dbg_open()`, `erst_dbg_release()`, `erst_dbg_read()`, `erst_dbg_write()`, and `erst_dbg_ioctl()`. Ioctls support `APEI_ERST_CLEAR_RECORD` and `APEI_ERST_GET_RECORD_COUNT`. It uses ERST core APIs such as `erst_get_record_id_begin()`, `erst_get_record_id_next()`, `erst_read_record()`, `erst_write()`, and `erst_clear()`.

## Control Flow
Open starts an ERST record-ID iteration. Reads walk record IDs, skip records removed by other users, resize a kernel buffer up to `ERST_DBG_RECORD_LEN_MAX`, and copy one complete CPER record to user space. Writes require `CAP_SYS_ADMIN`, copy a user-supplied CPER record, verify `record_length`, and persist it through ERST. Release ends the ID iterator.

## State And Persistence
`erst_dbg_buf` and length are process-shared module state guarded by `erst_dbg_mutex`. Persistent storage is owned by firmware through ERST core, not this debug layer.

## Dependencies And Integration Points
Depends on the ERST core, CPER record layout, miscdevice infrastructure, user-copy helpers, and the global `erst_disable` switch.

## Risks
Risks include user-provided malformed CPER records, records disappearing during iteration, large record memory allocation, and privileged writes modifying platform persistent error storage.

## Test Signals
Exercise open/read EOF behavior on empty stores, ioctl count/clear, write permission checks, oversized writes, dynamic buffer resizing, and read retry when a record disappears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/erst-dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/erst.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/erst.c

## Purpose
Implements ACPI APEI Error Record Serialization Table support. It exposes firmware persistent error storage as kernel ERST APIs and as a pstore backend for panic/dmesg/MCE data.

## Important APIs, Types, And Functions
Exports `erst_get_record_count()`, `erst_get_record_id_begin()`, `erst_get_record_id_next()`, `erst_get_record_id_end()`, `erst_write()`, `erst_read()`, `erst_read_record()`, and `erst_clear()`. `erst_ins_type[]` implements ERST-specific APEI instructions including variable operations, stalls, goto, base-address setup, and `MOVE_DATA`. `struct erst_erange` holds the firmware log address range, and `struct erst_record_id_cache` caches record IDs across iteration.

## Control Flow
`erst_init()` validates the ERST table, reserves and maps ERST resources, obtains the error log range, maps the range, and registers pstore if a backing buffer can be allocated. Read, write, and clear operations serialize through `erst_lock`, program ERST command inputs, execute firmware operations, poll busy/status, and translate firmware statuses to errno. pstore wraps payloads in CPER records and filters reads by the pstore creator GUID.

## State And Persistence
Persistent records live in firmware storage behind the ERST range. Kernel state includes the table pointer, mapped error range, pstore buffer, global disable flag, and a mutex/refcount-protected record-ID cache. `raw_spinlock_t erst_lock` protects interpreter and error range access, including contexts where sleeping is not acceptable.

## Dependencies And Integration Points
Integrates ACPI table access, APEI executor/resource helpers, CPER, pstore, vmalloc/kmalloc memory, NMI watchdog touch, and exported ERST APIs consumed by `erst-dbg.c`.

## Risks
Risks include firmware hangs, slow ERST timing interpretation, unsupported NVRAM ranges, `MOVE_DATA` in interrupt context, record-ID cache staleness, pstore buffer sizing, and lock constraints around panic/NMI paths.

## Test Signals
Check ERST table validation, log range mapping, pstore registration, read/write/clear status translation, record-ID iteration under deletion, unsupported NVRAM behavior, timeout warnings, and pstore CPER type decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/erst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes-nvidia.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes-nvidia.c

## Purpose
Registers an NVIDIA-specific GHES vendor CPER section handler and prints NVIDIA error payload fields when firmware reports the matching section GUID.

## Important APIs, Types, And Functions
Defines `struct cper_sec_nvidia` for the vendor payload and `struct nvidia_ghes_private` for the notifier. Main functions are `nvidia_ghes_notify()`, `nvidia_ghes_print_error()`, and `nvidia_ghes_probe()`.

## Control Flow
The platform driver matches ACPI HID `NVDA2012`. Probe allocates private state and registers a device-managed GHES vendor notifier. On notification, the handler imports the CPER section GUID, ignores non-NVIDIA sections, validates minimum payload size, prints metadata at severity-dependent log level, validates variable register array length, then prints register address/value pairs.

## State And Persistence
State is device-managed notifier/private memory. There is no persistent state beyond kernel logs.

## Dependencies And Integration Points
Depends on GHES vendor notifier APIs, ACPI platform matching, CPER generic data helpers, GUID helpers, and little-endian conversion.

## Risks
Malformed firmware may advertise too-small sections or a register count exceeding section length. The handler avoids out-of-bounds register access by checking `struct_size()` before iterating.

## Test Signals
Use synthetic CPER vendor records for GUID filtering, minimum-size rejection, severity log level selection, zero-register sections, truncated register arrays, and device-managed notifier unregister on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes-nvidia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes.c

## Purpose
Implements ACPI Generic Hardware Error Source handling. GHES is the firmware-first runtime path for reading CPER error status blocks, reporting them, dispatching subsystem recovery, and registering notification mechanisms.

## Important APIs, Types, And Functions
Exports `ghes_estatus_pool_init()`, `ghes_estatus_pool_region_free()`, vendor notifier registration helpers, CXL CPER work registration helpers, `ghes_get_devices()`, and GHES report-chain registration. Core functions include `ghes_new()`, `ghes_read_estatus()`, `ghes_clear_estatus()`, `ghes_do_proc()`, `ghes_proc()`, `ghes_in_nmi_queue_one_entry()`, and `ghes_probe()`.

## Control Flow
HEST creates `GHES` platform devices, and this driver probes enabled generic error sources. Probe validates notification type, maps the error status address and optional GHESv2 ack register, installs the chosen notifier path, links the device for EDAC, and handles pending errors. Runtime handlers read a CPER status block, validate it, panic on fatal severity, rate-limit duplicate logs through an RCU cache, process each CPER section, clear firmware status, and acknowledge GHESv2 if needed. NMI-like paths copy records into a gen_pool-backed llist and defer processing to irq_work.

## State And Persistence
State includes per-source `struct ghes`, HED/SEA/NMI lists, EDAC device list, fixmap locks, gen_pool for atomic copies/work items, RCU error-status cache, CXL FIFOs, and vendor notifier chain. Errors are transient; persistence is only through downstream pstore or subsystem logging.

## Dependencies And Integration Points
Integrates ACPI HEST/GHES, APEI register helpers, CPER parsers, memory failure, AER, CXL event handling, vendor CPER notifiers, EDAC, SDEI, NMI, HED, IRQ, timers, RAS tracing/logging, and firmware-first `_OSC` setup.

## Risks
Important risks are atomic-context memory availability, fixmap serialization, duplicate/flooded CPER reports, malformed CPER lengths, fatal-error ordering, synchronous error SIGBUS behavior, FIFO overflow for CXL work, and RCU/list lifetime on notifier removal.

## Test Signals
Validate all notification types, CPER length/header rejection, fatal panic path, corrected/uncorrected ratelimiting, memory-failure queueing for sync and async errors, AER recovery queueing, CXL event FIFO overflow handling, vendor notifier dispatch, GHESv2 ack writes, and probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes_helpers.c

## Purpose
Provides CXL CPER protocol-error helper routines used by GHES and CXL workqueue consumers.

## Important APIs, Types, And Functions
Exports `cxl_cper_sec_prot_err_valid()` and `cxl_cper_setup_prot_err_work_data()`. These operate on `struct cxl_cper_sec_prot_err` and fill `struct cxl_cper_prot_err_work_data`.

## Control Flow
Validation requires agent address and protocol error log valid bits, a RAS capability size matching `struct cxl_ras_capability_regs`, and warns if device-like agents lack serial number. Setup accepts known CXL agent types, copies the CPER protocol section, skips DVSEC bytes, copies the RAS capability registers, and maps CPER severity to AER severity.

## State And Persistence
No file-local state. Output state is the work-data object passed by caller.

## Dependencies And Integration Points
Depends on CXL event structures, AER severity conversion, and GHES CXL protocol error dispatch.

## Risks
The helper assumes the caller has already ensured enough backing CPER section data for the DVSEC and RAS capability offsets. Invalid agent types and unexpected RAS sizes are rejected.

## Test Signals
Cover missing valid bits, bad `err_len`, missing serial warning cases, each accepted agent type, rejected default agent type, and severity conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/hest.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/apei/hest.c

## Purpose
Parses the ACPI Hardware Error Source Table and registers GHES platform devices for generic firmware-first error sources.

## Important APIs, Types, And Functions
The main public entry is `acpi_hest_init()`. Internal helpers include `apei_hest_parse()`, `hest_esrc_len()`, `is_ghes_assist_struct()`, `hest_parse_cmc()`, `hest_parse_ghes_count()`, and `hest_parse_ghes()`. It exports the global `hest_disable`.

## Control Flow
Initialization reads the HEST table unless disabled, walks all error sources with length checks, enables architecture CMC firmware-first support when advertised, counts generic error sources, allocates an array for GHES platform devices, and registers each enabled generic source as a `GHES` platform device with a pointer to its HEST entry.

## State And Persistence
State includes the HEST table pointer, disable status, and cached IA machine-check structures used to identify unsupported GHES_ASSIST entries. GHES platform devices persist after initialization.

## Dependencies And Integration Points
Depends on ACPI table parsing, architecture `arch_apei_enable_cmcff()`, GHES globals, platform devices, and `ghes_estatus_pool_init()`.

## Risks
Malformed source lengths, table overflows, duplicate GHES source IDs, unsupported GHES_ASSIST handling, and partial platform-device registration failures are the primary risks.

## Test Signals
Check boot with missing HEST, `hest_disable`, bad lengths/counts, duplicate GHES IDs, disabled generic sources, GHES_ASSIST skip behavior, and rollback if GHES device registration or pool allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/apei/hest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/Kconfig

## Purpose
Declares ARM64 ACPI feature symbols for IORT, GTDT, AGDI, APMT, and MPAM.

## Important APIs, Types, And Functions
This is Kconfig metadata rather than C code. It defines `ACPI_IORT`, `ACPI_GTDT`, `ACPI_AGDI`, `ACPI_APMT`, and `ACPI_MPAM`. `ACPI_AGDI` has a user-visible prompt and depends on `ARM_SDE_INTERFACE`.

## Control Flow
The symbols control which ARM64 ACPI implementation files are built by the sibling Makefile.

## State And Persistence
Configuration state is persisted in kernel build configuration.

## Dependencies And Integration Points
Feeds the ARM64 ACPI Makefile and feature-specific init calls in `init.c`.

## Risks
Incorrect dependencies can build code without required architecture support or hide needed table parsers.

## Test Signals
Validate defconfig and randconfig coverage, especially AGDI with and without SDEI, and ensure built objects match enabled symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/Makefile -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/Makefile

## Purpose
Maps ARM64 ACPI Kconfig symbols to object files and always builds common DMA, init, and thermal CPU frequency hooks.

## Important APIs, Types, And Functions
Build entries include `agdi.o`, `apmt.o`, `ffh.o`, `gtdt.o`, `iort.o`, `mpam.o`, `cpuidle.o`, `amba.o`, plus unconditional `dma.o`, `init.o`, and `thermal_cpufreq.o`.

## Control Flow
Kbuild includes objects based on `obj-$(CONFIG_...)` or `obj-y`.

## State And Persistence
No runtime state; affects build products.

## Dependencies And Integration Points
Ties this directory to ARM64 ACPI, AMBA, processor idle, FFH, IORT, GTDT, APMT, AGDI, and MPAM feature symbols.

## Risks
Missing object mappings silently disable platform support even if symbols are selected. Unconditional objects must not depend on optional code without guards.

## Test Signals
Use build matrix coverage for each config symbol and verify unresolved symbols do not appear when optional objects are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/agdi.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/agdi.c

## Purpose
Parses the Arm Generic Diagnostic Dump and Reset Interface table and registers a panic-inducing SDEI or interrupt handler for diagnostic dump/reset events.

## Important APIs, Types, And Functions
`struct agdi_data` carries signaling mode, SDEI event, GSIV, NMI use, and IRQ. Main functions are `acpi_agdi_init()`, `agdi_probe()`, SDEI and interrupt probe/remove helpers, and the panic handlers.

## Control Flow
`acpi_agdi_init()` reads the AGDI table, prepares platform data from either GSIV or SDEI event fields, registers a platform device, and then registers the platform driver. Probe chooses interrupt or SDEI mode from the table flags. Interrupt mode registers a GSI, tries `request_nmi()` first, and falls back to `request_irq()`. SDEI mode registers and enables the event.

## State And Persistence
State lives in platform data copied from the ACPI table. Runtime state tracks the registered IRQ and whether it is an NMI. No persistent storage is used.

## Dependencies And Integration Points
Depends on ACPI table access, SDEI, GSI registration, NMI/IRQ APIs, platform devices, and ARM64 init dispatch.

## Risks
The handler intentionally panics the system. Remove paths can fail to unregister an in-progress SDEI event. Interrupt mode must unregister GSI and free the right NMI/IRQ kind.

## Test Signals
Check no-op behavior without AGDI table, interrupt and SDEI modes, NMI fallback to IRQ, GSI registration failure, SDEI unregister retry, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/agdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/amba.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/amba.c

## Purpose
Creates AMBA bus devices from selected ACPI-described ARM peripherals.

## Important APIs, Types, And Functions
Registers an ACPI scan handler matching `ARMH0061` and `ARMH0330`. Main functions are `acpi_amba_init()`, `amba_register_dummy_clk()`, and `amba_handler_attach()`.

## Control Flow
Initialization registers a fixed dummy `apb_pclk` and adds the ACPI scan handler. Attach skips ACPI nodes that already have a physical device, allocates an AMBA device, extracts the first memory resource and up to `AMBA_NR_IRQS` IRQs, assigns an ACPI fwnode, optionally attaches the parent's physical device, and calls `amba_device_add()`.

## State And Persistence
Created AMBA devices persist in the device model. The dummy clock is global clock state.

## Dependencies And Integration Points
Integrates ACPI scan, AMBA bus, resource parsing, clkdev, fwnode, and parent device linkage.

## Risks
Risks include missing memory resources, duplicate physical-node creation, dummy clock registration failures not being checked, and resource parsing changes affecting AMBA probing.

## Test Signals
Test matching HIDs, resource extraction, parent device assignment, already-bound ACPI nodes, AMBA add failure cleanup, and driver binding for PL061 and DMA-330.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/amba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/apmt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/apmt.c

## Purpose
Parses the ARM APMT table and creates platform devices for architectural PMU nodes.

## Important APIs, Types, And Functions
Main functions are `acpi_apmt_init()`, `apmt_init_platform_devices()`, `apmt_add_platform_device()`, and `apmt_init_resources()`. Devices are named `arm-cs-arch-pmu`.

## Control Flow
Initialization obtains the APMT table and keeps it mapped for runtime node access. The parser walks nodes by length, allocates a static fwnode for each, builds memory resources for page 0 and optional page 1, maps overflow GSIs to IRQ resources, stores the node pointer in platform data, assigns the fwnode, and adds the platform device.

## State And Persistence
`apmt_table` remains mapped after successful initialization because platform data points into it. Platform devices and their fwnodes persist.

## Dependencies And Integration Points
Depends on ACPI APMT structures, GSI registration, platform devices, and the CoreSight architectural PMU driver.

## Risks
Node length and table boundary trust is a risk because the loop advances by firmware-provided lengths. IRQ registration failures result in devices without IRQ resources rather than total failure.

## Test Signals
Test missing table, malformed node lengths, dual-page resources, no-overflow IRQ nodes, failed fwnode allocation, failed platform data/resource addition, and PMU driver probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/apmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/cpuidle.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/cpuidle.c

## Purpose
Implements ARM64 ACPI FFH low-power idle support using PSCI CPU suspend.

## Important APIs, Types, And Functions
Exports `acpi_processor_ffh_lpi_probe()` and defines `acpi_processor_ffh_lpi_enter()`. Internal validation is in `psci_acpi_cpu_init_idle()`.

## Control Flow
Probe checks that the CPU has ACPI LPI data, PSCI `cpu_suspend` exists, and every non-index-zero LPI state's low 32-bit address encodes a valid PSCI power state. Enter reads the LPI address as PSCI state and invokes the CPU PM idle helper, choosing retention or full idle based on `arch_flags`.

## State And Persistence
No file-local state. It consumes per-CPU ACPI processor LPI state and PSCI operation pointers.

## Dependencies And Integration Points
Integrates ACPI processor idle, PSCI, CPU PM, and cpuidle.

## Risks
Firmware can provide invalid power states or unsupported FFH encodings. Incorrect retention classification can call the wrong CPU PM helper.

## Test Signals
Check CPUs without LPI, missing PSCI suspend, invalid PSCI state rejection, retention and non-retention entry paths, and suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/dma.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/dma.c

## Purpose
Applies ARM64 ACPI DMA addressing limits and DMA range maps to devices.

## Important APIs, Types, And Functions
Defines `acpi_arch_dma_setup(struct device *dev)`.

## Control Flow
The helper ensures `dev->dma_mask` exists, picks a default limit from `coherent_dma_mask` or 32-bit fallback, skips devices with an existing range map, queries `_DMA` ranges through `acpi_dma_get_range()`, falls back to IORT limits when no ACPI range exists, then constrains `bus_dma_limit`, `coherent_dma_mask`, and `dma_mask`.

## State And Persistence
Mutates per-device DMA fields and may attach `dev->dma_range_map`.

## Dependencies And Integration Points
Depends on ACPI DMA range parsing, IORT DMA limits, dma-direct helpers, and generic device DMA masks.

## Risks
Missing initial `dma_mask` is tolerated with a warning. Incorrect firmware limits can unnecessarily constrain devices or allow unreachable DMA.

## Test Signals
Exercise devices with `_DMA` ranges, IORT fallback, no range information, preexisting range maps, zero coherent masks, and mask clamping boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/ffh.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/ffh.c

## Purpose
Implements ARM64 architecture callbacks for ACPI FFH operation regions through SMCCC SMC/HVC calls.

## Important APIs, Types, And Functions
Defines `struct acpi_ffh_data`, `acpi_ffh_address_space_arch_setup()`, and `acpi_ffh_address_space_arch_handler()`.

## Control Flow
Setup requires SMCCC 1.2 and a valid SMC or HVC conduit, allocates per-region context, copies ACPI FFH metadata, and stores function pointers for 32-bit and 64-bit calls. The handler validates offset 0 for 32-bit fast calls and offset 1 for 64-bit fast calls, restricts allowed SMCCC owners to standard, SIP, and OEM, copies arguments from the ACPI value buffer, invokes the conduit, and writes results back.

## State And Persistence
Per-region context persists as the ACPI address-space region context until teardown by the ACPI core.

## Dependencies And Integration Points
Depends on ACPI FFH infrastructure, ARM SMCCC version/conduit detection, SMC/HVC call wrappers, and ACPI exception return conventions.

## Risks
Invalid function IDs, wrong call width, excessive length, unsupported SMCCC version, or no conduit all fail with ACPI errors. Owner filtering is important to prevent arbitrary SMCCC calls.

## Test Signals
Test SMCCC version gating, SMC and HVC conduits, 32-bit and 64-bit offsets, owner rejection, length rejection, and result copy-back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/ffh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/gtdt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/gtdt.c

## Purpose
Parses the ARM Generic Timer Description Table for architected timer PPIs, MMIO timer frames, and SBSA generic watchdog platform devices.

## Important APIs, Types, And Functions
Exports early helpers `acpi_gtdt_init()`, `acpi_gtdt_map_ppi()`, and `acpi_gtdt_c3stop()`. Device-init logic is in `gtdt_platform_timer_init()`, `gtdt_parse_timer_block()`, and `gtdt_import_sbsa_gwdt()`.

## Control Flow
`acpi_gtdt_init()` stores GTDT bounds and counts valid platform timer structures for revision 2 or later. PPI helpers map timer GSIs and report always-on state. At device init, the table is reacquired with permanent mappings, platform timers are walked, non-secure watchdogs become `sbsa-gwdt` devices, and timer blocks become `gtdt-arm-mmio-timer` devices after frame validation and IRQ mapping.

## State And Persistence
An initdata descriptor stores table pointers during parsing. Registered platform devices persist. Mapped GSIs remain registered unless error cleanup explicitly unregisters them.

## Dependencies And Integration Points
Integrates ACPI GTDT, GSI registration, ARM arch timer code, platform devices, and SBSA watchdog driver.

## Risks
Malformed platform timer lengths, mismatched counts, duplicate or invalid frame numbers, missing base addresses, and partial IRQ mapping failures are key firmware risks.

## Test Signals
Check revision less than 2, count mismatch clamping, PPI polarity/trigger mapping, c3stop flags, secure timer frame skipping, duplicate frame rejection, watchdog without IRQ, and platform-device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/gtdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.c

## Purpose
Provides the ARM64 ACPI architecture initialization fan-out for optional table/device parsers.

## Important APIs, Types, And Functions
Defines `acpi_arch_init()`.

## Control Flow
At architecture ACPI init time, it conditionally calls `acpi_agdi_init()`, `acpi_apmt_init()`, `acpi_iort_init()`, and `acpi_amba_init()` based on build-time config.

## State And Persistence
No local state. It triggers registration side effects in the target modules.

## Dependencies And Integration Points
Depends on the declarations in `init.h` and the Makefile/Kconfig feature symbols.

## Risks
Ordering matters: table parsers that create platform devices run before later driver probes. Missing guards would create unresolved references when optional objects are disabled.

## Test Signals
Use config combinations to ensure each optional init is called only when built and that ACPI boot without optional tables remains quiet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.h

## Purpose
Declares ARM64 ACPI initialization entry points shared by `init.c` and optional table parser files.

## Important APIs, Types, And Functions
Declares `acpi_agdi_init()`, `acpi_apmt_init()`, `acpi_iort_init()`, and `acpi_amba_init()`.

## Control Flow
No runtime control flow. The header enables `init.c` to call per-feature initialization functions.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `<linux/init.h>` for `__init` annotations and ties together the ARM64 ACPI init files.

## Risks
Prototype drift could cause build warnings or incorrect section annotations.

## Test Signals
Build with all optional feature combinations and verify declarations match definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/iort.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/iort.c

## Purpose
Implements ARM64 ACPI I/O Remapping Table parsing. It creates SMMU/PMCG platform devices, maps device IDs through IORT topology, configures MSI and IOMMU domains, exposes RMR reserved regions, and provides DMA address limits.

## Important APIs, Types, And Functions
Important exports include `iort_register_domain_token()`, `iort_deregister_domain_token()`, `iort_find_domain_token()`, `iort_msi_map_id()`, `iort_msi_xlate()`, `iort_its_translate_pa()`, `iort_pmsi_get_msi_info()`, `iort_get_device_domain()`, `iort_iwb_handle()`, `acpi_configure_pmsi_domain()`, `iort_iommu_get_resv_regions()`, `iort_get_rmr_sids()`, `iort_put_rmr_sids()`, `iort_iommu_configure_id()`, `iort_dma_get_ranges()`, `acpi_iort_init()`, and optionally `acpi_iort_dma_get_max_cpu_address()`.

## Control Flow
Initialization obtains IORT and walks nodes. SMMU, SMMUv3, and PMCG nodes receive static fwnodes, platform resources, platform data, optional DMA setup, MSI domains, and platform device registration. Runtime lookup maps ACPI named components, IWB devices, or PCI root complexes to IORT nodes, walks ID mappings with overlap workarounds, locates ITS/SMMU parents, and configures MSI or IOMMU fwspecs. RMR code scans RMR nodes for matching SIDs and builds IOMMU reserved regions.

## State And Persistence
State includes the permanent IORT table pointer, spinlock-protected IORT-node-to-fwnode list, spinlock-protected ITS MSI chip token list, and platform devices. Device IOMMU fwspecs, MSI domains, software node properties, DMA masks, and reserved-region lists are persistent device-model state.

## Dependencies And Integration Points
Integrates ACPI IORT, PCI, IRQ domains/ITS, IOMMU API, ARM SMMU and PMCG drivers, platform devices, ACPI fwnodes, DMA ops, NUMA proximity, and PCI ACS.

## Risks
Risks include malformed node lengths/references, ID mapping off-by-one firmware ambiguity, NULL output references, duplicate/conflicting mappings, missing fwnodes, unavailable SMMU drivers causing probe defer, RMR overlap/alignment issues, PCI firmware configuration not preserved for RMR SIDs, and partial platform-device setup leaks.

## Test Signals
Test node scanning bounds, PCI and named-component matching, MSI ID translation and ITS token lookup, platform MSI domain assignment, IOMMU fwspec setup for aliases, ATS/CANWBS flags, RMR reserved-region generation, SMMU/PMCG resource creation, ACS request, DMA limit extraction, and bad firmware warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/iort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/mpam.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/mpam.c

## Purpose
Parses the Arm MPAM ACPI table and creates `mpam_msc` platform devices for memory system components.

## Important APIs, Types, And Functions
Exports `acpi_mpam_parse_resources()` and `acpi_mpam_count_msc()`. Internal helpers handle IRQ registration, resource-node parsing, power-management links, interface decoding, MSC platform-device creation, and table parsing.

## Control Flow
`acpi_mpam_parse()` runs at `subsys_initcall_sync`, checks ACPI and MPAM CPU support, obtains the MPAM table, validates revision and MSC bounds, skips reserved or disabled MSCs, then creates platform devices. Each MSC may get MMIO resources or PCC channel properties, overflow/error IRQ resources, not-ready timing property, CPU affinity property derived from linked processor/container devices, software node properties, and a copy of the MSC table entry as platform data. Later, the MPAM driver calls `acpi_mpam_parse_resources()` to create RIS objects from resource nodes.

## State And Persistence
State is represented by created platform devices, software node properties, ACPI companions, device links, and platform data copies. The parser itself has no global mutable state.

## Dependencies And Integration Points
Integrates ACPI MPAM table structures, ARM MPAM core, GSI registration, ACPI processor/cache helpers, NUMA proximity mapping, PCC/MMIO interfaces, software nodes, and platform devices.

## Risks
Reserved MSC fields make MPAM globally unsafe and are skipped while still counted. Partitioned PPIs are unsupported. Resource-node bounds and functional dependency counts are critical. Bad proximity domains fall back to node 0.

## Test Signals
Test unsupported revisions, malformed MSC lengths, reserved field handling, disabled MSCs, MMIO and PCC interfaces, overflow/error IRQs, partitioned IRQ rejection, processor-container affinity, resource-node cache/memory RIS creation, and count-vs-parse behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/mpam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/thermal_cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/arm64/thermal_cpufreq.c

## Purpose
Provides an ARM64 ACPI hook for platform-specific thermal CPU frequency reduction percentage.

## Important APIs, Types, And Functions
Exports `acpi_arch_thermal_cpufreq_pctg()`. It compares the SMCCC SoC ID against `SMCCC_SOC_ID_T241`.

## Control Flow
The function reads `arm_smccc_get_soc_id_version()`. If the SoC is NVIDIA Tegra241, it returns `5`; otherwise it returns `0` to use default policy.

## State And Persistence
No local state.

## Dependencies And Integration Points
Depends on ARM SMCCC SoC ID support and is consumed by ACPI thermal/cpufreq code through the exported symbol.

## Risks
If SMCCC SoC ID is unavailable or changes encoding, the override is skipped. Hard-coded platform matching must remain narrow to avoid affecting unrelated systems.

## Test Signals
Mock or boot-test Tegra241 SoC ID, non-Tegra IDs, unavailable SMCCC ID behavior, and thermal cpufreq policy use of the returned percentage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/arm64/thermal_cpufreq.c -->
