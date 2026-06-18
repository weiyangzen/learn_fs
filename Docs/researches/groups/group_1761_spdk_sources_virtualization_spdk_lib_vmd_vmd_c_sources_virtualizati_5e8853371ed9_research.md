# Group Research: group_1761_spdk_sources_virtualization_spdk_lib_vmd_vmd_c_sources_virtualizati_5e8853371ed9

Scope: `Docs/research_subset_a.md` only. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vmd/vmd.c -->
# File Research: sources/virtualization/spdk/lib/vmd/vmd.c

## Purpose

Implements SPDK's Intel VMD PCI device provider. It discovers VMD controllers, maps their config/memory BARs, enumerates PCIe topology behind each VMD, exposes downstream NVMe endpoints as SPDK PCI devices of type `"vmd"`, and handles VMD hotplug/hotremove/rescan paths.

## Main Responsibilities

- Maintains global `g_vmd_container`, with up to `MAX_VMD_SUPPORTED` adapters.
- Maps VMD BAR0 as config space and BAR2 as memory window.
- Walks PCI buses behind VMD using config-space MMIO and constructs `vmd_pci_bus` / `vmd_pci_device` trees.
- Assigns BAR windows for endpoints and bridges, including a small per-hotplug-port memory allocator.
- Detects PCI/PCIe capabilities: PCIe, MSI, MSI-X, serial number.
- Hooks VMD-backed NVMe endpoints into the SPDK NVMe PCI driver via `spdk_pci_hook_device`.
- Registers a PCI provider named `vmd` with attach/detach callbacks.
- Provides public VMD operations:
  - `spdk_vmd_init`
  - `spdk_vmd_fini`
  - `spdk_vmd_pci_device_list`
  - `spdk_vmd_hotplug_monitor`
  - `spdk_vmd_remove_device`
  - `spdk_vmd_rescan`
  - `vmd_find_device`

## Key Control Flow

- `spdk_vmd_init()` calls `spdk_pci_enumerate(spdk_pci_vmd_get_driver(), vmd_enum_cb, ...)`.
- `vmd_enum_cb()` enables memory/bus mastering, initializes `vmd_adapter`, maps VMD BARs, increments adapter count, then calls `vmd_enumerate_devices()`.
- `vmd_enumerate_devices()` selects the VMD internal bus range, including ICX bus restriction handling, then calls `vmd_scan_pcibus()`.
- `vmd_scan_pcibus()` clears stale root-port config, scans depth-first with `vmd_scan_single_bus()`, logs topology, and caches scan-complete signatures in root-port prefetch upper registers.
- `vmd_scan_single_bus()` allocates device objects, distinguishes bridges from endpoints, allocates downstream bus numbers, initializes hotplug windows, recursively scans bridges, and initializes endpoints with `vmd_init_end_device()`.
- `vmd_init_end_device()` assigns BARs, sets up MSI-X masking/enabling, initializes the embedded `spdk_pci_device`, and hooks supported NVMe devices.

## Data Structures

Defined mostly in `vmd_internal.h`, used here as mutable runtime state:

- `vmd_container`: fixed global array of VMD adapters.
- `vmd_adapter`: per-controller BAR mappings, bus list, target NVMe list, address window state.
- `vmd_pci_bus`: topology node with bus numbers and device list.
- `vmd_pci_device`: SPDK PCI wrapper plus raw config-space header/capability pointers and BAR metadata.
- `vmd_hot_plug`: per-hotplug bridge memory allocator and reserved bus state.
- `pci_mem_mgr`: free/allocated/unused region descriptors for hotplug BAR allocation.

## Dependencies

- SPDK PCI/env APIs: `spdk_pci_enumerate`, `spdk_pci_device_map_bar`, `spdk_pci_hook_device`, `spdk_pci_unhook_device`, `spdk_pci_device_detach`.
- SPDK NVMe PCI driver lookup: `spdk_pci_nvme_get_driver`.
- PCI constants and packed register layouts from `vmd_spec.h`.
- Internal runtime structs from `vmd_internal.h`.

## Notable Behaviors

- Only storage express class devices (`PCI_CLASS_STORAGE_EXPRESS`) are treated as supported endpoints.
- VMD-backed PCI devices always use function 0 in attach path.
- Reuses root-port prefetch upper registers as scan-complete signatures.
- For IOMMU/IOVA correctness, VMD BAR physical addresses are read from config space rather than trusting `spdk_pci_device_map_bar()` physical output.
- Hotplug monitor checks PCIe slot/link status, scans for new devices after link-up, and marks missing devices pending removal on link-down.
- Multifunction devices are assumed absent behind VMD.

## Risks / Caveats

- Much of the code manipulates volatile PCI config-space register structs directly; correctness depends on struct layout matching hardware.
- Hotplug memory allocation has a fixed descriptor count (`ADDR_ELEM_COUNT`) and fixed reserved hotplug buses (`RESERVED_HOTPLUG_BUSES`).
- Only 32-bit bridge memory base/limit paths are handled in comments around base/limit propagation.
- Several error paths return generic `-1` or `-ENODEV`, so diagnostics depend heavily on SPDK logs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vmd/vmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vmd/vmd_internal.h -->
# File Research: sources/virtualization/spdk/lib/vmd/vmd_internal.h

## Purpose

Internal VMD runtime declarations shared by `vmd.c`. It defines the in-memory representation of VMD adapters, VMD-visible PCI buses/devices, BAR mappings, and hotplug memory bookkeeping.

## Key Contents

- Includes SPDK public VMD/env/util/log headers and `vmd_spec.h`.
- Forward declarations for VMD hotplug, adapter, and PCI device objects.
- `struct pci_bars`: virtual address, physical/start address, and size for a BAR.
- `struct vmd_pci_bus`: bus topology node with parent/self pointers, bus number fields, hotplug flags, and device list.
- `struct pci_mem_mgr`: memory-region descriptor used by hotplug BAR allocation queues.
- `struct vmd_hot_plug`: fixed hotplug window state, slot status cache, reserved bus numbers, and free/allocated/unused memory-region queues.
- `struct vmd_pci_device`: embeds `struct spdk_pci_device`, BAR array, parent/subordinate bus links, volatile config/capability pointers, identity/class fields, and hotplug flags.
- `struct vmd_adapter`: one VMD controller, including mapped BARs, VMD bus root, discovered targets, bus list, and scan state.
- Declares `vmd_find_device()`.

## Relationships

- Consumed directly by `vmd.c`.
- Depends on PCI register/capability layouts in `vmd_spec.h`.
- The embedded `spdk_pci_device` lets VMD downstream devices be passed through normal SPDK PCI driver machinery.

## Notes

- Several bitfields pack bus/domain/hotplug state; layout is internal and not serialized.
- Hotplug memory region count is fixed by `ADDR_ELEM_COUNT`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vmd/vmd_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vmd/vmd_spec.h -->
# File Research: sources/virtualization/spdk/lib/vmd/vmd_spec.h

## Purpose

Defines VMD/PCI/PCIe constants and register-layout structs used by the VMD implementation for direct PCI config-space access.

## Key Contents

- VMD limits and signatures:
  - `MAX_VMD_SUPPORTED`
  - `VMD_UPPER_BASE_SIGNATURE`
  - `VMD_UPPER_LIMIT_SIGNATURE`
- VMD config registers:
  - `PCI_VMD_VMCAP`
  - `PCI_VMD_VMCONFIG`
- PCI BAR, bridge, bus, class, command, and capability constants.
- Hotplug and memory-window constants:
  - `ADDR_ELEM_COUNT`
  - `PCI_MAX_BUS_NUMBER`
  - `RESERVED_HOTPLUG_BUSES`
  - `BAR_SIZE`
- PCI capability layouts:
  - enhanced capability header
  - serial number capability
  - common/type-0/type-1 PCI headers
  - MSI and MSI-X capability/table structs
  - PCIe capability unions for slot/link/root registers
- `struct pci_header` union wrapper for common/type-0/type-1 access.

## Relationships

- Included by `vmd_internal.h`, then used throughout `vmd.c`.
- Provides the raw register views that `vmd.c` casts over MMIO config space.

## Notes

- This is hardware ABI-style code; field order and widths are critical.
- Macros such as `CONFIG_OFFSET_ADDR` encode VMD config-space addressing assumptions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vmd/vmd_spec.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/Makefile -->
# File Research: sources/virtualization/spdk/module/Makefile

## Purpose

Top-level SPDK module build Makefile. It selects module subdirectories and generates module/system pkg-config files.

## Key Contents

- Sets `SPDK_ROOT_DIR` and includes common/module make fragments.
- Always builds core module directories: `bdev blob accel event sock scheduler keyring`.
- Conditionally adds:
  - `env_dpdk` when `CONFIG_ENV` is DPDK env.
  - `fsdev` when `CONFIG_FSDEV=y`.
  - `vfu_device` when `CONFIG_VFIO_USER=y`.
- Defines dependency ordering between module subdirs.
- Generates pkg-config files for bdev, accel, sock, scheduler, keyring, and syslibs.
- Filters build-tree `-L` paths from installed syslibs and replaces them with install libdir.

## Relationships

- `module/accel/Makefile` is one of the subdirectories reached through `DIRS-y`.
- Uses `scripts/pc_modules.sh` and `scripts/pc_libs.sh`.
- Installs/uninstalls generated pkg-config artifacts.

## Notes

- Build composition is driven by config variables from SPDK make infrastructure.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/Makefile

## Purpose

Build dispatcher for SPDK accel modules.

## Key Contents

- Always builds `error`, `ioat`, and `ae4dma`.
- Conditionally builds:
  - `dpdk_compressdev` for `CONFIG_DPDK_COMPRESSDEV`
  - `dsa` and `iaa` for `CONFIG_IDXD`
  - `dpdk_cryptodev` for `CONFIG_CRYPTO`
  - `cuda` for `CONFIG_CUDA`
  - `mlx5` when `CONFIG_RDMA_PROV=mlx5_dv`
- Delegates subdir traversal through `spdk.subdirs.mk`.

## Relationships

- Parent is `module/Makefile`.
- Child Makefiles define individual shared/static module libraries.

## Notes

- This file controls which hardware/software accel backends appear in a build.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/ae4dma/Makefile

## Purpose

Builds the AMD AE4DMA accel module library.

## Key Contents

- `LIBNAME = accel_ae4dma`
- Sources:
  - `accel_ae4dma.c`
  - `accel_ae4dma_rpc.c`
- Shared object version: `SO_VER := 2`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Included when `module/accel/Makefile` selects `ae4dma`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.c -->
# File Research: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.c

## Purpose

Implements an SPDK accel backend for AMD AE4DMA hardware, currently supporting copy operations.

## Main Responsibilities

- Registers an `spdk_accel_module_if` named `"ae4dma"` when enabled.
- Probes AE4DMA PCI devices with `spdk_ae4dma_probe`.
- Claims matching PCI devices and tracks them for detach.
- Allocates per-thread IO channels from hardware queues.
- Submits SPDK copy tasks via `spdk_ae4dma_build_copy`.
- Polls AE4DMA completions with `spdk_ae4dma_process_events`.
- Flushes built descriptors after batched submissions.
- Emits JSON config entry for `ae4dma_scan_accel_module`.

## Key Data

- `AE4DMA_MAX_CHANNELS = 2`.
- `g_ae4dma_enable`, `g_ae4dma_initialized`.
- `ae4dma_device`: hardware channel pointer and available queue count.
- `ae4dma_io_channel`: selected AE4DMA channel, queue id, and poller.
- Global device and PCI-device TAILQs guarded by `g_ae4dma_mutex` for queue allocation.

## Supported Operations

- `SPDK_ACCEL_OPC_COPY` only.

## Notes / Risks

- `ae4dma_supports_opcode()` asserts if queried before initialization.
- Device queue allocation is simple first-fit across devices.
- `probe_cb()` allocates a `pci_device` before claiming; if claim fails, the allocated entry is not removed in that local path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.h -->
# File Research: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.h

## Purpose

Small public-internal header for the AE4DMA accel module.

## Key Contents

- Header guard `SPDK_ACCEL_MODULE_AE4DMA_H`.
- Includes `spdk/stdinc.h`.
- Declares `void accel_ae4dma_enable_probe(void);`

## Relationships

- Used by `accel_ae4dma.c` and `accel_ae4dma_rpc.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma_rpc.c

## Purpose

Defines the startup RPC for enabling the AE4DMA accel module.

## Key Contents

- RPC handler `rpc_ae4dma_scan_accel_module`.
- Rejects any non-null parameters.
- Logs enablement, calls `accel_ae4dma_enable_probe()`, and returns JSON boolean `true`.
- Registers RPC:
  - `ae4dma_scan_accel_module`
  - startup phase only.

## Relationships

- Calls the enable function declared in `accel_ae4dma.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/cuda/Makefile

## Purpose

Builds the CUDA accel module library.

## Key Contents

- `LIBNAME = accel_cuda`
- C sources:
  - `accel_cuda.c`
  - `accel_cuda_rpc.c`
  - `cuda_utils.c`
- CUDA source:
  - `accel_cuda_kern.cu`
- Sets `CUDA_ARCH = 70`.
- Shared object version: `SO_VER := 7`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_CUDA`.
- The report group includes headers and C helpers but not the `.cu` implementation file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda.c -->
# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda.c

## Purpose

Implements an SPDK accel backend using CUDA streams and CUDA kernels for copy, fill, and XOR operations.

## Main Responsibilities

- Registers accel module `"accel_cuda"` after `cuda_scan_accel_module`.
- Verifies CUDA device availability with `cudaGetDeviceCount`.
- Creates a CUDA memory map via `cuda_utils_create_mem_map`.
- Creates per-channel CUDA streams and DMA buffers for kernel parameters/status.
- Schedules tasks onto idle streams, queues overflow tasks, and completes tasks from a poller.
- Falls back to software XOR for small XOR requests or too many sources.
- Emits JSON config for `cuda_scan_accel_module`.

## Key Data

- `ACCEL_CUDA_STREAMS_PER_CHANNEL = 4`.
- `ACCEL_CUDA_XOR_MIN_BUF_LEN = 4096`.
- `cuda_task`: SPDK task extension used in queues.
- `cuda_stream`: CUDA stream, current task, input pointer array, and status byte.
- `cuda_io_channel`: waiting/completion queues, idle stream queue, poller, per-stream buffers.

## Supported Operations

- `SPDK_ACCEL_OPC_XOR`
- `SPDK_ACCEL_OPC_FILL`
- `SPDK_ACCEL_OPC_COPY`

## Key Control Flow

- Submit functions validate task shape and call `_accel_cuda_start_request`.
- `_accel_cuda_submit_request` takes an idle stream, sets status to `-1`, launches the relevant CUDA kernel wrapper, and increments running count.
- `accel_cuda_poller` scans stream status bytes for completion, recycles streams, starts queued tasks, and completes finished SPDK accel tasks.

## Dependencies

- CUDA Runtime API.
- Kernel launch wrappers from `accel_cuda_kern.h`.
- Memory registration helper from `cuda_utils.h`.
- SPDK accel, env, thread, JSON, and XOR helpers.

## Notes / Risks

- Kernel completion is inferred from a status byte written by CUDA-side work; the `.cu` file defines the actual semantics.
- Only XOR has a software fallback; copy/fill require CUDA launch success.
- Channel creation allocates CUDA streams and SPDK DMA memory; failures clean up partially allocated resources.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda.h -->
# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda.h

## Purpose

Internal header for CUDA accel module configuration and enablement.

## Key Contents

- Header guard `SPDK_ACCEL_MODULE_CUDA_H`.
- Defines:
  - `ACCEL_CUDA_XOR_MIN_BUF_LEN 4096`
  - `ACCEL_CUDA_STREAMS_PER_CHANNEL 4`
- Declares `void accel_cuda_enable_probe(void);`

## Relationships

- Used by CUDA RPC and implementation files.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda_kern.h -->
# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda_kern.h

## Purpose

C/C++ ABI header for CUDA kernel launch wrappers used by `accel_cuda.c`.

## Key Contents

- Header guard `SPDK_ACCEL_CUDA_KERN_H`.
- `extern "C"` wrappers for C++ compilation.
- Defines:
  - `CUDA_CACHE_LINE_SIZE 128`
  - `CUDA_XOR_MAX_SOURCES 16`
- Declares launch functions:
  - `accel_cuda_xor_start`
  - `accel_cuda_copy_start`
  - `accel_cuda_fill_start`

## Relationships

- Implemented by CUDA source `accel_cuda_kern.cu` outside this requested group.
- Called from `accel_cuda.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda_kern.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda_rpc.c

## Purpose

Defines startup RPC for enabling the CUDA accel module.

## Key Contents

- RPC handler `rpc_cuda_scan_accel_module`.
- Rejects non-null params.
- Logs enablement, calls `accel_cuda_enable_probe()`, returns JSON boolean `true`.
- Registers:
  - `cuda_scan_accel_module`
  - startup phase only.

## Relationships

- Calls `accel_cuda_enable_probe()` from `accel_cuda.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/accel_cuda_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/cuda_utils.c -->
# File Research: sources/virtualization/spdk/module/accel/cuda/cuda_utils.c

## Purpose

Provides process-wide CUDA host-memory registration support through SPDK memory-map notifications.

## Main Responsibilities

- Registers memory with CUDA on SPDK memory-map register notifications using `cudaHostRegister(..., cudaHostRegisterMapped)`.
- Unregisters memory on unregister notifications with `cudaHostUnregister`.
- Maintains one global `cuda_mem_map` with reference counting.
- Provides:
  - `cuda_utils_create_mem_map`
  - `cuda_utils_free_mem_map`

## Key Data

- `struct cuda_mem_map`: SPDK mem map pointer plus refcount.
- `g_cuda_mem_map`: singleton map.
- `g_cuda_maps_mutex`: protects singleton/refcount.

## Dependencies

- CUDA Runtime API.
- SPDK `spdk_mem_map_alloc/free` notification mechanism.

## Notes / Risks

- All CUDA accel users share a single process-wide map.
- Registration failures return `-ENOMEM`, so memory-map creation can fail if CUDA cannot register an existing SPDK memory range.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/cuda_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/cuda_utils.h -->
# File Research: sources/virtualization/spdk/module/accel/cuda/cuda_utils.h

## Purpose

Header for CUDA memory-map helper API.

## Key Contents

- Opaque `struct cuda_mem_map`.
- Declares:
  - `struct cuda_mem_map *cuda_utils_create_mem_map(void);`
  - `void cuda_utils_free_mem_map(struct cuda_mem_map **map);`
- C++ compatible `extern "C"` block.

## Relationships

- Used by `accel_cuda.c` and implemented by `cuda_utils.c`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/cuda/cuda_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/Makefile

## Purpose

Builds the DPDK compressdev accel module.

## Key Contents

- Adds `$(ENV_CFLAGS)`.
- `LIBNAME = accel_dpdk_compressdev`
- Sources:
  - `accel_dpdk_compressdev.c`
  - `accel_dpdk_compressdev_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_DPDK_COMPRESSDEV`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.c -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.c

## Purpose

Implements an SPDK accel compression backend using DPDK compressdev PMDs for stateless deflate compression/decompression.

## Main Responsibilities

- Enables and registers accel module `"dpdk_compressdev"`.
- Discovers DPDK compressdev devices and configures queue pairs.
- Creates shared compression and decompression xforms.
- Maintains global device/qpair inventory and assigns one qpair per SPDK IO channel.
- Converts SPDK iovecs into DPDK mbuf chains using external buffers.
- Enqueues one DPDK compression op per SPDK accel task.
- Polls completions and completes SPDK tasks.
- Supports PMD selection: auto, QAT-only, MLX5 PCI-only, UADK-only.
- Writes config JSON for `compressdev_scan_accel_module`.

## Key Data

- PMD names:
  - `compress_qat`
  - `mlx5_pci`
  - `compress_uadk`
- `compress_dev`: DPDK device info, cdev id, shared xforms, SGL support, qpair list.
- `comp_device_qp`: unique device/qpair assignment record.
- `compress_io_channel`: selected PMD/qpair, poller, mbuf arrays, queued tasks.
- Global mempools:
  - `g_mbuf_mp`
  - `g_comp_op_mp`

## Supported Operations

- `SPDK_ACCEL_OPC_COMPRESS`
- `SPDK_ACCEL_OPC_DECOMPRESS`

## Supported Algorithms

- `SPDK_ACCEL_COMP_ALGO_DEFLATE`
- Level range reports min/max as `0/0`; hardware xform uses max deflate level by default.

## Key Control Flow

- `accel_compress_init()` optionally initializes UADK vdev, initializes all compressdevs, then registers IO device.
- `create_compress_dev()` configures a compressdev, queue pairs, starts it, creates private xforms, and records qpair objects.
- `_compress_operation()` calculates needed mbufs, attaches source/destination external buffers, checks SGL capability, sets xform, and enqueues the DPDK operation.
- `comp_dev_poller()` dequeues operations, updates output size, completes tasks, frees mbufs/op, and retries queued tasks.

## Notes / Risks

- The code uses DPDK dynamic mbuf fields to store the SPDK task pointer.
- `_setup_compress_mbuf()` splits buffers around physical-contiguity/size limits and chains mbufs.
- Channel creation picks the device with the most free qpairs for the chosen PMD.
- Module unregister destroys `g_comp_device_qp_lock`, making repeated lifecycle assumptions worth reviewing.
- Some error paths assert after failed operations, indicating expectation that normal runtime backpressure should be queued rather than fatal.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.h -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.h

## Purpose

Header for DPDK compressdev accel module enablement and PMD selection.

## Key Contents

- `enum compress_pmd`:
  - `COMPRESS_PMD_AUTO`
  - `COMPRESS_PMD_QAT_ONLY`
  - `COMPRESS_PMD_MLX5_PCI_ONLY`
  - `COMPRESS_PMD_UADK_ONLY`
  - `COMPRESS_PMD_MAX`
- Declares:
  - `void accel_dpdk_compressdev_enable(void);`
  - `int accel_compressdev_enable_probe(enum compress_pmd *opts);`

## Relationships

- Used by module implementation and RPC file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev_rpc.c

## Purpose

Defines startup RPC for enabling/configuring the DPDK compressdev accel module.

## Key Contents

- Decodes `pmd` from `rpc_compressdev_scan_accel_module_ctx`.
- Validates `pmd < COMPRESS_PMD_MAX`.
- Calls `accel_compressdev_enable_probe(&req.pmd)`.
- Calls `accel_dpdk_compressdev_enable()`.
- Returns JSON boolean `true`.
- Registers:
  - `compressdev_scan_accel_module`
  - startup phase only.

## Relationships

- Uses generated RPC context from `spdk_internal/rpc_autogen.h`.
- Calls API from `accel_dpdk_compressdev.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_compressdev/accel_dpdk_compressdev_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/Makefile

## Purpose

Builds the DPDK cryptodev accel module.

## Key Contents

- Adds `$(ENV_CFLAGS)`.
- `LIBNAME = accel_dpdk_cryptodev`
- Sources:
  - `accel_dpdk_cryptodev.c`
  - `accel_dpdk_cryptodev_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_CRYPTO`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.c -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.c

## Purpose

Implements an SPDK accel encryption/decryption backend using DPDK cryptodev PMDs.

## Main Responsibilities

- Registers accel module `"dpdk_cryptodev"` when enabled.
- Supports runtime/startup driver selection among AESNI_MB, QAT, MLX5 PCI, and UADK.
- Initializes DPDK virtual PMDs for AESNI_MB/UADK when selected.
- Discovers/configures cryptodev devices and queue pairs.
- Maintains per-driver qpair assignment for each SPDK IO channel.
- Splits SPDK crypto accel tasks into block-sized DPDK crypto ops.
- Uses LBA-derived IV values, incremented per crypto block.
- Tracks partial submissions, queued tasks, and poller completions.
- Creates and destroys DPDK crypto sessions for SPDK crypto keys.
- Reports cipher support and operation alignment requirements.

## Key Data

- Supported PMD names:
  - `crypto_aesni_mb`
  - `crypto_qat`
  - `mlx5_pci`
  - `crypto_uadk`
- Explicitly skips unsupported `crypto_qat_asym`.
- Supported ciphers:
  - AES-CBC for QAT, UADK, AESNI_MB.
  - AES-XTS for QAT, UADK, AESNI_MB, MLX5 PCI.
- `accel_dpdk_cryptodev_device`: DPDK device metadata and qpair list.
- `accel_dpdk_cryptodev_qp`: queue-pair state, outstanding op count, and QAT spread index.
- `accel_dpdk_cryptodev_key_priv`: selected driver, cipher, optional concatenated XTS key, and per-device key handles.
- `accel_dpdk_cryptodev_task`: SPDK task extension tracking total/submitted/completed crypto ops.
- Global mempools for sessions, mbufs, and crypto ops.

## Supported Operations

- `SPDK_ACCEL_OPC_ENCRYPT`
- `SPDK_ACCEL_OPC_DECRYPT`

## Key Control Flow

- `accel_dpdk_cryptodev_init()` creates vdev if needed, registers mbuf dynamic field, creates mempools, configures all DPDK crypto devices, and registers IO device.
- `_accel_dpdk_cryptodev_create_cb()` assigns one qpair per available driver to the channel and starts the poller.
- `accel_dpdk_cryptodev_submit_tasks()` detects in-place vs out-of-place operation, initializes task counters, and calls `accel_dpdk_cryptodev_process_task()`.
- `accel_dpdk_cryptodev_process_task()` validates key/module ownership, computes block count, caps batch size, allocates mbufs/ops, attaches iov blocks, sets IV and session, enqueues burst, and handles partial enqueue cases.
- `accel_dpdk_cryptodev_poller()` drains qpair completions, frees DPDK resources, completes tasks, and retries queued work.
- `accel_dpdk_cryptodev_key_init()` allocates key-private state, concatenates XTS keys for DPDK, and creates encrypt/decrypt sessions on selected devices.

## Notes / Risks

- One crypto op corresponds to one `block_size` chunk, because IV is based on logical block number.
- QAT qpair selection spreads work using a `32` qpair stride.
- MLX5 keys are bound to a specific device/protection domain, so keys are registered per MLX5 device.
- For QAT, `get_operation_info` requires alignment based on `block_size`.
- Key deinit wipes key handles and XTS concatenated key memory with `spdk_memset_s`.
- `accel_dpdk_cryptodev_fini()` only unregisters if `g_crypto_op_mp` exists; if init did not complete, fini has little to do.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.h -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.h

## Purpose

Header for DPDK cryptodev accel module control and driver conversion.

## Key Contents

- Includes public module enum header `spdk/module/accel/dpdk_cryptodev.h`.
- Declares:
  - `void accel_dpdk_cryptodev_enable(void);`
  - `int accel_dpdk_cryptodev_set_driver(enum spdk_accel_dpdk_cryptodev_driver driver);`
  - `enum spdk_accel_dpdk_cryptodev_driver accel_dpdk_cryptodev_get_driver(void);`
  - `const char *accel_dpdk_cryptodev_driver_to_str(enum spdk_accel_dpdk_cryptodev_driver driver);`

## Relationships

- Used by implementation and RPC file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev_rpc.c

## Purpose

Defines RPCs for enabling and selecting/querying the DPDK cryptodev accel driver.

## Key RPCs

- `dpdk_cryptodev_scan_accel_module`
  - startup only
  - rejects params
  - calls `accel_dpdk_cryptodev_enable()`
- `dpdk_cryptodev_set_driver`
  - startup only
  - decodes `driver_name`
  - calls `accel_dpdk_cryptodev_set_driver()`
- `dpdk_cryptodev_get_driver`
  - startup and runtime
  - rejects params
  - returns current driver string

## Relationships

- Uses generated RPC decode helpers from `spdk_internal/rpc_autogen.h`.
- Uses conversion/accessor functions from `accel_dpdk_cryptodev.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/dsa/Makefile

## Purpose

Builds the Intel DSA accel module.

## Key Contents

- `LIBNAME = accel_dsa`
- Sources:
  - `accel_dsa.c`
  - `accel_dsa_rpc.c`
- Shared object version: `SO_VER := 7`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_IDXD`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/accel_dsa.c -->
# File Research: sources/virtualization/spdk/module/accel/dsa/accel_dsa.c

## Purpose

Implements an SPDK accel backend for Intel DSA/IDXD devices.

## Main Responsibilities

- Registers accel module `"dsa"` after startup RPC enablement.
- Configures IDXD mode as kernel or user mode.
- Probes DSA devices and creates per-thread IDXD channels.
- Selects devices round-robin, constrained to the current core's NUMA socket.
- Submits copy, fill, dualcast, compare, CRC32C, copy+CRC32C, DIF, and DIX operations.
- Handles DSA busy backpressure through a queued task list.
- Uses iobuf for temporary DIX verify metadata generation.
- Registers DSA tracepoints for submit/complete counts.
- Writes config JSON for `dsa_scan_accel_module`.

## Supported Operations

- Always:
  - `COPY`
  - `FILL`
  - `DUALCAST`
  - `COMPARE`
  - `CRC32C`
  - `COPY_CRC32C`
- Only when IOMMU is enabled:
  - `DIF_VERIFY`
  - `DIF_GENERATE_COPY`
  - `DIF_VERIFY_COPY`
  - `DIX_GENERATE`
  - `DIX_VERIFY`

## Key Control Flow

- `accel_dsa_enable_probe(kernel_mode)` calls `spdk_idxd_set_config`, adds the module, and records mode.
- `accel_dsa_init()` probes DSA devices, registers iobuf module, then registers IO device.
- `_process_single_task()` maps SPDK accel opcodes to `spdk_idxd_submit_*` functions.
- `dsa_submit_task()` queues work when the IDXD channel is busy.
- `idxd_poll()` processes completions and retries queued tasks.
- `dsa_done()` completes SPDK tasks and performs software DIF detail verification if hardware returns `-EIO`.

## Notes / Risks

- The device selector requires a DSA device on the current NUMA socket; otherwise channel creation fails.
- DIX verify is implemented as DIX generate to temporary metadata plus `memcmp`, because DSA lacks a direct DIX verify operation.
- DIF strip overlap has a software fallback for a documented DSA overlap false-positive case.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/accel_dsa.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/accel_dsa.h -->
# File Research: sources/virtualization/spdk/module/accel/dsa/accel_dsa.h

## Purpose

Header for enabling the DSA accel backend.

## Key Contents

- Header guard `SPDK_ACCEL_ENGINE_DSA_H`.
- Includes `spdk/stdinc.h`.
- Declares `int accel_dsa_enable_probe(bool kernel_mode);`

## Relationships

- Used by DSA implementation and RPC file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/accel_dsa.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/accel_dsa_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/dsa/accel_dsa_rpc.c

## Purpose

Defines startup RPC for enabling the DSA accel module.

## Key Contents

- RPC handler `rpc_dsa_scan_accel_module`.
- Optional parameter:
  - `config_kernel_mode`
- Calls `accel_dsa_enable_probe(req.config_kernel_mode)`.
- Logs whether kernel-mode or user-mode DSA was enabled.
- Returns JSON boolean `true`.
- Registers:
  - `dsa_scan_accel_module`
  - startup phase only.

## Relationships

- Uses generated RPC context from `spdk_internal/rpc_autogen.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/dsa/accel_dsa_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/error/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/error/Makefile

## Purpose

Builds the accel error-injection module.

## Key Contents

- `LIBNAME = accel_error`
- Sources:
  - `accel_error.c`
  - `accel_error_rpc.c`
- Shared object version: `SO_VER := 4`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Always selected by `module/accel/Makefile`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/error/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/error/accel_error.c -->
# File Research: sources/virtualization/spdk/module/accel/error/accel_error.c

## Purpose

Implements a low-priority SPDK accel module that wraps the software accel module and injects configured errors for testing.

## Main Responsibilities

- Registers accel module `"error"` with priority `INT_MIN`.
- Wraps the software accel module's IO channel and submit path.
- Supports per-channel error injection settings copied from global config.
- Can corrupt task output or complete tasks with injected failure.
- Provides config JSON output for active injection rules.
- Currently supports injection for CRC32C operations.

## Injection Types

From header/API:
- `disable`
- `corrupt`
- `failure`

## Key Control Flow

- `accel_error_module_init()` obtains the `"software"` accel module, records its context size, and registers a wrapper IO device.
- `accel_error_submit_tasks()` checks whether to inject for the task opcode and interval/count settings.
- Corruption injection wraps the completion callback or sequence step callback, then forwards to software.
- Failure injection queues a synthetic completion handled by `accel_error_poller`.
- `accel_error_inject_error()` validates opcode support, updates global settings, and applies them to all existing channels with `spdk_for_each_channel`.

## Notes / Risks

- Only `SPDK_ACCEL_OPC_CRC32C` is supported by `accel_error_supports_opcode`.
- CRC corruption simply increments `*task->crc_dst`.
- The module depends on the software accel module being present.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/error/accel_error.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/error/accel_error.h -->
# File Research: sources/virtualization/spdk/module/accel/error/accel_error.h

## Purpose

Header for accel error-injection configuration API.

## Key Contents

- `enum accel_error_inject_type`:
  - `ACCEL_ERROR_INJECT_DISABLE`
  - `ACCEL_ERROR_INJECT_CORRUPT`
  - `ACCEL_ERROR_INJECT_FAILURE`
  - `ACCEL_ERROR_INJECT_MAX`
- `struct accel_error_inject_opts`:
  - opcode
  - type
  - count
  - interval
  - errcode
- Declares:
  - `int accel_error_inject_error(struct accel_error_inject_opts *opts);`
  - `const char *accel_error_get_type_name(enum accel_error_inject_type type);`

## Relationships

- Used by implementation and RPC file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/error/accel_error.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/error/accel_error_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/error/accel_error_rpc.c

## Purpose

Defines runtime RPC for configuring accel error injection.

## Key Contents

- RPC handler `rpc_accel_error_inject_error`.
- Decodes:
  - `opcode`
  - `type`
  - optional `count`
  - optional `interval`
  - optional `errcode`
- Defaults `count` to `UINT64_MAX`.
- Converts generated RPC context into `accel_error_inject_opts`.
- Calls `accel_error_inject_error`.
- Returns JSON boolean `true`.
- Registers:
  - `accel_error_inject_error`
  - runtime phase.

## Relationships

- Uses generated decoders for accel opcode and injection type.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/error/accel_error_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/iaa/Makefile

## Purpose

Builds the Intel IAA accel module.

## Key Contents

- `LIBNAME = accel_iaa`
- Sources:
  - `accel_iaa.c`
  - `accel_iaa_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Selected by `CONFIG_IDXD`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/accel_iaa.c -->
# File Research: sources/virtualization/spdk/module/accel/iaa/accel_iaa.c

## Purpose

Implements an SPDK accel compression backend for Intel IAA/IDXD devices.

## Main Responsibilities

- Registers accel module `"iaa"` after startup RPC enablement.
- Configures IDXD in user mode.
- Probes IAA devices and allocates per-thread IDXD channels.
- Submits deflate compression/decompression work to IDXD IAA operations.
- Queues tasks on `-EBUSY` and retries from poller.
- Registers IAA tracepoints for submit/complete counts.
- Writes config JSON for `iaa_scan_accel_module`.

## Supported Operations

- `SPDK_ACCEL_OPC_COMPRESS`
- `SPDK_ACCEL_OPC_DECOMPRESS`

## Supported Algorithms

- `SPDK_ACCEL_COMP_ALGO_DEFLATE`
- Level range returns `0/0`.

## Key Control Flow

- `accel_iaa_enable_probe()` sets IDXD config to user mode and adds the module.
- `accel_iaa_init()` probes devices matching IAA IDs and registers the IO device.
- `_process_single_task()` maps SPDK compress/decompress tasks to `spdk_idxd_submit_compress` or `spdk_idxd_submit_decompress`.
- `iaa_submit_tasks()` queues tasks if channel is busy.
- `idxd_poll()` processes completions and retries queued tasks.

## Notes / Risks

- Contains a TODO for iovec support and asserts if source/destination iovcnt exceeds 1.
- Device selection is NUMA-local round-robin and may fail if no local device/channel is available.
- Only user mode is supported by this module at present.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/accel_iaa.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/accel_iaa.h -->
# File Research: sources/virtualization/spdk/module/accel/iaa/accel_iaa.h

## Purpose

Header for enabling the IAA accel backend.

## Key Contents

- Header guard `SPDK_ACCEL_MODULE_IAA_H`.
- Includes `spdk/stdinc.h`.
- Declares `int accel_iaa_enable_probe(void);`

## Relationships

- Used by IAA implementation and RPC file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/accel_iaa.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/accel_iaa_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/iaa/accel_iaa_rpc.c

## Purpose

Defines startup RPC for enabling the IAA accel module.

## Key Contents

- RPC handler `rpc_iaa_scan_accel_module`.
- Rejects non-null params.
- Calls `accel_iaa_enable_probe()`.
- Logs `"Enabled IAA user-mode"`.
- Returns JSON boolean `true`.
- Registers:
  - `iaa_scan_accel_module`
  - startup phase only.

## Relationships

- Uses `accel_iaa.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/iaa/accel_iaa_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/ioat/Makefile

## Purpose

Builds the Intel IOAT accel module.

## Key Contents

- `LIBNAME = accel_ioat`
- Sources:
  - `accel_ioat.c`
  - `accel_ioat_rpc.c`
- Shared object version: `SO_VER := 8`, `SO_MINOR := 0`.
- Uses blank SPDK map file and `spdk.lib.mk`.

## Relationships

- Always selected by `module/accel/Makefile`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/accel_ioat.c -->
# File Research: sources/virtualization/spdk/module/accel/ioat/accel_ioat.c

## Purpose

Implements an SPDK accel backend for Intel IOAT DMA engines.

## Main Responsibilities

- Registers accel module `"ioat"` when enabled.
- Probes IOAT PCI devices, claims them, and tracks PCI devices for detach.
- Allocates one unallocated IOAT channel/device per SPDK IO channel.
- Supports copy and fill tasks using IOAT descriptor builders.
- Flushes IOAT descriptors after batched submit.
- Polls completions through `spdk_ioat_process_events`.
- Writes config JSON for `ioat_scan_accel_module`.

## Supported Operations

- `SPDK_ACCEL_OPC_COPY`
- `SPDK_ACCEL_OPC_FILL`

## Key Data

- `IOAT_MAX_CHANNELS` is declared in the header, but allocation here is one channel object per discovered IOAT device.
- `ioat_device`: IOAT channel pointer plus allocation flag.
- `ioat_io_channel`: selected IOAT channel/device and poller.
- Global device and PCI-device queues guarded by `g_ioat_mutex` for allocation state.

## Key Control Flow

- `accel_ioat_enable_probe()` sets enable flag and adds module.
- `accel_ioat_init()` probes IOAT devices and registers IO device.
- `ioat_create_cb()` reserves a free device/channel and starts poller.
- `ioat_submit_tasks()` builds fill/copy descriptors and flushes the channel.
- Unregister callback detaches IOAT and PCI devices.

## Notes / Risks

- Supports only single-iovec copy/fill and equal source/destination lengths for copy.
- `probe_cb()` allocates a PCI tracking object before claim; claim failure leaves the allocated object in the queue until module teardown.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/accel_ioat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/accel_ioat.h -->
# File Research: sources/virtualization/spdk/module/accel/ioat/accel_ioat.h

## Purpose

Header for IOAT accel module enablement.

## Key Contents

- Header guard `SPDK_ACCEL_MODULE_IOAT_H`.
- Defines `IOAT_MAX_CHANNELS 64`.
- Declares `void accel_ioat_enable_probe(void);`

## Relationships

- Used by IOAT implementation and RPC file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/accel_ioat.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/accel_ioat_rpc.c -->
# File Research: sources/virtualization/spdk/module/accel/ioat/accel_ioat_rpc.c

## Purpose

Defines startup RPC for enabling the IOAT accel module.

## Key Contents

- RPC handler `rpc_ioat_scan_accel_module`.
- Rejects non-null params.
- Logs enablement, calls `accel_ioat_enable_probe()`, returns JSON boolean `true`.
- Registers:
  - `ioat_scan_accel_module`
  - startup phase only.

## Relationships

- Uses `accel_ioat.h`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/ioat/accel_ioat_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/accel/mlx5/Makefile -->
# File Research: sources/virtualization/spdk/module/accel/mlx5/Makefile

## Purpose

Builds the MLX5 accel module library.

## Key Contents

- `LIBNAME = accel_mlx5`
- Sources:
  - `accel_mlx5.c`
  - `accel_mlx5_rpc.c`
- Shared object version: `SO_VER := 5`, `SO_MINOR := 0`.
- Uses blank SPDK map file.
- Adds local system libraries:
  - `-libverbs`
  - `-lmlx5`
- Included through `spdk.lib.mk`.

## Relationships

- Selected by `module/accel/Makefile` when `CONFIG_RDMA_PROV=mlx5_dv`.
- This work item includes only the Makefile, not the MLX5 C implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/accel/mlx5/Makefile -->