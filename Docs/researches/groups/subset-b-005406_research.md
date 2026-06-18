# subset-b-005406 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.h` declares the host-side Temporal Noise Reduction entry points: parameter encoding/dumping, frame-address configuration, binary configuration, and DMEM state initialization.

Important APIs, types, and functions: Important local symbols: `ia_css_tnr_encode`, `ia_css_tnr_dump`, `ia_css_tnr_debug_dtrace`, `ia_css_tnr_config`, `ia_css_tnr_configure`, `ia_css_init_tnr_state` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_TNR_HOST_H`

Control flow: Runtime code uses these declarations when a video binary enables TNR; host state is converted into ISP parameter/config sections and frame-buffer addresses before firmware execution.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The API is pointer-heavy and size arguments are not self-describing in the header, so callers must pass matching ISP structs and valid TNR frame arrays.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_param.h` defines the ISP-facing TNR parameter and configuration payloads, including coefficient/threshold fields and the DMA port plus frame-address table for temporal reference frames.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_tnr_params`, `ia_css_tnr_configuration`, `sh_css_isp_tnr_isp_config`; `__IA_CSS_TNR_PARAM_H`

Control flow: Host code fills `sh_css_isp_tnr_params` from public tuning values and `sh_css_isp_tnr_isp_config` from frame memory before the ISP kernel consumes them.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Incorrect `NUM_VIDEO_TNR_FRAMES` ordering, frame height, DMA port, or physical address values can make TNR read stale or wrong reference frames.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_state.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_state.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_state.h` defines the tiny TNR DMEM state block that tracks input and output buffer rotation indexes across temporal filtering.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_tnr_dmem_state`; `__IA_CSS_TNR_STATE_H`

Control flow: Firmware mutates these indexes while alternating temporal buffers; host initialization clears or seeds the state before a pipeline starts.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: A stale state block can swap previous/current-frame roles and create ghosting or memory aliasing.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_types.h` defines the public CSS TNR tuning contract: interpolation gain plus luma and chroma thresholds used to decide whether to blend with the previous frame.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_tnr_config`; `__IA_CSS_TNR_TYPES_H`

Control flow: Userspace or higher CSS code sets `ia_css_tnr_config`; host encoding converts u0.16 values into ISP parameter words.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Zero thresholds disable useful temporal blending, while high thresholds can smear motion; range checking is mostly documented rather than enforced here.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/uds/uds_1.0/ia_css_uds_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/uds/uds_1.0/ia_css_uds_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/uds/uds_1.0/ia_css_uds_param.h` defines Up/Down Scaling parameter bundles shared between host and SP, pairing crop position with `sh_css_uds_info` scale metadata.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_uds_config`, `sh_css_sp_uds_params`; `__IA_CSS_UDS_PARAM_H`

Control flow: Pipeline configuration populates crop and UDS coefficients, then copies equivalent data into SP-visible `sh_css_sp_uds_params`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: This header has no validation; invalid crop/scale combinations are caught only by callers or downstream UDS code.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/uds/uds_1.0/ia_css_uds_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.c` implements viewfinder decimation setup. It computes a log2 downscale that stays at or above the requested VF size, programs DMA output metadata, and writes the binary VF configuration.

Important APIs, types, and functions: Important local symbols: `ia_css_vf_config`, `sh_css_vf_downscale_log2`, `configure_kernel`, `configure_dma`, `ia_css_vf_configure` Types and constants: No named structs or enums are introduced here.; `IA_CSS_INCLUDE_CONFIGURATIONS`

Control flow: `ia_css_vf_configure()` calls `sh_css_vf_downscale_log2()`, clamps to binary capability, sets VF raw bit depth from firmware metadata, and delegates to `ia_css_configure_vf()`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The downscale loop is width-driven only, assumes divisibility between vector lanes and DMA port elements, and returns errors for overwide VF input.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.h` declares the VF host API for downscale computation, ISP config encoding, and binary-level VF configuration.

Important APIs, types, and functions: Important local symbols: `sh_css_vf_downscale_log2`, `ia_css_vf_config`, `ia_css_vf_configure` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_VF_HOST_H`

Control flow: Binary setup code includes this header to configure viewfinder output during `ia_css_binary_fill_info()`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Callers must provide coherent output/VF frame info and a writable downscale pointer.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_param.h` defines the ISP VF decimation config with downscale bits, enable flag, frame SP info, and DMA port-B configuration.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_vf_isp_config`, `dma`; `__IA_CSS_VF_PARAM_H`, `VFDEC_BITS_PER_PIXEL`

Control flow: Host code fills this struct, then the ISP kernel uses it to write the downscaled viewfinder plane.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Mismatched DMA `width_a_over_b` or disabled `info` leaves VF output absent or malformed.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_types.h` defines the public VF configuration object: log2 downscale and optional frame-info pointer.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_vf_configuration`; `__IA_CSS_VF_TYPES_H`

Control flow: A non-NULL `info` enables VF output and supplies DMA/frame layout.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The pointer is not owned by the struct, so lifetime and const-correctness are caller responsibilities.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.c` implements white-balance host encoding and debug dumping. It exports `default_wb_config` and converts public four-channel gain significands into ISP gain and shift words.

Important APIs, types, and functions: Important local symbols: `ia_css_wb_encode`, `ia_css_wb_dump`, `ia_css_wb_debug_dtrace` Types and constants: No named structs or enums are introduced here.; No exported preprocessor constants.

Control flow: `ia_css_wb_encode()` computes `gain_shift` from `integer_bits` and applies `uDIGIT_FITTING()` to Gr/R/B/Gb; debug helpers trace both encoded and public values.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Invalid `integer_bits` can create bad shifts or gain scaling; there is no local clamp beyond conversion macros.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.h` declares the white-balance default config, encoder, and debug dump entry points.

Important APIs, types, and functions: Important local symbols: `ia_css_wb_encode`, `ia_css_wb_dump`, `ia_css_wb_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_WB_HOST_H`

Control flow: Parameter assembly includes this header when writing WB ISP sections or diagnostic dumps.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Debug declarations are unconditional although implementations are conditionally compiled under `IA_CSS_NO_DEBUG`.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_param.h` defines the ISP white-balance parameter block: common gain shift and four Bayer-channel gains.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_wb_params`; `__IA_CSS_WB_PARAM_H`

Control flow: The ISP WB kernel reads these signed fields to apply channel gains.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Signed storage of fixed-point values makes overflow or bad scaling visible as color cast.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_types.h` defines the public white-balance tuning contract with common exponent and Gr/R/B/Gb gain significands.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_wb_config`; `__IA_CSS_WB_TYPES_H`

Control flow: Higher layers pass `ia_css_wb_config` to the encoder for fixed-point conversion.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The documented ranges are not enforced here, so callers need validation.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.c` implements XNR1 host encoding. It exports the default threshold, copies the XNR division table into VAMEM parameters, converts threshold to ISP bit depth, and traces public threshold values.

Important APIs, types, and functions: Important local symbols: `ia_css_xnr_table_vamem_encode`, `ia_css_xnr_encode`, `ia_css_xnr_table_debug_dtrace`, `ia_css_xnr_debug_dtrace` Types and constants: No named structs or enums are introduced here.; No exported preprocessor constants.

Control flow: Parameter setup encodes a scalar threshold and, when needed, a VAMEM table initialized by `ia_css_config_xnr_table()`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Threshold conversion narrows to 16 bits and depends on `SH_CSS_ISP_YUV_BITS`; table copy assumes matching union member layout.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.h` declares XNR1 scalar/table encoder and debug APIs.

Important APIs, types, and functions: Important local symbols: `ia_css_xnr_table_vamem_encode`, `ia_css_xnr_encode`, `ia_css_xnr_table_debug_dtrace`, `ia_css_xnr_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_XNR_HOST_H`

Control flow: Parameter assembly includes it to encode threshold and VAMEM table sections.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The table debug hook is a stub, limiting diagnostics.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_param.h` defines XNR1 ISP scalar and VAMEM parameter layouts, including compile-time table size selection.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_xnr_vamem_params`, `sh_css_isp_xnr_params`; `__IA_CSS_XNR_PARAM_H`, `SH_CSS_ISP_XNR_TABLE_SIZE_LOG2`, `SH_CSS_ISP_XNR_TABLE_SIZE`

Control flow: The pipe generator can set the table size to zero; normal host builds use system-global VAMEM table constants.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Build-mode-dependent table size can hide buffer assumptions between generator and runtime builds.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.c` implements XNR1 host encoding. It exports the default threshold, copies the XNR division table into VAMEM parameters, converts threshold to ISP bit depth, and traces public threshold values.

Important APIs, types, and functions: Important local symbols: `ia_css_config_xnr_table` Types and constants: `ia_css_xnr_table`; No exported preprocessor constants.

Control flow: Parameter setup encodes a scalar threshold and, when needed, a VAMEM table initialized by `ia_css_config_xnr_table()`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Threshold conversion narrows to 16 bits and depends on `SH_CSS_ISP_YUV_BITS`; table copy assumes matching union member layout.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.h` declares the mutable global `default_xnr_table` and its initialization function.

Important APIs, types, and functions: Important local symbols: `ia_css_config_xnr_table` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_XNR_TABLE_HOST_H`

Control flow: Host setup calls the initializer before table parameters are copied to ISP memory.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: No guard prevents use before initialization.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_types.h` defines the public XNR1 table and threshold config, including VAMEM1/VAMEM2 table shapes and reciprocal coefficient documentation.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_xnr_data`, `ia_css_xnr_table`, `ia_css_xnr_config`; `__IA_CSS_XNR_TYPES_H`, `IA_CSS_VAMEM_1_XNR_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_1_XNR_TABLE_SIZE`, `IA_CSS_VAMEM_2_XNR_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_2_XNR_TABLE_SIZE`

Control flow: CSS configuration passes scalar threshold plus optional table data to host encoders.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: VAMEM type must match the target ISP generation or coefficients are interpreted through the wrong array.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.c` implements XNR3 host encoding for ISP2401-style chroma noise reduction. It converts public sigma, coring, and blending values into ISP alpha/coring/blending parameters and fills VMEM lookup vectors.

Important APIs, types, and functions: Important local symbols: `ia_css_xnr3_encode`, `ia_css_xnr3_vmem_encode`, `ia_css_xnr3_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `XNR_MAX_ALPHA`, `XNR_MIN_SIGMA`, `XNR3_LOOK_UP_TABLE_POINTS`

Control flow: `compute_alpha()`, `compute_coring()`, and `compute_blending()` scale/clamp public fixed-point values; `ia_css_xnr3_encode()` writes scalar ISP params; `ia_css_xnr3_vmem_encode()` replicates 16 lookup points across four vector blocks.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Hard-coded lookup tables and filter size assumptions must match firmware KFS; asserts check table monotonicity only in assert-enabled builds.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.h` declares XNR3 default config plus scalar and VMEM encoders.

Important APIs, types, and functions: Important local symbols: `ia_css_xnr3_encode`, `ia_css_xnr3_vmem_encode`, `ia_css_xnr3_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_XNR3_HOST_H`

Control flow: ISP2401 parameter setup uses the scalar encoder and the VMEM encoder when XNR3 is present in a binary.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The debug function is a dummy, so runtime introspection is weak.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_param.h` defines ISP-side XNR3 fixed-point scale factors, alpha/coring/blending parameter structs, filter size, and VMEM arrays.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_xnr3_alpha_params`, `sh_css_xnr3_coring_params`, `sh_css_xnr3_blending_params`, `sh_css_isp_xnr3_params`, `sh_css_isp_xnr3_vmem_params`; `__IA_CSS_XNR3_PARAM_H`, `XNR_ALPHA_SCALE_LOG2`, `XNR_ALPHA_SCALE_FACTOR`, `XNR_CORING_SCALE_LOG2`, `XNR_CORING_SCALE_FACTOR`, `XNR_BLENDING_SCALE_LOG2`, `XNR_BLENDING_SCALE_FACTOR`, `XNR_FILTER_SIZE`

Control flow: Host encoding writes these structs into ISP DMEM/VMEM for the XNR3 kernel.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: `XNR_FILTER_SIZE` is a compile-time constant and comments restrict it to known values; firmware mismatch would corrupt gradients.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_types.h` defines public XNR3 sigma, coring, and blending tuning structs and their host-side fixed-point scales.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_xnr3_sigma_params`, `ia_css_xnr3_coring_params`, `ia_css_xnr3_blending_params`, `ia_css_xnr3_config`; `__IA_CSS_XNR3_TYPES_H`, `IA_CSS_XNR3_SIGMA_SCALE`, `IA_CSS_XNR3_CORING_SCALE`, `IA_CSS_XNR3_BLENDING_SCALE`

Control flow: Higher CSS configuration populates dark/bright values per plane before host conversion.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Values outside documented fixed-point ranges are not validated in the type contract.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.c` implements YNR1 and Y Edge Enhancement host encoding. It exports default noise-reduction and edge-enhancement configs, converts public gains/thresholds into ISP params, dumps encoded values, and zeroes YNR VMEM state.

Important APIs, types, and functions: Important local symbols: `ia_css_nr_encode`, `ia_css_yee_encode`, `ia_css_nr_dump`, `ia_css_yee_dump`, `ia_css_nr_debug_dtrace`, `ia_css_ee_debug_dtrace`, `ia_css_init_ynr_state` Types and constants: No named structs or enums are introduced here.; No exported preprocessor constants.

Control flow: `ia_css_nr_encode()` fills luma/chroma thresholds and gains; `ia_css_yee_encode()` derives directional thresholds, coring, scale, clipping, and detail gain from NR/EE config.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Several magic constants encode tuning policy; arithmetic uses shifts and fitting macros without local range validation.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.h` declares YNR/YEE defaults, encoders, dump/debug functions, and state initialization.

Important APIs, types, and functions: Important local symbols: `ia_css_nr_encode`, `ia_css_yee_encode`, `ia_css_nr_dump`, `ia_css_yee_dump`, `ia_css_nr_debug_dtrace`, `ia_css_ee_debug_dtrace`, `ia_css_init_ynr_state` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_YNR_HOST_H`

Control flow: Parameter setup uses this header for preview/video YNR1 and YEE1 kernels.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: State initialization takes `void *`, so type safety is intentionally weak.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_param.h` defines ISP parameter blocks for luma noise reduction and edge enhancement.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_ynr_params`, `sh_css_isp_yee_params`; `__IA_CSS_YNR_PARAM_H`

Control flow: The ISP kernel reads thresholds, directional gain, coring, scale, clip, and Y clip values from these blocks.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: All fields are signed scalar words; bad fixed-point conversion can cause oversharpening or clipping artifacts.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_types.h` defines public NR, EE, and combined YEE configuration structures used for BNR/YNR/CNR and sharpening.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_nr_config`, `ia_css_ee_config`, `ia_css_yee_config`; `__IA_CSS_YNR_TYPES_H`

Control flow: Public CSS tuning values are passed through the host encoders into YNR/YEE ISP params.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The same NR config feeds several kernels, so one mis-tuned value can affect Bayer, luma, and chroma paths.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.c` implements YNR2/YEE2 and Fringe Control host encoding. It exports default YNR/FC configs and copies public edge, corner, coring, gain, and crop values into ISP parameter structs.

Important APIs, types, and functions: Important local symbols: `ia_css_ynr_encode`, `ia_css_fc_encode`, `ia_css_ynr_dump`, `ia_css_fc_dump`, `ia_css_fc_debug_dtrace`, `ia_css_ynr_debug_dtrace` Types and constants: No named structs or enums are introduced here.; No exported preprocessor constants.

Control flow: `ia_css_ynr_encode()` maps four sensitivity gains; `ia_css_fc_encode()` maps positive/negative coring, gain, and crop limits; debug functions trace public values.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The C file declares dump functions without definitions here, relying on other build objects or unused references.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.h` declares YNR2/FC defaults, encoders, dump functions, and debug trace helpers.

Important APIs, types, and functions: Important local symbols: `ia_css_ynr_encode`, `ia_css_fc_encode`, `ia_css_ynr_dump`, `ia_css_fc_dump`, `ia_css_fc_debug_dtrace`, `ia_css_ynr_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_YNR2_HOST_H`

Control flow: Still-pipe parameter code includes it for ISP2 still YNR2/YEE2/FC2 kernels.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Consumers must keep YNR2 and FC parameter sections synchronized because FC is used with YNR2/YEE2.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_param.h` defines ISP parameter blocks for YNR2/YEE2 edge/corner sensing and FC2 fringe-control coring/gain/crop.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_yee2_params`, `sh_css_isp_fc_params`; `__IA_CSS_YNR2_PARAM_H`

Control flow: Host encoded values are copied into these blocks before still-pipe execution.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Mixed signed and unsigned fields make negative crop limits easy to mishandle.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_types.h` defines public YNR2 edge/corner sensitivity and Fringe Control tuning contracts.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_ynr_config`, `ia_css_fc_config`; `__IA_CSS_YNR2_TYPES_H`

Control flow: Still capture configuration provides these values for host encoding.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Documented ranges are not enforced locally; invalid crop/gain limits can produce halos or color fringing.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/input_buf.isp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/input_buf.isp.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/input_buf.isp.h` defines the ISP input-buffer geometry used by continuous capture: double-buffer height, line count, fixed VMEM base address, extra left-padding vectors, and the maximum vectors per input line.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_INPUT_BUF_ISP_H_`, `INPUT_BUF_HEIGHT`, `INPUT_BUF_LINES`, `ENABLE_CONTINUOUS`, `EXTRA_INPUT_VECTORS`, `MAX_VECTORS_PER_INPUT_LINE_CONT`, `INPUT_BUF_ADDR`

Control flow: Continuous-mode binaries and SP-side assumptions use a fixed input-buffer size and address so the SP can address ISP input memory consistently.

State and persistence behavior: No persistent storage exists. Values are compile-time constants or per-binary memory-address contracts consumed during ISP/SP pipeline setup.

Dependencies and integration points: These headers integrate generated Hive/ISP code, CSS host runtime, frame allocation, input formatter setup, and stream-format selection.

Risks and edge cases: `ENABLE_CONTINUOUS` defaults to zero here, but the constants remain compiled; sensor widths near `SH_CSS_MAX_SENSOR_WIDTH` depend on correct `DIV_ROUND_UP()` and padding.

Test signals: Validate continuous and non-continuous builds, maximum sensor width alignment, frame-plane address wiring, raw/YUV/binary stream format selection, and compile compatibility with generated ISP code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/input_buf.isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/isp_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/isp_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/isp_types.h` defines shared ISP mode types: stream-format classes and `s_isp_frames`, a large table of XMEM base pointers for output, second output, input YUV/raw, VF, overlay, GDC, and post-ISP buffers.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_3a_output`, `sh_stream_format`, `s_isp_frames`; `_ISP_TYPES_H_`

Control flow: Every ISP binary can receive or share this frame-address structure so firmware and host agree on memory locations for planes and intermediate products.

State and persistence behavior: No persistent storage exists. Values are compile-time constants or per-binary memory-address contracts consumed during ISP/SP pipeline setup.

Dependencies and integration points: These headers integrate generated Hive/ISP code, CSS host runtime, frame allocation, input formatter setup, and stream-format selection.

Risks and edge cases: The struct is a pointer ABI with many similarly named plane fields; wrong plane assignment causes silent frame corruption.

Test signals: Validate continuous and non-continuous builds, maximum sensor width alignment, frame-plane address wiring, raw/YUV/binary stream format selection, and compile compatibility with generated ISP code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/modes/interface/isp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_global.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_global.h` defines ISP2400 input-system global enums and configuration structs for CSI ports, channels, sources, buffering modes, IB memory regions, TPG/PRBS/gpfifo sources, and configuration flags.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `isp2400_input_system_cfg_s`, `sync_generator_cfg_s`, `tpg_cfg_s`, `prbs_cfg_s`, `gpfifo_cfg_s`, `ib_buffer_s`, `csi_cfg_s`, `mipi_lane_cfg_t`, `input_system_source_t`, `input_system_connection_t`, `input_system_multiplex_t`, `input_system_sink_t`; `N_CSI_PORTS`, `N_CHANNELS`, `IB_CAPACITY_IN_WORDS`

Control flow: Higher-level input-system setup accumulates these structs, then commits them into receiver/backend/acquisition/input-buffer hardware programming.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: Configuration flags can express set, blocked, required, and conflict states; bad reconciliation can over-allocate the 384-word input-buffer capacity or route streams incorrectly.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_local.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_local.h` maps ISP2400 input-system register aliases, offsets, MIPI formats, IRQ-info bits, receiver port offsets, subsystem offsets, and complete channel/session configuration structs.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `target_cfg2400_s`, `channel_cfg_s`, `input_system_cfg2400_s`, `mipi_format_2400_t`, `rx_irq_info_t`; `__INPUT_SYSTEM_2400_LOCAL_H_INCLUDED__`, `_HRT_CSS_RECEIVER_DEVICE_READY_REG_IDX`, `_HRT_CSS_RECEIVER_IRQ_STATUS_REG_IDX`, `_HRT_CSS_RECEIVER_IRQ_ENABLE_REG_IDX`, `_HRT_CSS_RECEIVER_TIMEOUT_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_INIT_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_RAW16_18_DATAID_REG_IDX`, `_HRT_CSS_RECEIVER_SYNC_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_RX_COUNT_REG_IDX`, `_HRT_CSS_RECEIVER_FS_TO_LS_DELAY_REG_IDX`

Control flow: Implementation code uses these aliases to program receiver ports/backends, input switch, target ISP/SP/stream2mem blocks, and multicast/multiplexer routing.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: Many macros alias hardware register indexes; a wrong offset or generation mismatch writes a valid value to the wrong register.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_private.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_private.h` implements inline register load/store helpers for ISP2400 input-system, receiver, receiver-port, and subsystem MMIO windows.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `__INPUT_SYSTEM_2400_PRIVATE_H_INCLUDED__`

Control flow: Each helper asserts ID and base validity, computes base plus optional port/subsystem offset plus register stride, and calls `ia_css_device_load_uint32()` or `ia_css_device_store_uint32()`.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: Assertions may disappear in production builds, leaving invalid IDs or `-1` bases to produce bad MMIO addresses.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_public.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_public.h` declares the ISP2400 input-system public API for receiver compression/port/IRQ control, raw register access, configuration reset/commit, and user-level CSI/FIFO/SRAM/XMEM/PRBS/GPFIFO channel configuration.

Important APIs, types, and functions: Important local symbols: `receiver_set_compression`, `receiver_port_enable`, `is_receiver_port_enabled`, `receiver_irq_enable`, `receiver_irq_clear` Types and constants: No named structs or enums are introduced here.; `__INPUT_SYSTEM_2400_PUBLIC_H_INCLUDED__`

Control flow: Callers build a session by invoking channel-configuration functions, then commit the accumulated configuration to hardware; register helpers expose low-level diagnostics and control.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: The API comments acknowledge minimal checking in user functions, so callers must supply coherent channel IDs, port modes, region sizes, target configs, and frame counts.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_input_system_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_support.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_support.h` provides host-build compatibility aliases for ISP2400 vector/memory types and helper macros to address ISP DMEM, VMEM, VAMEM1, VAMEM2, and optional histogram memories.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_isp2400_support_h`, `hrt_isp_vamem1_store_16`, `hrt_isp_vamem2_store_16`, `hrt_isp_dmem`, `hrt_isp_vmem`, `hrt_isp_dmem_master_port_address`, `hrt_isp_vmem_master_port_address`, `hrt_isp_hist`, `hrt_isp_hist_master_port_address`

Control flow: It has no runtime control flow; it expands hardware-memory access macros used by host code, simulator/crun builds, and generated ISP support code.

State and persistence behavior: No state is stored here. The macros address live ISP memory spaces through HRT properties when used by callers.

Dependencies and integration points: It depends on HRT memory helper macros and ISP feature flags such as `ISP_HAS_HIST`; it integrates low-level memory access with host-side code that includes Hive headers.

Risks and edge cases: Type aliases are only supplied when `ISP2400_VECTOR_TYPES` is absent, so build configuration changes can alter visible types. Incorrect cell or memory-property use writes to the wrong ISP memory.

Test signals: Compile host and ISP2400-vector builds, exercise VAMEM/DMEM/VMEM address macros in simulator tests, and verify histogram helpers only compile when histogram support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_global.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_global.h` defines ISP2401 input-system global data models for stream2mmio, ibuf controller, DMA, CSI RX, metadata, pixel generator, stream configuration, and virtual stream state.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `input_system_channel_s`, `input_system_channel_cfg_s`, `input_system_input_port_s`, `input_system_input_port_cfg_s`, `isp2401_input_system_cfg_s`, `virtual_input_system_stream_s`, `virtual_input_system_stream_cfg_s`, `input_system_source_type_t`, `csi_rx`, `metadata`, `pixelgen`, `csi_rx_cfg`; `N_CSI_PORTS`, `INPUT_SYSTEM_N_STREAM_ID`, `ISP_INPUT_BUF_START_ADDR`, `NUM_OF_INPUT_BUF`, `NUM_OF_LINES_PER_BUF`, `LINES_OF_ISP_INPUT_BUF`, `ISP_INPUT_BUF_STRIDE`

Control flow: Configuration code maps an input port and stream into a CSI/pixelgen source, stream2mmio path, ibuf controller, DMA channel, optional metadata channel, and online/offline stream relation.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: The virtual stream model carries validity, metadata, online, and linked-stream fields; inconsistent combinations can desynchronize main and metadata streams.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_local.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_local.h` defines ISP2401 MIPI packet-format IDs and compressor context sizing.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `mipi_format_2401_t`; `__INPUT_SYSTEM_2401_LOCAL_H_INCLUDED__`, `N_MIPI_FORMAT_CUSTOM`, `N_MIPI_COMPRESSOR_CONTEXT`

Control flow: CSI RX backend configuration uses these numeric MIPI data type values when programming LUT entries for image and metadata packets.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: The 2401 format list excludes RAW16/RAW18 support present in 2400, so cross-generation reuse can accept unsupported formats incorrectly.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_private.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_private.h` implements ISP2401 private inline diagnostics for the ibuf controller, including register load/store, per-process state capture, full controller state capture, and formatted dump output.

Important APIs, types, and functions: Important local symbols: `ibuf_ctrl_reg_load`, `ibuf_ctrl_reg_store`, `ibuf_ctrl_get_proc_state`, `ibuf_ctrl_get_state`, `ibuf_ctrl_dump_state` Types and constants: No named structs or enums are introduced here.; `__INPUT_SYSTEM_2401_PRIVATE_H_INCLUDED__`

Control flow: `ibuf_ctrl_get_proc_state()` reads every process register bank, `ibuf_ctrl_get_state()` loops over processes, and `ibuf_ctrl_dump_state()` prints the snapshot.

State and persistence behavior: State is hardware register state, accumulated in-memory configuration structs, input-buffer allocations, stream validity flags, and diagnostic snapshots. Nothing is persisted to disk.

Dependencies and integration points: These files depend on CSS receiver, acquisition/capture, input switch, stream2mmio, ibuf controller, isys DMA, CSI RX, pixel generator, device-access, and print/assert support headers.

Risks and edge cases: This diagnostic code trusts process counts and register definitions from platform headers; stale definitions make dumps misleading.

Test signals: Cover all CSI ports, virtual channels, MIPI formats, metadata enablement, online/offline paths, PRBS/TPG sources, register read/write helpers, IRQ status/clear paths, IB capacity accounting, and generation-specific 2400 versus 2401 format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2401_input_system_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_acquisition_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_acquisition_defs.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_acquisition_defs.h` defines the acquisition-unit register map, reset values, token fields, command/ack token IDs, MIPI packet metadata fields, and packet data type constants.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_isp_acquisition_defs_h`, `_ISP_ACQUISITION_REG_ALIGN`, `_ISP_ACQUISITION_BYTES_PER_ELEM`, `NOF_ACQ_IRQS`, `MEM2STREAM_FSM_STATE_BITS`, `ACQ_SYNCHRONIZER_FSM_STATE_BITS`, `NOF_ACQ_REGS`, `ACQ_START_ADDR_REG_ID`, `ACQ_MEM_REGION_SIZE_REG_ID`, `ACQ_NUM_MEM_REGIONS_REG_ID`

Control flow: The acquisition unit reads memory regions into a stream and reports packet/region acknowledgements using the encoded token layout documented here.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: Bitfield indexes for packet length, data type, channel, and memory-region ID overlap by token type; using the wrong token interpretation corrupts control flow.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_acquisition_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_capture_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_capture_defs.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_capture_defs.h` defines the capture-unit register map, command and acknowledgement tokens, packet metadata layout, MIPI data type constants, and capture FSM state IDs.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_isp_capture_defs_h`, `_ISP_CAPTURE_REG_ALIGN`, `_ISP_CAPTURE_BITS_PER_ELEM`, `_ISP_CAPTURE_BYTES_PER_ELEM`, `_ISP_CAPTURE_BYTES_PER_WORD`, `_ISP_CAPTURE_ELEM_PER_WORD`, `NOF_IRQS`, `CAPT_NOF_REGS`, `CAPT_START_MODE_REG_ID`, `CAPT_START_ADDR_REG_ID`

Control flow: Capture programming writes start/init/stop and memory-region registers, then hardware reports packet received/written, region written, flush, SOP, and stop acknowledgements.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: Start/stop/freeze/resume/init tokens share low bits and require exact packing; bad memory region sizes or restart addresses can overrun capture buffers.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp_capture_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mamoiada_params.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mamoiada_params.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mamoiada_params.h` describes the Mamoiada ISP hardware profile: vector width, memory depths, register-file sizes, feature switches, cache parameters, immediate sizes, FIFO depths, shielding, and streaming port presence.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `RTL_VERSION`, `ISP_BRANCHDELAY`, `ISP_BUS_WIDTH`, `ISP_BUS_ADDR_WIDTH`, `ISP_BUS_BURST_SIZE`, `ISP_SCALAR_WIDTH`, `ISP_SLICE_NELEMS`, `ISP_VEC_NELEMS`, `ISP_VEC_ELEMBITS`, `ISP_VEC_ELEM8BITS`

Control flow: Generated ISP code and host-side build logic use these compile-time constants to size memories, align vectors, and expose capabilities such as IRQ, soft reset, LUT, histogram, VALSU, and streaming ports.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: This is a hardware contract rather than executable code; any mismatch with firmware or silicon invalidates many derived buffer and parameter sizes.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mamoiada_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/isp_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/isp_mmu.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/isp_mmu.c` implements the generic AtomISP two-level ISP MMU page-table manager: page-table allocation/free, map, unmap, remap detection, error logging, initialization, TLB-range fallback, and teardown.

Important APIs, types, and functions: Important local symbols: `free_mmu_map`, `atomisp_get_pte`, `atomisp_set_pte`, `isp_pte_to_pgaddr`, `isp_pgaddr_to_pte_valid`, `alloc_page_table`, `free_page_table`, `mmu_remap_error`, `mmu_unmap_l2_pte_error`, `mmu_unmap_l1_pte_error`, `mmu_unmap_l1_pt_error`, `mmu_l2_map`, `mmu_l1_map`, `mmu_map` Types and constants: No named structs or enums are introduced here.; `NR_PAGES_2GB`

Control flow: Mapping lazily allocates an uncached DMA32 L1 table, allocates L2 tables on demand, writes valid PTEs for each ISP virtual page, and rolls back partial maps on error. Unmapping clears L2 PTEs, decrements per-L1 refcounts, frees empty L2 tables, and teardown frees all remaining tables.

State and persistence behavior: State is in-memory page tables, `mmu->l1_pte`, `base_address`, L2 refcounts, callback pointers, and hardware TLB/cache state. There is no persistence after driver teardown.

Dependencies and integration points: The code depends on Linux page allocation, DMA32 constraints, x86 cacheability APIs, AtomISP device logging, `struct isp_mmu_client`, PTE macros, and hardware invalidation through `ia_css_mmu_invalidate_cache()`.

Risks and edge cases: Rollback calls back into unmap while holding mapping context, refcount underflow is possible after invalid unmaps, and failure paths depend on correct page alignment and PTE validity masks.

Test signals: Test mapping/unmapping across L1 boundaries, duplicate mappings, partial allocation failure rollback, invalid unmap diagnostics, DMA32 allocation failure, init validation for missing callbacks/masks, exit with populated tables, and TLB flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/isp_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/sh_mmu_mrfld.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/sh_mmu_mrfld.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/sh_mmu_mrfld.c` defines the Merrifield/Silicon Hive ISP3000 MMU client adapter, converting physical addresses to PTEs and page-directory bases and flushing the hardware cache/TLB.

Important APIs, types, and functions: Important local symbols: `sh_phys_to_pte`, `sh_pte_to_phys`, `sh_get_pd_base`, `sh_tlb_flush` Types and constants: `isp_mmu_client`; `MERR_VALID_PTE_MASK`

Control flow: `sh_mmu_mrfld` supplies callbacks used by `isp_mmu_init()`: `phys_to_pte`, `pte_to_phys`, `get_pd_base`, and `tlb_flush_all`.

State and persistence behavior: State is in-memory page tables, `mmu->l1_pte`, `base_address`, L2 refcounts, callback pointers, and hardware TLB/cache state. There is no persistence after driver teardown.

Dependencies and integration points: The code depends on Linux page allocation, DMA32 constraints, x86 cacheability APIs, AtomISP device logging, `struct isp_mmu_client`, PTE macros, and hardware invalidation through `ia_css_mmu_invalidate_cache()`.

Risks and edge cases: The valid-bit mask is hardware-specific; using this client on the wrong MMU generation would translate addresses incorrectly.

Test signals: Test mapping/unmapping across L1 boundaries, duplicate mappings, partial allocation failure rollback, invalid unmap diagnostics, DMA32 allocation failure, init validation for missing callbacks/masks, exit with populated tables, and TLB flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu/sh_mmu_mrfld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu_defs.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu_defs.h` defines the minimal MMU register indexes for TLB invalidation and page-table base address plus register alignment.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_mmu_defs_h`, `_HRT_MMU_INVALIDATE_TLB_REG_IDX`, `_HRT_MMU_PAGE_TABLE_BASE_ADDRESS_REG_IDX`, `_HRT_MMU_REG_ALIGN`

Control flow: MMU programming code uses these indexes when telling hardware where the page directory is and when invalidating TLB entries.

State and persistence behavior: These files provide compile-time hardware contracts only. Runtime state lives in device registers, token FIFOs, memory regions, or generated firmware structures.

Dependencies and integration points: They integrate with input-system configuration, capture/acquisition hardware, MMU register programming, generated ISP code, and CSS firmware ABI assumptions.

Risks and edge cases: Small constants have large blast radius: a wrong base-address or invalidate register index leaves stale or absent mappings.

Test signals: Mechanically verify bitfield widths/indexes, reset values, MIPI data type values, token pack/unpack paths, MMIO register offsets, and build-time consistency against firmware-generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/mmu_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/interface/ia_css_binary.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/interface/ia_css_binary.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/interface/ia_css_binary.h` declares the central CSS binary-selection and binary-metadata API, including mode constants, descriptor structs, selected-binary state, grid/shading helpers, parameter lifetime helpers, and ISP binary enumeration.

Important APIs, types, and functions: Important local symbols: `ia_css_binary_init_infos`, `ia_css_binary_uninit`, `ia_css_binary_fill_info`, `ia_css_binary_find`, `ia_css_binary_get_shading_info`, `ia_css_binary_3a_grid_info`, `ia_css_binary_dvs_grid_info`, `ia_css_binary_dvs_stat_grid_info`, `ia_css_binary_max_vf_width`, `ia_css_binary_destroy_isp_parameters`, `ia_css_binary_get_isp_binaries` Types and constants: `ia_css_cas_binary_descr`, `ia_css_binary_descr`, `ia_css_binary`; `_IA_CSS_BINARY_H_`, `IA_CSS_BINARY_MODE_COPY`, `IA_CSS_BINARY_MODE_PREVIEW`, `IA_CSS_BINARY_MODE_PRIMARY`, `IA_CSS_BINARY_MODE_VIDEO`, `IA_CSS_BINARY_MODE_PRE_ISP`, `IA_CSS_BINARY_MODE_GDC`, `IA_CSS_BINARY_MODE_POST_ISP`, `IA_CSS_BINARY_MODE_ANR`, `IA_CSS_BINARY_MODE_CAPTURE_PP`

Control flow: Pipeline code fills `ia_css_binary_descr`, calls `ia_css_binary_find()`, receives a populated `ia_css_binary`, then queries grid/shading/VF limits and eventually destroys allocated ISP parameters.

State and persistence behavior: State is process-local firmware metadata (`all_binaries`, `binary_infos`), loaded blob XMEM addresses, per-selected-binary frame/grid/table metrics, and allocated ISP parameter segments. `ia_css_binary_uninit()` and `ia_css_binary_destroy_isp_parameters()` release that state; nothing is file-backed.

Dependencies and integration points: Binary selection depends on `sh_css_blob_info`, HMM allocation, ISP parameter allocation, frame/public CSS types, VF/SC/SDIS helpers, firmware metadata, DVS/BDS macros, and AtomISP logging.

Risks and edge cases: The descriptor combines many boolean feature gates and frame-info pointers; invalid combinations are mostly rejected in implementation rather than by the type system.

Test signals: Cover each binary mode, online/offline input sources, VF and no-VF outputs, multiple output pins, BDS factors, high-speed/reduced/continuous/striped variants, DVS envelope sizing, unsupported formats, firmware-load failure, and parameter cleanup after partial fill failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/interface/ia_css_binary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/src/binary.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/src/binary.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/src/binary.c` implements CSS ISP binary inventory, matching, sizing, grid/shading metadata, parameter allocation, and cleanup.

Important APIs, types, and functions: Important local symbols: `ia_css_binary_dvs_env`, `ia_css_binary_internal_res`, `ia_css_binary_compute_shading_table_bayer_origin`, `binary_get_shading_info_type_1`, `ia_css_binary_get_shading_info`, `sh_css_binary_common_grid_info`, `ia_css_binary_dvs_grid_info`, `ia_css_binary_dvs_stat_grid_info`, `ia_css_binary_3a_grid_info`, `binary_init_pc_histogram`, `binary_init_metrics`, `binary_supports_output_format`, `binary_supports_vf_format`, `supports_bds_factor` Types and constants: `sh_css_shading_table_bayer_origin_compute_results`; `MAX_SPEC_DECI_FACT_LOG2`, `MIN_SPEC_DECI_FACT_LOG2`, `DECI_FACT_LOG2_5_SMALLEST_FRAME_WIDTH_BQ`, `DECI_FACT_LOG2_4_SMALLEST_FRAME_WIDTH_BQ`

Control flow: `ia_css_binary_init_infos()` loads ISP firmware blobs into `all_binaries` and mode lists. `ia_css_binary_find()` filters candidates by continuity, striping, pipe version, feature flags, input source, output/VF formats, frame sizes, BDS/DPC, and then calls `ia_css_binary_fill_info()`. Fill-info allocates ISP parameters, derives internal/input/output/VF sizes, DVS envelope, morph and statistics table dimensions, DIS info, and left padding.

State and persistence behavior: State is process-local firmware metadata (`all_binaries`, `binary_infos`), loaded blob XMEM addresses, per-selected-binary frame/grid/table metrics, and allocated ISP parameter segments. `ia_css_binary_uninit()` and `ia_css_binary_destroy_isp_parameters()` release that state; nothing is file-backed.

Dependencies and integration points: Binary selection depends on `sh_css_blob_info`, HMM allocation, ISP parameter allocation, frame/public CSS types, VF/SC/SDIS helpers, firmware metadata, DVS/BDS macros, and AtomISP logging.

Risks and edge cases: Candidate matching is order-sensitive, has many early `continue` gates, and mixes firmware metadata with caller frame descriptors; small mistakes can select no binary or a subtly wrong binary.

Test signals: Cover each binary mode, online/offline input sources, VF and no-VF outputs, multiple output pins, BDS factors, high-speed/reduced/continuous/striped variants, DVS envelope sizing, unsupported formats, firmware-load failure, and parameter cleanup after partial fill failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/binary/src/binary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq.h` declares the host/SP buffer queue and event queue API: queue mapping, module init/deinit, buffer enqueue/dequeue, psys/isys event enqueue/dequeue, tagger command enqueue, and queue diagnostics.

Important APIs, types, and functions: Important local symbols: `ia_css_query_internal_queue_id`, `ia_css_queue_map`, `ia_css_queue_map_init`, `ia_css_bufq_init`, `ia_css_bufq_enqueue_buffer`, `ia_css_bufq_dequeue_buffer`, `ia_css_bufq_enqueue_psys_event`, `ia_css_bufq_dequeue_psys_event`, `ia_css_bufq_enqueue_isys_event`, `ia_css_bufq_dequeue_isys_event`, `ia_css_bufq_enqueue_tag_cmd`, `ia_css_bufq_deinit`, `ia_css_bufq_dump_queue_info` Types and constants: No named structs or enums are introduced here.; `_IA_CSS_BUFQ_H`, `BUFQ_EVENT_SIZE`

Control flow: CSS initialization maps buffer types to per-thread queues, initializes remote SP queue handles, and uses these APIs to pass buffers/events between host and SP firmware.

State and persistence behavior: State is static in-memory queue handles, buffer-type-to-queue maps, availability bitmaps, and SP-resident circular queues. No data persists after driver/runtime reset.

Dependencies and integration points: The queue layer depends on SP firmware queue offsets, `ia_css_queue`, `ia_css_eventq`, buffer type enums, SP thread constants, tagger commands, and CSS debug tracing.

Risks and edge cases: Queue IDs are shared ABI values with SP firmware; mismatched thread or queue IDs cause lost buffers or blocked pipelines.

Test signals: Test map/unmap lifecycle, reserved parameter queues, queue exhaustion, invalid thread/queue IDs, enqueue full/dequeue empty behavior, psys/isys event payload ordering, tagger command delivery, and queue-info dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq_comm.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq_comm.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq_comm.h` defines the shared queue ID enum, maximum queue count, dynamic-buffer limit per thread, and reserved parameter/per-frame parameter queue IDs.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_queue_id`; `_IA_CSS_BUFQ_COMM_H`, `SH_CSS_MAX_NUM_QUEUES`, `SH_CSS_MAX_DYNAMIC_BUFFERS_PER_THREAD`, `IA_CSS_PARAMETER_SET_QUEUE_ID`, `IA_CSS_PER_FRAME_PARAMETER_SET_QUEUE_ID`

Control flow: Both host queue mapping and SP firmware agree that queues A and B are reserved for parameter sets and per-frame parameter sets.

State and persistence behavior: State is static in-memory queue handles, buffer-type-to-queue maps, availability bitmaps, and SP-resident circular queues. No data persists after driver/runtime reset.

Dependencies and integration points: The queue layer depends on SP firmware queue offsets, `ia_css_queue`, `ia_css_eventq`, buffer type enums, SP thread constants, tagger commands, and CSS debug tracing.

Risks and edge cases: Adding buffer types without increasing queues can exhaust the C-H dynamic mapping range.

Test signals: Test map/unmap lifecycle, reserved parameter queues, queue exhaustion, invalid thread/queue IDs, enqueue full/dequeue empty behavior, psys/isys event payload ordering, tagger command delivery, and queue-info dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/interface/ia_css_bufq_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/src/bufq.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/src/bufq.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/src/bufq.c` implements CSS host/SP queue mapping and remote queue handle initialization, plus enqueue/dequeue wrappers for buffers, psys/isys events, and tagger commands.

Important APIs, types, and functions: Important local symbols: `map_buffer_type_to_queue_id`, `unmap_buffer_type_to_queue_id`, `ia_css_queue_map_init`, `ia_css_queue_map`, `ia_css_query_internal_queue_id`, `init_bufq`, `ia_css_bufq_init`, `ia_css_bufq_enqueue_buffer`, `ia_css_bufq_dequeue_buffer`, `ia_css_bufq_enqueue_psys_event`, `ia_css_bufq_dequeue_psys_event`, `ia_css_bufq_dequeue_isys_event`, `ia_css_bufq_enqueue_isys_event`, `ia_css_bufq_enqueue_tag_cmd` Types and constants: `sh_css_queues`; `BUFQ_DUMP_FILE_NAME_PREFIX_SIZE`

Control flow: `ia_css_queue_map_init()` marks queues free and maps invalid. `ia_css_queue_map()` reserves fixed queues for parameter buffers or first available C-H queue. `ia_css_bufq_init()` builds remote queue handles from SP firmware offsets. Enqueue/dequeue functions validate IDs, resolve handles, and call `ia_css_queue_*` or `ia_css_eventq_*` helpers.

State and persistence behavior: State is static in-memory queue handles, buffer-type-to-queue maps, availability bitmaps, and SP-resident circular queues. No data persists after driver/runtime reset.

Dependencies and integration points: The queue layer depends on SP firmware queue offsets, `ia_css_queue`, `ia_css_eventq`, buffer type enums, SP thread constants, tagger commands, and CSS debug tracing.

Risks and edge cases: Mapping relies on assertions for duplicate/exhausted allocation, `deinit` is a no-op, and polled dequeue functions intentionally suppress tracing.

Test signals: Test map/unmap lifecycle, reserved parameter queues, queue exhaustion, invalid thread/queue IDs, enqueue full/dequeue empty behavior, psys/isys event payload ordering, tagger command delivery, and queue-info dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/bufq/src/bufq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug.h` declares the broad CSS debug and diagnostics API: trace levels/macros, global dtrace level control, binary/frame/resolution/config dumpers, SP sleep/wake controls, FIFO and MIPI diagnostics, DMA debug-mode controls, PC dumps, hang-status dumps, and external command handling.

Important APIs, types, and functions: Important local symbols: `__printf`, `ia_css_debug_set_dtrace_level`, `ia_css_debug_get_dtrace_level`, `ia_css_debug_dump_gac_state`, `ia_css_debug_dump_sp_sw_debug_info`, `ia_css_debug_print_sp_debug_state`, `ia_css_debug_binary_print`, `ia_css_debug_sp_dump_mipi_fifo_high_water`, `ia_css_debug_dump_pif_a_isp_fifo_state`, `ia_css_debug_dump_pif_b_isp_fifo_state`, `ia_css_debug_dump_str2mem_sp_fifo_state`, `ia_css_debug_dump_all_fifo_state`, `ia_css_debug_frame_print`, `ia_css_debug_enable_sp_sleep_mode` Types and constants: `ia_css_debug_enable_param_dump`; `_IA_CSS_DEBUG_H_`, `IA_CSS_DEBUG_ERROR`, `IA_CSS_DEBUG_WARNING`, `IA_CSS_DEBUG_VERBOSE`, `IA_CSS_DEBUG_TRACE`, `IA_CSS_DEBUG_TRACE_PRIVATE`, `IA_CSS_DEBUG_PARAM`, `IA_CSS_DEBUG_INFO`, `IA_CSS_ERROR`, `IA_CSS_WARNING`

Control flow: Callers use macros such as `IA_CSS_ENTER`, `IA_CSS_ERROR`, and `IA_CSS_LEAVE_ERR_PRIVATE`; those call `ia_css_debug_dtrace()`, which is gated by `dbg_level` and eventually prints through `sh_css_vprint()`.

State and persistence behavior: Debug state is runtime-only: global `dbg_level`, live pipeline/frame/config pointers passed to dumpers, SP debug state, and hardware diagnostic registers. Output goes to tracing/log sinks but this header does not persist files.

Dependencies and integration points: Debug declarations integrate CSS stream/pipe/frame/binary types, metadata, SP debug state, AtomISP internals, and low-level hardware diagnostics.

Risks and edge cases: Tracing is global and can be noisy in polled paths; debug APIs expose low-level controls such as DMA-channel disable/enable that can perturb a live pipeline.

Test signals: Validate trace-level gating, format-string coverage, dumpers with NULL or inactive pipeline members where permitted, SP sleep/wake debug paths, DMA debug-mode toggles, pipe graph output, and high-frequency event polling without log flooding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_internal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_internal.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_internal.h` is a placeholder/internal debug header noting that more debug-related code should move out of internal CSS headers.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; No exported preprocessor constants.

Control flow: It currently contributes no declarations beyond licensing/comment context.

State and persistence behavior: Debug state is runtime-only: global `dbg_level`, live pipeline/frame/config pointers passed to dumpers, SP debug state, and hardware diagnostic registers. Output goes to tracing/log sinks but this header does not persist files.

Dependencies and integration points: Debug declarations integrate CSS stream/pipe/frame/binary types, metadata, SP debug state, AtomISP internals, and low-level hardware diagnostics.

Risks and edge cases: Its emptiness can mislead include users into believing an internal debug contract exists here.

Test signals: Validate trace-level gating, format-string coverage, dumpers with NULL or inactive pipeline members where permitted, SP sleep/wake debug paths, DMA debug-mode toggles, pipe graph output, and high-frequency event polling without log flooding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_pipe.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_pipe.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_pipe.h` declares internal pipe-graph debug helpers for graph prologue/epilogue, pipeline stage dumping, SP raw-copy frame dumping, and stream-config dumping.

Important APIs, types, and functions: Important local symbols: `ia_css_debug_pipe_graph_dump_prologue`, `ia_css_debug_pipe_graph_dump_epilogue`, `ia_css_debug_pipe_graph_dump_stage`, `ia_css_debug_pipe_graph_dump_sp_raw_copy`, `ia_css_debug_pipe_graph_dump_stream_config` Types and constants: No named structs or enums are introduced here.; `_IA_CSS_DEBUG_PIPE_H_`

Control flow: Pipeline diagnostic code calls these functions around stage traversal to emit a graph representation of the active stream/pipe.

State and persistence behavior: Debug state is runtime-only: global `dbg_level`, live pipeline/frame/config pointers passed to dumpers, SP debug state, and hardware diagnostic registers. Output goes to tracing/log sinks but this header does not persist files.

Dependencies and integration points: Debug declarations integrate CSS stream/pipe/frame/binary types, metadata, SP debug state, AtomISP internals, and low-level hardware diagnostics.

Risks and edge cases: The API accepts live pipeline-stage and frame pointers, so dump code must tolerate partially configured or torn-down pipelines.

Test signals: Validate trace-level gating, format-string coverage, dumpers with NULL or inactive pipeline members where permitted, SP sleep/wake debug paths, DMA debug-mode toggles, pipe graph output, and high-frequency event polling without log flooding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/debug/interface/ia_css_debug_pipe.h -->
