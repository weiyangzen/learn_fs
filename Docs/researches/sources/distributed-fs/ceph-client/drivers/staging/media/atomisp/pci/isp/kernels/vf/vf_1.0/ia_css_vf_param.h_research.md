# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_param.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf_param.h` defines the ISP VF decimation config with downscale bits, enable flag, frame SP info, and DMA port-B configuration.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: `sh_css_isp_vf_isp_config`, `dma`; `__IA_CSS_VF_PARAM_H`, `VFDEC_BITS_PER_PIXEL`

Control flow: Host code fills this struct, then the ISP kernel uses it to write the downscaled viewfinder plane.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Mismatched DMA `width_a_over_b` or disabled `info` leaves VF output absent or malformed.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
