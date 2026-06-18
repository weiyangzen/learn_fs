# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_param.h` defines the ISP-facing TNR parameter and configuration payloads, including coefficient/threshold fields and the DMA port plus frame-address table for temporal reference frames.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_tnr_params`, `ia_css_tnr_configuration`, `sh_css_isp_tnr_isp_config`; `__IA_CSS_TNR_PARAM_H`

Control flow: Host code fills `sh_css_isp_tnr_params` from public tuning values and `sh_css_isp_tnr_isp_config` from frame memory before the ISP kernel consumes them.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Incorrect `NUM_VIDEO_TNR_FRAMES` ordering, frame height, DMA port, or physical address values can make TNR read stale or wrong reference frames.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
