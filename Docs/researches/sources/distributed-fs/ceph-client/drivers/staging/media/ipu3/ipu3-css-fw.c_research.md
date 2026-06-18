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
