# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/xnr/xnr_1.0/ia_css_xnr_types.h` defines the public XNR1 table and threshold config, including VAMEM1/VAMEM2 table shapes and reciprocal coefficient documentation.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_xnr_data`, `ia_css_xnr_table`, `ia_css_xnr_config`; `__IA_CSS_XNR_TYPES_H`, `IA_CSS_VAMEM_1_XNR_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_1_XNR_TABLE_SIZE`, `IA_CSS_VAMEM_2_XNR_TABLE_SIZE_LOG2`, `IA_CSS_VAMEM_2_XNR_TABLE_SIZE`

Control flow: CSS configuration passes scalar threshold plus optional table data to host encoders.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: VAMEM type must match the target ISP generation or coefficients are interpreted through the wrong array.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
