# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_support.h

Purpose: `sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp2400_support.h` provides host-build compatibility aliases for ISP2400 vector/memory types and helper macros to address ISP DMEM, VMEM, VAMEM1, VAMEM2, and optional histogram memories.

Important APIs, types, and functions: Important local symbols: No function bodies; this file is a data/type contract. Types and constants: No named structs or enums are introduced here.; `_isp2400_support_h`, `hrt_isp_vamem1_store_16`, `hrt_isp_vamem2_store_16`, `hrt_isp_dmem`, `hrt_isp_vmem`, `hrt_isp_dmem_master_port_address`, `hrt_isp_vmem_master_port_address`, `hrt_isp_hist`, `hrt_isp_hist_master_port_address`

Control flow: It has no runtime control flow; it expands hardware-memory access macros used by host code, simulator/crun builds, and generated ISP support code.

State and persistence behavior: No state is stored here. The macros address live ISP memory spaces through HRT properties when used by callers.

Dependencies and integration points: It depends on HRT memory helper macros and ISP feature flags such as `ISP_HAS_HIST`; it integrates low-level memory access with host-side code that includes Hive headers.

Risks and edge cases: Type aliases are only supplied when `ISP2400_VECTOR_TYPES` is absent, so build configuration changes can alter visible types. Incorrect cell or memory-property use writes to the wrong ISP memory.

Test signals: Compile host and ISP2400-vector builds, exercise VAMEM/DMEM/VMEM address macros in simulator tests, and verify histogram helpers only compile when histogram support is enabled.
