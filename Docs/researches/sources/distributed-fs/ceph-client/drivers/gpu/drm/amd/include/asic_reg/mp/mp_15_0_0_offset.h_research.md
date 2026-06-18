<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_offset.h

Purpose: generated AMD MP 15.0.0 register-address metadata for MPASP, MPASP public PCRU, MP1 SMN, and MP1 public CRU blocks. It gives the amdgpu driver symbolic offsets and base indexes for MP firmware communication registers in the newer ASIC generation.

Important APIs/types/functions: the file exports address macros, not functions or types. MPASP SMN includes C2P message registers `60` through `79`, `100` through `103`, `109`, plus `regMPASP_SMN_IH_CREDIT`, `regMPASP_SMN_IH_SW_INT`, and `regMPASP_SMN_IH_SW_INT_CTRL`, all with base index `0`. `mp_SmuMpASPPub_PcruDec` adds public PCRU C2P registers `regMPASP_PCRU1_MPASP_C2PMSG_64` through `71` at offsets `0x4280` through `0x4287` with base index `3`. MP1 SMN provides the full `regMP1_SMN_C2PMSG_0` through `127` sequence, IH registers, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_EXT_SCRATCH0` through `31`, generally with base index `1`. MP1 public firmware flags are exposed as `regMP1_CRU1_MP1_FIRMWARE_FLAGS` with base index `5`.

Control flow: no executable control flow exists. Downstream code uses each `reg*` macro and matching `_BASE_IDX` to form register accesses through AMD's MMIO/SMN access helpers. The address-block comments identify the required base aperture for each register family.

State and persistence: no software state is stored. The constants address hardware state used for host-to-firmware messages, software interrupt delivery and acknowledgement, scratch exchanges, and public firmware status flags. The MPASP public PCRU registers add a public-addressed path for selected MPASP C2P messages.

Dependencies and integration points: depends on the AMD register-generation scheme and the amdgpu register accessor layer. It pairs with `mp_15_0_0_sh_mask.h` for field masks and with ASIC-specific SMU/MP code selecting MP 15.0.0 definitions.

Risks: compared with MP 14.0.2, the MPASP register set is narrower at the SMN level and adds a public PCRU block; copying assumptions between generations can route MPASP accesses through the wrong block. The `regMP1_CRU1_MP1_FIRMWARE_FLAGS_BASE_IDX` value is `5`, unlike MP 14.0.2's public block base index, so version selection is safety-critical. Repetitive full MP1 C2P sequences can hide missing entries, and any offset/base-index mismatch can cause reads or writes against unrelated hardware.

Test signals: generated-header linting should verify paired `reg*` and `_BASE_IDX` macros, monotonic C2P offset ranges, and expected base indexes per address block. Build tests catch missing references; hardware tests should cover MP1 message submission, MPASP message submission through both SMN and PCRU paths where used, interrupt handling, and scratch register communication on MP 15.0.0 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_0_offset.h -->
