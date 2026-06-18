# subset-b-003630 research

Grouped research for the Imagination PowerVR DRM free-list, firmware, GEM, HWRT, and job submission files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.c

## Purpose
Implements PowerVR parameter-manager free lists: kernel bookkeeping, firmware-facing freelist structures, host-side growth on firmware requests, reconstruction after HWR, and lifetime management for free lists referenced by HWRT datasets.

## Important APIs, types, and functions
- `pvr_get_free_list_min_pages()` returns the minimum local freelist size, with RogueXE and BRN66011-specific thresholds.
- `pvr_free_list_create()` validates UAPI create arguments, binds the userspace-provided PM/FW protected list BO, allocates a firmware ID, creates the FW freelist object, and seeds it with initial pages.
- `pvr_free_list_process_grow_req()` handles firmware FWCCB grow requests and replies with `ROGUE_FWIF_KCCB_CMD_FREELIST_GROW_UPDATE`.
- `pvr_free_list_process_reconstruct_req()` rebuilds one or more free lists and sends `FREELISTS_RECONSTRUCTION_UPDATE`.
- Internal helpers include `free_list_create_kernel_structure()`, `free_list_fw_init()`, `pvr_free_list_grow()`, `pvr_free_list_insert_node_locked()`, and `calculate_free_list_ready_pages_locked()`.

## Control flow
Creation checks growth invariants, alignment to `ROGUE_BIF_PM_FREELIST_BASE_ADDR_ALIGNSIZE`, nonzero maximum pages, and that the target GPU virtual address maps to a PM/FW protected GEM object with no CPU userspace access. The free list is assigned a global firmware ID via `pvr_dev->free_list_ids`, then a FW object is initialized and `pvr_free_list_grow()` allocates the initial backing pages.

Growing allocates a `pvr_free_list_node`, creates a cached device GEM allocation sized in PM physical pages, walks its DMA pages, writes PFNs into the freelist stack object from the calculated stack offset, and reserves `ready_pages` so firmware can handle OOM quickly before host growth completes. Firmware grow requests first account for previously consumed ready pages, attempt another grow of `grow_pages`, then report new and ready page counts back through KCCB.

Reconstruction looks up each FW freelist ID, rebuilds the freelist stack from the tracked memory-block list, resets firmware counters in the mapped freelist structure, and marks attached HWRT data as HWR while clearing `HWRTDATA_HAS_LAST_GEOM`.

## State and persistence
Persistent state lives in `struct pvr_free_list`: FW ID, current/max/grow/ready pages, the userspace freelist GEM BO, FW object, GPU address, memory block list, and HWRT linkage list. `free_list_ids` maps FW IDs to live objects and `pvr_file->free_list_handles` owns file handles. Page memory persists as `pvr_free_list_node` objects until release. The FW freelist struct stores current stack top, device address, grow state, and page counters.

## Dependencies and integration points
Depends on GEM allocation/mapping, VM lookup of userspace GPU addresses, FW object helpers, xarrays, KCCB/FWCCB messaging, Rogue FWIF layouts, and HWRT datasets. HWRT data is linked to the local freelist so reconstruction can reset render-target state. Release invokes `pvr_fw_structure_cleanup()` and may process pending FWCCB work before retrying cleanup when firmware reports busy.

## Risks
The page-count arithmetic is alignment-sensitive and uses reserved ready pages, so off-by-one or underflow errors can corrupt the freelist stack. Growth updates host state before KCCB response and must stay consistent with firmware consumption. Reconstruction maps HWRT FW objects inside the freelist lock; errors are warning-only. FW cleanup returning `-EBUSY` is retried once after FWCCB processing, so persistent firmware ownership still becomes a warning path.

## Test signals
Exercise create argument validation, PM/FW-protected BO requirements, initial grow, grow request response counts, reconstruction after HWR, HWRT unlink on destroy, and cleanup busy retry. Useful runtime signals are WARNs from malformed IDs, invalid DMA PFN width, FW cleanup failures, KCCB send failures, and successful page-count changes visible in firmware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.h

## Purpose
Declares the PowerVR freelist object model and APIs used by ioctl creation, HWRT setup, firmware grow/reconstruct callbacks, and file teardown.

## Important APIs, types, and functions
- `struct pvr_free_list_node` represents one host allocation inserted into a firmware freelist stack.
- `struct pvr_free_list` stores the object refcount, device pointer, userspace stack BO, FW structure object, firmware ID, page accounting, grow policy, memory block list, HWRT list, and GPU address.
- `pvr_free_list_create()`, `pvr_destroy_free_lists_for_file()`, `pvr_free_list_put()`, `pvr_free_list_add_hwrt()`, and `pvr_free_list_remove_hwrt()` provide lifecycle and relationship management.
- `pvr_free_list_lookup()` looks up file handles; `pvr_free_list_lookup_id()` looks up firmware IDs with `kref_get_unless_zero()`.
- `pvr_free_list_process_grow_req()` and `pvr_free_list_process_reconstruct_req()` are firmware-event entry points.

## Control flow
The header has only inline lookup/reference flow. File-handle lookup locks `pvr_file->free_list_handles`, loads the pointer, and takes a normal reference. Firmware-ID lookup locks `pvr_dev->free_list_ids` and avoids resurrecting objects already in release by using `kref_get_unless_zero()`.

## State and persistence
It defines all long-lived freelist state. The lock protects mutable page counters and the memory/HWRT lists; xarrays provide external handles and firmware ID lookup. References persist across HWRT and firmware callback use until `pvr_free_list_put()` reaches zero.

## Dependencies and integration points
Depends on `pvr_device`, Linux `kref`, `list_head`, `mutex`, `xarray`, UAPI create arguments, and Rogue FWIF request structs. It is consumed by HWRT, job/resource teardown, FWCCB processing, and ioctl handlers that create/destroy free lists.

## Risks
Callers must balance lookups with `pvr_free_list_put()`. The header exposes enough struct fields that implementation invariants, especially lock coverage around page counts and lists, can be violated by future callers if not kept private by convention.

## Test signals
Build coverage catches FWIF type drift and lookup signature mismatches. Runtime tests should verify handle lookup, FW ID lookup during concurrent teardown, and paired add/remove of HWRT list nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.c

## Purpose
Implements common firmware validation, image processing, firmware heap/address management, boot-time FWIF structure creation, firmware object allocation, cleanup requests, MTS scheduling, boot wait, and hard-reset reinitialization for all supported firmware processors.

## Important APIs, types, and functions
- Firmware image handling: `pvr_fw_validate()`, `pvr_fw_get_device_info()`, `pvr_fw_validate_init_device_info()`, `layout_get_sizes()`, `pvr_fw_process()`.
- Section lookup and relocation helpers: `pvr_fw_find_layout_entry()`, `pvr_fw_find_mmu_segment()`, `pvr_fw_find_private_data()`.
- Lifecycle: `pvr_fw_init()`, `pvr_fw_fini()`, `pvr_wait_for_fw_boot()`, `pvr_fw_hard_reset()`.
- FW object APIs: `pvr_fw_object_create()`, `pvr_fw_object_create_and_map()`, `pvr_fw_object_create_and_map_offset()`, `pvr_fw_object_destroy()`, `pvr_fw_object_get_fw_addr_offset()`, `pvr_fw_obj_get_gpu_addr()`.
- Firmware communication support: `pvr_fw_structure_cleanup()` and `pvr_fw_mts_schedule()`.

## Control flow
Validation treats the last 4 KiB of the firmware file as the info header and layout table, checks version, layout entry sizes/count, open-source firmware flag, supported major version, GPU BVNC match, and non-wrapping section ranges. Device-info data immediately before the header initializes quirks, enhancements, features, and feature parameters.

`pvr_fw_init()` chooses a processor definition table by `processor_type`, calls processor `init()`, initializes the firmware `drm_mm`, processes the firmware image, initializes KCCB/FWCCB and return slots, creates FWIF structures, starts the processor, then polls `fwif_sysinit->firmware_started`. Failure unwinds in strict reverse order. `pvr_fw_fini()` destroys FWIF structures, CCBs, code/data objects, checks that no FW objects remain, tears down the FW address allocator, and calls processor `fini()`.

Firmware processing sizes allocations by layout section type, maps code at firmware heap offset 0, maps private data either at a fixed layout address for processors that require it or from the general heap, optionally maps coremem code/data, asks the processor-specific parser to populate host-side shadow buffers, copies those buffers to FW memory, unmaps CPU mappings, and creates the connection-control object in the fixed config heap.

FW object creation wraps GEM allocation, implicit PM/FW protection, firmware `drm_mm` allocation or reservation, processor-specific VM mapping, CPU mapping, optional init callback, and insertion into `fw_objs.list`. Destroy removes the object from the list, unmaps from processor address space, drops GEM, and frees the wrapper.

## State and persistence
`pvr_dev->fw_dev` stores the firmware handle, parsed header/layout pointers, version, processor definitions, firmware heap geometry, `drm_mm`, booted flag, persistent CPU mappings for FWIF structures, and a tracked list of FW objects. Firmware code/data shadow copies in `pvr_fw_mem` persist after boot so hard reset can repopulate memory. FW objects persist in both GPU/FW address spaces until explicitly destroyed. Objects without `PVR_BO_FW_NO_CLEAR_ON_RESET` are zeroed and reinitialized on hard reset.

## Dependencies and integration points
Depends on Linux firmware loading, DRM managed locks/MM allocator, GEM helpers, processor definitions from META/MIPS/RISC-V files, KCCB/FWCCB CCB code, FW trace setup, start/stop sequencing, PVR feature/quirk metadata, device clocks, VM mapping, and Rogue FWIF structures. Cleanup requests are used by context, HWRT, and freelist teardown.

## Risks
Firmware format parsing is trust-boundary code; it validates many sizes but ELF-specific parsing is delegated. `pvr_wait_for_fw_boot()` busy-polls for up to 5 seconds. FW object destroy intentionally leaks memory if unmap fails, preventing use-after-unmap but leaving allocations behind. Hard reset maps every tracked object and warns but continues if mapping returns an error, so a failed vmap could still lead to invalid access. Address calculations depend on processor-specific cacheability encodings and fixed config heap offsets.

## Test signals
Test validation should cover bad header versions, closed-source flag, unsupported major version, wrong BVNC, malformed layout table, missing private-data section, processor-type selection, boot timeout, init unwind paths, cleanup busy/timeout/EIO returns, FW object fixed-offset reservation, hard reset reinitialization, and FW object leak warnings on final teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.h

## Purpose
Defines the common firmware object, processor abstraction, firmware memory inventory, device firmware state, processor-type enum, and public firmware APIs shared by the PowerVR DRM driver.

## Important APIs, types, and functions
- `struct pvr_fw_object` wraps a GEM object mapped into firmware address space, its `drm_mm_node`, FW address offset, reset init callback, and list node.
- `struct pvr_fw_defs` is the processor vtable for init/fini, image processing, VM map/unmap, FW address conversion, wrapper init, IRQ check/clear, and fixed-data-address policy.
- `struct pvr_fw_mem` enumerates code/data/core sections plus FWIF objects such as connection control, OSINIT, SYSINIT, trace, power sync, fault page, runtime config, and MMU-cache sync.
- `struct pvr_fw_device` stores firmware metadata, boot state, processor data, heap geometry, address allocator, mapped FWIF pointers, trace state, and tracked FW-object list.
- Public APIs cover validation/init/fini, boot wait, hard reset, MTS kick, heap info calculation, layout lookup, MMU segment lookup, FW structure cleanup, FW object creation/mapping/destruction, address queries, and ELF command-stream processing.

## Control flow
The header mostly declares call surfaces. Inline wrappers delegate FW object CPU mapping to GEM vmap/vunmap, DMA lookup to GEM DMA address lookup, default FW address lookup to offset 0, and object-size lookup to the backing GEM size.

## State and persistence
It defines the driver-wide firmware persistence model: parsed firmware metadata, code/data shadows, FWIF shared structures, processor-specific data, mapped objects, and reset callbacks. `PVR_BO_FW_NO_CLEAR_ON_RESET` in the backing GEM flags controls whether an object survives hard reset without zero/init.

## Dependencies and integration points
Includes firmware info, trace, GEM, and DRM MM definitions. Processor definitions are provided externally by architecture files. Most driver subsystems depend on these helpers for firmware-visible allocations and addresses, including CCBs, contexts, HWRT, free lists, MMU cache commands, and trace.

## Risks
The vtable is mandatory for most operations; a missing or wrong processor callback breaks boot or address encoding. Many structures are shared with firmware ABI headers, so layout drift is high impact. Inline unmap-and-destroy assumes the object is currently CPU mapped.

## Test signals
Build coverage catches ABI signature drift. Runtime signals include firmware boot success, correct per-processor address encodings, successful creation/destruction of FW objects, and hard reset preserving only no-clear objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_info.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_info.h

## Purpose
Defines the driver-side metadata format appended to PowerVR firmware binaries: section IDs, section types, firmware info header, layout entries, and device-info header.

## Important APIs, types, and functions
- `FW_BLOCK_SIZE` fixes firmware metadata alignment to 4 KiB.
- `PVR_FW_INFO_MAX_NUM_ENTRIES` limits layout table entries to 8.
- `enum pvr_fw_section_id` names META, MIPS, and RISC-V code/data/private/core/boot sections.
- `enum pvr_fw_section_type` classifies entries as code, data, coremem code, coremem data, or none.
- `struct pvr_fw_info_header` carries metadata version, layout dimensions, BVNC, page size, compatibility flags, firmware version, and device-info size.
- `struct pvr_fw_layout_entry` maps firmware virtual sections to base address, max size, allocation size, and allocation offset.
- `struct pvr_fw_device_info_header` sizes BRN, ERN, feature, and feature-parameter masks that follow it.

## Control flow
This file has no runtime control flow. `pvr_fw.c` interprets the layout described in the comment: original firmware image, device info, info header, then layout table in the final 4 KiB block.

## State and persistence
No mutable state is defined here. The structs describe on-disk firmware metadata that is retained by pointer in `pvr_dev->fw_dev` after validation.

## Dependencies and integration points
Used by the common firmware validator and by processor-specific loaders to identify sections. Its IDs must match firmware build tooling and the Rogue firmware ABI expected by the kernel driver.

## Risks
Any incompatible struct layout, enum value change, or version mismatch makes firmware unloadable. The maximum layout entry count constrains future firmware section growth. Device-info size and mask sizes are parsed from firmware and must remain well-formed.

## Test signals
Firmware validation logs for unsupported info version, format mismatch, wrong BVNC, unsupported firmware version, and malformed layout entries are the primary signals. Build tests should catch enum users when new processor sections are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.c

## Purpose
Implements the META firmware-processor backend: slave-port register reads, wrapper setup, LDR firmware parsing, bootloader configuration generation, segment MMU/cache setup, firmware address conversion, VM mapping, and META IRQ handling.

## Important APIs, types, and functions
- `pvr_meta_cr_read32()` reads META registers through the slave port with ready/idle polling.
- `pvr_meta_wrapper_init()` programs META boot mode and Garten wrapper fence settings.
- LDR parsing helpers `meta_ldr_cmd_loadmem()`, `meta_ldr_cmd_zeromem()`, `meta_ldr_cmd_config()`, and `process_ldr_command_stream()` populate code/data/core sections and boot configuration.
- Boot configuration helpers `configure_seg_id()`, `configure_seg_mmu()`, and `configure_meta_caches()` append register/value pairs to the bootloader argument area.
- `pvr_meta_fw_process()`, `pvr_meta_init()`, `pvr_meta_get_fw_addr_with_offset()`, `pvr_meta_vm_map()`, `pvr_meta_vm_unmap()`, `pvr_meta_irq_pending()`, and `pvr_meta_irq_clear()` implement `pvr_fw_defs_meta`.

## Control flow
META init declares a 32 MiB firmware heap. Processing starts by writing privileged JTAG access, then configures the segment MMU for the FW data section, walks the META LDR command stream, appends cache setup, terminates the boot argument list, and optionally supplies coremem code address/size. LDR `LOADMEM` copies firmware payloads into the host section backing selected by `pvr_fw_find_mmu_segment()`, `ZEROMEM` clears non-coremem ranges, and `CONFIG` converts firmware register-write commands into bootloader arguments.

Wrapper initialization sets META master boot mode, routes Garten idle to META, and configures wrapper fence PC/DM fields. Firmware address conversion adds the META data segment base and sets uncached bits for uncached FW objects. VM mapping uses the kernel VM context at the reserved firmware heap address.

## State and persistence
META-specific persistent state is mostly encoded in bootloader arguments written into the FW code allocation and in the common firmware heap metadata. No processor-private heap object is allocated in this file. FW object mappings persist in the kernel VM context until common FW object teardown.

## Dependencies and integration points
Depends on Rogue META register definitions, LDR block structures, feature `meta_coremem_size`, common firmware layout helpers, kernel VM mapping, and common start/stop code. `pvr_fw_start()` calls the wrapper callback; `pvr_fw_stop()` uses `pvr_meta_cr_read32()` to decide whether debugger halt state permits skipping Garten idle polling.

## Risks
The LDR parser is firmware input parsing and relies on bounds checks around nested L1/L2 blocks; malformed lengths or offsets return `-EINVAL`. The `switch` syntax is unusual but compiles as a switch over `l1_data->cmd & mask`; future edits could easily break it. Segment and cache register sequences are boot-critical, and address cacheability is encoded in firmware-visible addresses.

## Test signals
Test with valid META LDR firmware, malformed LDR next pointers and block lengths, missing FW data layout entries, coremem present/absent, slave-port timeout paths, META IRQ status/clear, and boot failures after wrapper/segment/cache changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.h

## Purpose
Declares the small public META helper surface needed outside the META backend.

## Important APIs, types, and functions
- Forward declares `struct pvr_device`.
- Declares `pvr_meta_cr_read32(struct pvr_device *pvr_dev, u32 reg_addr, u32 *reg_value_out)`.

## Control flow
No runtime control flow is present. The declared function is implemented in `pvr_fw_meta.c` and used by firmware stop code for META-specific halt/debugger state inspection.

## State and persistence
No state is stored here. State accessed by the declared function is hardware slave-port register state.

## Dependencies and integration points
Depends only on Linux integer types and `pvr_device` forward declaration. Included by META implementation and start/stop code.

## Risks
The header intentionally exposes only a low-level register read helper. Broader META internals should remain private to avoid coupling generic firmware stop/start paths to META boot implementation details.

## Test signals
Build coverage catches declaration drift. Runtime signal is successful `pvr_fw_stop()` behavior on META firmware, including timeout propagation from slave-port polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.c

## Purpose
Implements the MIPS firmware-processor backend: firmware heap initialization, MIPS VM setup/teardown, ELF firmware processing, boot-data patching, wrapper/remap register programming, firmware address conversion, and MIPS IRQ handling.

## Important APIs, types, and functions
- `pvr_mips_init()` initializes a 16 MiB firmware heap with a 1 MiB reserved area and calls `pvr_vm_mips_init()`.
- `pvr_mips_fini()` tears down MIPS VM state.
- `pvr_mips_fw_process()` parses ELF firmware and patches MIPS boot data with DMA addresses, register base, stack address, and page-table pages.
- `pvr_mips_wrapper_init()` configures wrapper mode and boot/data/exception address remaps.
- `pvr_mips_get_fw_addr_with_offset()`, `pvr_mips_irq_pending()`, and `pvr_mips_irq_clear()` complete `pvr_fw_defs_mips`.

## Control flow
Firmware processing first delegates PT_LOAD copying to `pvr_fw_process_elf_command_stream()`, then requires layout entries for boot code, boot data, exception code, and stack. It resolves DMA addresses in code/data GEM objects, writes stack/register/page-table metadata into the bootloader configuration area inside boot data, and handles host page sizes larger than the firmware's expected 4 KiB pages.

Wrapper init requires physical bus width greater than 32 bits, configures microMIPS wrapper mode, maps boot code, boot data, and exception code remap windows to DMA addresses, applies BRN63553 remap5 workaround on 36-bit cores, sets Garten wrapper idle control, and enables EJTAG probe.

## State and persistence
MIPS-specific persistent state is stored in `struct pvr_fw_mips_data`, including page-table pages, CPU mapping, DMA addresses for page tables and boot sections, cache policy, and PFN mask. The firmware heap reserves 1 MiB. MIPS addresses are formed from the firmware heap offset masked by the heap size and ORed with `0xC0000000`.

## Dependencies and integration points
Depends on MIPS firmware ABI definitions, `pvr_vm_mips_*` map/unmap/init/fini functions, common ELF processing, GEM DMA address lookup, PVR feature `phys_bus_width`, and quirk BRN63553. It is selected by `pvr_fw_init()` through the common processor vtable.

## Risks
MIPS support is constrained to wider-than-32-bit physical bus configurations. Missing required layout sections fails boot processing. Remap registers directly use DMA addresses and alignment masks; wrong section offsets or DMA lookup errors become boot failures or WARNs. Host page-size conversion for the firmware page table is a portability-sensitive path.

## Test signals
Validate MIPS firmware boot on supported bus widths, failure on missing layout sections, BRN63553 behavior on 36-bit cores, IRQ pending/clear registers, page-table DMA address population with non-4K host pages, and correct teardown through `pvr_vm_mips_fini()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.h

## Purpose
Defines MIPS firmware private data used by the common firmware device state and MIPS backend.

## Important APIs, types, and functions
- `PVR_MIPS_PT_PAGE_COUNT` converts the firmware's maximum 4 KiB page-table footprint into host pages.
- `struct pvr_fw_mips_data` stores page-table pages, CPU page-table pointer, DMA mappings for each page, boot code/data/exception DMA addresses, cache policy, and PFN mask.

## Control flow
No executable control flow exists in the header. The macro handles host `PAGE_SIZE` differences at compile time.

## State and persistence
The struct is persistent processor-private firmware state under `pvr_fw_device.processor_data.mips_data`. It survives for the firmware lifetime and is used during boot wrapper setup and VM mapping.

## Dependencies and integration points
Depends on Rogue MIPS ABI constants, `asm/page.h`, and Linux math/types. Used by `pvr_fw_mips.c`, common firmware state, and MIPS VM helpers.

## Risks
The firmware assumes 4 KiB page-table granularity even when host pages are larger. Any mismatch in `ROGUE_MIPSFW_MAX_NUM_PAGETABLE_PAGES` or `ROGUE_MIPSFW_PAGE_SIZE_4K` changes allocation and DMA programming requirements.

## Test signals
Build coverage for different host page sizes and runtime MIPS firmware boot are the main signals. Page-table DMA values in boot data should map all firmware-required 4 KiB pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_riscv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_riscv.c

## Purpose
Implements the RISC-V firmware-processor backend: wrapper remap programming, ELF firmware processing, coremem boot-data patching, firmware heap setup, VM mapping, firmware address conversion, and IRQ handling.

## Important APIs, types, and functions
- `pvr_riscv_wrapper_init()` programs FWCORE bootloader code/data remap windows from firmware object GPU addresses.
- `struct rogue_riscv_fw_boot_data` describes boot-data fields patched at the start of FW data memory.
- `pvr_riscv_fw_process()` loads ELF PT_LOAD segments and patches optional coremem code/data addresses and sizes.
- `pvr_riscv_init()` initializes a 32 MiB firmware heap.
- `pvr_riscv_get_fw_addr_with_offset()`, `pvr_riscv_vm_map()`, `pvr_riscv_vm_unmap()`, `pvr_riscv_irq_pending()`, and `pvr_riscv_irq_clear()` complete `pvr_fw_defs_riscv`.

## Control flow
Firmware processing is straightforward: common ELF processing populates code/data/core allocations, then boot data at the start of data memory is filled with GPU virtual addresses, FW addresses, and object sizes for coremem sections if they exist. Wrapper init builds common remap options from heap size and FW private MMU context, asserts address alignment, writes bootloader code and data remap registers, and sets Garten idle control before common start code releases the FW core and toggles `ROGUE_CR_FWCORE_BOOT`.

## State and persistence
No extra processor-private state is allocated. RISC-V persistent state is the common firmware heap, FW objects, and boot-data fields. Firmware address cacheability is encoded by ORing either shared uncached or shared cached region bases into the FW address.

## Dependencies and integration points
Depends on Rogue RISC-V register/region macros, common ELF processing, kernel VM mapping, FW object GPU/FW address helpers, and common start/stop code. Selected by the common firmware vtable for RISC-V processor type.

## Risks
Remap register programming assumes FW object GPU addresses satisfy hardware alignment. The boot-data struct is local to this file and must stay ABI-compatible with firmware. Cacheability is address-region based, so incorrect object flags translate into wrong FW-visible regions.

## Test signals
Validate RISC-V firmware boot with and without coremem sections, remap alignment WARNs, IRQ pending/clear behavior, boot-data contents, and correct behavior for cached versus uncached FW objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.c

## Purpose
Sequences GPU/FW hardware start and stop: AXI ACE-Lite configuration, BIF catalogue programming, SLC setup, soft-reset sequencing, processor wrapper boot, RISC-V boot trigger, and idle polling before shutdown reset.

## Important APIs, types, and functions
- `pvr_fw_start()` performs hardware reset release and firmware processor boot.
- `pvr_fw_stop()` waits for idle, detaches MTS thread associations, performs extra BIF/SLC idle checks, handles META debugger state and MARS-layout differences, then asserts soft reset.
- Helpers `rogue_axi_ace_list_init()`, `rogue_bif_init()`, and `rogue_slc_init()` program bus, MMU catalogue, and SLC control registers.

## Control flow
Start optionally disables secure bus protection, clears RISC-V boot, asserts full soft reset, releases Rascal/Dust, releases everything except the firmware processor, initializes SLC, runs the processor-specific wrapper, configures AXI ACE-Lite, programs BIF catalogue bases for non-MIPS processors, delays for reset timing, releases the firmware processor, and for RISC-V writes `FWCORE_BOOT`.

Stop checks feature `layout_mars`, waits for Sidekick and SLC idle when applicable, clears MTS DM associations for thread 0 and additionally thread 1 on META, polls BIF and BIFPM MMU/read/SLC status registers, repeats idle checks, optionally reads META halt status to skip Garten idle when a debugger is attached, waits for Garten or MARS idle as appropriate, then asserts the platform-specific soft-reset mask.

## State and persistence
The file does not own C objects but mutates persistent hardware register state: soft reset, bus coherency, BIF/FWCORE page catalogue bases, SLC control, wrapper configuration, MTS associations, and RISC-V boot control. The state persists in hardware until reset or reprogramming.

## Dependencies and integration points
Depends on firmware processor type and callbacks, PVR feature/quirk queries, kernel VM page-table root DMA address, register read/write/poll helpers, META slave-port read helper, and common firmware init/fini. Called by `pvr_fw_init()` and unwind/fini paths.

## Risks
Start/stop is timing and platform-order sensitive. Wrong soft-reset masks, missing delays, MIPS/non-MIPS BIF differences, secure bus handling, SLC cache policy, or idle-poll masks can hang the GPU or fail boot. Stop has multiple timeout paths and META debugger behavior alters Garten idle waiting.

## Test signals
Boot and shutdown on META, MIPS, and RISC-V processors; timeout returns from SLC/Sidekick/BIF polls; RISC-V FWCORE boot transitions; secure bus feature coverage; MARS-layout cores; and suspend/resume or hard-reset loops are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.h

## Purpose
Declares the common firmware processor start and stop APIs.

## Important APIs, types, and functions
- Forward declares `struct pvr_device`.
- Declares `pvr_fw_start()` and `pvr_fw_stop()`.

## Control flow
No runtime flow exists in the header. It exposes start/stop sequencing to common firmware initialization and teardown.

## State and persistence
No state is stored here. The declared functions mutate hardware register state and firmware boot state in their implementation.

## Dependencies and integration points
Included by `pvr_fw.c` and implemented by `pvr_fw_startstop.c`. It keeps hardware sequencing separate from common firmware object allocation.

## Risks
Signature changes affect firmware init unwind paths. The header hides all processor/platform-specific details, which is appropriate for keeping callers from depending on reset internals.

## Test signals
Build coverage catches declaration drift. Runtime validation belongs to `pvr_fw_start()` and `pvr_fw_stop()` boot/shutdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.c

## Purpose
Implements firmware trace buffer allocation, initial/module/debugfs trace-mask control, KCCB logtype updates, trace snapshot parsing, and debugfs files for per-thread firmware logs.

## Important APIs, types, and functions
- `pvr_fw_trace_init()` allocates per-thread FW trace buffers and a trace-buffer control structure.
- `pvr_fw_trace_fini()` destroys those objects.
- `pvr_fw_trace_debugfs_init()` creates `trace_N` files and `trace_mask`.
- `validate_group_mask()`, `build_log_type()`, and `update_logtype()` validate and apply enabled trace groups.
- Seq-file helpers `fw_trace_open()`, `fw_trace_seq_start()`, `fw_trace_seq_next()`, `fw_trace_seq_show()`, and `fw_trace_release()` expose a stable snapshot while firmware may keep writing.

## Control flow
Initialization allocates an uncached no-clear FW object for each firmware thread trace ring, reads the initial mask from the optional `init_fw_trace_mask` module parameter, allocates the no-clear control object with `tracebuf_ctrl_init()`, fills firmware addresses and host pointers for each ring, and records pointers to each thread's control-space entry.

Changing `trace_mask` validates that the requested groups are a subset of `ROGUE_FWIF_LOG_TYPE_GROUP_MASK`, updates local `group_mask` and firmware control `log_type`, then under `reset_sem` and `drm_dev_enter()` sends `ROGUE_FWIF_KCCB_CMD_LOGTYPE_UPDATE` and waits for completion. Opening a trace file copies the ring and assertion info, records the firmware write pointer as start offset, and uses seq iteration to decode valid IDs through `stid_fmts`.

## State and persistence
`struct pvr_fw_trace` stores the control FW object/mapping, per-thread buffer objects/mappings, current group mask, and FW tracebuf-space pointers. Trace buffers and control structures use `PVR_BO_FW_NO_CLEAR_ON_RESET`, so they persist across hard reset instead of being zeroed by common FW object reset.

## Dependencies and integration points
Depends on common FW object helpers, KCCB command submission, reset semaphore/device-enter lifetime protection, debugfs, module parameters, Rogue firmware trace ABI, string-format table `stid_fmts`, and FWIF trace structures. `pvr_fw_create_structures()` wires the trace control address into SYSINIT.

## Risks
Trace parsing trusts firmware-produced IDs and format table parameter counts, stopping on corrupt or unknown IDs. `update_logtype()` mutates local state before KCCB completion, so a failed update can leave host state ahead of firmware. Buffers are copied without locking against firmware writes by design, producing consistent snapshots only after the copy.

## Test signals
Validate debugfs file creation, module parameter validation, mask set/get, KCCB logtype update success/failure, trace output formatting, assertion formatting, corrupt trace IDs, no-clear behavior across hard reset, and teardown after partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.h

## Purpose
Defines firmware trace state structures and declares firmware trace lifecycle/debugfs APIs.

## Important APIs, types, and functions
- `struct pvr_fw_trace_buffer` stores a FW buffer object, CPU mapping, and pointer to the firmware control entry for one thread.
- `struct pvr_fw_trace` stores the control object/mapping, per-thread buffers, and enabled trace group mask.
- Declares `pvr_fw_trace_init()`, `pvr_fw_trace_fini()`, and `pvr_fw_trace_debugfs_init()`.

## Control flow
No executable flow exists in the header. It defines the state consumed by common firmware initialization and debugfs setup.

## State and persistence
The structures represent persistent trace state owned by `pvr_fw_device`. Buffers are firmware-visible allocations and, in the implementation, are marked no-clear-on-reset.

## Dependencies and integration points
Depends on DRM file definitions, Linux types, and Rogue FWIF trace structs. The header is included by `pvr_fw.h`, `pvr_fw.c`, and the trace implementation.

## Risks
The array size is `ROGUE_FW_THREAD_MAX`; firmware/control structure thread-count mismatches are guarded in implementation by build checks. Adding trace groups or changing FWIF trace structures must keep these wrappers in sync.

## Test signals
Compile-time structure compatibility and runtime debugfs trace output are the main signals. Initialization must allocate one buffer per firmware thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_util.c

## Purpose
Provides a shared ELF PT_LOAD firmware loader used by non-META firmware processor backends.

## Important APIs, types, and functions
- `pvr_fw_process_elf_command_stream()` walks an ELF32 program header table and copies loadable segments into the appropriate firmware section allocations.

## Control flow
The function treats the firmware buffer as an ELF32 image, obtains the program header table from `e_phoff`, iterates `e_phnum` entries, skips non-`PT_LOAD` entries, resolves each loadable virtual address and memory size through `pvr_fw_find_mmu_segment()`, copies `p_filesz` bytes from the firmware file, and zeroes the remaining `p_memsz - p_filesz` bytes.

## State and persistence
It does not own state. It mutates the host-side code/data/core memory images passed by the caller; those images are later copied into FW objects and retained as reset shadows by `pvr_fw.c`.

## Dependencies and integration points
Depends on Linux ELF definitions, common firmware segment lookup, and DRM error logging. Used by MIPS and RISC-V firmware processing, while META uses its LDR parser.

## Risks
This is firmware input parsing. It relies on the firmware validator and `pvr_fw_find_mmu_segment()` for bounds/section checks, but it does not independently validate ELF header bounds, program header bounds, or `p_offset + p_filesz` against the firmware size. Malformed ELF metadata could therefore drive out-of-bounds reads if accepted earlier.

## Test signals
Use valid MIPS/RISC-V ELF firmware, PT_LOAD sections spanning code/data/core ranges, zero-fill behavior where `p_memsz > p_filesz`, invalid virtual addresses, and malformed ELF headers/program tables to validate rejection or hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.c

## Purpose
Implements PowerVR GEM buffer object creation, flag validation, CPU mapping policy, dma-buf export restrictions, userspace mmap restrictions, handle conversion, zeroing, and DMA-address lookup over shmem GEM backing storage.

## Important APIs, types, and functions
- `pvr_gem_object_create()` creates and zeroes PowerVR GEM objects with validated flags.
- `pvr_gem_create_object()` is the DRM object factory.
- `pvr_gem_object_into_handle()` and `pvr_gem_object_from_handle()` bridge PowerVR objects and DRM file handles.
- `pvr_gem_object_vmap()` and `pvr_gem_object_vunmap()` wrap shmem vmap/vunmap with cache synchronization for CPU-cached objects.
- `pvr_gem_get_dma_addr()` resolves a byte offset to a DMA address in the scatter-gather table.
- Object funcs customize free, export, mmap, pin, sg-table, vmap, and vunmap behavior.

## Control flow
Creation rejects zero-size or invalid flags, forces CPU cached mode on DMA-coherent devices, creates a shmem object, sets write-combine mapping policy when not CPU cached, stores immutable PowerVR flags, obtains/pins the sg table, synchronizes it for device access, and zeroes the full rounded object size through vmap. Export rejects PM/FW-protected objects with `-EPERM`. Mmap rejects objects without `DRM_PVR_BO_ALLOW_CPU_USERSPACE_ACCESS`.

CPU vmap locks the reservation object, maps through shmem, and if the object is CPU cached and already has an sg table, syncs for CPU. Vunmap syncs cached sg tables back for device before unmapping. DMA address lookup walks mapped DMA SG entries accumulating lengths until the requested offset falls within an entry.

## State and persistence
Persistent object state is `struct pvr_gem_object.flags` plus the shmem GEM base, page backing, sg table, vmap pointer, reservation object, and mmap offset. Flags are treated as immutable after creation and drive future CPU/device mapping behavior. BO contents are zeroed at creation.

## Dependencies and integration points
Depends on DRM GEM shmem helpers, PRIME export, dma-buf, DMA mapping APIs, device DMA coherency properties, and PVR VM/FW object code. Firmware objects are built on this GEM layer with implicit PM/FW protection.

## Risks
Cache coherency depends on correct flag selection and DMA syncs. `pvr_gem_get_dma_addr()` warns but proceeds if `sgt` is missing, which would dereference invalid state if callers violate backing assumptions. PM/FW protection is enforced for export and mmap, but all ioctl paths must also validate kernel-only flags.

## Test signals
Validate flag rejection, PM/FW protected export/mmap denial, userspace-access mmap success, DMA-coherent CPU cached override, zeroed allocation contents, vmap/vunmap cache sync paths, handle ownership transfer, and DMA address lookup across multi-entry sg tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.h

## Purpose
Defines PowerVR GEM object flags, the PowerVR shmem GEM wrapper, conversion helpers, and public GEM utility APIs.

## Important APIs, types, and functions
- Kernel-only flags `PVR_BO_CPU_CACHED` and `PVR_BO_FW_NO_CLEAR_ON_RESET` occupy high reserved bits; `PVR_BO_KERNEL_FLAGS_MASK` and `PVR_BO_UNDEFINED_MASK` support validation.
- Firmware mapping presets `PVR_BO_FW_FLAGS_DEVICE_CACHED` and `PVR_BO_FW_FLAGS_DEVICE_UNCACHED` describe device-cache policy.
- `struct pvr_gem_object` embeds `drm_gem_shmem_object` at offset 0 and stores immutable `flags`.
- Conversion macros bridge PowerVR, shmem, and base GEM objects.
- Declares object creation, handle conversion, page sg-table access, vmap/vunmap, DMA-address lookup, refcount get/put, and size helper APIs.

## Control flow
Only small inline helpers exist: sg-table retrieval delegates to shmem, references delegate to DRM GEM get/put, and size reads the base GEM object size.

## State and persistence
The header defines the persistent per-buffer flag state used for CPU caching, firmware reset preservation, PM/FW protection, device cache bypass, and userspace CPU access. The embedded layout assertion makes generic GEM/shmem conversion safe.

## Dependencies and integration points
Depends on DRM GEM/shmem/MM headers, UAPI BO flags, Rogue heap/meta constants, Linux scatterlist/types, and PVR device/file forward declarations. Used by almost every memory, VM, firmware, free-list, context, and job subsystem.

## Risks
Flag namespace mistakes can expose kernel-only flags to userspace or break validation. Since `flags` is const, behavior that needs mutable cache policy would require new object creation rather than modification. The comment contains a typo in "shem_gem" but the macro names are correct.

## Test signals
Build assertions for object layout, flag validation through create ioctl tests, and runtime GEM object creation/mapping/export/mmap tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.c

## Purpose
Implements hardware render target dataset creation and teardown. It validates freelist dependencies, computes render target/tile/MSAA hardware register values, creates common and per-RT firmware structures, allocates optional render-target arrays, and links HWRT data to free lists for reconstruction.

## Important APIs, types, and functions
- `pvr_hwrt_dataset_create()` creates a dataset with two RT data structures and common FW state.
- `pvr_destroy_hwrt_datasets_for_file()` and `pvr_hwrt_dataset_put()` manage lifetime.
- Internal initialization helpers include `hwrt_init_kernel_structure()`, `hwrt_init_common_fw_structure()`, and `hwrt_data_init_fw_structure()`.
- Register-value helpers include `get_cr_isp_mtile_size_val()`, `get_cr_multisamplectl_val()`, and `get_cr_te_aa_val()`.
- `struct pvr_rt_mtile_info` stores derived macrotile geometry used to fill common HWRT data.

## Control flow
Creation allocates a dataset, looks up all required freelists from file handles, rejects local freelists below `pvr_get_free_list_min_pages()`, computes tile counts from render dimensions and feature tile size, chooses macrotile layout based on `simple_parameter_format_version`, fills common HWRT register values and merge/MSAA/region-header fields, then creates a FW object initialized from the common struct.

For each of the two RT data slots, it records FW addresses for the common object and freelists, stores userspace-supplied device addresses for tail pointers, vheap table, RTC, PM mlist, macrotile array, and region headers, initializes RTA control, optionally allocates SRTC and RAA FW objects for multi-layer render targets, creates the per-RT HWRT FW object, and links the HWRT data to the local freelist. Release sends FW cleanup for each HWRT data object before destroying per-slot and common FW objects and dropping freelist refs.

## State and persistence
`struct pvr_hwrt_dataset` persists under a file handle with a kref, two `pvr_hwrt_data` entries, freelist references, common FW object, and `max_rts`. Each `pvr_hwrt_data` has a local copy of firmware state, a FW object, optional SRTC/RAA objects, and a freelist node. Firmware sees both common and per-RT structures until cleanup and destruction.

## Dependencies and integration points
Depends on freelist lookup/refcounting, common FW object helpers, Rogue FWIF render structures, Rogue CR bitfield definitions, PVR feature values for tile and sample layout, and xarray handle storage. Jobs reference `pvr_hwrt_data` for geometry/fragment submissions, and free-list reconstruction resets linked HWRT state.

## Risks
The code trusts many UAPI-provided GPU device addresses and sizes after basic setup; validation likely occurs in stream/UAPI layers. Feature-derived MSAA/tile bitfields are hardware-sensitive. Cleanup warnings during release indicate firmware still owns HWRT state. Partial initialization must unwind optional SRTC/RAA and freelist links correctly.

## Test signals
Validate dataset creation for single-layer and multi-layer render targets, all supported sample counts, simple and non-simple parameter formats, local freelist minimum enforcement, bad freelist handles, cleanup on partial failures, FW cleanup warnings, and geometry/fragment jobs using both RT data slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.h

## Purpose
Defines hardware render target data structures and lookup/lifetime APIs used by render submissions and file teardown.

## Important APIs, types, and functions
- `struct pvr_hwrt_data` stores one per-RT FW object, local firmware data copy, freelist linkage node, optional SRTC/RAA objects, and back pointer to its dataset.
- `struct pvr_hwrt_dataset` stores refcount, device pointer, common FW object/data, the fixed RT data array, referenced free lists, and maximum render targets.
- `pvr_hwrt_dataset_create()`, `pvr_destroy_hwrt_datasets_for_file()`, and `pvr_hwrt_dataset_put()` provide lifecycle APIs.
- Inline `pvr_hwrt_dataset_lookup()`, `pvr_hwrt_data_lookup()`, `pvr_hwrt_data_put()`, and `pvr_hwrt_data_get()` manage handle lookup and refcounts.

## Control flow
Dataset lookup locks the file xarray, loads a dataset handle, and takes a reference. RT data lookup first acquires the dataset, verifies the requested index is within the two-element data array, and returns the embedded data pointer while the dataset reference keeps it alive.

## State and persistence
The dataset owns both common and per-RT firmware state and freelist references. Per-RT data pointers are not independently refcounted; they borrow the dataset refcount and must be released with `pvr_hwrt_data_put()`.

## Dependencies and integration points
Depends on `pvr_device`, Rogue FWIF shared structs, UAPI HWRT creation args, xarrays, krefs, and freelist/FW object forward declarations. Jobs use HWRT data for geometry/fragment commands and reservation dependencies.

## Risks
Embedded per-RT data lifetime depends on correct dataset refcount handling. Future code must not store a `pvr_hwrt_data *` without holding the dataset reference. The fixed array sizes are tied to Rogue FWIF constants asserted in the implementation.

## Test signals
Build coverage for FWIF constant changes, handle lookup tests, out-of-range RT data index rejection, and job submission lifetime tests while datasets are concurrently destroyed are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.c

## Purpose
Implements userspace job submission conversion into firmware commands, job object lifetime, sync dependency/signal preparation, reservation locking/fence updates, queue push, and geometry/fragment pairing for atomic render submission.

## Important APIs, types, and functions
- `pvr_submit_jobs()` is the ioctl-facing entry point for batch job submission.
- `create_job()` allocates and initializes one `pvr_job`.
- `pvr_job_fw_cmd_init()` dispatches to geometry, fragment, compute, and transfer command builders.
- `prepare_job_syncs()` and `prepare_job_syncs_for_each()` collect sync ops, add dependencies, arm jobs, and update signal fences.
- `prepare_job_resvs_for_each()`, `update_job_resvs_for_each()`, and `pvr_jobs_link_geom_frag()` handle reservation locking, fence publication, and render-pair linking.
- `pvr_job_put()` releases job resources through `pvr_job_release()`.

## Control flow
Submission rejects empty batches, copies the userspace job array, allocates per-job helper data, creates each job and copies sync-op arrays, flushes deferred MMU work, initializes a `drm_exec`, prepares sync dependencies/signals for each job, locks context and HWRT reservation objects, detects adjacent geometry->fragment pairs with an explicit scheduled-fence dependency, updates reservation fences, pushes jobs to queues, and finally publishes signal fences.

Job creation validates command stream presence, disallows HWRT handles for non-render jobs, allocates an ID in `pvr_dev->job_ids`, looks up the context and optional HWRT data, builds the FW command from the user stream through `pvr_stream_process()`, converts UAPI flags to FW flags, writes HWRT FW addresses for render jobs, and initializes the scheduler queue job.

Geometry/fragment pairing requires adjacent geometry then fragment jobs, same context, same HWRT, and a dependency from fragment to geometry scheduled fence. The geometry job is made to submit the fragment job atomically, the fragment KCCB fence is dropped, cross pointers are installed, and the fragment holds a reference on the geometry job.

## State and persistence
Each `pvr_job` persists in `pvr_dev->job_ids` with a kref, scheduler job base, type/id, optional paired job, CCB fences, done fence, context ref, HWRT data ref, command buffer, firmware CCB command type, and power-management reference flag. Reservation fences are attached to HWRT firmware objects as write usage for geometry and read usage for fragment. Sync signal fences are staged in an xarray until all push operations are past the must-succeed point.

## Dependencies and integration points
Depends on context lookup and queues, DRM scheduler, DRM exec/reservation locking, PVR stream definitions, sync object helpers, MMU flush, PM helpers, KCCB/CCCB queue code, HWRT data, GEM reservation objects, and UAPI job/flag layouts. Queue implementation consumes `pvr_job_submit()`/job fields after push.

## Risks
The point after reservation update is intentionally must-succeed because fences are externally visible. Pairing assumes adjacent jobs in the ioctl batch and specific dependency shape; otherwise geometry and fragment are scheduled independently. Error paths mutate `args->jobs.count` while unwinding partial work. Sync preparation arms jobs before later reservation locking, so cleanup must release all refs/fences correctly. Incorrect context type or HWRT validation would let incompatible FW commands reach queues.

## Test signals
Validate empty submission rejection, malformed command streams, invalid flags per job type, context-type checks, HWRT handle/index checks, sync dependency import and signal fence publication, MMU flush failure unwind, geometry/fragment pairing and non-pairing cases, reservation fence usage, queue push order, and job release removing IDs and PM refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.h

## Purpose
Defines the PowerVR scheduler job object, reference and power-management helpers, and submission/queue-facing job APIs.

## Important APIs, types, and functions
- `struct pvr_job` embeds `drm_sched_job` and stores kref, UAPI job type, ID, paired job, CCCB/KCCB/done fences, device/context pointers, firmware command buffer and length, FW CCB command type, optional HWRT data, and PM reference state.
- `pvr_job_get()` and `pvr_job_put()` manage job references.
- `pvr_job_get_pm_ref()` and `pvr_job_release_pm_ref()` attach/detach GPU power references to jobs.
- Declares queue/scheduler helpers `pvr_job_wait_first_non_signaled_native_dep()`, `pvr_job_non_native_deps_done()`, `pvr_job_fits_in_cccb()`, `pvr_job_submit()`, and ioctl entry `pvr_submit_jobs()`.

## Control flow
Inline PM flow is idempotent: acquiring a PM ref returns immediately if already held, otherwise calls `pvr_power_get()` and records `has_pm_ref`; release only calls `pvr_power_put()` when the flag is set. `pvr_job_get()` is a nullable kref increment.

## State and persistence
The job object holds all state needed between ioctl parsing, scheduler queuing, firmware submission, and completion. Paired geometry/fragment jobs hold cross references, and the PM ref flag persists until release or explicit PM release.

## Dependencies and integration points
Depends on DRM scheduler, GEM fence types, UAPI job types, PVR power management, and forward declarations for contexts, devices, files, HWRT data, and queues. The implementation coordinates with queue, sync, context, and HWRT subsystems.

## Risks
Job lifetime is shared between scheduler, queue code, sync fences, and pairing references. Any unbalanced `pvr_job_get()` or PM reference leaks jobs or power; premature release can leave scheduler/firmware with stale command pointers.

## Test signals
Build coverage for scheduler API changes, PM get/put balance tests, paired job lifetime tests, and submission completion tests that ensure `pvr_job_release()` cleans context/HWRT/queue resources are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.h -->
