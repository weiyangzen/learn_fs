# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_param.h` defines XNR1 ISP scalar and VAMEM parameter layouts, including compile-time table size selection.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_xnr_vamem_params`, `sh_css_isp_xnr_params`; `__IA_CSS_XNR_PARAM_H`, `SH_CSS_ISP_XNR_TABLE_SIZE_LOG2`, `SH_CSS_ISP_XNR_TABLE_SIZE`

Control flow: The pipe generator can set the table size to zero; normal host builds use system-global VAMEM table constants.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Build-mode-dependent table size can hide buffer assumptions between generator and runtime builds.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
