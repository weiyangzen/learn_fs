# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_param.h` defines the ISP white-balance parameter block: common gain shift and four Bayer-channel gains.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_wb_params`; `__IA_CSS_WB_PARAM_H`

Control flow: The ISP WB kernel reads these signed fields to apply channel gains.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Signed storage of fixed-point values makes overflow or bad scaling visible as color cast.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
