# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/tnr/tnr_1.0/ia_css_tnr.host.h` declares the host-side Temporal Noise Reduction entry points: parameter encoding/dumping, frame-address configuration, binary configuration, and DMEM state initialization.

Important APIs, types, and functions: Important local symbols: `ia_css_tnr_encode`, `ia_css_tnr_dump`, `ia_css_tnr_debug_dtrace`, `ia_css_tnr_config`, `ia_css_tnr_configure`, `ia_css_init_tnr_state` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_TNR_HOST_H`

Control flow: Runtime code uses these declarations when a video binary enables TNR; host state is converted into ISP parameter/config sections and frame-buffer addresses before firmware execution.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The API is pointer-heavy and size arguments are not self-describing in the header, so callers must pass matching ISP structs and valid TNR frame arrays.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
