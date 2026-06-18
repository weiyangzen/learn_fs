# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_2/ia_css_ynr2.host.h` declares YNR2/FC defaults, encoders, dump functions, and debug trace helpers.

Important APIs, types, and functions: Important local symbols: `ia_css_ynr_encode`, `ia_css_fc_encode`, `ia_css_ynr_dump`, `ia_css_fc_dump`, `ia_css_fc_debug_dtrace`, `ia_css_ynr_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_YNR2_HOST_H`

Control flow: Still-pipe parameter code includes it for ISP2 still YNR2/YEE2/FC2 kernels.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Consumers must keep YNR2 and FC parameter sections synchronized because FC is used with YNR2/YEE2.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
