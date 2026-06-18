<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2_priv.h

## Purpose
`sp2_priv.h` contains private state and register-bit definitions for the SP2 Common Interface driver. It is included by `sp2.c`, not intended as the board-facing API.

## Important APIs, Types, And Functions
`struct sp2` holds cached status, the bound I2C client, DVB adapter, embedded `dvb_ca_en50221` instance, current access mode, next status poll time, and the board callback/private context. Constants define module access spaces (`SP2_CI_ATTR_ACS`, `SP2_CI_IO_ACS`), read/write direction values, and module control bits including detection, access selects, TS input/output enable, and reset.

## Control Flow
The control-bit definitions drive `sp2_ci_op_cam()` access switching, `sp2_ci_slot_reset()` reset toggling, `sp2_ci_slot_ts_enable()` stream enabling, and `sp2_ci_poll_slot_status()` detect-bit interpretation.

## State And Persistence
The state object is allocated at I2C probe, attached to client data, used by CA callbacks through `en50221->data`, and freed at remove. Hardware state is represented by the module control register bits, while cached status and access type reduce polling and redundant register writes.

## Dependencies And Integration Points
It includes `sp2.h` and `media/dvb_frontend.h`, tying private state to both public SP2 config and DVB core types.

## Risks And Test Signals
Bit definitions are hardware contracts; wrong values can hold CAM reset, disable TS, or select the wrong CAM memory space. Test signals are correct transitions in register `0x00` during reset, access-space switching, detect status, and TS enable on a logic analyzer or via successful CAM operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/sp2_priv.h -->
