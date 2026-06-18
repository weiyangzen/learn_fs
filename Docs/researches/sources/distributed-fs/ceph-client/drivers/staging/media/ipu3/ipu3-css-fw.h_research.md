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
