# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb_types.h` defines the public white-balance tuning contract with common exponent and Gr/R/B/Gb gain significands.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_wb_config`; `__IA_CSS_WB_TYPES_H`

Control flow: Higher layers pass `ia_css_wb_config` to the encoder for fixed-point conversion.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The documented ranges are not enforced here, so callers need validation.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
