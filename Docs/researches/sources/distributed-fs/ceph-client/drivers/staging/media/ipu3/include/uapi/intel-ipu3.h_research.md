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
