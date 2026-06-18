# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr_types.h` defines the public CSS TNR tuning contract: interpolation gain plus luma and chroma thresholds used to decide whether to blend with the previous frame.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_tnr_config`; `__IA_CSS_TNR_TYPES_H`

Control flow: Userspace or higher CSS code sets `ia_css_tnr_config`; host encoding converts u0.16 values into ISP parameter words.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Zero thresholds disable useful temporal blending, while high thresholds can smear motion; range checking is mostly documented rather than enforced here.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
