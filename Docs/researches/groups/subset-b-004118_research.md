# Research: subset-b-004118

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.c

## Purpose
This is the Intel IPU3 CIO2 PCI capture driver. It exposes four CSI-2 receiver queues as V4L2 video devices and bridge subdevices, programs CIO2 CSI/MIPI/DMA registers, manages videobuf2 DMA-SG buffers through hardware FBPT/LOP tables, binds firmware-described camera sensors through the async notifier, and handles runtime and system power management.

## Important APIs, types, and functions
The file-local `formats[]` table maps supported RAW10/Y10 media-bus codes to IPU3 packed V4L2 fourccs. `cio2_find_format()` and `cio2_bytesperline()` drive format negotiation. FBPT setup is handled by `cio2_fbpt_init_dummy()`, `cio2_fbpt_entry_init_dummy()`, `cio2_fbpt_entry_init_buf()`, and `cio2_fbpt_entry_enable()`. Hardware setup and teardown are `cio2_hw_init()` and `cio2_hw_exit()`. IRQ paths are `cio2_irq()`, `cio2_irq_handle_once()`, `cio2_buffer_done()`, and `cio2_queue_event_sof()`. The vb2 operations queue, prepare, start, and stop capture through `cio2_vb2_*`; V4L2 ioctl and subdev pad operations implement format enumeration, validation, and frame-sync events. PCI entry points are `cio2_pci_probe()` and `cio2_pci_remove()`.

## Control flow and integration points
Probe first calls `ipu_bridge_init()` so missing firmware graph endpoints can be synthesized from ACPI SSDB data, then enables the PCI device, maps BAR0, enables MSI, allocates dummy DMA pages, registers media/V4L2 devices, creates four queue/subdev/video entities, requests the IRQ, and registers async sensor matches. A successful sensor bind fills `q->sensor`, CSI-2 port/lane metadata, and the per-port register base. Streaming starts from vb2: runtime PM resumes the PCI device, the media pipeline starts, CIO2 CSI/MIPI/PBM/LTR/DMA registers are programmed from active subdev format and sensor link frequency, then the remote sensor is asked to stream. Completion interrupts advance the circular FBPT queue, mark vb2 buffers done, and queue SOF frame-sync events.

## State, persistence, and dependencies
Persistent driver state lives in `struct cio2_device` and `struct cio2_queue`: current queue, streaming flag, media graph objects, active capture format, FBPT memory, queued buffer ring, dummy LOP/page safety net, frame sequence, and async notifier. Hardware state is transient MMIO programming and D0I3 runtime power state. Dependencies include PCI/MSI, DMA coherent allocation, vb2 DMA-SG, V4L2/media controller, fwnode endpoint parsing, `v4l2_get_link_freq()`, and the Intel IPU bridge.

## Risks and test signals
Risks are FBPT/LOP DMA ordering, ring index races around DMA read pointer, bad link-frequency timing, unsupported format/lane combinations, incorrect media graph validation, stale buffers across suspend, and unbalanced runtime PM on start failures. Test signals include successful probe with media graph links, `/dev/video*` and subdev nodes, `v4l2-ctl --stream-mmap` capture, SOF events, sensor stream on/off, no CSI2/DMA error logs, suspend/resume while streaming, buffer payload lengths matching `sizeimage`, and no DMA halt after queued-buffer churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.h

## Purpose
This header is the hardware and software contract for the IPU3 CIO2 driver. It defines CIO2 identity constants, image limits, queue sizes, MMIO register offsets and bit fields, CSI-2 timing coefficients, FBPT layout, and the core per-device/per-queue/per-buffer structures used by `ipu3-cio2.c`.

## Important APIs, types, and definitions
Important constants include `CIO2_PCI_ID`, `CIO2_DMA_MASK`, `CIO2_IMAGE_MAX_WIDTH/HEIGHT`, `CIO2_MAX_LOPS`, `CIO2_MAX_BUFFERS`, `CIO2_NUM_PORTS`, `CIO2_QUEUES`, and `CIO2_DMA_CHAN`. Register macros cover CSI receiver, MIPI backend, interrupt control, PBM, LTR, DMA channel registers, and pixel formatter state. `struct cio2_csi2_timing`, `struct cio2_buffer`, `struct csi2_bus_info`, `struct cio2_queue`, `struct cio2_device`, and packed `struct cio2_fbpt_entry` define driver state and DMA ABI. Inline helpers map V4L2 files and vb2 queues back to `struct cio2_queue`.

## Control flow and integration points
The `.c` file relies on these definitions when allocating DMA tables, calculating timing register values, programming MMIO blocks, decoding interrupts, validating media links, and walking queue rings. The packed FBPT structure is read and modified by both CPU and CIO2 DMA, so field order and size are part of the hardware interface. The device and queue structs tie together Linux PCI, media controller, V4L2 subdev, video_device, and vb2 subsystems.

## State, persistence, and dependencies
This header does not persist data by itself, but it defines every persistent in-memory object owned by the driver. Coherent dummy buffers and FBPTs are represented by DMA handles stored in `cio2_device` and `cio2_queue`. The macros depend on Linux bit, DMA, media, V4L2, and vb2 headers and on page-size assumptions for LOP and FBPT sizing.

## Risks and test signals
The main risks are ABI drift in the packed FBPT, incorrect register masks/shifts, wrong queue sizing derived from `PAGE_SIZE`, invalid DMA mask assumptions, and stale constants for CIO2 timing or interrupt layout. Build coverage for all include paths, sparse/packed-struct warnings, probe/register readback, streaming DMA completion, interrupt decoding, and suspend/resume buffer survival are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Kconfig

## Purpose
This Kconfig entry declares the Intel IPU6 camera driver option `VIDEO_INTEL_IPU6`, covering the 6th generation Intel Image Processing Unit used for camera capture on Intel SoCs.

## Important APIs, types, and functions
The option is a tristate named "Intel IPU6 driver". It depends on ACPI or compile testing, `VIDEO_DEV`, `X86`, DMA support, and compatibility with optional `IPU_BRIDGE`. It selects `AUXILIARY_BUS`, `IOMMU_IOVA`, `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_SG`, and `V4L2_FWNODE`.

## Control flow and integration points
Enabling this symbol builds the IPU6 core and ISYS modules through the Makefile. The selected subsystems are required by the source files in this group: auxiliary devices for ISYS/PSYS children, IOVA for IPU6 MMU DMA mapping, media controller and V4L2 subdev APIs for the camera graph, and fwnode parsing for firmware-described sensors.

## State, persistence, and dependencies
Kconfig stores only build-time configuration. Its dependency set determines whether the runtime driver can register PCI, auxiliary, media, V4L2, and DMA paths safely.

## Risks and test signals
Risks are missing selected symbols, enabling the driver on unsupported non-X86 platforms, or compile-test paths that do not cover optional bridge combinations. Test signals include `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, builds with and without `IPU_BRIDGE`, and successful module generation for both `intel_ipu6` and `intel_ipu6_isys`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Makefile

## Purpose
This Makefile defines the object composition for the IPU6 driver modules. It splits common PCI/firmware/DMA/MMU/buttress logic into `intel-ipu6.o` and input-system capture logic into `intel-ipu6-isys.o`.

## Important APIs, types, and functions
`intel-ipu6-y` includes `ipu6.o`, `ipu6-bus.o`, `ipu6-dma.o`, `ipu6-mmu.o`, `ipu6-buttress.o`, `ipu6-cpd.o`, and `ipu6-fw-com.o`. `intel-ipu6-isys-y` includes ISYS core, CSI-2, firmware ABI, video, queue, subdev, and MCD/JSL/DWC PHY implementations. Both modules are controlled by `obj-$(CONFIG_VIDEO_INTEL_IPU6)`.

## Control flow and integration points
The core module provides exported namespace symbols such as CPD parsing, buttress authentication, DMA helpers, and fw-com queues. The ISYS module consumes those symbols for capture pipelines and firmware messaging. This split mirrors runtime topology: PCI core probes the IPU, creates auxiliary devices, and ISYS binds as an auxiliary driver.

## State, persistence, and dependencies
The file has no runtime state but determines link boundaries and symbol visibility. Any source added to IPU6 must be assigned to the correct module or exported/imported symbols will fail.

## Risks and test signals
Risks include omitted objects, wrong module split, namespace/export failures, and init-order assumptions hidden by built-in builds. Test signals are modular and built-in kernel builds, `modpost` without unresolved symbols, module load/unload of `intel_ipu6` and `intel_ipu6_isys`, and probe ordering with auxiliary devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.c

## Purpose
This file implements the private IPU6 auxiliary bus glue used to expose IPU subsystems, such as ISYS and PSYS, as auxiliary devices under the PCI parent. It also attaches a runtime-PM domain that powers subsystem buttress controls around generic child suspend/resume.

## Important APIs, types, and functions
`ipu6_bus_initialize_device()` allocates `struct ipu6_bus_device`, initializes its embedded `auxiliary_device`, associates platform data and a buttress power-control descriptor, installs the PM domain, and enables runtime PM in a forbidden state. `ipu6_bus_add_device()` registers the auxiliary device, adds it to `isp->devices` under `ipu6_bus_mutex`, and allows runtime PM. `ipu6_bus_del_devices()` disables runtime PM, removes list entries, deletes auxiliary devices, and uninitializes them. `bus_pm_runtime_suspend()` and `bus_pm_runtime_resume()` wrap `pm_generic_runtime_*()` with `ipu6_buttress_power()`.

## Control flow and integration points
The PCI core initializes a bus device, then adds it so a matching auxiliary driver can bind. Runtime resume powers the subsystem first and then resumes the child driver; runtime suspend suspends the child driver first and then powers down the hardware. On power-down failure the code attempts to resume the child to leave the device usable.

## State, persistence, and dependencies
State is the allocated `ipu6_bus_device`, list membership in `isp->devices`, platform data, firmware pointers, MMU pointer, package directory data, and buttress control descriptor. Dependencies include Linux auxiliary bus, runtime PM, PM domains, PCI drvdata, and `ipu6_buttress_power()`.

## Risks and test signals
Risks are PM ordering bugs, leaked auxiliary devices on add/delete errors, use-after-free of platform data, and list races if deletion overlaps driver callbacks. Test signals include auxiliary probe/remove, runtime PM get/put cycles, power-domain transition logs, error injection for power-down failure, and clean module unload with no remaining devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.h

## Purpose
This header defines the IPU6 auxiliary device abstraction shared by the PCI core, buttress, DMA, firmware, and ISYS/PSYS auxiliary drivers.

## Important APIs, types, and functions
`struct ipu6_bus_device` embeds `struct auxiliary_device` and stores auxiliary driver metadata, list linkage, platform data, MMU, parent `ipu6_device`, buttress control, firmware image, firmware scatterlist, and firmware package directory DMA state. `struct ipu6_auxdrv_data` provides top-half and threaded IRQ callbacks plus a flag for threaded wakeup. Helper macros convert devices and auxiliary devices to `ipu6_bus_device` and access driver data. The public functions are `ipu6_bus_initialize_device()`, `ipu6_bus_add_device()`, and `ipu6_bus_del_devices()`.

## Control flow and integration points
The header is the contract between the PCI parent and auxiliary subsystem drivers. Buttress IRQ dispatch uses `auxdrv_data` callbacks. Firmware authentication and CPD package directory logic use the firmware and package fields. DMA helpers use `adev->mmu` and the auxiliary device for logging and ownership.

## State, persistence, and dependencies
The structure persists for the lifetime of each auxiliary child and is released by the auxiliary device release callback. It depends on Linux auxiliary bus, device, IRQ, list, scatterlist, and type definitions plus forward-declared IPU6-specific types.

## Risks and test signals
Risks are lifetime mismatches between embedded auxiliary device and IPU6-specific resources, stale `auxdrv_data` during IRQ dispatch, and missing initialization of firmware/MMU/package fields before consumers run. Test signals include probe/remove with KASAN, IRQs during bind/unbind, firmware load/authentication, DMA allocation through `adev->mmu`, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.c

## Purpose
This file manages the IPU6 buttress block: subsystem power, secure-mode IPC with CSE, firmware authentication, top-level interrupt dispatch, firmware image mapping, TSC synchronization, reference-clock discovery, and restore/cleanup of buttress state.

## Important APIs, types, and functions
`ipu6_buttress_init()` initializes locks, completions, CSE IPC register offsets, interrupt enables, secure-mode state, ref-clock selection, and IPC reset. `ipu6_buttress_ipc_reset()`, `ipu6_buttress_ipc_send_bulk()`, and helpers implement the CSE doorbell/CSR protocol. `ipu6_buttress_power()` changes ISYS/PSYS power/frequency controls and polls power state. `ipu6_buttress_isr()` and `ipu6_buttress_isr_threaded()` dispatch IPU subsystem IRQs and complete IPC sends/receives. `ipu6_buttress_map_fw_image()` maps firmware into PCI DMA and IPU6 IOVA space. `ipu6_buttress_authenticate()`, `ipu6_buttress_reset_authentication()`, and `ipu6_buttress_auth_done()` drive secure firmware boot. TSC APIs are `ipu6_buttress_start_tsc_sync()`, `ipu6_buttress_tsc_read()`, and `ipu6_buttress_tsc_ticks_to_ns()`.

## Control flow and integration points
Runtime PM calls `ipu6_buttress_power()` through the bus PM domain. Secure firmware boot maps firmware/package directory, writes CSE source registers, sends BOOT_LOAD, waits for security status and bootloader magic in PSYS space, then sends AUTHENTICATE_RUN. The main IRQ reads buttress status, clears it, delegates ISYS/PSYS IRQs through `ipu6_auxdrv_data`, handles CSE IPC completions, logs fatal events, disables lines needing threaded work, and reenables them from the threaded handler.

## State, persistence, and dependencies
Persistent state is `isp->buttress`: mutexes, CSE IPC completions/register offsets, constraints list, cached watchdog value, secure mode, and ref clock. It depends on buttress register definitions, PCI DMA APIs, IPU6 DMA/MMU helpers, firmware scatterlists, completions, runtime PM, and auxiliary driver IRQ callbacks.

## Risks and test signals
High-risk areas are CSE IPC reset sequencing, timeout handling, secure/non-secure mode branching, power-state polling, IRQ storm limiting, SG firmware mapping/unmapping, and TSC rollover conversion. Test signals include successful IPC reset, firmware authentication completion, no BOOT_LOAD/AUTHENTICATE timeout, runtime PM power transitions for ISYS/PSYS, IRQ handling without stuck disabled lines, firmware unmap on errors, TSC sync success, and suspend/resume restore of IRQ/WDT state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.h

## Purpose
This header declares buttress power, IPC, authentication, firmware mapping, interrupt, and TSC interfaces used across the IPU6 core and auxiliary drivers.

## Important APIs, types, and definitions
Frequency constants define allowed forced ISYS/PSYS frequency ranges. `struct ipu6_buttress_ctrl` describes subsystem frequency-control and power-status register fields. `struct ipu6_buttress_ipc` stores completion objects, CSE NACK handling, received data, and register offsets. `struct ipu6_buttress` groups mutexes, CSE IPC, constraints, watchdog cache, forced suspend flag, and reference clock. `struct ipu6_ipc_buttress_bulk_msg` describes CSE IPC commands. Public functions include IPC reset, firmware map/unmap, power control, secure-mode/authentication helpers, TSC helpers, buttress ISR functions, init/exit, CSI port config, and restore.

## Control flow and integration points
The bus PM domain calls `ipu6_buttress_power()`, the PCI driver calls init/exit and ISR entry points, CPD/firmware boot paths call map/authenticate helpers, and ISYS code uses TSC conversion for timestamps. Exported symbols form the cross-module API between `intel_ipu6` and `intel_ipu6_isys`.

## State, persistence, and dependencies
The structs are embedded in `struct ipu6_device` and persist for the PCI device lifetime. The header depends on completions, IRQ types, lists, mutexes, firmware/scatterlist forward declarations, and IPU6 bus/device types.

## Risks and test signals
Risks are struct/API changes that break module boundaries, incomplete mutex initialization, incorrect power control descriptors, and mismatched IPC register offsets. Test signals include modpost namespace checks, secure and non-secure probe paths, runtime PM transitions, firmware authentication, IRQ dispatch, and TSC timestamp consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-buttress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.c

## Purpose
This file validates Intel CPD firmware containers and builds the IPU package directory consumed by secure firmware boot/authentication. It extracts manifest, metadata, and module-data entries, validates size/layout/type constraints, and creates a DMA-visible package directory containing component addresses, sizes, IDs, versions, manifest, and metadata.

## Important APIs, types, and functions
`ipu6_cpd_validate_cpd_file()` is the public validator. It calls `ipu6_cpd_validate_cpd()`, checks the `$CPD` marker, validates manifest size, validates metadata with `ipu6_cpd_validate_metadata()`, and validates module data with `ipu6_cpd_validate_moduledata()`. `ipu6_cpd_create_pkg_dir()` allocates package-directory memory with `ipu6_dma_alloc()`, parses module data via `ipu6_cpd_parse_module_data()`, copies manifest and metadata, and syncs the allocation. `ipu6_cpd_free_pkg_dir()` releases the DMA buffer. Helpers retrieve CPD entries and metadata component IDs/versions.

## Control flow and integration points
The PCI core validates the firmware file after request_firmware and later creates a package directory for PSYS. Buttress authentication writes the package directory DMA address to firmware source registers. The parser uses metadata component IDs/versions to encode package directory entries and module-data CPD offsets to compute DMA addresses relative to the mapped firmware image.

## State, persistence, and dependencies
State is stored in `adev->pkg_dir`, `adev->pkg_dir_dma_addr`, and `adev->pkg_dir_size` until freed. Validation depends on `isp->cpd_metadata_cmpnt_size`, which differs between IPU6 variants. The code depends on bitfield helpers, DMA allocation wrappers, CPD ABI structs, and IPU6 bus/device state.

## Risks and test signals
Risks are unchecked integer/offset assumptions, malformed firmware with inconsistent CPD header lengths, component metadata-size mismatches, package-directory overflow beyond 15 entries plus header, and wrong component ID/version encoding. Test signals include valid firmware load, rejected corrupted headers/offsets/metadata, package directory DMA sync before authentication, no leaks on parse failure, and CSE authentication using the generated directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.h

## Purpose
This header defines the host-side CPD firmware container ABI used by IPU6 firmware validation and package-directory creation.

## Important APIs, types, and definitions
Constants define string/field sizes, metadata extension/image types, package directory server indices, client package type, and hash sizes for IPU6 and IPU6SE. ABI structs include `ipu6_cpd_module_data_hdr`, packed `ipu6_cpd_hdr`, `ipu6_cpd_ent`, metadata component headers and component variants, metadata extension, and client package header. Public functions are `ipu6_cpd_create_pkg_dir()`, `ipu6_cpd_free_pkg_dir()`, and `ipu6_cpd_validate_cpd_file()`.

## Control flow and integration points
`ipu6-cpd.c` uses these definitions to walk firmware blobs, while `ipu6.c` invokes validation/package setup during firmware load. Buttress authentication ultimately consumes the DMA package directory built from these ABI records.

## State, persistence, and dependencies
The header has no mutable state; its packed layouts are persisted in firmware files and must match CSE/IPU firmware expectations. It forward-declares `ipu6_device` and `ipu6_bus_device` for public APIs.

## Risks and test signals
Risks are ABI layout drift, wrong packing, incorrect hash-size selection for IPU6SE, or constants that no longer match firmware images. Test signals are firmware validation on all supported IPU6 variants, static layout checks if added, and negative tests for malformed CPD files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.c

## Purpose
This file provides IPU6 DMA allocation, mmap, SG mapping, unmapping, and cache synchronization. It bridges normal PCI DMA addresses into IPU6 IOVA space through the IPU6 MMU and tracks vmapped allocations so CPU, PCI DMA, and firmware-visible addresses remain correlated.

## Important APIs, types, and functions
`struct vm_info` tracks vmapped pages, IPU6 IOVA, virtual address, size, and list linkage. `ipu6_dma_alloc()` allocates pages, allocates an IOVA range, maps each page for PCI DMA, maps each PCI DMA address into IPU6 MMU, vmap()s pages, and records state. `ipu6_dma_free()` reverses that mapping and invalidates the IPU6 TLB. `ipu6_dma_map_sg()` converts an already PCI-DMA-mapped scatterlist to contiguous IPU6 IOVA entries, while `ipu6_dma_unmap_sg()` restores PCI DMA addresses and unmaps the IPU6 MMU. Sync helpers flush CPU cache ranges; `ipu6_dma_mmap()` inserts allocated pages into userspace VMAs.

## Control flow and integration points
Firmware communication, CPD package directories, firmware image mapping, and ISYS capture queues call these helpers to get firmware-visible memory. SG users first map through generic DMA APIs, then call IPU6 DMA mapping to rewrite SG DMA addresses into IPU6 IOVAs. Free/unmap paths must restore mappings before generic DMA unmap.

## State, persistence, and dependencies
State lives in `mmu->vma_list`, `mmu->dmap->iovad`, and the IPU6 MMU page tables. Dependencies include Linux IOVA allocation, page allocation, vmap/vunmap, cache flushing, scatterlists, PCI DMA APIs, and `ipu6_mmu_map()/unmap()/iova_to_phys()`.

## Risks and test signals
Risks are leaked IOVAs or pages on partial failures, stale cache lines when firmware reads host buffers, unsupported non-zero SG offsets, SG address restoration bugs, TLB invalidation omissions, and mismatched rounded sizes. Test signals include allocation/free stress, SG map/unmap round trips, mmap validation, firmware queue operation, IOMMU fault absence, KASAN/KMEMLEAK runs, and capture buffers surviving queue churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.h

## Purpose
This header declares IPU6 DMA/MMU mapping APIs and the `ipu6_dma_mapping` container used by the IPU6 MMU direct-map layer.

## Important APIs, types, and functions
`struct ipu6_dma_mapping` contains an `ipu6_mmu_info` pointer and an `iova_domain`. Public APIs cover cache sync for single allocations and scatterlists, DMA allocation/free, userspace mmap, SG map/unmap, and SG-table map/unmap.

## Control flow and integration points
The DMA helpers are consumed by firmware package creation, buttress firmware mapping, fw-com shared queue allocation, and ISYS video queue paths. They are part of the exported `INTEL_IPU6` namespace and rely on each `ipu6_bus_device` carrying a valid MMU pointer.

## State, persistence, and dependencies
The header has no runtime state but defines the IOVA domain holder used by `ipu6-mmu.c` and `ipu6-dma.c`. It depends on Linux IOVA, scatterlist, types, and IPU6 bus definitions.

## Risks and test signals
Risks are API misuse with unmapped or non-synced buffers, incorrect direction/attrs assumptions, and missing MMU initialization. Test signals include modular builds, firmware shared-memory setup, video buffer mapping, mmap capture paths, and clean unmap/free under error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.c

## Purpose
This file implements the generic IPU6 firmware communication layer. It allocates shared queue memory, builds firmware syscom configuration, starts/stops the firmware communication cell, and provides ring-token operations for host-to-firmware and firmware-to-host queues.

## Important APIs, types, and functions
Internal ABI structs are `ipu6_fw_sys_queue`, `ipu6_fw_sys_queue_res`, and `ipu6_fw_syscom_config`; they describe queue buffers and DMEM read/write index registers. `ipu6_fw_com_prepare()` builds one DMA allocation containing config, queue descriptors, firmware-specific config, and queue token storage. `ipu6_fw_com_open()` writes TUnit magic, syscom command/state boot parameters, config address, and starts the cell. `ipu6_fw_com_ready()`, `ipu6_fw_com_close()`, and `ipu6_fw_com_release()` manage lifecycle. `ipu6_send_get_token()/put_token()` and `ipu6_recv_get_token()/put_token()` implement lockless ring access using DMEM indices.

## Control flow and integration points
ISYS creates an `ipu6_fw_com_cfg` with queue sizes, specific firmware config, DMEM base, and callbacks. Prepare lays out memory and syncs it through `ipu6_dma_sync_single()`. Open writes boot parameters in buttress firmware parameter registers and calls the subsystem-specific start callback. Runtime command paths reserve a send token, fill it, and advance the write index; interrupt/response paths read a receive token and advance the read index.

## State, persistence, and dependencies
`struct ipu6_fw_com_context` owns the DMA buffer, IPU6 IOVA, queue descriptor arrays, DMEM base, config address, callbacks, and boot-parameter offset. The state persists while firmware communication is open. Dependencies include IPU6 DMA helpers, MMIO access, subsystem `cell_ready`/`cell_start` callbacks, and firmware syscom ABI state/command constants.

## Risks and test signals
Risks include queue layout mismatches with firmware, missing overflow checks in aggregate sizes, stale cache for config/specific data, invalid ring indices, release while firmware still running, and queue full/empty races. Test signals include ISYS firmware reaching READY, stream commands producing responses, queue wraparound, no WARN on DMEM indices, successful close/release, and firmware command timeouts only on deliberate fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.h

## Purpose
This header exposes the generic firmware communication configuration and token-queue API used by IPU6 subsystem-specific firmware layers.

## Important APIs, types, and functions
`struct ipu6_fw_syscom_queue_config` describes token count and token size. `struct ipu6_fw_com_cfg` supplies queue arrays, queue counts, DMEM address, firmware-specific configuration blob, callback hooks, and buttress boot-parameter offset. Public functions prepare, open, check readiness, close, release, and get/put send/receive tokens. `SYSCOM_BUTTRESS_FW_PARAMS_ISYS_OFFSET` identifies the ISYS boot-parameter area.

## Control flow and integration points
ISYS fills this config in `ipu6-fw-isys.c`, then uses the returned opaque `ipu6_fw_com_context` for all firmware command and response queues. The opaque context keeps the header independent of queue memory layout internals.

## State, persistence, and dependencies
The header stores no state. The config's callback pointers are critical because fw-com does not know how to start or query each subsystem cell. Dependencies are minimal forward declarations for `ipu6_fw_com_context` and `ipu6_bus_device`.

## Risks and test signals
Risks are invalid queue counts/sizes, missing callbacks, wrong DMEM or boot-parameter offset, and callers using token pointers after release. Test signals include build coverage for consumers, ISYS firmware open/close, queue full handling, and command/response traffic across all configured queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.c

## Purpose
This file adapts the generic fw-com layer to the IPU6 input-system firmware ABI. It configures ISYS queue topology, starts/stops the SP cell, sends stream/proxy commands, receives firmware responses, and provides debug dumps for stream configuration and frame buffer sets.

## Important APIs, types, and functions
`ipu6_fw_isys_init()` configures fw-com queues and opens communication. `ipu6_isys_fwcom_cfg_init()` builds proxy, device, and per-stream message queue sizes plus SRAM partitioning. `start_sp()` and `query_sp()` control the ISYS SP status register. `ipu6_fw_isys_complex_cmd()` and `ipu6_fw_isys_simple_cmd()` send stream commands. `ipu6_fw_isys_send_proxy_token()` sends proxy MMIO writes and polls `handle_proxy_response()`. `ipu6_fw_isys_close()` and `ipu6_fw_isys_cleanup()` close/release fw-com. `ipu6_fw_isys_get_resp()` and `ipu6_fw_isys_put_resp()` wrap receive-token access. Dump helpers log stream config and frame-buffer payloads.

## Control flow and integration points
On ISYS runtime bring-up, queue counts are derived from requested streams and hardware maximums, then passed to `ipu6_fw_com_prepare()` with ISYS-specific config. `ipu6_fw_com_open()` starts SP, and the code polls for READY. Stream open/start/capture/stop/flush/close commands are sent by placing payload DMA addresses into per-stream send queues. Proxy writes use the proxy send queue and wait for a matching request ID on the proxy response queue.

## State, persistence, and dependencies
State is `isys->fwcom`, protected during close by `isys->power_lock`, plus devm-allocated queue config and ISYS firmware config. The code depends on fw-com, IPU6 ISYS platform data, SP status registers, firmware ABI types, cache flushing for command payloads, and ISYS stream management code in other files.

## Risks and test signals
Risks are queue-count mismatch with firmware, failure to release fw-com after open errors, stale payload cache before commands, proxy response ID mismatches, command queue full returns, and close races with IRQ handlers. Test signals include ISYS firmware READY, stream open/start/capture responses, proxy writes completing, command timeout handling, clean runtime suspend close/reopen, and debug dumps matching configured pins/buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.h

## Purpose
This header defines the IPU6 ISYS firmware ABI: queue layout, stream sources, command/response types, frame formats, pin descriptors, stream configuration, frame buffer payloads, error records, and command/response queue tokens.

## Important APIs, types, and definitions
Constants define maximum input/output pins, stream IDs for IPU6/IPU6SE, queue bases and counts, retry/timeouts, sensor-type ranges, and pin-plane limits. Enums define response types, send command types, queue types, stream sources, CSI-2 virtual channels, firmware frame formats, pin types, MIPI store/capture/sensor modes, and firmware/proxy errors. ABI structs include `ipu6_fw_isys_fw_config`, input/output pin info, stream config, frame buffer set, response info, proxy response, and send/receive/proxy queue tokens. Public functions initialize/close/cleanup ISYS firmware communication, send simple/complex/proxy commands, get/put responses, and dump configs.

## Control flow and integration points
`ipu6-fw-isys.c` fills and sends these structures. ISYS queue/video code builds stream and frame-buffer payloads from V4L2 media graph state and capture buffers. Firmware responses identified by `ipu6_fw_isys_resp_type` drive buffer completion, SOF/EOF events, stream command acknowledgements, and error reporting.

## State, persistence, and dependencies
The header encodes shared memory layout between host and firmware, so field order and sizes are persistent ABI. It depends only on Linux types and forward declarations, but consumers depend on these definitions being identical to firmware.

## Risks and test signals
Risks include ABI drift, wrong queue base calculations, unsupported frame-format mapping, stream ID overflow, bad pin counts, and mismatched response interpretation. Test signals are firmware open/start/capture/stop across IPU6 and IPU6SE variants, response decoding for all expected types, multi-stream queue routing, and negative tests for firmware-reported errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.c

## Purpose
This file implements IPU6 ISYS CSI-2 receiver subdevices. It handles supported media-bus formats, CSI-2 timing calculation from sensor link frequency, receiver error capture/logging, stream enable/disable with PHY power, crop/format subdev operations, SOF/EOF event reporting, and remote CSI-2 frame descriptor lookup.

## Important APIs, types, and functions
`csi2_supported_codes[]` lists accepted media-bus formats. `ipu6_isys_csi2_get_link_freq()` queries the remote sensor. `ipu6_isys_csi2_calc_timing()` computes clock/data terminate and settle values. `ipu6_isys_csi2_set_stream()` programs CSI FE/PPI/IRQ registers and calls `isys->phy_set_power()`. Pad operations include `ipu6_isys_csi2_enable_streams()`, `ipu6_isys_csi2_disable_streams()`, `ipu6_isys_csi2_set_sel()`, and `ipu6_isys_csi2_get_sel()`. `ipu6_isys_csi2_init()` registers the subdevice. `ipu6_isys_register_errors()` and `ipu6_isys_csi2_error()` collect/log receiver errors. `ipu6_isys_csi2_get_remote_desc()` reads upstream frame descriptors.

## Control flow and integration points
When streams are enabled, the code translates source-pad stream masks to sink streams, calculates timing, enables receiver hardware, powers the selected PHY, and then enables the remote sensor/subdev stream. Disable reverses hardware and remote streaming. Crop operations support source-pad vertical cropping and adjust Bayer order when needed. Firmware response handling in other ISYS files calls SOF/EOF event helpers and remote descriptor lookup to route streams and virtual channels.

## State, persistence, and dependencies
Persistent state is `struct ipu6_isys_csi2`: embedded ISYS subdev, ISYS pointer, video outputs, base MMIO, receiver error bitfield, lane count, and port. Dependencies include media controller routing/streams API, V4L2 controls/events/subdev state, platform CSI register definitions, ISYS subdev helpers, and platform-specific PHY callbacks.

## Risks and test signals
Risks are link-frequency errors, invalid lane/port combinations, stream mask translation mistakes, IRQ mask/clear ordering, duplicate or missing sensor stream toggles, incorrect Bayer crop conversion, and receiver errors lost when IRQs are disabled. Test signals include media graph format/routing validation, stream enable/disable on every CSI port, SOF events, remote frame descriptor VC matching, receiver error logging under injected CSI faults, and no PHY power failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.h

## Purpose
This header declares the CSI-2 receiver data structures, pad/VC constants, timing coefficients, error descriptor type, and public CSI-2 helper APIs for IPU6 ISYS.

## Important APIs, types, and definitions
Constants define 16 virtual channels, one sink pad, eight source pads, invalid VC marker, and timing coefficients for clock/data terminate and settle registers. `struct ipu6_isys_csi2` stores the subdevice, ISYS pointer, output video objects, MMIO base, accumulated receiver errors, lane count, and port. `struct ipu6_isys_csi2_timing` carries calculated timing values. APIs cover init/cleanup, link-frequency lookup, SOF/EOF event reporting, receiver error registration/logging, and remote frame descriptor retrieval.

## Control flow and integration points
ISYS core allocates one of these structures per CSI-2 port and registers it as a V4L2 subdevice. Queue/video stream setup uses these APIs to resolve CSI-2 descriptors and generate frame events. PHY drivers consume the config/timing data passed from CSI-2 stream enable paths.

## State, persistence, and dependencies
State persists for each registered CSI-2 subdevice lifetime. The header depends on IPU6 ISYS subdev/video headers and media/V4L2 frame descriptor forward declarations.

## Risks and test signals
Risks are pad-count assumptions, VC range mismatches, timing coefficient drift, and stale structure fields after cleanup. Test signals include subdevice registration for all ports, media routing across eight source pads, frame descriptor VC validation, and stream events tied to correct CSI port and stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-dwc-phy.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-dwc-phy.c

## Purpose
This file implements the Synopsys DWC D-PHY power/configuration path for IPU6 CSI-2 receivers. It programs DPHY MMIO and test-interface registers, selects frequency ranges from sensor link rate, supports two-PHY aggregation for 4-lane ports, handles termination calibration reuse, and powers PHYs up/down for CSI-2 streaming.

## Important APIs, types, and functions
Low-level helpers include `dwc_dphy_read/write()`, mask variants, test-interface read/write helpers, `dwc_dphy_pwr_up()`, and `ipu6_isys_dwc_phy_reset()`. `freqranges[]` maps Mbps ranges to `hsfreq`, default Mbps, and DDL oscillator targets. `ipu6_isys_dwc_phy_config()` programs HSFREQRANGE, optional forced term calibration, DDL target, deskew polarity, CFGCLKFREQRANGE from buttress ref clock, and DFT controls. `ipu6_isys_dwc_phy_aggr_setup()` configures master/slave aggregated PHY clocking. Public entry point `ipu6_isys_dwc_phy_set_power()` validates port/lane, calculates Mbps, and powers the right PHY or PHY pair.

## Control flow and integration points
CSI-2 stream enable calls this via `isys->phy_set_power()`. The function reads link frequency from the matching CSI-2 subdevice, converts to Mbps, resets PHYs, configures one PHY for 1/2-lane mode or primary/secondary PHYs for 4-lane aggregation, and polls for idle/ULP readiness. Stream disable resets the relevant PHYs.

## State, persistence, and dependencies
Most state is hardware register state. `isys->phy_termcal_val` persists a term-calibration value learned from PHY E and reused later. Dependencies include ISYS platform base/register offsets, CSI-2 link-frequency helper, buttress reference clock, bitfield helpers, delays, and poll timeouts.

## Risks and test signals
Risks are unsupported link rates, bad frequency table selection, 4-lane aggregation on odd ports, test-interface timeout, stale termcal override, incorrect ref-clock calculation, and PHY not reaching idle/ULP. Test signals include successful streaming at multiple link frequencies, 1/2/4-lane configurations, aggregation on valid ports only, no DWC IFC timeout logs, stable repeated stream toggles, and CSI receiver error-free capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-dwc-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-jsl-phy.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-jsl-phy.c

## Purpose
This file implements the IPU6SE/JSL CSI-2 PHY configuration path. It programs fixed PHY/AFE tuning registers, configures port lane routing, writes CSI receiver timing values, and enables CSI RX controls for supported ports.

## Important APIs, types, and functions
`csi2_port_cfg[]` maps lane split modes to SIP port configuration values. `phy_port_cfg[]` maps driver port/lane pairs to BB indices and AFE config values. `ipu6_isys_csi2_phy_config_by_port()` applies common low-speed tuning and per-port AFE configuration. `ipu6_isys_csi2_set_port_cfg()` validates 1/2/4 lane requests and writes SIP framebuffer port config. `ipu6_isys_csi2_set_timing()` writes clock/data settle and terminate timing to SIP top registers. `ipu6_isys_csi2_rx_control()` enables CSI RX control registers. Public entry `ipu6_isys_jsl_phy_set_power()` performs enable-side configuration.

## Control flow and integration points
The CSI-2 receiver calls this through `isys->phy_set_power()` during stream enable. For `on == false`, it currently returns without extra shutdown work, leaving stream disable to CSI-2 receiver register programming. For enable, it validates the port, applies PHY config, writes DPHY timer increment, writes timing, sets port config, and enables CSI RX control.

## State, persistence, and dependencies
State is hardware register programming in the IPU/ISYS MMIO spaces. The code depends on IPU6SE platform register offsets, CSI-2 timing passed from the receiver, lane/port topology tables, and bitfield helpers.

## Risks and test signals
Risks are hard-coded tuning values, unsupported lane counts, missing shutdown sequencing, wrong BB/port mapping for board variants, and the note that this path only supports below 1.5 Gbps. Test signals include capture on ports 0 and 2 with 1/2/4 lanes, rejected unsupported lane counts, stable stream toggles, timing register readback, and no CSI receiver sync/CRC/overflow errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-jsl-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-mcd-phy.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-mcd-phy.c

## Purpose
This file implements MCD D-PHY setup for IPU6 ISYS platforms with one or two MCD PHY blocks. It applies large per-lane/port register tables for 1-, 2-, and 4-lane configurations, powers PHY blocks with reference counting, and programs all active sensor PHY configurations discovered by the async notifier.

## Important APIs, types, and functions
`common_init_regs[]` holds common PHY initialization writes. `x1_*`, `x2_*`, and `x4_*` register tables encode per-port lane configurations. `ipu6_isys_mcd_phy_powerup_ack()`, `ipu6_isys_mcd_phy_powerdown_ack()`, `ipu6_isys_mcd_phy_reset()`, and `ipu6_isys_mcd_phy_ready()` manage hub power/reset/ready state. `ipu6_isys_mcd_phy_common_init()` applies common init for PHYs represented by bound sensors. `ipu6_isys_driver_port_to_phy_port()` normalizes driver CSI port numbering to PHY port numbering and validates lane counts. `ipu6_isys_mcd_phy_config()` writes per-sensor PHY tables. Public `ipu6_isys_mcd_phy_set_power()` performs refcounted power transitions.

## Control flow and integration points
CSI-2 stream enable calls `ipu6_isys_mcd_phy_set_power()`. If the target PHY already has users, the refcount is incremented and no reconfiguration is done. Otherwise the code powers up, deasserts reset, applies common init for all bound sensors, applies per-port/lane config from notifier metadata, asserts reset release/ready sequencing, then sets refcount to one. On disable, the refcount is decremented and the PHY is powered down only when the last user stops.

## State, persistence, and dependencies
Persistent state is the static `phy_power_ref_count[]` per PHY and hardware register state. The config walker depends on `isys->notifier.done_list` entries carrying `sensor_async_sd` CSI-2 port/lane data. It also depends on IPU6 platform CSI register definitions, `isp->base`, `isys->pdata->base`, poll timeouts, and V4L2 async notifier state.

## Risks and test signals
Risks are global static refcounts across devices, notifier-list assumptions during power transitions, invalid port-to-phy remapping, table errors in hard-coded register values, unsupported 4-lane on invalid ports, and missing rollback after config/ready failures. Test signals include multi-camera concurrent streaming sharing one PHY, balanced refcount powerdown, valid 1/2/4-lane ports, PHY power/ready ack success, repeated stream toggles, and no CSI receiver errors after common/per-port config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-mcd-phy.c -->
