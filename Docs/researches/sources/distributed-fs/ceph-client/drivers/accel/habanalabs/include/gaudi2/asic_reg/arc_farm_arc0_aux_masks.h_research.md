## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_masks.h

### Purpose
`arc_farm_arc0_aux_masks.h` is the generated field-mask header for Gaudi2 ARC farm ARC0 auxiliary registers. It defines shifts and masks for run/halt control, reset, wakeup, message/status, queue and DCCM controls, address-region translation, termination/error handling, protection, ordering, and upper-DCCM enable fields.

### Important APIs, Types, And Functions
The file exports 454 `ARC_FARM_ARC0_AUX_*` field definitions plus the include guard. Most fields follow the generated `*_SHIFT` and `*_MASK` pattern. Key groups include `RUN_HALT_*`, `ARC_RST_*`, `WAKE_UP_EVENT`, `ARC_INT_*`, `CAUSE`, `DCCM_QUEUE_*`, `QMAN_ARC_CQ_SHADOW_CI`, `CBU_*`, `LBU_*`, `DCCM_*`, `ARC_REGION_CFG_*`, `ARC_AXI_ORDERING_*`, and `MME_ARC_UPPER_DCCM_EN`.

### Control Flow
The header has no executable code. Runtime code uses these masks to compose values written to ARC0 AUX registers, extract status/error fields, configure memory region ASIDs/protection/MMU bypass, and control reset/halt or wakeup behavior. Security code pairs these masks with the address map to decide which fields are exposed or protected.

### State, Persistence, And Dependencies
The fields affect persistent hardware state in ARC auxiliary registers until reset or reprogramming. Address-region configuration persists as ARC-visible address translation state, while queue and interrupt fields reflect live firmware communication state. The masks depend on `arc_farm_arc0_aux_regs.h` for register addresses and on common bitfield helpers in driver code.

### Integration Points
`gaudi2_regs.h` includes this mask header. It integrates with `gaudi2_security.c` range rules, ARC firmware boot/control, and `gaudi2_arc_common_packets.h` region IDs. Fields such as `ARC_REGION_CFG_*_ASID`, `MMU_BP`, and `PROT_VAL*` connect ARC address regions to MMU/security policy.

### Risks
Generated mask mistakes are difficult to diagnose because writes still hit valid registers but alter wrong bits. Region config fields are security-sensitive: wrong ASID, protection, or MMU-bypass bits can grant ARC firmware unintended access. Run/halt/reset masks are sequencing-sensitive and can leave ARC firmware stuck if bit positions drift.

### Test Signals
Test ARC0 halt/run/reset/wakeup flows, interrupt cause/mask handling, DCCM queue configuration, ARC region ASID/protection/MMU-bypass programming, CBU/LBU/DCCM terminate paths, and ordering-control behavior. Security tests should verify allowed fields cannot bypass protected memory policy.
