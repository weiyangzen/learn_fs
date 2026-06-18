## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_axuser_regs.h

### Purpose
`arc_farm_arc0_dup_eng_axuser_regs.h` is the generated Gaudi2 address map for ARC farm ARC0 duplicate-engine AXUSER configuration registers. These registers control AXI user attributes for high-bandwidth and low-bandwidth transactions, including ASID, MMU bypass, security, privilege, data type, discard, snoop, and override controls.

### Important APIs, Types, And Functions
The file defines 19 `mmARC_FARM_ARC0_DUP_ENG_AXUSER_*` constants from `mmARC_FARM_ARC0_DUP_ENG_AXUSER_HB_ASID` at `0x4E89900` through `mmARC_FARM_ARC0_DUP_ENG_AXUSER_LB_OVRD` at `0x4E8994C`. The names are split between `HB_*` and `LB_*` register families plus shared `*_EMEM_CPAGE` and override controls.

### Control Flow
The header has no code. Initialization/security flows program these registers to attach the correct AXUSER attributes to ARC duplicate-engine traffic. MMU/security code may update ASID, MMU bypass, privilege/security, and override fields while configuring ARC access to device and host memory regions.

### State, Persistence, And Dependencies
The state is hardware AXUSER attribute configuration. It persists until reset or explicit reprogramming and affects all subsequent transactions from the corresponding duplicate engine. Field interpretation depends on the matching AXUSER mask header included by aggregate Gaudi2 register headers.

### Integration Points
`gaudi2_regs.h` includes this file. The addresses integrate with Gaudi2 security/MMU initialization, ARC farm register-range protection, and ARC memory-region setup described by `gaudi2_arc_common_packets.h` and ARC AUX region registers.

### Risks
AXUSER configuration is security-critical. Wrong ASID or MMU-bypass settings can route transactions through the wrong address space or bypass translation. Incorrect secure/privilege bits can either block legitimate firmware traffic or grant unintended access. Override registers are especially sensitive because they can force attributes regardless of per-transaction intent.

### Test Signals
Test ARC duplicate-engine memory accesses under expected ASIDs, MMU bypass disabled/enabled only where intended, secure and privileged access checks, HB/LB path coverage, override behavior, and fault reporting for disallowed accesses. Security tests should verify that attribute programming matches the device memory policy after reset and firmware boot.
