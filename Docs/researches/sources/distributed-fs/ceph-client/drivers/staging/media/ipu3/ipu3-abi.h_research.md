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
