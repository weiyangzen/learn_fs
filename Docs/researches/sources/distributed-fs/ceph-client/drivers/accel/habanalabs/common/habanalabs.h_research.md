# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs.h

## Purpose

`habanalabs.h` is the central private header for the HabanaLabs accelerator kernel driver. It defines the common driver object model, ASIC abstraction table, firmware loader state, memory-management structures, queues, command submissions, synchronization primitives, interrupts, debug/state-dump structures, reset/error tracking, register/polling macros, inline helpers, and cross-file function prototypes. Nearly every common driver subsystem and ASIC-specific implementation uses this header as the shared contract.

## Important APIs, Types, and Macros

- Global constants define driver name, PCI vendor ID, mmap offset encoding, reset flags, timeouts, queue/CQ/EQ sizes, CPU-accessible shared memory size, hash sizes, and security/protection-block parameters.
- Firmware/boot types include `enum hl_fw_component`, `enum hl_fw_types`, `struct static_fw_load_mgr`, `struct dynamic_fw_load_mgr`, `struct pre_fw_load_props`, `struct fw_image_props`, and `struct fw_load_mgr`.
- Hardware abstraction is centered on `struct hl_asic_funcs`, a large function-pointer table for lifecycle, DMA, queues, MMU, firmware messaging/loading, interrupts/events, debug, memory access, reset support, and ASIC-specific feature mapping.
- Device capabilities are held in `struct asic_fixed_properties`, covering queue properties, CPU-CP info, MMU layouts, memory regions, SRAM/DRAM sizes, enabled/binning masks, firmware status/capability bits, interrupt ranges, completion mode, security flags, dynamic firmware loading, page-size support, compute reset, and feature switches.
- Runtime device ownership is represented by `struct hl_device`, which owns PCI BAR mappings, DRM/cdev devices, workqueues, queues, DMA pools, locks, ASIC properties/functions, VM/MMU state, debugfs state, firmware loader state, PCI memory regions, reset/error/heartbeat state, counters, clocks, binning masks, and bring-up/testing parameters.
- User/process state is modeled by `struct hl_fpriv`, `struct hl_ctx_mgr`, and `struct hl_ctx`; command execution uses `struct hl_cs`, `struct hl_cs_job`, `struct hl_cs_parser`, `struct hl_fence`, `struct hl_cs_compl`, and multi-CS completion structs.
- Memory management structures include `struct hl_mem_mgr`, `struct hl_mmap_mem_buf`, `struct hl_cb`, `struct hl_userptr`, `struct hl_vm`, `struct hl_vm_phys_pg_pack`, `struct hl_vm_hash_node`, VA range/block descriptors, and MMU page-table metadata.
- Register and polling macros include `RREG32`, `WREG32`, read-modify-write helpers, `hl_poll_timeout()`, `hl_poll_timeout_elbi()`, `hl_poll_reg_array_timeout()`, and `hl_poll_timeout_memory()`.
- Inline helpers include `hl_get_sg_info()`, `hl_mem_area_inside_range()`, `hl_mem_area_crosses_range()`, and `to_hl_device()`.

## Control Flow and Contract Shape

The header is declarative, but it defines the control contracts followed by the implementation files. Device lifecycle flows through `hl_device_init()`, ASIC `early/sw/hw/late` callbacks, queue/MMU/context initialization, firmware initialization, sysfs/debugfs/hwmon setup, and suspend/resume/reset/fini callbacks. IOCTL control flows through DRM file open/release, `hl_ioctl_t` dispatch descriptors, per-FD `hl_fpriv`, per-context `hl_ctx`, and handlers for command buffers, command submissions, waits, memory, info, and debug. Command submissions are parsed into jobs, mapped or patched into command buffers, scheduled to hardware queues, tracked by fences and mirror lists, completed by IRQ workqueues, and timed out/reset through TDR state. Memory mapping flows through mmap type encoding, mappable memory buffer behaviors, command buffers, userptr pinning, DRAM page packs, VA reservations, and MMU function tables.

## State and Persistence Behavior

The header defines in-memory kernel state. Device lifetime state lives in `hl_device`: hardware resources, DMA pools, BAR mappings, workqueues, IRQ queues, memory managers, reset counters, heartbeat counters, firmware loader data, and feature flags. Context lifetime state lives in `hl_ctx`: ASID, CS sequence, pending fences, VA ranges, MMU hash tables, command-buffer VA pool, encapsulated-signal manager, and counters. File lifetime state lives in `hl_fpriv`: context manager, memory manager, notifier event, debugfs linkage, and current context. Command lifetime state lives in `hl_cs` and `hl_cs_job`: job lists, fences, timeouts, staged submission metadata, encapsulated signals, timestamps, and completion/abort flags. Error state deliberately captures first/root-cause data for timeouts, RAZWI, undefined opcode, page fault, firmware error, hardware error, and engine error.

## Dependencies and Integration Points

This header pulls in CPU-CP, QMAN, MMU, DRM uAPI, PCI/DMA, debugfs, eventfd, rwsem, genalloc, Coresight, dma-buf, and local security interfaces. It exposes prototypes for device lifecycle, queues, contexts, MMU, firmware, PCI, hwmon/sysfs, command buffers, command submissions, memory, state dump, error capture, debugfs, security/protection bits, and IOCTL handlers. The `struct hl_asic_funcs` table is the key integration boundary: common code calls it for operations that differ by ASIC or simulator mode, while ASIC files install the table through `goya_set_asic_funcs()`, `gaudi_set_asic_funcs()`, or `gaudi2_set_asic_funcs()`. `RREG32` and `WREG32` route register access through this abstraction.

## Risks and Edge Cases

- The header is broad and tightly coupled; changing central structures or callback signatures affects many implementation files.
- Many fields require specific locks, atomics, workqueue sequencing, or IDR/refcount ownership.
- Polling macros are statement-expression macros that evaluate conditions repeatedly and depend on caller-local variables.
- Address range helpers must be used with overflow- and zero-size-aware inputs.
- `struct fw_load_mgr` uses a union for static vs dynamic loader state, so code must only read the active member.
- `u8` feature flags and firmware masks must be initialized consistently or queues, interrupts, MMU features, or firmware boot paths can silently change.
- Debugfs stubs compile to no-ops when `CONFIG_DEBUG_FS` is disabled.
- Simulator support through nullable `pdev` and ASIC register callbacks means hardware-only assumptions need explicit checks.

## Test Signals

Strong validation includes successful compilation across supported ASIC configurations and `CONFIG_DEBUG_FS` modes, device init/fini on each ASIC function table, static and dynamic firmware loading through the `fw_load_mgr` contract, CPU-CP message tests, queue/CQ/EQ init and interrupt handling, context create/free, command submission completion and timeout paths, MMU map/unmap/cache invalidation for host- and device-resident page tables, mmap type decoding, debugfs state-dump generation, error capture preservation, reset work sequencing, and hwmon/sysfs firmware-backed sensor reads. Header-specific regression tests should focus on structure contract changes, callback table initialization completeness, macro behavior under timeout/error paths, and lock/refcount ownership in lifecycle and teardown paths.
