# Research Group subset-b-000947

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/firmware_if.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/firmware_if.c

## Purpose

`firmware_if.c` implements the common HabanaLabs kernel-driver firmware interface. It covers firmware image acquisition and copying, CPU-CP packet submission, preboot readiness detection, static and dynamic firmware boot protocols, boot-error decoding, hardware-monitor and telemetry requests, PLL/frequency/power operations, secure-attestation requests, and generic CPU-CP passthrough. It is the concrete implementation behind many `hl_fw_*` declarations in `habanalabs.h`, and it relies on ASIC-specific callbacks for queue operations, firmware image placement, PLL index mapping, BAR/register access, and per-ASIC boot-loader initialization.

## Important APIs and Functions

- `hl_fw_version_cmp()` compares parsed firmware SW version fields stored on `struct hl_device` against a caller-supplied version.
- `hl_request_fw()`, `hl_release_firmware()`, `hl_fw_copy_fw_to_device()`, `hl_fw_load_fw_to_device()` wrap Linux firmware loading, validate size/alignment, and copy firmware bytes through MMIO.
- `hl_fw_send_cpu_message()` is the central CPU-CP packet path. It allocates CPU-accessible DMA memory, serializes the CPU queue with `send_cpu_message_lock`, submits a queue BD, polls the packet fence, decodes firmware return codes, scrubs the submitted BD control field, and frees the DMA buffer.
- CPU-CP convenience wrappers include IRQ unmasking, heartbeat/test packets, soft reset, device activity, EEPROM, monitor dump, PCI counters, energy, PLL info, power, DRAM row data, engine-core ASID, signed device info, secure attestation, and generic passthrough.
- `hl_fw_wait_preboot_ready()`, `hl_fw_read_preboot_status()`, and helpers read preboot status/error/capability registers, decide whether the dynamic loader is available, and initialize the proper firmware loader.
- `hl_fw_dynamic_send_protocol_cmd()` implements the dynamic COMMS register protocol: clear status, send command, wait for ACK, clear again, send NOOP, and optionally wait for OK with another clear/NOOP cycle.
- `hl_fw_dynamic_request_descriptor()`, `hl_fw_dynamic_read_and_validate_descriptor()`, and `hl_fw_dynamic_validate_descriptor()` fetch firmware-provided descriptors, validate magic/version/CRC and memory bounds, and record the image destination region.
- `hl_fw_dynamic_init_cpu()` and `hl_fw_static_init_cpu()` are the two high-level boot paths selected by `hl_fw_init_cpu()`.
- `hl_fw_get_frequency()`, `hl_fw_set_frequency()`, `hl_fw_get_clk_rate()`, `hl_fw_get_max_power()`, and `hl_fw_set_max_power()` expose firmware-backed clock and power control.

## Control Flow

Firmware boot starts outside this file with ASIC setup filling `hdev->fw_loader` and `hdev->asic_prop`. `hl_fw_read_preboot_status()` initializes pre-load parameters, waits for preboot, reads preboot capability/status registers, sets `asic_prop.dynamic_fw_load`, calls the ASIC firmware-loader initializer, and reads legacy preboot versions if static loading is required.

`hl_fw_init_cpu()` branches to dynamic or static boot:

- Dynamic boot resets the COMMS state, optionally sends the current reset cause, requests a descriptor, updates reserved FW memory and preboot/binning information when stopping before boot CPU, otherwise loads boot-fit, waits for boot-fit, updates boot-fit state, initializes DRAM scrambling, optionally skips BMC, loads Linux, waits for Linux, updates Linux state, and adjusts interrupt interface compatibility.
- Static boot waits for a boot-fit request, loads boot-fit via ASIC callback when requested, signals readiness via static message registers, waits for boot-loader readiness, reads boot-fit version, updates state, initializes DRAM scrambling, optionally loads Linux through the ASIC callback, handles BMC skip, waits for Linux SRAM availability, reads boot errors, and updates Linux state.

CPU-CP runtime requests mostly construct `struct cpucp_packet`, call `hdev->asic_funcs->send_cpu_message()`, and interpret `result` or DMA-returned buffers. Larger responses use `hl_cpu_accessible_dma_pool_alloc()` and pass the DMA address in the packet.

## State and Persistence Behavior

This file mutates durable per-device kernel state rather than external persistent storage. Important state includes:

- Firmware version fields: `fw_inner_major_ver`, `fw_inner_minor_ver`, `fw_sw_major_ver`, `fw_sw_minor_ver`, and `fw_sw_sub_minor_ver`.
- Firmware load state: `hdev->fw_loader.fw_comp_loaded`, dynamic descriptor validity, current dynamic response, image region, image size, boot image properties, timeouts, and skip-BMC flag.
- ASIC firmware capabilities: `fw_preboot_cpu_boot_dev_sts*`, `fw_bootfit_cpu_boot_dev_sts*`, `fw_app_cpu_boot_dev_sts*`, validity flags, `dynamic_fw_load`, `fw_security_enabled`, `hard_reset_done_by_fw`, `gic_interrupts_enable`, and reserved firmware memory.
- Runtime health: `device_cpu_disabled` is set on CPU-CP timeouts, `device_cpu_is_halted` prevents repeated halt requests, and heartbeat timestamps are updated in `heartbeat_debug_info`.
- Binning and DRAM state from preboot can update `tpc_binning`, `dram_binning`, `edma_binning`, `decoder_binning`, `rotator_binning`, and invoke ASIC property/mask recalculation.

The firmware blobs themselves are requested from the Linux firmware subsystem and released after copying. DMA buffers are allocated from a per-device gen_pool-backed CPU-accessible region and freed after each request.

## Dependencies and Integration Points

The file depends on `habanalabs.h`, `hl_boot_if.h`, `cpucp_if.h` types included through the header, kernel firmware loading, CRC32, vmalloc, PCI helpers, gen_pool, and Habanalabs tracepoints. It calls common helpers such as `hl_hw_queue_submit_bd()`, `hl_hw_queue_inc_ci_kernel()`, `hl_device_operational()`, `hl_build_hwmon_channel_info()`, `hl_get_pci_memory_region()`, and the polling/register macros from `habanalabs.h`.

Its strongest integration point is `hdev->asic_funcs`. ASIC code supplies CPU message transport, boot-fit/Linux copying for static mode, MSI layout, PLL mapping, firmware preload/loader register initialization, DRAM scrambling, DRAM property recalculation, and binning masks. Runtime users include sysfs/hwmon/info ioctl paths, reset code, heartbeat work, interrupt initialization, PCI setup, and device open/activity paths.

## Risks and Edge Cases

- CPU-CP queue serialization assumes the CPU queue behaves as an effective single-entry synchronous queue. Any alternate transport must preserve fence semantics and BD scrubbing.
- `hl_fw_send_cpu_message()` marks `device_cpu_disabled` after timeout; follow-on calls return `-EAGAIN`, so false timeouts can degrade the device until reset.
- Dynamic descriptor validation uses firmware-reported data size and copies into a temporary buffer. CRC and bounds checks are critical because descriptor addresses drive MMIO copies into SRAM/DRAM BARs.
- `hl_fw_dynamic_validate_memory_bound()` checks end address against region and BAR bounds but relies on normal unsigned arithmetic; overflow-sensitive address/size inputs should remain guarded by firmware descriptor validation and known region selection.
- Version parsing assumes specific strings containing `-fw-`, optional `-rc-`, and bounded numeric fields. Format drift clears version fields or fails boot-version processing.
- Static and dynamic boot paths both read boot-error registers in failure paths, but some warnings are intentionally non-fatal depending on masks and runtime flags such as BMC enablement.
- Some wrappers suppress logging on `-EAGAIN`, treating disabled CPU as expected during reset or device-down paths.
- Firmware feature compatibility is handled by capability bits and special cases, for example advanced CPU-CP return codes, EQ index checking, dynamic PLL map, MSI-info packet fallback, and single interrupt interface fallback.

## Test Signals

Useful validation signals include successful preboot readiness, correct dynamic/static loader selection from boot-device status bits, successful descriptor CRC/bounds validation, boot-fit/Linux state transitions, `fw_comp_loaded` bit updates, CPU queue test/heartbeat returning `CPUCP_PACKET_FENCE_VAL`, populated `asic_prop.cpucp_info`, hwmon channel creation, parsed preboot/SW versions, and no boot errors under the configured `boot_error_status_mask`. Negative tests should cover malformed firmware names/sizes, descriptor CRC mismatch, unsupported/invalid PLL indices, CPU-CP timeout and advanced return-code handling, invalid version strings, BMC skip timeout, and both static and dynamic boot failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/firmware_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs.h

## Purpose

`habanalabs.h` is the central private header for the HabanaLabs accelerator kernel driver. It defines the common driver object model, ASIC abstraction table, firmware loader state, memory-management structures, queues, command submissions, synchronization primitives, interrupts, debug/state-dump structures, reset/error tracking, register/polling macros, inline helpers, and cross-file function prototypes. Nearly every common driver subsystem and ASIC-specific implementation uses this header as the shared contract.

## Important APIs, Types, and Macros

- Global constants define driver name, PCI vendor ID, mmap offset encoding, reset flags, timeouts, queue/CQ/EQ sizes, CPU-accessible shared memory size, hash sizes, and security/protection-block parameters.
- Firmware/boot types include `enum hl_fw_component`, `enum hl_fw_types`, `struct static_fw_load_mgr`, `struct dynamic_fw_load_mgr`, `struct pre_fw_load_props`, `struct fw_image_props`, and `struct fw_load_mgr`.
- Hardware abstraction is centered on `struct hl_asic_funcs`, a large function-pointer table for lifecycle, DMA, queues, MMU, firmware messaging/loading, interrupts/events, debug, memory access, reset support, and ASIC-specific feature mapping.
- Device capabilities are held in `struct asic_fixed_properties`, covering queue properties, CPU-CP info, MMU layouts, physical memory regions, SRAM/DRAM sizes, enabled/binning masks, firmware boot status/capability bits, user interrupt ranges, cache line size, completion mode, security flags, dynamic firmware loading, page-size support, compute reset, and other ASIC feature switches.
- Runtime device ownership is represented by `struct hl_device`, which owns PCI BAR mappings, DRM/cdev devices, workqueues, kernel queues, completion/event queues, DMA pools, CPU-accessible DMA pool, locks, ASIC properties/functions, VM/MMU state, debugfs state, firmware loader state, PCI memory regions, reset/error/heartbeat state, counters, clocks, binning masks, and bring-up/testing parameters.
- User/process state is modeled by `struct hl_fpriv`, `struct hl_ctx_mgr`, and `struct hl_ctx`; command execution uses `struct hl_cs`, `struct hl_cs_job`, `struct hl_cs_parser`, `struct hl_fence`, `struct hl_cs_compl`, and multi-CS completion structs.
- Memory management structures include `struct hl_mem_mgr`, `struct hl_mmap_mem_buf`, `struct hl_cb`, `struct hl_userptr`, `struct hl_vm`, `struct hl_vm_phys_pg_pack`, `struct hl_vm_hash_node`, VA range/block descriptors, and MMU page-table metadata.
- Register and polling macros include `RREG32`, `WREG32`, read-modify-write helpers, `hl_poll_timeout()`, `hl_poll_timeout_elbi()`, `hl_poll_reg_array_timeout()`, and `hl_poll_timeout_memory()`.
- Inline helpers include `hl_get_sg_info()`, `hl_mem_area_inside_range()`, `hl_mem_area_crosses_range()`, and `to_hl_device()`.

## Control Flow and Contract Shape

The header is declarative, but it defines the control contracts followed by the implementation files:

- Device lifecycle flows through `hl_device_init()`, ASIC `early/sw/hw/late` callbacks, queue/MMU/context initialization, firmware preboot and CPU initialization, sysfs/debugfs/hwmon setup, and eventual suspend/resume/reset/fini callbacks.
- IOCTL control flows through DRM file open/release, `hl_ioctl_t` dispatch descriptors, per-FD `hl_fpriv`, per-context `hl_ctx`, and subsystem handlers for command buffers, command submissions, waits, memory, info, and debug.
- Command submissions are parsed into jobs, mapped/patched into command buffers, scheduled to hardware queues, tracked by fences and mirror lists, completed by CQ/EQ IRQ workqueues, and timed out/reset through TDR state.
- Firmware integration flows through `fw_load_mgr`, CPU-CP packet prototypes, ASIC firmware callbacks, and `asic_fixed_properties` capability bits.
- Memory mapping flows through mmap offset type encoding, mappable memory buffer behaviors, command buffers, userptr pinning, DRAM physical page packs, VA reservations, and MMU function tables for device-resident or host-resident page tables.
- Error and reset handling flows through `hl_error_info`, `hl_reset_info`, event handling prototypes, state-dump specs, heartbeat debug data, and notifier/eventfd state.

## State and Persistence Behavior

The header defines in-memory kernel state. There is no direct disk persistence, but some fields persist for the lifetime of a device, file descriptor, context, or command submission:

- Device lifetime state: `hl_device` owns hardware resources, DMA pools, BAR mappings, workqueues, IRQ queues, memory managers, reset counters, heartbeat counters, firmware loader data, and feature flags.
- Context lifetime state: `hl_ctx` owns ASID, CS sequence, pending fences, VA ranges, MMU hash tables, command-buffer VA pool, encapsulated-signal manager, and per-context counters.
- File lifetime state: `hl_fpriv` owns context manager, memory manager, notifier event, debugfs linkage, and current context pointer.
- Command lifetime state: `hl_cs` and `hl_cs_job` track job lists, fences, timeouts, staged submission metadata, encapsulated signals, timestamps, and completion/abort flags.
- Memory lifetime state is reference-counted through `kref`, `idr`, atomic mapping counters, gen_pool allocations, and per-context hash tables.
- Error state deliberately captures first/root-cause data for timeouts, RAZWI, undefined opcode, page fault, firmware error, hardware error, and engine error so later events do not automatically overwrite diagnostic context.

## Dependencies and Integration Points

This header pulls in CPU-CP, QMAN, MMU, DRM uAPI, PCI/DMA, debugfs, eventfd, rwsem, genalloc, Coresight, and dma-buf kernel interfaces, plus local `security.h`. It is included by common driver C files and ASIC-specific files for Goya, Gaudi, and Gaudi2. It exposes prototypes for device lifecycle, queues, contexts, MMU, firmware, PCI, hwmon/sysfs, command buffers, command submissions, memory, state dump, error capture, debugfs, security/protection bits, and IOCTL handlers.

The `struct hl_asic_funcs` table is the key integration boundary. Common code calls it for operations that differ by ASIC or simulator mode, while ASIC files install the table through `goya_set_asic_funcs()`, `gaudi_set_asic_funcs()`, or `gaudi2_set_asic_funcs()`. The `RREG32`/`WREG32` macros also route register access through this abstraction.

## Risks and Edge Cases

- The header is broad and tightly coupled: changing a central structure such as `hl_device`, `asic_fixed_properties`, `hl_ctx`, or `hl_asic_funcs` can affect many implementation files and ABI-like internal contracts.
- Many fields are protected by specific locks, atomics, or workqueue sequencing. Misusing `send_cpu_message_lock`, `mmu_lock`, context locks, debugfs locks, IDR locks, or interrupt spinlocks can introduce races.
- Polling macros are statement-expression macros that evaluate condition expressions repeatedly and depend on the caller's `hdev` and local variables. Callers must avoid side effects in conditions and choose sleep/timeout values correctly.
- Address range helpers must guard overflow-sensitive inputs. `hl_mem_area_inside_range()` checks `end_address > address`, while `hl_mem_area_crosses_range()` computes `address + size - 1` and expects sane nonzero sizes.
- `struct fw_load_mgr` uses a union for static vs dynamic loader state. Code must not read the inactive member after dynamic/static selection changes.
- Several booleans are stored as `u8` feature flags, and many masks are firmware- or ASIC-defined. Incorrect initialization can silently disable queues, interrupts, MMU features, or firmware loading paths.
- Debugfs stubs compile to no-ops when `CONFIG_DEBUG_FS` is disabled, so code must not depend on debugfs side effects for correctness.
- Simulator support is embedded through nullable `pdev`, ASIC register callbacks, and comments about non-upstreamed behavior. Hardware-only assumptions need to be checked against simulator paths.

## Test Signals

Strong validation includes successful compilation across supported ASIC configurations and `CONFIG_DEBUG_FS` on/off, device init/fini on each ASIC function table, static and dynamic firmware loading through the `fw_load_mgr` contract, CPU-CP message tests, queue/CQ/EQ init and interrupt handling, context create/free, command submission completion and timeout paths, MMU map/unmap/cache invalidation for host- and device-resident page tables, mmap type decoding, debugfs state-dump generation, error capture preservation, reset work sequencing, and hwmon/sysfs firmware-backed sensor reads. Header-specific regression tests should focus on structure contract changes, callback table initialization completeness, macro behavior under timeout/error paths, and lock/refcount ownership in lifecycle and teardown paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs.h -->
