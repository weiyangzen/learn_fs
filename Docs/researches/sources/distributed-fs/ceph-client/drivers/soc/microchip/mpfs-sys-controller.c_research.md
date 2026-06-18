# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-sys-controller.c

## Purpose
Mailbox-backed PolarFire SoC system controller core. It provides blocking service transactions, optional bitstream flash access, consumer lifetime management, and registers platform subdevices for RNG, generic service, and auto-update features depending on compatible data.

## Important APIs, Types, And Functions
Exports `mpfs_blocking_transaction()`, `mpfs_sys_controller_get_flash()`, and `mpfs_sys_controller_get()`. Main private type is `struct mpfs_sys_controller` with mailbox client/channel, completion, optional `mtd_info`, and `kref` consumers. `struct mpfs_syscon_config` chooses subdevices for `microchip,mpfs-sys-controller` and `microchip,pic64gx-sys-controller`.

## Control Flow
Probe allocates the controller, optionally resolves `microchip,bitstream-flash` to an MTD device, configures a blocking mailbox client with a 30-second timeout, requests mailbox channel 0, initializes completion and kref, stores driver data, then registers configured subdevices with the controller as parent. The RX callback only completes the pending transaction.

`mpfs_blocking_transaction()` serializes all transactions with `transaction_lock`, reinitializes the completion, sends the mailbox message, and waits for a completion. Because hardware only interrupts on service success, send completion without RX completion is treated as `-EBADMSG` and callers inspect the message response status. Remove drops the controller reference, and final kref release frees the mailbox channel and memory.

`mpfs_sys_controller_get()` is used by subdevices. It validates the parent compatible, fetches parent drvdata, increments the kref unless zero, and attaches a devm cleanup action to put the reference.

## State And Persistence
Persistent external state includes system-controller firmware services, mailbox state, and optional MTD flash. Driver state is heap-allocated, reference-counted, and shared by subdevices. The global `transaction_lock` enforces one in-flight transaction across all instances.

## Dependencies And Integration Points
Depends on mailbox framework, `soc/microchip/mpfs.h` message ABI, MTD for bitstream flash, OF phandles, platform device registration, completions, and krefs. Subdevice names are consumed by Microchip RNG, generic service, and auto-update drivers.

## Risks
The global transaction mutex serializes all controller transactions and can become a bottleneck. Timeout behavior depends on mailbox send semantics and firmware status being written into `msg->response`. Probe error paths after successful mailbox channel acquisition and before devm ownership are limited; subdevice registration warns but does not fail the parent. `mpfs_sys_controller_get()` calls `of_node_put(dev->parent->of_node)` after `of_match_node()`, which is sensitive because it does not acquire that node locally.

## Test Signals
Expected signals are successful mailbox channel request, `Registered MPFS system controller`, working subdevice probes, correct `-EBADMSG` on failed services without RX completion, and stable kref behavior when subdrivers probe and remove.
