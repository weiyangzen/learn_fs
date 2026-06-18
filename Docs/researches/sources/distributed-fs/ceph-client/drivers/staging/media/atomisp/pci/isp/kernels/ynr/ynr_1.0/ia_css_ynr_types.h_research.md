# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_types.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/ynr/ynr_1.0/ia_css_ynr_types.h` defines public NR, EE, and combined YEE configuration structures used for BNR/YNR/CNR and sharpening.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `ia_css_nr_config`, `ia_css_ee_config`, `ia_css_yee_config`; `__IA_CSS_YNR_TYPES_H`

Control flow: Public CSS tuning values are passed through the host encoders into YNR/YEE ISP params.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: The same NR config feeds several kernels, so one mis-tuned value can affect Bayer, luma, and chroma paths.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
