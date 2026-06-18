## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_reg_map.h

### Purpose
`gaudi_reg_map.h` defines semantic aliases for Gaudi PSOC scratchpad and cold-reset registers. It gives higher-level names to generated `mmPSOC_GLOBAL_CONF_*` register constants so boot, firmware update, interrupt polling, and reset code can use intent-oriented names.

### Important APIs, Types, And Functions
The file maps aliases such as `mmHW_STATE`, `mmGIC_*_IRQ_*_POLL_REG`, `mmCPU_BOOT_DEV_STS0/1`, `mmFUSE_VER_OFFSET`, `mmCPU_CMD_STATUS_TO_HOST`, `mmCPU_BOOT_ERR0/1`, `mmUPD_STS`, `mmUPD_CMD`, `mmPREBOOT_VER_OFFSET`, `mmUBOOT_VER_OFFSET`, `mmRDWR_TEST`, `mmBTL_ID`, `mmPREBOOT_PCIE_EN`, `mmCOLD_RST_DATA`, and `mmUPD_PENDING_STS` to scratchpad or cold-reset flop registers.

### Control Flow
There are no functions. Boot and update flows read and write these aliases while coordinating with firmware. Interrupt/polling code uses the GIC aliases to check event, QMAN, DMA, halt, and host interrupt state. Reset code exchanges cold-reset state through `mmCOLD_RST_DATA`.

### State, Persistence, And Dependencies
The represented state is PSOC scratchpad/cold-reset hardware state. Some scratchpad values persist across firmware stages or warm/cold reset boundaries depending on register class. The aliases depend on generated `mmPSOC_GLOBAL_CONF_*` symbols being visible through `gaudi_regs.h`.

### Integration Points
`gaudi.c` includes this file for boot, reset, update, and interrupt coordination. `gaudi_coresight.c` also includes it for debug paths that need PSOC register names. The file ties firmware-interface structures from `gaudi_fw_if.h` to specific scratch registers.

### Risks
Alias drift can make code write the wrong scratchpad register while still compiling. Because these registers are used for boot/update handshakes and interrupt polling, mistakes can produce firmware boot failures, missed interrupts, or broken recovery. Ambiguous names are avoided here by keeping one alias per semantic scratchpad role.

### Test Signals
Validate firmware boot-state transitions, preboot/U-Boot version reporting, update command/status handshakes, GIC polling registers, read/write scratchpad tests, and cold-reset data exchange. Recovery tests should confirm `mmCPU_BOOT_ERR*` and `mmCOLD_RST_DATA` aliases are read correctly after failures.
