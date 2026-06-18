## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_reg_map.h

### Purpose
`goya_reg_map.h` aliases Goya PSOC scratchpad and global configuration registers to semantic CPU/firmware names used by the driver.

### Important APIs, Types, And Functions
The macros map queue base/length/consumer-index fields (`mmCPU_PQ_*`, `mmCPU_EQ_*`, `mmCPU_CQ_*`), boot/update/version status (`mmCPU_BOOT_DEV_STS*`, `mmCPU_BOOT_ERR*`, `mmUPD_*`, `mmPREBOOT_VER_OFFSET`, `mmUBOOT_VER_OFFSET`), command/status exchange (`mmCPU_CMD_STATUS_TO_HOST`, `mmPSOC_GLOBAL_CONF_KMD_MSG_TO_CPU`), and hardware state (`mmHW_STATE`) onto underlying `mmPSOC_GLOBAL_CONF_*` registers.

### Control Flow
There is no runtime flow. Driver code reads and writes the semantic aliases while performing firmware boot, queue setup, update coordination, and status polling.

### State, Persistence, And Dependencies
State is stored in PSOC scratchpad/global registers that survive long enough for host-firmware coordination, with `mmUPD_PENDING_STS` using non-reset flop storage. The header depends on generated ASIC register macros being included before use.

### Integration Points
The aliases integrate Goya firmware interface code, boot diagnostics, event/command queue setup, and update flows with the generated register map.

### Risks
Scratchpads are shared firmware/driver ABI. Reusing an index for a different purpose or including this header without the underlying register definitions causes silent misprogramming or build failures.

### Test Signals
Boot should report sane firmware version/status values, queue base/length registers should match allocated queues, update status should survive intended resets, and read/write test scratchpads should round-trip.
