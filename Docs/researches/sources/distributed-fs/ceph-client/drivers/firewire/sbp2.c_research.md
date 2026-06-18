# sources/distributed-fs/ceph-client/drivers/firewire/sbp2.c

## Purpose
Implements the FireWire SBP-2 storage transport, exposing SCSI devices over IEEE 1394 logical units. The driver binds to SBP-2 unit directories, creates a `Scsi_Host` per FireWire target, logs into each SBP-2 LUN, translates SCSI commands into SBP-2 ORBs, and reconnects or blocks SCSI I/O across FireWire bus resets.

## APIs, Types, And Functions
Key state is split between `struct sbp2_target` for the FireWire unit/Scsi_Host and `struct sbp2_logical_unit` for each LUN. ORB lifetime is represented by `struct sbp2_orb`, with management and command specializations for login/logout/reconnect and SCSI I/O. Module parameters `exclusive_login` and `workarounds` alter multi-initiator behavior and device quirk handling.

The FireWire driver entry points are `sbp2_probe()`, `sbp2_update()`, and `sbp2_remove()` in `struct fw_driver`. SCSI integration is via `scsi_driver_template`: `sbp2_scsi_queuecommand()`, `sbp2_scsi_sdev_init()`, `sbp2_scsi_sdev_configure()`, and `sbp2_scsi_abort()`. FireWire status writes arrive through `sbp2_status_write()` registered as an address handler.

## Control Flow
Probe rejects local-node targets, allocates a `Scsi_Host`, enables physical DMA, parses the Config ROM for management-agent address, LUN entries, GUID/model/firmware metadata, clamps the management ORB timeout, applies workarounds, and queues delayed login work for every discovered LUN.

`sbp2_login()` sends a management login ORB, stores the command block agent address and login ID, programs `CSR_BUSY_TIMEOUT`, resets the SBP-2 agent, and creates a SCSI device. On later reconnects, `sbp2_reconnect()` issues `SBP2_RECONNECT_REQUEST`, refreshes node/generation information, resets the agent, cancels stale ORBs, and unblocks SCSI requests. `sbp2_update()` handles FireWire bus-reset updates by enabling DMA again, conditionally blocking stale LUNs, and queueing reconnect work.

SCSI commands allocate `struct sbp2_command_orb`, map scatter-gather data as either a direct descriptor or page table, DMA-map the command ORB, then write the ORB pointer to the target agent. Completion can come from the FireWire transaction callback or from a target status write; krefs cover both races. Status blocks are converted into SCSI result/sense data, DMA mappings are released, and `scsi_done()` completes the command.

## State, Persistence, And Dependencies
Runtime state includes login IDs, generation numbers, command block agent addresses, outstanding ORB lists, high-memory status FIFO handlers, DMA mappings, SCSI devices, and target block counters. There is no on-disk persistence; user-visible state is SCSI device presence and the `ieee1394_id` sysfs attribute. Dependencies include FireWire core transactions/address handlers, IEEE 1212 CSR parsing, DMA mapping, workqueues, and the SCSI mid-layer.

## Integration Points
The driver integrates with `fw_bus_type` through the SBP-2 IEEE 1394 ID table, with SCSI scanning/removal and error handling, with sysfs via `ieee1394_id`, and with initramfs compatibility through `MODULE_ALIAS("sbp2")`. Quirk flags affect SCSI inquiry length, mode-sense behavior, capacity correction, power-condition start/stop, and maximum transfer size.

## Risks And Test Signals
Major risks are ORB completion races, stale FireWire generation/node IDs during bus resets, DMA unmap correctness, leaked address handlers or SCSI devices on probe failures, and quirk regressions for old bridge firmware. Useful test signals are FireWire SBP-2 disk attach/remove, repeated bus resets during I/O, SCSI timeout/abort handling, multi-LUN devices, module parameter coverage, and sysfs `ieee1394_id` formatting. No in-file KUnit tests exist.
