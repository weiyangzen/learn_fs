# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.c

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.c` implements YNR2/YEE2 and Fringe Control host encoding. It exports default YNR/FC configs and copies public edge, corner, coring, gain, and crop values into ISP parameter structs.

Important APIs, types, and functions: Important local symbols: `ia_css_ynr_encode`, `ia_css_fc_encode`, `ia_css_ynr_dump`, `ia_css_fc_dump`, `ia_css_fc_debug_dtrace`, `ia_css_ynr_debug_dtrace` Types and constants: No named structs or enums are introduced here.; No exported preprocessor constants.

Control flow: `ia_css_ynr_encode()` maps four sensitivity gains; `ia_css_fc_encode()` maps positive/negative coring, gain, and crop limits; debug functions trace public values.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The C file declares dump functions without definitions here, relying on other build objects or unused references.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
