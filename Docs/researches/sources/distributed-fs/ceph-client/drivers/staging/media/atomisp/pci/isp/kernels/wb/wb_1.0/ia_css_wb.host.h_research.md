# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/wb/wb_1.0/ia_css_wb.host.h` declares the white-balance default config, encoder, and debug dump entry points.

Important APIs, types, and functions: Important local symbols: `ia_css_wb_encode`, `ia_css_wb_dump`, `ia_css_wb_debug_dtrace` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_WB_HOST_H`

Control flow: Parameter assembly includes this header when writing WB ISP sections or diagnostic dumps.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Debug declarations are unconditional although implementations are conditionally compiled under `IA_CSS_NO_DEBUG`.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
