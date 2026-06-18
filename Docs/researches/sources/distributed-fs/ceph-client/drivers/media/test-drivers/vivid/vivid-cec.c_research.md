# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.c

## Purpose
`vivid-cec.c` emulates HDMI CEC adapters and a shared CEC bus for VIVID HDMI inputs/outputs.

## Important APIs, types, and functions
`vivid_cec_alloc_adap()` creates a CEC adapter with monitor capabilities and VIVID CEC ops. `vivid_cec_bus_thread()` is the kernel thread that models signal-free-time readiness, bus arbitration, ACK/NACK status, timing delays, transmit completion, and delivery to destination adapters. `vivid_cec_adap_transmit()` queues a pending transfer in the receiver-side device's `xfers[]` slot indexed by initiator. `find_dest_adap()` checks whether a destination logical address exists on the local HDMI input adapter or on connected HDMI output adapters. `vivid_received()` implements test responses for `CEC_MSG_SET_OSD_STRING` and `CEC_MSG_VENDOR_COMMAND_WITH_ID`.

## Control flow
CEC adapters call `adap_transmit`, which records message bytes, length, adapter, and desired signal-free time under `cec_xfers_slock`, then wakes the bus thread. The thread selects ready transfers, marks simultaneous losers as arbitration lost, checks destination validity, sleeps to emulate bus time, calls `cec_transmit_attempt_done()`, and delivers successful messages via `cec_received_msg()` to all relevant virtual adapters except the sender.

## State and persistence
CEC state lives in `struct vivid_dev`: receive/transmit adapters, `xfers[]`, signal-free time, last initiator, waitqueue, and OSD text. OSD text may persist until cleared or replaced depending on the CEC display-control value.

## Dependencies and integration points
The file depends on the kernel CEC framework, VIVID connection maps from `vivid-core.h`, HDMI-to-output menu state, and the VIVID core thread lifecycle. It is compiled only when `CONFIG_VIDEO_VIVID_CEC` is enabled.

## Risks and test signals
Risks include simplified arbitration that uses initiator-level rather than bit-level precision, one pending transfer per initiator slot, connection-map races if topology changes, and incorrect timing under scheduler delays. Test signals include CEC compliance tests, successful OSD string handling on sink adapters, vendor-command reply behavior, expected arbitration-lost statuses, and NACKs for unconfigured destinations.
