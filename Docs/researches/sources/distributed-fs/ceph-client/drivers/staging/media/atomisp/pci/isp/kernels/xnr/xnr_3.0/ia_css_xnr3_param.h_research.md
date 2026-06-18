# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_param.h` defines ISP-side XNR3 fixed-point scale factors, alpha/coring/blending parameter structs, filter size, and VMEM arrays.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_xnr3_alpha_params`, `sh_css_xnr3_coring_params`, `sh_css_xnr3_blending_params`, `sh_css_isp_xnr3_params`, `sh_css_isp_xnr3_vmem_params`; `__IA_CSS_XNR3_PARAM_H`, `XNR_ALPHA_SCALE_LOG2`, `XNR_ALPHA_SCALE_FACTOR`, `XNR_CORING_SCALE_LOG2`, `XNR_CORING_SCALE_FACTOR`, `XNR_BLENDING_SCALE_LOG2`, `XNR_BLENDING_SCALE_FACTOR`, `XNR_FILTER_SIZE`

Control flow: Host encoding writes these structs into ISP DMEM/VMEM for the XNR3 kernel.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: `XNR_FILTER_SIZE` is a compile-time constant and comments restrict it to known values; firmware mismatch would corrupt gradients.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
