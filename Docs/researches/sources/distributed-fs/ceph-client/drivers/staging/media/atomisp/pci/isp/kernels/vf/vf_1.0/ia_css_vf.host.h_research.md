# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/vf/vf_1.0/ia_css_vf.host.h` declares the VF host API for downscale computation, ISP config encoding, and binary-level VF configuration.

Important APIs, types, and functions: Important local symbols: `sh_css_vf_downscale_log2`, `ia_css_vf_config`, `ia_css_vf_configure` Types and constants: No named structs or enums are introduced here.; `__IA_CSS_VF_HOST_H`

Control flow: Binary setup code includes this header to configure viewfinder output during `ia_css_binary_fill_info()`.

State and persistence behavior: These kernel parameter files have no filesystem persistence. State is transient CSS pipeline configuration, SP/ISP DMEM or VMEM parameter payloads, global default tuning tables, and in a few cases per-frame or per-pipeline state initialized before firmware execution.

Dependencies and integration points: They depend on AtomISP CSS types such as `ia_css_frame_info`, `ia_css_binary`, `dma_port_config`, `type_support.h`, firmware metadata, and ISP fixed-point helper macros. Integration is through binary parameter allocation/configuration paths that copy host structs into ISP-visible memory.

Risks and edge cases: Callers must provide coherent output/VF frame info and a writable downscale pointer.

Test signals: Exercise default and boundary tuning values, disabled/ineffective settings, maximum documented ranges, binary parameter upload, debug dumps when compiled, and image-quality checks for artifacts such as smear, color cast, aliasing, haloing, or missing VF output.
