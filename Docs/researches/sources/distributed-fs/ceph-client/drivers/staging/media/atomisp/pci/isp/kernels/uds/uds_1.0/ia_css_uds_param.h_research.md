# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/uds/uds_1.0/ia_css_uds_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/uds/uds_1.0/ia_css_uds_param.h` defines Up/Down Scaling parameter bundles shared between host and SP, pairing crop position with `sh_css_uds_info` scale metadata.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_uds_config`, `sh_css_sp_uds_params`; `__IA_CSS_UDS_PARAM_H`

Control flow: Pipeline configuration populates crop and UDS coefficients, then copies equivalent data into SP-visible `sh_css_sp_uds_params`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: This header has no validation; invalid crop/scale combinations are caught only by callers or downstream UDS code.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
