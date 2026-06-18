<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti_wilink_st.h -->
# sources/distributed-fs/ceph-client/include/linux/ti_wilink_st.h

## Purpose
declares the Texas Instruments WiLink shared-transport core API and internal data structures for multiplexing Bluetooth, FM, and GPS protocols over a shared UART/TTY link.

## Important APIs, Types, and Functions
The file is 440 lines and exports these visible symbol families: types/enums `proto_type`, `st_proto_s`, `st_data_s`, `chip_version`, `kim_data_s`, `bts_header`, `bts_action`, `bts_action_send`, `bts_action_wait`, `bts_action_delay`, `bts_action_serial`, `hci_command`, `fm_event_hdr`, `gps_event_hdr`, and 1 more; macros/constants `TI_WILINK_ST_H`, `ST_NOTEMPTY`, `ST_EMPTY`, `ST_INITIALIZING`, `ST_REG_IN_PROGRESS`, `ST_REG_PENDING`, `ST_WAITING_FOR_RESP`, `ST_TX_SENDING`, `ST_TX_WAKEUP`, `GPS_STUB_TEST`, `LDISC_TIME`, `CMD_RESP_TIME`, `CMD_WR_TIME`, `GPIO_HIGH`, and 24 more; function-like macros `MAKEWORD`; inline helpers none; external prototypes `char`, `st_register`, `st_unregister`, `st_get_uart_wr_room`, `st_int_write`, `st_write`, `st_ll_send_frame`, `st_tx_wakeup`, `st_core_init`, `st_core_exit`, `st_kim_ref`, `gps_chrdrv_stub_write`, `gps_chrdrv_stub_init`, `st_kim_start`, and 11 more.

## Control Flow
Protocol drivers register `st_proto_s` records with channel IDs and callbacks. KIM coordinates line-discipline installation, firmware script parsing, chip enable/disable, and protocol registration. ST core receives UART frames, reconstructs protocol skbs by channel/header length, queues TX skbs, and low-level PM code moves the chip between asleep/awake states.

## State and Persistence Behavior
`st_data_s` holds protocol tables, registered flags, RX/TX state machines, queues, lock, TTY pointer, PM state, and KIM backpointer. `kim_data_s` tracks completions, firmware entry, response buffer, UART settings, chip version, and line-discipline state. BTS action structs model firmware script records.

## Dependencies and Integration Points
It depends on skbuffs, tty/platform/firmware/completion/workqueue types supplied by implementation files, and integrates with TI BT/FM/GPS protocol drivers and board platform data. Direct includes are `linux/skbuff.h`.

## Risks and Edge Cases
UART framing and PM handshakes are race-prone. Length-field offsets, channel IDs, tx wakeups, firmware waits, and sleep/wake ACK ordering must match chip firmware. Platform GPIO and baud/flow-control callbacks are board-specific.

## Test Signals
Register/unregister each protocol, parse BTS firmware actions, simulate partial UART frames, stress TX queue wakeups, test sleep/wake LL state transitions, and validate firmware download plus BT/FM/GPS traffic on WiLink hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ti_wilink_st.h -->
