# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_ace.c

## Purpose
`mei_ace.c` is the Intel IVSC ACE MEI client driver. It sends firmware IPC commands to get the ACE firmware id and switch camera sensor ownership between IVSC firmware and the host CPU. It also links runtime PM with the IVSC CSI MEI device and clears ACPI dependencies after switching ownership to the host.

## Important APIs, Types, And Functions
The file defines ACE command/notification bitfield structures, command IDs (`ACE_GET_FW_ID`, switch to host/IVSC), event types, and `struct mei_ace`. Key functions are `construct_command()`, `mei_ace_send()`, `ace_set_camera_owner()`, `ace_get_firmware_id()`, `mei_ace_rx()`, `mei_ace_setup_dev_link()`, `mei_ace_post_probe_work()`, probe/remove, and runtime suspend/resume.

## Control Flow
Probe allocates state, enables the MEI client, registers the receive callback, sends `ACE_GET_FW_ID`, enables runtime PM, finds the sibling CSI MEI client by UUID-derived child name, creates a PM runtime device link, and schedules work. The work switches camera ownership to the host and clears ACPI dependencies so sensor devices can probe.

`mei_ace_send()` serializes commands with a mutex and one completion. It waits first for an ACK, validates command id/status, and for ownership commands waits for a second command response. RX distinguishes ACK notifications from events, stores ACK/response data, updates firmware id on `GET_FW_ID`, and completes waiters.

Runtime suspend switches the camera back to IVSC; runtime resume switches it to host. Remove cancels work, drops the device link, disables PM, switches to IVSC, disables MEI, and destroys the mutex.

## State And Persistence
State is per MEI client: firmware id, latest ACK/response, completion, mutex, CSI device/link, and post-probe work. Sensor ownership is hardware/firmware state, not persistent storage.

## Dependencies And Integration Points
The driver depends on MEI client bus, ACPI, runtime PM, workqueues, and the IVSC CSI sibling UUID. It coordinates with camera sensor ACPI dependencies and with the CSI driver through a PM runtime device link.

## Risks And Test Signals
`mei_ace_setup_dev_link()` stores `ace->csi_dev = csi_dev` after `put_device(csi_dev)`, but the stored pointer is not later dereferenced except link deletion; still, pointer lifetime should be reviewed if future code uses it. Command ACK/response matching relies on one outstanding command. Tests should cover firmware timeout, killable waits, bad ACK command id/status, missing CSI sibling/fwnode deferral, runtime PM ownership flips, remove while work is pending, and sensor probe sequencing.
