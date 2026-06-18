# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr.host.h` declares YNR/YEE defaults, encoders, dump/debug functions, and state initialization.

Important APIs, types, and functions: Important local symbols: `ia_css_nr_encode`, `ia_css_yee_encode`, `ia_css_nr_dump`, `ia_css_yee_dump`, `ia_css_nr_debug_dtrace`, `ia_css_ee_debug_dtrace`, `ia_css_init_ynr_state` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_YNR_HOST_H`

Control flow: Parameter setup uses this header for preview/video YNR1 and YEE1 kernels.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: State initialization takes `void *`, so type safety is intentionally weak.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
