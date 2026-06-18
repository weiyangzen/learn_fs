# sources/distributed-fs/ceph-client/drivers/tty/rpmsg_tty.c

## Purpose
Provides a tty frontend for RPMsg endpoints named `rpmsg-tty`, creating `/dev/ttyRPMSG<N>` devices so userspace can exchange RPMsg messages through standard tty read/write paths.

## Important APIs, types, and functions
- `struct rpmsg_tty_port` embeds `struct tty_port`, stores an IDR index, and points at the backing `struct rpmsg_device`.
- ID allocation is handled by global `tty_idr` under `idr_lock`.
- TTY operations are `rpmsg_tty_install()`, `rpmsg_tty_open()`, `rpmsg_tty_close()`, `rpmsg_tty_write()`, `rpmsg_tty_write_room()`, `rpmsg_tty_hangup()`, and `rpmsg_tty_cleanup()`.
- RPMsg integration is through `rpmsg_tty_probe()`, `rpmsg_tty_cb()`, `rpmsg_tty_remove()`, `rpmsg_driver_tty_id_table`, and `rpmsg_tty_rpmsg_drv`.
- Driver lifetime is `rpmsg_tty_init()`/`rpmsg_tty_exit()`.

## Control flow
Module init allocates a dynamic tty driver for up to 32 raw tty devices, disables canonical echo/output postprocessing by default, registers the tty driver, then registers the RPMsg driver. When a remote processor announces `rpmsg-tty`, probe allocates a port, assigns an ID, initializes the tty port with destructor operations, registers the tty device, stores `rpdev`, and binds the cport as device driver data.

RX runs from the RPMsg callback. Non-empty inbound payloads are copied into the tty flip buffer and pushed; truncation is reported with ratelimited logging. TX runs from tty `.write`: it queries RPMsg endpoint MTU, clips the tty write to one RPMsg message, and uses `rpmsg_trysend()` so tty writers are not indefinitely blocked by unavailable RPMsg buffers.

Removal hangs up users, unregisters the tty device, and drops the tty port reference. The port destructor removes the IDR entry and frees the allocation.

## State and persistence behavior
State is per live RPMsg channel: IDR slot, `tty_port` reference count, registered tty device, and `rpdev` pointer. There is no persistent state. The driver intentionally implements no hardware or software flow control; write capacity is the RPMsg MTU and backpressure is surfaced as short writes or `rpmsg_trysend()` errors.

## Dependencies and integration points
Depends on the RPMsg bus and endpoint MTU/send APIs, tty core/tty_port helpers, flip buffers, IDR, and module registration. Userspace observes dynamic `ttyRPMSG<N>` devices.

## Risks and edge cases
- `rpmsg_tty_install()` assumes `idr_find()` returns a live cport for the tty index; mismatched unregister/open races would be serious.
- RX truncation can occur if tty flip buffers are full; the driver logs but drops excess data.
- `rpmsg_trysend()` can return `-ENOMEM`, so callers must handle transient write failures.
- No flow control means high-throughput remote senders can overrun tty buffers.

## Test signals
Probe/remove with a remote endpoint named `rpmsg-tty`, creation of `ttyRPMSG<N>`, open/close/hangup behavior, RX payload delivery including zero-length rejection and truncation logging, MTU-limited writes, and retry behavior when RPMsg buffers are unavailable.
