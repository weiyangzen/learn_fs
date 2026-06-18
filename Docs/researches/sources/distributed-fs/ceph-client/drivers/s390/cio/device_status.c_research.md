# sources/distributed-fs/ceph-client/drivers/s390/cio/device_status.c

Purpose: accumulates interruption-response-block status for CCW command-mode I/O and starts/finalizes basic sense when concurrent sense data is absent.

Important APIs/types/functions: public helpers are `ccw_device_accumulate_irb()`, `ccw_device_do_sense()`, `ccw_device_accumulate_basic_sense()`, and `ccw_device_accumulate_and_sense()`. Internal helpers copy ECW/ESW fields, validate ESW presence, detect control checks, and handle path-not-operational bits.

Control flow: `ccw_device_accumulate_irb()` ignores IRBs without status pending, logs channel/interface checks, updates path masks when PNO is present, copies transport-mode IRBs wholesale, and otherwise accumulates solicited command-mode SCSW/ESW/ECW fields into the device DMA IRB. Unit check without concurrent sense sets `flags.dosense`. `ccw_device_do_sense()` starts the static SENSE CCW only after device/subchannel activity has ended. W4SENSE completion copies sense information and clears delayed-sense state.

State and persistence behavior: state is accumulated in `cdev->private->dma_area->irb`, `flags.dosense`, `flags.doverify`, and `sch->lpm`. It reflects pending runtime I/O status only and is cleared by the FSM after handler delivery.

Dependencies and integration points: used by `device_fsm.c` online and W4SENSE interrupt handling, by internal request handling, and by CIO low-level start. Depends on SCSW/ESW architecture helpers, `to_io_private(sch)->dma_area->sense_ccw`, and path verification event routing.

Risks and test signals: status validity rules are subtle; copying invalid ESW/ECW fields can mislead drivers. Sense start during active I/O must return busy. Tests should cover command versus transport IRBs, clear-function reset of accumulated status, PNO-triggered verification, unit check with concurrent sense, unit check needing basic sense, activity-pending sense deferral, and channel-control-check logging.
