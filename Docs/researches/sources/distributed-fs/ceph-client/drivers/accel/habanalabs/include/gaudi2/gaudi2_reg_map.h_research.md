<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_reg_map.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_reg_map.h

## Purpose
Provides semantic aliases for Gaudi2 registers used as firmware/driver scratchpads, queue polling controls, boot status channels, reset status, watchdog GPIO registers, PID command registers, and ARM-to-management message registers.

## Important APIs, Types, And Functions
- `mmHW_STATE`, `mmPID_STATUS_REG`, `mmARM_STATUS_REG`, and `mmCPU_RST_STATUS_TO_HOST` abstract important status registers.
- `mmGIC_*_IRQ_CTRL_POLL_REG` aliases scratchpad registers for TPC, MME, DMA, ROT, NIC, DMA completion, PI update, halt, interrupt registration, and soft-reset polling.
- `mmENGINE_ARC_IRQ_CTRL_POLL_REG` is a shared scratchpad for ARC DCCM queue-full notification and is explicitly last-event-wins.
- `mmPID_CMD_*` aliases PID command request/response and telemetry registers.
- `mmWD_GPIO_*` aliases watchdog GPIO control.
- `mmARM_MSG_*` and `mmMGMT_MSG_*` define boot interface exchange registers between ARM and ARC1 management firmware.

## Control Flow
Gaudi2 initialization and firmware communication code uses these aliases rather than raw generated register names. Boot and reset paths read status aliases, interrupt routing code writes GIC polling aliases, PID command code exchanges request/response values, and ARM/MGMT boot paths pass boot error/device status through spare registers.

## State And Persistence Behavior
The aliases point to hardware scratchpad or control registers. State persists only in device registers across the relevant boot/reset phase. Some registers are cold-reset flops and can carry reset-source or pending-update information across reset boundaries.

## Dependencies And Integration Points
Depends on generated register definitions such as `mmPSOC_GLOBAL_CONF_SCRATCHPAD_*`, `mmPSOC_PID_PID_CMD_*`, `mmCPU_IF_SPECIAL_GLBL_SPARE_*`, and `mmCPU_MSTR_IF_SPECIAL_GLBL_SPARE_*`. Integrates with Gaudi2 firmware boot, CPUCP/PID commands, MSI/GIC event routing, watchdog handling, reset-source reporting, and telemetry.

## Risks And Edge Cases
Because aliases hide physical registers, a wrong alias can silently break host/firmware protocol. `mmENGINE_ARC_IRQ_CTRL_POLL_REG` intentionally overwrites prior unhandled events; code must tolerate event coalescing/loss there. Scratchpad allocation conflicts are a risk when adding new firmware features.

## Test Signals
Signals include firmware boot status transitions, PID command request/response success, interrupt polling registers matching expected CPU event IDs, watchdog GPIO behavior, reset-source visibility after reset, and boot error/status propagation between ARM and management firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_reg_map.h -->
