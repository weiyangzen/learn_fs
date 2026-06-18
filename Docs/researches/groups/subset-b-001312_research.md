# subset-b-001312 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gpuvm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gpuvm.c

## Purpose
`amdgpu_amdkfd_gpuvm.c` is the KFD-to-AMDGPU GPU virtual memory bridge. It allocates KFD-visible memory objects, enforces KFD system/TTM/VRAM accounting, attaches allocations to one or more AMDGPU VMs, maps and unmaps PTEs, handles peer-device DMA mappings through shared BOs, SG BOs, or DMABUF imports, and restores mappings after eviction, MMU notifier invalidation, reset, suspend, or CRIU resume.

## Important APIs, types, and functions
The main exported KFD-facing entry points are `amdgpu_amdkfd_gpuvm_acquire_process_vm()`, `amdgpu_amdkfd_gpuvm_alloc_memory_of_gpu()`, `amdgpu_amdkfd_gpuvm_free_memory_of_gpu()`, `amdgpu_amdkfd_gpuvm_map_memory_to_gpu()`, `amdgpu_amdkfd_gpuvm_unmap_memory_from_gpu()`, `amdgpu_amdkfd_gpuvm_sync_memory()`, `amdgpu_amdkfd_gpuvm_import_dmabuf_fd()`, `amdgpu_amdkfd_gpuvm_export_dmabuf()`, `amdgpu_amdkfd_gpuvm_restore_process_bos()`, and `amdgpu_amdkfd_evict_userptr()`. Memory accounting is handled by `amdgpu_amdkfd_gpuvm_init_mem_limits()`, `amdgpu_amdkfd_reserve_mem_limit()`, `amdgpu_amdkfd_unreserve_mem_limit()`, `amdgpu_amdkfd_get_available_memory()`, and `kfd_debugfs_kfd_mem_limits()`. Internal helpers are centered on `struct kgd_mem`, `struct kfd_mem_attachment`, `struct amdkfd_process_info`, `struct bo_vm_reservation_context`, `kfd_mem_attach()`, `kfd_mem_detach()`, `map_bo_to_gpuvm()`, `update_gpuvm_pte()`, `unmap_bo_from_gpuvm()`, and the userptr restore helpers.

## Control flow
KFD first converts an AMDGPU VM into a compute VM with `amdgpu_amdkfd_gpuvm_acquire_process_vm()`. That calls `amdgpu_vm_make_compute()`, initializes per-process state in `init_kfd_vm()`, validates the VM page directory/table BOs, attaches the per-process eviction fence to the root BO, and records the VM in `process_info->vm_list_head`.

Allocation starts in `amdgpu_amdkfd_gpuvm_alloc_memory_of_gpu()`. It derives the BO domain and TTM type from KFD flags: VRAM, GTT, userptr, doorbell, MMIO remap, coherent/uncached variants, contiguous VRAM, and AQL queue wraparound. It reserves KFD memory limits, creates an AMDGPU GEM object, grants the VM's DRM file VMA-node access, creates a KFD GEM handle, installs `bo->kfd_bo`, initializes `kgd_mem`, and adds it to either `kfd_bo_list` or `userptr_valid_list`. Userptr allocations register HMM/MMU notifier state and pin current user pages through `init_user_pages()`. Doorbell and MMIO SG BOs are pinned in GTT. Ordinary KFD BOs are validated and fenced with the process eviction fence.

Mapping begins with `amdgpu_amdkfd_gpuvm_map_memory_to_gpu()`. It serializes against restore work with `process_info->lock`, attaches the BO to the target VM if needed, reserves the BO and VM page tables through `drm_exec`, validates page tables, maps one or two VA ranges for AQL queues, updates PTEs unless the userptr is invalid, updates PDEs, and increments both attachment and `kgd_mem` mapping state. Unmapping uses the mirrored reservation path, calls `amdgpu_vm_bo_unmap()`, clears freed page-table entries, syncs the PTE update fence, and decrements the mapping count. Freeing refuses still-mapped BOs, removes the BO from restore lists, unregisters HMM, removes eviction fences, detaches all VM attachments, frees SG tables and sync objects, revokes VMA access, deletes the KFD GEM handle, drops DMABUF references, and finally releases the GEM object.

Peer mapping is decided in `kfd_mem_attach()`. Local BOs, same-hive VRAM, and reusable userptr/GTT DMA maps share the original BO. Peer userptr and SG doorbell/MMIO paths create DMA-mappable SG BOs with `create_dmamap_sg_bo()`. Peer GTT/VRAM uses exported/imported DMABUFs. `kfd_mem_dmamap_attachment()` dispatches to userptr SG mapping, DMABUF validation, or resource DMA mapping before VM PTE updates; the matching unmap helpers move BOs back to CPU/system placement and free DMA maps.

Eviction and restore are two-stage. Userptr MMU notifier callbacks call `amdgpu_amdkfd_evict_userptr()`, mark `kgd_mem` invalid, quiesce KFD queues on first invalidation, and schedule `restore_userptr_work`. The worker reacquires the process mm, refreshes invalid user pages with HMM, validates userptr BOs, rewrites mapped PTEs, confirms ranges under the notifier lock, and resumes queues. Whole-process memory eviction uses `amdgpu_amdkfd_gpuvm_restore_process_bos()`: reserve all VM PDs and KFD BOs, validate BOs, validate page tables, update KFD and non-KFD VM mappings, update PDEs, wait for sync, replace a signaled eviction fence, and attach the new fence to restorable BOs and VM roots.

## State and persistence behavior
All state is runtime-only. The static `kfd_mem_limit` tracks global KFD system and TTM usage under a spinlock. Per-device `adev->kfd.vram_used[]` and `vram_used_aligned[]` track XCP-scoped VRAM accounting. `struct kgd_mem` stores allocation flags, BO, VA, domain, attachments, sync state, DMABUF/export metadata, import state, userptr invalidation count, HMM range, AQL state, and process back pointer. `struct kfd_mem_attachment` stores per-VM BO VA, PTE flags, mapped state, attachment type, VA, and target device. `struct amdkfd_process_info` stores compute VMs, KFD BO lists, valid/invalid userptr lists, eviction fence, delayed restore work, PID, CRIU/MMU-notification state, and locks. No information is persisted across driver unload or process lifetime.

## Dependencies and integration points
This file depends on AMDGPU VM, GEM, TTM, HMM, DMA-BUF, DMA mapping, DRM reservation/execution locking, XGMI peer topology, RAS reserved-page accounting, KFD process/queue control, KFD SMI events, and UAPI allocation flags from `kfd_ioctl.h`. It integrates with KFD via `kgd_mem` objects and eviction fences, with TTM through BO placement/validation/pinning, with VM code through BO VA mappings and PDE/PTE updates, with HMM through MMU interval notifiers, and with peer GPUs through XGMI, PCIe peer access, SG BOs, and DMABUF import/export.

## Risks and edge cases
The highest-risk areas are lock ordering across `process_info->lock`, `notifier_lock`, `mem->lock`, `drm_exec`, BO reservations, and VM page-table locks; userptr invalidations while mapping or freeing; unbalanced KFD memory accounting; stale SG/DMA maps after eviction; replacing unsignaled eviction fences; partial attach unwind for AQL double mappings; and peer access differences between same-hive XGMI, large-BAR PCIe, same IOMMU group, and direct-mapped RAM. `amdgpu_amdkfd_reserve_system_mem()` increments accounting without taking `mem_limit_lock`, so callers must be constrained by initialization/lifetime assumptions. Several paths intentionally ignore or downgrade errors during cleanup, which is pragmatic but makes fault injection important.

## Test signals
Useful signals include ROCm/KFD allocation and free coverage for VRAM, GTT, userptr, doorbell, MMIO remap, coherent, uncached, contiguous, AQL, and imported DMABUF memory; multi-GPU peer mapping over same XGMI hive and PCIe; map/unmap/free ordering including still-mapped `-EBUSY`; oversubscription of system, TTM, and XCP VRAM limits; HMM invalidation under concurrent CPU unmap/remap; CRIU resume with blocked MMU notifications; GPU reset and suspend/resume restore; GWS add/remove; debugfs memory-limit output; and lockdep/fault-injection coverage for BO creation, DMA mapping, page-table validation, and fence replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gpuvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.c

## Purpose
`amdgpu_atombios.c` is the legacy ATOMBIOS parser and interpreter integration layer for AMDGPU. It converts VBIOS data tables into driver-visible display, clock, voltage, memory, scratch-register, and sysfs state, and provides register callbacks used by the ATOM bytecode interpreter.

## Important APIs, types, and functions
External entry points include `amdgpu_atombios_init()`, `amdgpu_atombios_fini()`, `amdgpu_atombios_sysfs_init()`, `amdgpu_atombios_i2c_init()`, `amdgpu_atombios_oem_i2c_init()`, `amdgpu_atombios_lookup_i2c_gpio()`, `amdgpu_atombios_lookup_gpio()`, `amdgpu_atombios_get_connector_info_from_object_table()`, `amdgpu_atombios_get_clock_info()`, `amdgpu_atombios_get_gfx_info()`, `amdgpu_atombios_get_vram_width()`, `amdgpu_atombios_get_asic_ss_info()`, `amdgpu_atombios_get_clock_dividers()`, `amdgpu_atombios_get_data_table()`, and scratch helpers. SI-only helpers under `CONFIG_DRM_AMDGPU_SI` expose memory PLL, voltage, SVI2, and memory-controller register-table parsing. Important internal unions mirror firmware table revisions: `firmware_info`, `igp_info`, `asic_ss_info`, `get_clock_dividers`, `voltage_object_info`, and `vram_info`.

## Control flow
Initialization allocates `struct card_info`, installs MMIO and placeholder PLL/MC callbacks, parses the already-fetched VBIOS with `amdgpu_atom_parse()`, initializes the ATOM mutex, and then branches between newer atomfirmware helpers and legacy scratch/FB-scratch allocation depending on `adev->is_atom_fw`. Display discovery parses the object header, display path, connector, encoder, and router tables. It maps ATOM connector object IDs to DRM connector types, creates encoders, decodes router DDC/clock routing records, looks up DDC and HPD GPIOs, adds connectors, and finally links encoders to connectors.

Clock and capability discovery reads the legacy `FirmwareInfo` table to seed PPLL/SPLL/MPLL ranges, default SCLK/MCLK/DISPCLK, DP external clock, max pixel clock, firmware flags, and current PM clocks. `amdgpu_atombios_get_clock_dividers()` executes the `ComputeMemoryEnginePLL` command table using the revision-specific parameter layout and decodes returned PLL divisors. Spread-spectrum and IGP override helpers parse ASIC/internal system info tables. SI-specific paths execute ATOM command tables for memory PLL, dynamic memory settings, and voltage, and parse voltage object and VRAM timing tables.

Scratch handling writes BIOS scratch registers to hand display switching and DPMS semantics to the driver, expose engine-hung and backlight state, and test whether ASIC init is required. Sysfs setup publishes read-only `vbios_version` and conditionally `vbios_build`. Finalization frees ATOM scratch, indirect I/O storage, context, and card-info structures.

## State and persistence behavior
The file populates runtime fields in `adev->mode_info`, `adev->clock`, `adev->pm`, `adev->gfx.config`, `adev->gfx.cu_info`, `adev->bios_scratch_reg_offset`, display connector/encoder lists, and sysfs device attributes. ATOM context scratch memory is heap-allocated and freed during shutdown. Persistent input is only the VBIOS image already stored in memory; no output is persisted beyond hardware registers and driver structures.

## Dependencies and integration points
It depends on `atom.c` parser/executor APIs, legacy ATOM table definitions, AMDGPU display helpers, AMDGPU I2C helpers, DRM connector types, MMIO access macros, SI configuration, and the newer `amdgpu_atomfirmware` helpers for atomfirmware devices. It is reached after BIOS acquisition in `amdgpu_bios.c` and before display, clock, power, and memory-management subsystems consume parsed VBIOS data.

## Risks and edge cases
Table parsing is pointer arithmetic over firmware-controlled binary layouts. Bad sizes, unsupported revisions, connector object IDs beyond the conversion table, malformed record chains, or bogus offsets can break discovery. Several MC/PLL callbacks are stubs returning zero, so command tables that require those spaces would not work through this integration. Clock default fallbacks and unit conversions differ by table revision. AQL-like doubled mappings are not involved here, but FB scratch allocation and SR-IOV VRAM reservations must match TTM expectations. Big-endian `copy_swap()` only supports small stack arrays sized for current ATOM parameter blocks.

## Test signals
Test signals include boot on legacy pre-Vega ASICs with diverse connector object tables, HPD/DDC/router combinations, sysfs `vbios_version` and `vbios_build`, display hotplug, PLL divider command execution for supported ATOM revisions, spread-spectrum lookup, SI voltage and memory timing parsing, SR-IOV VRAM reservation tables, malformed VBIOS table rejection, and clean init/fini under probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.h

## Purpose
`amdgpu_atombios.h` declares the legacy ATOMBIOS data structures and helper APIs consumed by AMDGPU display, clock, power, memory, and initialization code. It is the private interface for code that needs parsed legacy VBIOS information or ATOM command execution results.

## Important APIs, types, and functions
Key types include `struct atom_clock_dividers`, `struct atom_mpll_param`, `struct atom_memory_info`, `struct atom_memory_clock_range_table`, `struct atom_mc_reg_table`, and voltage-table structures. Constants define memory type encodings, AC timing limits, MC register array limits, and voltage entry limits. Prototypes expose GPIO/I2C lookup/init, connector object parsing, clock/gfx/VRAM info, spread-spectrum info, clock dividers, SI-only memory PLL/timing/voltage helpers, GPU virtualization table detection, BIOS scratch manipulation, endian-safe ATOM copy, data-table lookup, lifecycle init/fini, and sysfs init.

## Control flow
The header has no executable flow. It defines the call surface implemented by `amdgpu_atombios.c`: callers initialize the ATOM context, query tables or execute commands through these helpers, then tear the context down at device shutdown.

## State and persistence behavior
The declared structures are transient containers for values parsed from VBIOS tables or returned by ATOM command tables. They do not own persistent storage. Functions declared here update `struct amdgpu_device` runtime fields, hardware scratch registers, and caller-provided output buffers.

## Dependencies and integration points
The header assumes AMDGPU core types such as `struct amdgpu_device`, GPIO/I2C records, `struct amdgpu_atom_ss`, and UMA/clock-related structures are visible to includers. `CONFIG_DRM_AMDGPU_SI` gates older Southern Islands helpers. It integrates legacy ATOMBIOS parsing with display, power management, memory controller setup, and sysfs.

## Risks and edge cases
Many structures contain endian-sensitive bitfields that must match ATOM firmware layouts. Constants such as `VBIOS_MC_REGISTER_ARRAY_SIZE`, `VBIOS_MAX_AC_TIMING_ENTRIES`, and `MAX_VOLTAGE_ENTRIES` must stay aligned with implementation bounds checks. The header repeats the `amdgpu_atombios_get_clock_dividers()` prototype, which is harmless but a maintenance smell.

## Test signals
Build coverage with and without `CONFIG_DRM_AMDGPU_SI`, big-endian compile coverage for bitfields and `copy_swap()`, and runtime table parsing on legacy VBIOS revisions are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.c

## Purpose
`amdgpu_atomfirmware.c` parses newer ATOM firmware master data/command tables, mainly used by Vega10 and later devices. It extracts firmware capabilities, scratch register offsets, VRAM/UMC/integrated-system memory information, UMA carveout choices, ECC/RAS data, clock references, GFX topology, firmware-reserved framebuffer size, and executes the newer ASIC init command table.

## Important APIs, types, and functions
Public helpers include `amdgpu_atomfirmware_query_firmware_capability()`, `amdgpu_atomfirmware_gpu_virtualization_supported()`, `amdgpu_atomfirmware_scratch_regs_init()`, `amdgpu_atomfirmware_allocate_fb_scratch()`, `amdgpu_atomfirmware_get_integrated_system_info()`, `amdgpu_atomfirmware_get_umc_info()`, `amdgpu_atomfirmware_get_vram_info()`, `amdgpu_atomfirmware_get_uma_carveout_info()`, `amdgpu_atomfirmware_mem_ecc_supported()`, `amdgpu_atomfirmware_sram_ecc_supported()`, `amdgpu_atomfirmware_dynamic_boot_config_supported()`, `amdgpu_atomfirmware_ras_rom_addr()`, `amdgpu_atomfirmware_get_clock_info()`, `amdgpu_atomfirmware_get_gfx_info()`, `amdgpu_atomfirmware_mem_training_supported()`, `amdgpu_atomfirmware_get_fw_reserved_fb_size()`, and `amdgpu_atomfirmware_asic_init()`. Internal unions cover revisioned `firmware_info`, `igp_info`, `umc_info`, `vram_info`, `vram_module`, `smu_info`, and `gfx_info` tables.

## Control flow
Most helpers compute a v2.1 master-table index with `get_index_into_master_table()`, call `amdgpu_atom_parse_data_header()` or `amdgpu_atom_parse_cmd_header()`, check table revision, cast `ctx->bios + data_offset` to the matching revisioned structure, then copy selected little-endian fields into AMDGPU runtime state or caller outputs. Firmware capability is cached in `adev->mode_info.firmware_flags` by `amdgpu_atombios_init()`, and later helpers test that cache for virtualization, SRAM ECC, dynamic boot config, and memory training.

`amdgpu_atomfirmware_allocate_fb_scratch()` parses `vram_usagebyfirmware` v2.1/v2.2, creates SR-IOV firmware/driver VRAM reservations when requested, skips reservation parsing for dynamic critical-region VFs, and allocates ATOM interpreter scratch memory with a 20 KiB fallback. Memory-info helpers select APU integrated-system tables, UMC tables, or dGPU VRAM module tables and convert ATOM memory type encodings to AMDGPU VRAM type enums. Clock info combines firmware, SMU, UMC, and Navi+ GFX table data to initialize default clocks and SPLL/MPLL reference parameters. ASIC init builds an `asic_init_ps_allocation_v2_1` parameter block from boot clocks and calls `amdgpu_atom_execute_table()`.

## State and persistence behavior
This file updates runtime fields in `adev->mode_info`, `adev->clock`, `adev->pm`, `adev->gfx.config`, `adev->gfx.cu_info`, `adev->bios_scratch_reg_offset`, `adev->ras_default_ecc_enabled`, and TTM VRAM reservation state. It allocates `ctx->scratch` in system memory. It reads firmware tables from the in-memory VBIOS only and does not persist derived state outside the driver/hardware runtime.

## Dependencies and integration points
It depends on ATOM firmware table definitions, `amdgpu_atom_parse_*()` and `amdgpu_atom_execute_table()`, TTM VRAM reservation helpers, RAS state, scratch register access, SMU/UMC/GFX table contracts, and SoC generation enums such as `CHIP_NAVI10`. It is selected by `amdgpu_atombios_init()` when `adev->is_atom_fw` is true and feeds memory, RAS, display/clock, and ASIC initialization code.

## Risks and edge cases
Revision handling is intentionally strict; unsupported `frev`/`crev` combinations return `-EINVAL` or false. Firmware-controlled offsets and module sizes must be valid; malformed VRAM module chains or module IDs can cause wrong memory geometry. Several helpers rely on `bios_scratch_reg_offset` being initialized before reading module/vendor scratch values. `amdgpu_atomfirmware_get_clock_info()` calls `BUG()` for unexpected Navi+ GFX table revisions, which makes malformed or future firmware especially risky. SR-IOV reservation flag interpretation must match firmware semantics to avoid reserving wrong VRAM ranges.

## Test signals
Signals include boot/probe on Vega, Navi, and newer ASICs with different firmware table revisions; APU integrated-system and UMA carveout parsing; UMC and VRAM module memory-width/type/vendor results; ECC/RAS capability detection; firmware-reserved framebuffer size; dynamic boot and memory-training capability bits; SR-IOV VF dynamic critical-region behavior; ASIC init command execution; malformed table revision tests; and comparing parsed clocks/GFX topology with hardware discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.h

## Purpose
`amdgpu_atomfirmware.h` declares AMDGPU's helper interface for newer ATOM firmware tables. It lets other AMDGPU components query firmware capabilities, memory geometry, RAS/ECC support, clocks, GFX topology, framebuffer reservations, and ASIC init behavior without directly parsing the v2.1 master table layout.

## Important APIs, types, and functions
The header defines `get_index_into_master_table(master_table, table_name)` for computing table indices from master table structures. It declares helpers for firmware capability flags, GPU virtualization support, scratch register initialization, FB scratch allocation, integrated-system/UMC/VRAM/UMA carveout info, memory and SRAM ECC, RAS ROM address, memory training, dynamic boot config, firmware-reserved FB size, GFX/clock info, and `amdgpu_atomfirmware_asic_init()`.

## Control flow
There is no executable flow in the header. Callers include it to invoke the implementation in `amdgpu_atomfirmware.c`, typically after `amdgpu_atombios_init()` has parsed a VBIOS into `adev->mode_info.atom_context`.

## State and persistence behavior
The declared functions read VBIOS-backed ATOM firmware tables and update runtime `struct amdgpu_device` fields or caller-provided output buffers. The header itself owns no state and defines no persistent data.

## Dependencies and integration points
It depends on `struct amdgpu_device`, `struct amdgpu_uma_carveout_info`, and ATOM firmware structure definitions being available in includers. It is the interface between core AMDGPU initialization/power/RAS/memory code and the newer ATOM firmware parser.

## Risks and edge cases
The index macro depends on exact C structure layout of the ATOM master table definitions. If firmware table definitions change without matching implementation updates, callers can query the wrong table. The prototypes also imply that callers must tolerate `-EINVAL`, `-ENODEV`, or false for unsupported firmware revisions.

## Test signals
Build coverage across ASIC generations, probe-time parsing on atomfirmware devices, and targeted tests for missing or unsupported tables are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atpx_handler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atpx_handler.c

## Purpose
`amdgpu_atpx_handler.c` implements ACPI ATPX support for hybrid graphics and legacy switchable GPU platforms. It detects systems with AMD ATPX firmware methods, validates supported power/mux functions, applies platform quirks, and registers callbacks with `vga_switcheroo` for GPU switching and dGPU power control.

## Important APIs, types, and functions
The external APIs are `amdgpu_register_atpx_handler()`, `amdgpu_unregister_atpx_handler()`, `amdgpu_has_atpx()`, `amdgpu_has_atpx_dgpu_power_cntl()`, and `amdgpu_is_atpx_hybrid()`. Important internal state is `static struct amdgpu_atpx_priv amdgpu_atpx_priv`, containing detection flags, bridge PM usability, quirks, ACPI handles, and `struct amdgpu_atpx`. ACPI method wrappers include `amdgpu_atpx_call()`, `amdgpu_atpx_verify_interface()`, `amdgpu_atpx_validate()`, `amdgpu_atpx_set_discrete_state()`, display/I2C mux switching, and switch start/end notifications.

## Control flow
Registration calls `amdgpu_atpx_detect()`, which scans VGA and display-class PCI devices, finds an `ATPX` ACPI handle, counts display devices, records bridge D3 capability, and applies PCI subsystem quirks. When exactly two display devices and ATPX are present, it logs the ACPI path, sets global detection state, initializes ATPX, and registers a `vga_switcheroo_handler`.

Initialization verifies the ATPX interface by executing `ATPX_FUNCTION_VERIFY_INTERFACE`, checking the returned buffer size, and decoding supported function bits. Validation optionally calls `GET_PX_PARAMETERS`, interprets valid flags, promotes implied mux/power-control support, handles Microsoft Hybrid Graphics by preferring bridge PM when usable unless a quirk forces ATPX, and records whether displays require dGPU power. Runtime switch callbacks translate the requested `vga_switcheroo_client_id` into ATPX integrated/discrete IDs and call switch-start, display-mux, I2C-mux, and switch-end methods. Power callbacks ignore IGD power and call ATPX power control for the dGPU.

## State and persistence behavior
State is process-global kernel memory in `amdgpu_atpx_priv`: detected method, selected ACPI handles, function support, hybrid flag, bridge PM flag, quirks, and display-power requirement. ACPI calls may change platform firmware state, mux routing, or dGPU power state. There is no file-backed persistence.

## Dependencies and integration points
The file depends on ACPI object evaluation, PCI device enumeration, bridge D3 capabilities, `vga_switcheroo`, AMD ACPI ATPX constants from `amd_acpi.h`, and AMDGPU PCI IDs for quirks. It integrates early in AMDGPU module/device setup through register/unregister calls and provides global query helpers used by power-management and hybrid-graphics decisions.

## Risks and edge cases
ACPI firmware buffer parsing trusts the first `u16` size after ensuring a small minimum, so malformed buffers remain a risk. Device enumeration relies on exactly two display devices to enable ATPX; unusual hybrid systems may be missed. Global state means multiple GPUs share one ATPX handler. Hybrid systems with broken `_PR3` bridge power need quirks to force ATPX power control. ACPI calls return allocated buffers that must always be freed. The switch callback currently returns success even if one of the intermediate ATPX method calls fails.

## Test signals
Signals include boot on known ATPX and non-ATPX laptops, Microsoft Hybrid Graphics systems with and without bridge D3, quirked Dell/Acer/Lenovo devices, `vga_switcheroo` switch and power operations, ACPI failure injection for each ATPX method, suspend/resume dGPU power behavior, and absence of handler registration on systems without exactly two display devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atpx_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_benchmark.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_benchmark.c

## Purpose
`amdgpu_benchmark.c` provides an internal BO-move benchmark for AMDGPU. It allocates kernel BOs in selected memory domains, repeatedly copies between GPU addresses with the buffer copy engine, waits for fences, and logs throughput for predefined test modes.

## Important APIs, types, and functions
The public entry point is `amdgpu_benchmark(struct amdgpu_device *adev, int test_number)`. Internal helpers are `amdgpu_benchmark_move()`, `amdgpu_benchmark_do_move()`, and `amdgpu_benchmark_log_results()`. Constants define 1024 iterations and a table of 17 common framebuffer-like sizes.

## Control flow
`amdgpu_benchmark()` serializes tests with `adev->benchmark_mutex`, selects one of eight test modes, and calls `amdgpu_benchmark_move()` for fixed 1 MiB copies, powers-of-two GPU page sweeps, or common display-mode-size sweeps across GTT-to-VRAM, VRAM-to-GTT, and VRAM-to-VRAM directions. Each move creates source and destination kernel BOs, obtains GPU addresses, locks the default memory-management entity, loops over `amdgpu_copy_buffer()`, waits each returned fence, measures elapsed time with `ktime_get()`, logs throughput, and frees both BOs.

## State and persistence behavior
The file allocates temporary kernel BOs and fences only for the duration of each benchmark. It writes no persistent state; output is kernel log messages. `adev->benchmark_mutex` is the only long-lived state it uses.

## Dependencies and integration points
It depends on AMDGPU BO allocation/free helpers, the default VM/memory-management entity, `amdgpu_copy_buffer()`, DMA fences, domain constants, GPU page size, and kernel timing/logging. It is typically driven by AMDGPU debug/module benchmark plumbing rather than normal rendering paths.

## Risks and edge cases
Throughput divides by elapsed milliseconds; extremely fast runs could risk division by zero, although 1024 iterations normally avoids that. Benchmark results include fence wait overhead and serialization through the default entity, so they are diagnostic rather than pure bandwidth. If `adev->mman.buffer_funcs` is unavailable, BOs are created but no copy/log result is produced. Cleanup can overwrite error values, so the code logs the error before freeing.

## Test signals
Signals include running all benchmark IDs 1-8, invalid test-number `-EINVAL`, BO allocation failure injection, copy/fence wait failure handling, domains with and without VRAM, availability of buffer functions, and checking that repeated benchmarks free BOs and fences cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bios.c

## Purpose
`amdgpu_bios.c` locates, reads, validates, and releases the AMD GPU VBIOS image. It supports APU and dGPU retrieval paths including PCI ROM BAR, VRAM BAR copies, platform ROM resources, ACPI ATRM and VFCT tables, ASIC ROM register reads, disabled ROM BAR access, and SR-IOV dynamic critical-region VBIOS data.

## Important APIs, types, and functions
External entry points include `amdgpu_get_bios()`, `amdgpu_bios_release()`, `amdgpu_read_bios()`, and `amdgpu_soc15_read_bios_from_rom()`. Internal helpers include `check_atom_bios()`, `amdgpu_read_bios_from_vram()`, `amdgpu_read_bios_from_rom()`, `amdgpu_read_platform_bios()`, ACPI `amdgpu_atrm_get_bios()`/`amdgpu_acpi_vfct_bios()`, `amdgpu_read_disabled_bios()`, `amdgpu_get_bios_apu()`, `amdgpu_get_bios_dgpu()`, and `amdgpu_prefer_rom_resource()`.

## Control flow
All read paths allocate or duplicate a candidate VBIOS into `adev->bios`, set `adev->bios_size` when appropriate, and validate it with `check_atom_bios()`. Validation checks the `0x55 0xaa` ROM signature, reads the ATOM header offset at `0x48`, verifies the buffer is large enough, and accepts `ATOM` or byte-swapped `MOTA`.

APU lookup tries VFCT, VRAM BAR, PCI ROM BAR, then platform ROM. dGPU lookup tries ACPI ATRM, VFCT, VRAM BAR for SR-IOV, ROM BAR/platform in an order influenced by `IORESOURCE_ROM_SHADOW`, ASIC-specific ROM reads, and disabled ROM BAR reads. `amdgpu_get_bios()` selects APU or dGPU order and marks `adev->is_atom_fw` for Vega10 and newer ASICs. `amdgpu_soc15_read_bios_from_rom()` is a low-level helper that reads 32-bit ROM data through SMUIO index/data registers, with optional NBIO ROM offset.

## State and persistence behavior
The file owns the heap buffer `adev->bios` and size `adev->bios_size` until released. It also sets `adev->is_atom_fw` after successful lookup. The VBIOS image is copied from firmware/platform/hardware sources into kernel memory; no on-disk persistence is created.

## Dependencies and integration points
It depends on PCI ROM mapping/resource APIs, IO remapping, ACPI ATRM/VFCT tables, AMDGPU SR-IOV dynamic data helpers, ASIC `read_bios_from_rom`/`read_disabled_bios` callbacks, SMUIO/NBIO register callbacks, and ATOM parser expectations. It runs before `amdgpu_atombios_init()` consumes `adev->bios`.

## Risks and edge cases
The retrieval order is platform-sensitive. Some systems expose stale or shadowed ROM resources; hence the ROM/platform preference check. ATRM reads a fixed 256 KiB buffer in 4 KiB pages and validates the full allocation, even if the ACPI method returned less than a page at the end. VFCT parsing must reject short or truncated ACPI tables. VRAM BAR reads assume a 256 KiB copy unless SR-IOV dynamic data returns a size. `check_atom_bios()` is necessary but not a complete bounds validation for all later ATOM table offsets.

## Test signals
Signals include BIOS retrieval on APUs, dGPUs, PX/ATRM laptops, UEFI VFCT systems, SR-IOV VFs with and without dynamic critical regions, shadow ROM platforms, disabled-ROM fallback, SoC15 register ROM reads, malformed signature/header rejection, and release/retry paths that leave `adev->bios` and `bios_size` consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.c

## Purpose
`amdgpu_bo_list.c` implements user-managed buffer-object lists used by AMDGPU command submission. It copies BO list entries from userspace, resolves GEM handles to AMDGPU BO references, orders non-userptr BOs by priority, separates userptr entries, tracks special GDS/GWS/OA resources, stores lists in per-file IDR handles, and frees lists with RCU-safe lifetime management.

## Important APIs, types, and functions
The main APIs are `amdgpu_bo_list_create()`, `amdgpu_bo_list_get()`, `amdgpu_bo_list_put()`, `amdgpu_bo_create_list_entry_array()`, and `amdgpu_bo_list_ioctl()`. Internal helpers are `amdgpu_bo_list_free_rcu()`, `amdgpu_bo_list_free()`, `amdgpu_bo_list_entry_cmp()`, and `amdgpu_bo_list_destroy()`. Constants define max priority, bucket count, and a 128K entry cap.

## Control flow
The ioctl first copies userspace entry data with `amdgpu_bo_create_list_entry_array()`, handling both current ABI entry size and smaller/larger compatible entry sizes. Create builds a flexible `struct amdgpu_bo_list`, looks up each GEM handle in the caller's DRM file, references the BO, rejects userptr BOs from another process, places non-userptr entries from the front and userptr entries from the back, clamps priority, records special-domain objects, traces entries, sorts only the non-userptr prefix by priority, initializes the list mutex, and returns the list. The ioctl then allocates an IDR handle for create, removes and drops a handle for destroy, or atomically replaces a handle for update.

Lookup is RCU-protected: `amdgpu_bo_list_get()` finds the IDR entry and takes a kref unless it is already zero. Release decrements the kref; final free unreferences all BOs and schedules RCU freeing of the flexible allocation after destroying the mutex.

## State and persistence behavior
BO lists are per-DRM-file runtime objects stored in `fpriv->bo_list_handles` under `fpriv->bo_list_lock`. Each list stores referenced BO pointers, optional BO VA/range metadata for command submission, priority, invalidation flags, special resource pointers, `first_userptr`, entry count, a kref, RCU head, and a command-submission mutex. No persistent state exists beyond the file descriptor lifetime.

## Dependencies and integration points
The file depends on DRM GEM handle lookup, AMDGPU BO reference helpers, TTM userptr ownership checks, Linux IDR, RCU, kref, sort, uaccess helpers, tracepoints, and the AMDGPU BO-list UAPI structures. It integrates directly with command submission, which later reserves, validates, and maps the listed BOs.

## Risks and edge cases
Large user-supplied `bo_number` values are capped, but memory pressure from near-limit lists is still significant. Compatibility copying must zero-fill missing fields to avoid uninitialized priorities or handles. Userptr BO ownership is checked against `current->mm`; shared or stale process contexts must be rejected. Destroy silently succeeds for nonexistent IDs. Update must drop the old list only after replacement succeeds. Sorting excludes userptr entries, so code consuming the list must honor `first_userptr`.

## Test signals
Signals include BO list create/update/destroy/get for valid and invalid handles, ABI size compatibility, priority clamping and ordering, userptr same-mm and cross-mm behavior, GDS/GWS/OA detection, near-limit entry counts, concurrent lookup/destroy RCU behavior, and command submission with mixed userptr and non-userptr entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.h

## Purpose
`amdgpu_bo_list.h` defines the private BO-list data structures and helper prototypes shared between AMDGPU ioctl handling and command submission. It describes how a list stores BO references, associated VM metadata, priorities, userptr split point, and special resources.

## Important APIs, types, and functions
Important types are `struct amdgpu_bo_list_entry` and `struct amdgpu_bo_list`. Entries hold `bo`, optional `bo_va`, priority, optional HMM range, and a user-invalidation flag. Lists hold RCU/kref lifetime fields, special `gds_obj`, `gws_obj`, `oa_obj` pointers, `first_userptr`, `num_entries`, a command-submission mutex, and a flexible entry array. Prototypes expose list get/put, UAPI entry-array copying, and list creation. Iteration macros cover all entries or only userptr entries.

## Control flow
The header has no executable flow. It defines the contracts implemented in `amdgpu_bo_list.c` and consumed by command-submission paths: callers obtain a referenced list by handle, iterate entries, lock `bo_list_mutex` while using it for submission, and release it with `amdgpu_bo_list_put()`.

## State and persistence behavior
The structures describe runtime-only per-file BO-list state. Lifetime is kref and RCU based; the flexible array is immutable in size after creation but entries can carry submission-time metadata such as BO VA and HMM range.

## Dependencies and integration points
The header depends on `drm/amdgpu_drm.h` for UAPI structures, forward declarations for AMDGPU BO/VA/file-private types, Linux RCU/kref/mutex primitives through includers, and HMM range support. It is part of the command-submission and BO-list ioctl boundary.

## Risks and edge cases
Flexible-array allocation size must match `num_entries`, and iteration macros assume `entries` is valid through `num_entries`. `first_userptr` partitions non-userptr from userptr entries; incorrect maintenance would break userptr-specific reservation/validation. The list mutex protects command-submission access, not IDR lifetime by itself.

## Test signals
Compile coverage, BO-list ioctl tests, command submission with special resources, userptr-only and mixed lists, and RCU/kref lifetime tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cgs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cgs.c

## Purpose
`amdgpu_cgs.c` implements AMDGPU's Common Graphics Services adapter. It wraps register access and firmware lookup behind `struct cgs_ops` so older power-management/SMU-facing code can interact with AMDGPU devices through the CGS abstraction.

## Important APIs, types, and functions
The public lifecycle functions are `amdgpu_cgs_create_device()` and `amdgpu_cgs_destroy_device()`. Internal ops include direct register reads/writes, indirect register reads/writes for PCIE/SMC/UVD/DIDT/GC CAC/SE CAC spaces, firmware type conversion, firmware version lookup, and `amdgpu_cgs_get_firmware_info()`. `struct amdgpu_cgs_device` embeds `struct cgs_device` and stores the backing `struct amdgpu_device`.

## Control flow
Creation allocates an `amdgpu_cgs_device`, installs `amdgpu_cgs_ops`, and stores `adev`. Register ops translate CGS calls to AMDGPU MMIO macros. Firmware info first handles non-SMU microcode by converting CGS firmware IDs to `AMDGPU_UCODE_ID`, reading the already-loaded firmware header, returning kernel pointer, image size, MC address, version, firmware version, and feature version, with special handling for MEC jump tables. SMU firmware requests choose ASIC-specific firmware filenames when `adev->pm.fw` is not loaded, request the firmware, optionally register it for PSP loading, parse the SMC firmware header, print it, update PM firmware version, and return image metadata.

## State and persistence behavior
The CGS wrapper owns one heap allocation per CGS device. Firmware info reads and may populate runtime firmware state in `adev->pm.fw`, `adev->pm.fw_version`, `adev->firmware.ucode[AMDGPU_UCODE_ID_SMC]`, and `adev->firmware.fw_size`. Register accesses directly read or mutate hardware registers. There is no durable persistence.

## Dependencies and integration points
It depends on CGS interfaces, AMDGPU register macros, firmware request/release helpers, AMDGPU ucode header layouts, PM/SMU firmware storage, PSP firmware loading state, PCI device/revision IDs, and ASIC enums. It integrates with legacy SMU/power-management components that expect CGS operations rather than native AMDGPU calls.

## Risks and edge cases
Firmware filename selection is a large ASIC/revision switch and can break new revisions if not updated. Audio endpoint indirect register access is explicitly unimplemented. Unsupported indirect spaces call `BUG()`, which is severe for bad callers. SMU firmware loading mutates shared `adev->pm.fw` state and must align with broader firmware loading policy. MEC JT1/JT2 sizing and offsets depend on firmware header fields being sane.

## Test signals
Signals include CGS creation/destruction, register read/write smoke tests for each supported indirect space, firmware info queries for SDMA/CP/RLC/MEC and SMU IDs across supported ASICs, missing firmware failure paths, PSP load-type accounting, kicker firmware selection by PCI revision/device, and rejection of unsupported firmware IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cgs.c -->
