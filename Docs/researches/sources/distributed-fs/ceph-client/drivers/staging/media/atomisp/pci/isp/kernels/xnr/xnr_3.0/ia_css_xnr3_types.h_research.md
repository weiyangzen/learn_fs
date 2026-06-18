# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_3.0/ia_css_xnr3_types.h` defines public XNR3 sigma, coring, and blending tuning structs and their host-side fixed-point scales.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_xnr3_sigma_params`, `ia_css_xnr3_coring_params`, `ia_css_xnr3_blending_params`, `ia_css_xnr3_config`; `__IA_CSS_XNR3_TYPES_H`, `IA_CSS_XNR3_SIGMA_SCALE`, `IA_CSS_XNR3_CORING_SCALE`, `IA_CSS_XNR3_BLENDING_SCALE`

Control flow: Higher CSS configuration populates dark/bright values per plane before host conversion.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Values outside documented fixed-point ranges are not validated in the type contract.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
