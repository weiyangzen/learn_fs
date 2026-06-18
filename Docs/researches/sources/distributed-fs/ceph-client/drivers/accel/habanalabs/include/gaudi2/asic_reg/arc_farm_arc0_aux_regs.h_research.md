## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_regs.h

### Purpose
`arc_farm_arc0_aux_regs.h` is the generated Gaudi2 register-address map for ARC farm ARC0 auxiliary registers. It provides symbolic addresses for ARC run/halt/reset, cluster identity, interrupts, scratchpads, DCCM queues, CBU/LBU/DCCM address windows, ARC region configuration, error termination, ordering control, and upper-DCCM enablement.

### Important APIs, Types, And Functions
The file defines 284 `mmARC_FARM_ARC0_AUX_*` constants from `mmARC_FARM_ARC0_AUX_RUN_HALT_REQ` at `0x4E88100` through `mmARC_FARM_ARC0_AUX_MME_ARC_UPPER_DCCM_EN` at `0x4E88920`. Important groups include run/halt and reset request/ack registers, cluster and wakeup registers, message and interrupt registers, scratchpads, DCCM queue base/head/tail/alert registers, CBU/LBU/DCCM base/mask/terminate registers, 16 ARC region config registers, AXI ordering controls, and MME upper DCCM controls.

### Control Flow
There are no functions. Driver and firmware-control flows write these registers to start or stop ARC0, reset it, wake it, configure memory regions, set up DCCM queues, and diagnose termination/error conditions. `gaudi2_security.c` treats the ARC0 AUX ranges as a template for protection rules and instance-offset expansion.

### State, Persistence, And Dependencies
The represented state is live ARC auxiliary hardware state. Configuration registers persist across normal operation until reset/reprogramming, while counters and termination/error registers reflect runtime faults. The file is included through `gaudi2_regs.h` and interpreted through `arc_farm_arc0_aux_masks.h`.

### Integration Points
Gaudi2 security setup references ranges such as `RUN_HALT_REQ` to `RUN_HALT_ACK`, `CLUSTER_NUM` to `WAKE_UP_EVENT`, scratchpad and DCCM queue ranges, and final ordering/upper-DCCM registers. ARC firmware packet concepts from `gaudi2_arc_common_packets.h` depend on these registers for ARC-visible address-region setup.

### Risks
ARC0 AUX is a central control surface. Wrong addresses can prevent firmware boot, leave ARC halted, corrupt DCCM queues, or expose wrong memory regions. Since ARC0 ranges are used to compute other ARC instances, any base or range error can become a fleet-wide Gaudi2 security/control bug.

### Test Signals
Validate ARC0 run/halt/reset acknowledgments, wakeup events, scratchpad read/write, DCCM queue push/pop and alert messages, ARC region programming for all 16 regions, terminate/error capture paths, AXI ordering controls, and security range replication to ARC1+ instances.
