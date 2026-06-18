# subset-b-005414 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/include/uapi/intel-ipu3.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/include/uapi/intel-ipu3.h

## Purpose

`intel-ipu3.h` is the public UAPI contract for the Intel IPU3 ImgU V4L2 metadata interfaces. It defines the userspace-visible metadata formats `V4L2_META_FMT_IPU3_PARAMS` and `V4L2_META_FMT_IPU3_STAT_3A`, the IPU3 private V4L2 control base, and the packed structures that userspace passes through the parameters meta-output queue or receives through the 3A statistics meta-capture queue. The file is almost entirely ABI data layout: fixed-size integer fields, bitfields, packed/aligned structs, LUT dimensions, grid dimensions, and flags.

## Important APIs, types, and data contracts

The 3A statistics side is centered on `struct ipu3_uapi_stats_3a`. It aggregates AWB, AE, AF, and AWB filter-response outputs, embeds the `ipu3_uapi_4a_config` used for statistics generation, exposes stripe/bubble debugging information, and reports fixed-function enable status through `ipu3_uapi_ff_status`. Supporting types include `ipu3_uapi_grid_config`, AWB cell/buffer/config types, AE histogram/grid/weight/CCM types, AF filter/grid/raw-buffer types, AWB-FR raw/config types, and per-stripe bubble metadata.

The parameter side is centered on `struct ipu3_uapi_params`, which is the payload for `V4L2_META_FMT_IPU3_PARAMS`. It contains `struct ipu3_uapi_flags use`, then the actual parameter blocks: `ipu3_uapi_acc_param`, linearization VMEM, TNR3 VMEM/DMEM, XNR3 VMEM/DMEM, and optical black-level grid parameters. `ipu3_uapi_flags` is the update mask; each bit indicates whether the matching pipeline block should be refreshed from this metadata buffer.

`struct ipu3_uapi_acc_param` is the largest composed configuration. It groups accelerator/fixed-function controls for Bayer noise reduction, green disparity, demosaic, CCM, gamma, CSC, chroma downscale, shading, image enhancement/filter-directed denoise, Y downscalers, chroma noise reduction, luma edge enhancement/noise reduction, total color correction, advanced noise reduction, and 3A statistic configuration. Most leaf structs map directly to hardware register fields and use documented fixed-point ranges.

The file also defines the large ISP memory payloads that are not part of the ACC cluster: `ipu3_uapi_isp_lin_vmem_params`, `ipu3_uapi_isp_tnr3_vmem_params`, `ipu3_uapi_isp_tnr3_params`, `ipu3_uapi_isp_xnr3_vmem_params`, `ipu3_uapi_isp_xnr3_params`, and `ipu3_uapi_obgrid_param`.

## Control flow and runtime behavior

This header has no executable control flow. Its effective control flow is data-driven in the driver: userspace fills `ipu3_uapi_params`, sets bits in `ipu3_uapi_flags`, queues the metadata buffer, and the IPU3 CSS parameter code copies either user-provided values, previous values, or generated defaults into firmware memory according to those flags and the active firmware binary's offset tables. For statistics, firmware/ISP hardware writes data into the layouts described by `ipu3_uapi_stats_3a`; userspace consumes those buffers after V4L2 dequeue.

The order and packing of fields are the behavior. Many structures are declared `__packed` and key subobjects are `aligned(32)`, matching firmware and device memory expectations. Several buffers reserve extra bubble/stripe space to match how the image is split into up to `IPU3_UAPI_MAX_STRIPES` stripes and how padding bubbles are inserted between statistics sets.

## State and persistence

No state is persisted by this header. It describes transient per-frame and per-stream state carried in V4L2 metadata buffers. The `use` flags make partial parameter updates possible: if a bit is not set, the runtime can preserve older parameter memory or synthesize defaults. Statistics buffers include exposure/config correlation fields indirectly through firmware-side metadata, while this UAPI file mainly carries the raw statistics payloads and current statistics configuration.

## Dependencies and integration points

The header depends only on kernel UAPI integer types from `<linux/types.h>` and on V4L2 symbols supplied by including contexts, such as `v4l2_fourcc`, `V4L2_CID_USER_BASE`, and V4L2 metadata queues. Internally, `ipu3-abi.h` includes this file and embeds many UAPI structures inside firmware-facing ABI structures. `ipu3-css-params.c` consumes `ipu3_uapi_params` and `ipu3_uapi_flags` when constructing late-bound ISP parameter memory. V4L2-facing IPU3 code advertises these metadata formats and sizes to userspace.

## Risks and sharp edges

This is a stable userspace ABI. Any field reorder, size change, alignment change, enum/constant change, or bitfield layout change can break existing userspace and firmware assumptions. The bitfields are particularly sensitive because they encode hardware register layouts and fixed-point values. The many documented ranges are not enforced in this header, so validation must happen in driver code, userspace libraries, or firmware; out-of-range values can produce bad image quality or firmware errors. Large embedded arrays make `struct ipu3_uapi_params` and `struct ipu3_uapi_stats_3a` expensive to copy and sensitive to size mismatches. Reserved fields should remain zeroed by producers to avoid future ABI conflicts.

## Test signals

Useful test signals include compile-time structure size/offset checks where available, V4L2 metadata format negotiation using the expected buffer sizes, parameter queue tests that toggle each `ipu3_uapi_flags` bit and verify only the intended firmware memory region changes, and streaming tests that confirm 3A statistics buffers contain plausible AWB/AF/AWB-FR data for one- and two-stripe modes. ABI regression tests should compare `sizeof`/`offsetof` values against known-good kernel/user builds. Negative tests should cover undersized metadata buffers, nonzero reserved fields where validation exists, and malformed grid dimensions or LUT ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/include/uapi/intel-ipu3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-abi.h

## Purpose

`ipu3-abi.h` is the driver/firmware/hardware ABI description for the IPU3 ImgU CSS implementation. It is not the public userspace UAPI; instead it includes `include/uapi/intel-ipu3.h` and translates or embeds those public parameter structures into the memory layouts expected by the SPs, ISP, bootloader, accelerator cluster, queues, and firmware binary metadata. It also defines register offsets, bit masks, queue event encodings, memory identifiers, frame formats, and pipeline stage descriptors used by `ipu3-css.c`, `ipu3-css-params.c`, and the firmware loader.

## Important APIs, types, and data contracts

The low-level hardware section defines ImgU register offsets and control/status bits: power management, ISP/SP control/start/icache registers, TLB invalidation, IRQ controllers, GP stream monitor status, GDC LUT addresses, SP/ISP DMEM bases, and PM state masks. `imgu_addr_t` is the CSS/device address type used throughout DMA-visible ABI structures.

The fixed-function parameter section defines internal versions of ACC and statistics blocks. Important examples include `imgu_abi_shd_config`, `imgu_abi_dvs_stat_config`, `imgu_abi_osys_config`, `imgu_abi_bds_config`, `imgu_abi_anr_config`, `imgu_abi_af_config`, `imgu_abi_ae_config`, `imgu_abi_awb_fr_config`, `imgu_abi_awb_config`, and the aggregate `imgu_abi_acc_param`. These are firmware-facing layouts that combine public UAPI parameter structs with derived per-stripe data, operation lists, transfer descriptors, output-system/scaler data, and reserved device memory such as the DPC block.

Pipeline and frame descriptors include `imgu_abi_frame_sp_info`, `imgu_abi_frame_sp`, `imgu_abi_frames_sp`, `imgu_abi_sp_stage`, `imgu_abi_isp_stage`, and `imgu_abi_sp_group`. They describe frame planes, buffer sources, stage flags, crop/resize information, binary addresses, per-stage firmware blobs, and SP pipeline configuration.

Firmware binary metadata is represented by `imgu_abi_blob_info`, `imgu_abi_binary_info`, `imgu_abi_isp_param_segments`, and many smaller `imgu_abi_binary_*_info` structs. These records tell the driver where firmware sections are in the firmware file, where data/bss land in SP/ISP memory, which formats and features a binary supports, which DMA channels are used, and how large parameter/config/state memory regions are in each memory class.

Runtime communication types include `imgu_abi_queues`, `imgu_abi_queue_info`, event constants such as `IMGU_ABI_EVENT_BUFFER_ENQUEUED`, firmware event type constants such as `IMGU_ABI_EVTTYPE_3A_STATS_DONE`, buffer descriptors in `imgu_abi_buffer`, metadata/statistics descriptors, bootloader DMA command entries, and SP init DMEM configuration.

## Control flow and runtime behavior

This header is declarative, but it encodes the runtime protocol. During CSS initialization, register constants are used to reset/start the ISP and SPs, program instruction cache addresses, invalidate TLBs, check idle state, and configure the GDC LUT. Firmware metadata structures parsed by `ipu3-css-fw.c` select the bootloader and SP binaries and expose ISP binary capabilities. When a pipeline is configured, `ipu3-css.c` fills `imgu_abi_sp_stage`, `imgu_abi_isp_stage`, `imgu_abi_sp_group`, DDR address maps, and per-class parameter memory based on the selected `imgu_abi_binary_info`.

At streaming time, host and firmware communicate through the queues described by `imgu_abi_queues`: the host enqueues buffer addresses and events, the SP returns completed buffer/event records, and event bit encodings identify frame done, 3A stats done, metadata done, pipeline done, firmware warnings/asserts, and related milestones. Parameter state is moved through parameter-set descriptors and per-frame memory maps.

Stripe-based processing is a recurring control-flow concept. `imgu_abi_stripe_data` records effective/downscaled/BDS/output/block stripes, overlap vectors, GDC buffer dimensions, and decimation. Several blocks have per-stripe configs or operation lists so the firmware can process an image in one or two stripes with predictable transfer/process-line steps.

## State and persistence

All state described here is runtime device, firmware, or per-frame state. Persistent state is not stored in this header. Important runtime state includes SP software states (`imgu_abi_sp_swstate`), bootloader states (`imgu_abi_bl_swstate`), queue start/end indices, per-frame buffer descriptors, ISP reference/TNR state buffers, parameter-set IDs, exposure IDs, stage running flags, and CSS virtual addresses. The host maintains corresponding allocations and writes these packed structures into DMA-visible memory or MMIO/DMEM regions.

## Dependencies and integration points

`ipu3-abi.h` depends on `include/uapi/intel-ipu3.h` for public parameter structures and constants such as `IPU3_UAPI_MAX_STRIPES` and vector sizes. It assumes common kernel macros such as `BIT`, `DIV_ROUND_UP`, `ALIGN`, `max`, `__aligned`, and `__packed` from its includers. `ipu3-css-fw.h` embeds firmware-facing ABI types such as `imgu_abi_binary_info` and `imgu_abi_blob_info`. `ipu3-css-fw.c` validates many fields defined here, including frame format enum bounds, block dimensions, parameter-class offsets, and stripe count. `ipu3-css.c` and `ipu3-css-params.c` are the main consumers that fill and copy these layouts into mapped CSS memory.

## Risks and sharp edges

This file is tightly coupled to firmware binaries. A mismatch between structure layout and the firmware build can corrupt DMEM/VMEM interpretation, queue indices, stage descriptors, or blob loading. Many fields are packed bitfields mapping hardware registers, so compiler/layout assumptions and signedness matter. Array dimensions and reserved regions, especially the large `dpc[240832]` block in `imgu_abi_acc_param`, must remain consistent with firmware expectations. Queue sizes are fixed and small; incorrect producer/consumer step/start/end handling can overrun or deadlock communication. Register constants are direct MMIO offsets, so mistakes can affect power, IRQ, or memory translation state. The header also has many derived sizing macros, so changes to base constants can silently alter VMEM layout.

## Test signals

Strong signals include successful firmware initialization with all binary metadata passing bounds checks, hardware start reaching expected SP/BL software states, queue loop tests that enqueue/dequeue buffers and events without index corruption, and end-to-end streaming that receives output frames plus `IMGU_ABI_EVTTYPE_3A_STATS_DONE` where enabled. ABI layout tests should verify sizes/offsets of stage, queue, buffer, blob, and parameter structures against firmware expectations. Negative tests should exercise malformed firmware metadata: invalid format enum values, overlarge stripe counts, out-of-range memory offsets, bad blob sizes, missing boot/SP binaries, and invalid block dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-fw.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-fw.c

## Purpose

`ipu3-css-fw.c` implements IPU3 CSS firmware loading, validation, reporting, DMA mapping, cleanup, and a small helper for locating parameter substructures inside a selected firmware binary's parameter memory. It is the runtime bridge between Linux firmware files and the packed ABI structures from `ipu3-css-fw.h` and `ipu3-abi.h`.

## Important APIs and functions

`imgu_css_fw_init(struct imgu_css *css)` requests firmware using three compatible names, interprets the file as `struct imgu_fw_header`, validates the file header and every binary descriptor, records the bootloader and two SP binary indices, allocates DMA mappings for all firmware blobs, and copies each validated blob into device-visible memory.

`imgu_css_fw_cleanup(struct imgu_css *css)` releases every DMA-mapped firmware blob, frees the binary map array, releases the firmware object, and clears `css->binary` and `css->fw`.

`imgu_css_fw_obgrid_size(const struct imgu_fw_info *bi)` computes the optical-black grid buffer size from the selected ISP binary's internal maximum width/height, the `IMGU_OBGRID_TILE_SIZE`, vector alignment, page alignment, `struct ipu3_uapi_obgrid_param`, and firmware stripe count.

`imgu_css_fw_pipeline_params(...)` takes a pipeline id, parameter class, memory id, firmware offset/size descriptor, expected C structure size, and a binary parameter buffer. It verifies that the requested firmware parameter region fits within the selected binary's declared memory initializer size, warns on exact size mismatch, rejects firmware regions smaller than the expected struct, and returns a pointer to `binary_params + par->offset`.

`imgu_css_fw_show_binary(...)` is a debug-only reporting helper. For ISP binaries, it logs binary id, mode, BDS support, VF settings, input/internal/output dimensions, and supported output/VF formats.

## Control flow

Initialization first tries `intel/ipu/irci_irci_ecr-master_20161208_0213_20170112_1500.bin`, then `intel/irci_irci_ecr-master_20161208_0213_20170112_1500.bin`, then `intel/ipu3-fw.bin`. After request success, it performs coarse file-header checks: firmware size must hold at least one binary header, `h_size` must match `sizeof(struct imgu_fw_bi_file_h)`, and the flexible binary header array must fit inside the firmware file.

It then iterates over `file_header.binary_nr`. For every binary, it validates that `prog_name_offset` points inside the firmware, that the program name is NUL-terminated within the file and shorter than `IMGU_ABI_MAX_BINARY_NAME`, that blob size equals text plus icache plus data plus padding size, and that blob offset plus blob size fits inside the file. Bootloader binaries are recorded in `css->fw_bl` and their MMIO/DMEM offsets are checked against `css->iomem_length`. SP and SP1 binaries are recorded in `css->fw_sp[0]` and `[1]` and their many communication/state offsets are checked against `css->iomem_length`.

ISP binaries get additional semantic validation: pipeline mode must be within `IPU3_CSS_PIPE_ID_NUM`, stripe count must not exceed `IPU3_UAPI_MAX_STRIPES`, output/VF format counts and entries must be within `IMGU_ABI_FRAME_FORMAT_NUM`, block width and output block height must be positive and no larger than `BLOCK_MAX`, and the param/config/state memory-offset tables must fit inside the firmware file. Valid ISP binaries are logged through `imgu_css_fw_show_binary`.

After validation, the loader requires one bootloader and both SP binaries. It allocates `css->binary` as an array of CSS DMA maps, allocates a DMA buffer for each blob, and copies blob bytes from firmware storage into the mapped buffer. Any validation or allocation failure goes to cleanup and returns an error.

## State and persistence

The file mutates `struct imgu_css`: `fw`, `fwp`, `fw_bl`, `fw_sp[]`, and `binary`. These fields remain live for later hardware startup and parameter configuration. The backing firmware object is held until cleanup, and copied blob DMA buffers persist for the CSS lifetime. There is no disk persistence and no firmware rewriting.

## Dependencies and integration points

The file uses Linux firmware APIs (`request_firmware`, `release_firmware`), device logging, allocation helpers, and IPU3 DMA map helpers (`imgu_dmamap_alloc`, `imgu_dmamap_free`). It depends on `ipu3-css.h` for `struct imgu_css`, pipe state, firmware indices, and device context; `ipu3-css-fw.h` for firmware file structures and names; `ipu3-dmamap.h` for mapped blob storage; and `ipu3-abi.h`/UAPI constants for validation.

The loaded `css->binary` array is consumed by `ipu3-css.c` when programming SP/ISP icache addresses and bootloader DMA commands. `css->fwp` and selected `imgu_fw_info` records are used across CSS format selection, pipeline setup, and parameter generation. `imgu_css_fw_pipeline_params` is called by `ipu3-css.c` and `ipu3-css-params.c` to safely locate firmware-described parameter/config/state subregions.

## Risks and sharp edges

The loader performs important bounds checks, but it still treats firmware bytes as packed C structures once the coarse header passes. Any missing bound around a nested offset could become an out-of-bounds read or invalid MMIO/DMEM address later. Pointer arithmetic uses firmware-provided offsets; the code carefully checks program names, blobs, and memory-offset table locations, but future fields added to firmware structs must receive similar validation. The size check in `imgu_css_fw_pipeline_params` warns when firmware size differs from the expected struct size and only rejects smaller regions; larger regions are accepted for compatibility, so callers must only touch `par_size` bytes. Cleanup must be called on partial failure to avoid leaking DMA maps.

## Test signals

Positive tests include successful load of each supported firmware filename, logs showing firmware version and valid ISP binaries, populated `fw_bl` and both `fw_sp` indices, non-null DMA maps for every binary, and successful subsequent CSS hardware start. Negative tests should cover missing firmware, truncated file headers, bad `h_size`, binary array larger than file size, unterminated or too-long names, blob size mismatches, blob ranges beyond file size, invalid boot/SP offsets, invalid ISP modes, too many stripes, bad format counts/values, bad block sizes, missing bootloader/SP binaries, and DMA allocation failure. Parameter helper tests should verify out-of-range offsets return `NULL`, undersized firmware parameters return `NULL`, and larger compatible firmware parameters return the expected buffer offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-fw.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-fw.h

## Purpose

`ipu3-css-fw.h` defines the on-disk/in-memory firmware file format used by the IPU3 CSS firmware loader and declares the firmware loader helper APIs. It names the supported firmware files, enumerates firmware binary kinds, describes firmware-provided offset tables for ISP parameter/config/state memories, and defines the per-binary metadata structures consumed by `ipu3-css-fw.c`, `ipu3-css.c`, and `ipu3-css-params.c`.

## Important APIs, types, and data contracts

Firmware names are declared as `IMGU_FW_NAME`, `IMGU_FW_NAME_20161208`, and `IMGU_FW_NAME_IPU_20161208`; the loader tries these for compatibility with different firmware install paths.

`enum imgu_fw_type` distinguishes SP, SP1, ISP, bootloader, and accelerator firmware records. `enum imgu_fw_acc_type` classifies accelerator binaries as normal/output/viewfinder/standalone.

`struct imgu_fw_isp_parameter` is the fundamental offset descriptor: an offset into an ISP memory class plus a size. The three offset table structs group these descriptors by parameter class. `imgu_fw_param_memory_offsets` covers late-bound VMEM/DMEM parameters such as LIN, TNR3, XNR3, plane I/O, and RGBIR. `imgu_fw_config_memory_offsets` covers configuration-time DMEM structures such as iterator, DVS, output, raw, input YUV, TNR/TNR3, and ref config. `imgu_fw_state_memory_offsets` covers mutable DMEM state for TNR/TNR3/ref.

`union imgu_fw_all_memory_offsets` provides a generic representation for parameter/config/state offset-table pointers. `struct imgu_fw_binary_xinfo` wraps `struct imgu_abi_binary_info` for ISP binaries and adds host-only metadata: accelerator type, supported output/VF format arrays, number of output pins, firmware xmem address, blob descriptor pointer/index, offset table pointers, and linked-list pointer.

`struct imgu_fw_sp_info`, `struct imgu_fw_bl_info`, and `struct imgu_fw_acc_info` describe firmware-specific SP, bootloader, and accelerator data. SP info includes DMEM offsets for init data, per-frame data, groups, host/SP queues and commands, software state, sleep/TLB controls, debug/perf addresses, entry points, and current-binary/thread fields. Bootloader info provides DMA command count/list, software state, and entry point.

`struct imgu_fw_info` is each binary header entry. It carries header size, firmware type, type-specific union, `imgu_abi_blob_info`, linked-list/dynamic fields, loaded/code handles, and `imgu_abi_isp_param_segments` memory initializer information. `struct imgu_fw_bi_file_h` is the file header with a 64-byte version, binary count, and file-header size. `struct imgu_fw_header` is the flexible-array top-level firmware image.

The declared functions are `imgu_css_fw_init`, `imgu_css_fw_cleanup`, `imgu_css_fw_obgrid_size`, and `imgu_css_fw_pipeline_params`.

## Control flow and runtime behavior

This header has no executable flow, but it defines the format that drives firmware loader flow. The loader casts firmware bytes to `struct imgu_fw_header`, walks `binary_header[]`, switches on `imgu_fw_type`, validates per-type offsets, records required boot/SP binaries, and maps each `imgu_abi_blob_info` blob into DMA memory. Later CSS code dereferences the SP and bootloader info fields to write entry points, DMEM init blocks, bootloader DMA commands, queue locations, software-state addresses, and host/SP command areas. ISP parameter code reads the memory offset tables to locate firmware-specific parameter slots rather than hard-coding offsets.

## State and persistence

The structures model persistent firmware-file metadata while the firmware object is loaded, plus runtime dynamic fields inside `imgu_fw_info` such as `next`, `loaded`, `isp_code`, `handle`, and `mem_initializers`. The driver stores a pointer to the top-level `imgu_fw_header` in `css->fwp` and keeps it valid until firmware cleanup. The firmware itself remains immutable; runtime state is kept in CSS allocations, mapped binary blobs, SP/ISP DMEM, and host-side CSS structures.

## Dependencies and integration points

The header depends on ABI definitions from `ipu3-abi.h`; it uses `struct imgu_abi_binary_info`, `imgu_abi_blob_info`, `imgu_abi_isp_param_segments`, `enum imgu_abi_param_class`, and `enum imgu_abi_memories`. It also expects `struct imgu_css` from `ipu3-css.h` in function prototypes and kernel integer/alignment types from including contexts. `ipu3.c` advertises the firmware names through `MODULE_FIRMWARE`, `ipu3-css-fw.c` implements the declared functions, `ipu3-css.c` consumes boot/SP/ISP firmware metadata for hardware startup and pipeline setup, and `ipu3-css-params.c` consumes the offset tables for parameter binding.

## Risks and sharp edges

This header defines an externally supplied binary file format. Field width, alignment, and packing must match the firmware generator and the loader. Several fields are offsets into either the firmware file, CSS MMIO/DMEM address spaces, or device memory, so confusing address domains can cause invalid writes or out-of-bounds reads. Because the firmware binary headers are read directly from file bytes, any new field or format revision needs explicit loader validation. `union imgu_fw_all_memory_offsets` stores offset-table pointers as 64-bit fields, which is convenient for file compatibility but requires careful interpretation by the host.

## Test signals

Useful tests include building the driver against this header, loading all advertised firmware names, checking that `MODULE_FIRMWARE` names match these macros, validating that firmware with known-good headers produces expected `imgu_fw_info` values, and confirming that parameter/config/state offset tables route `imgu_css_fw_pipeline_params` to the intended memory regions. Negative tests should mutate firmware type, binary count, header size, blob metadata, SP/BL offsets, format arrays, and offset table pointers to ensure the loader rejects corrupted images before any hardware startup uses the metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-fw.h -->
