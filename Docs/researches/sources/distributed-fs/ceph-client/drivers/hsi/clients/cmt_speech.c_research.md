# sources/distributed-fs/ceph-client/drivers/hsi/clients/cmt_speech.c

## Purpose
`cmt_speech.c` implements the Nokia CMT speech HSI client. It exposes a single misc character device, `/dev/cmt_speech`, that lets userspace exchange control commands and shared-memory audio/data buffers with a modem over two HSI channels named `speech-control` and `speech-data`. It is layered on top of the SSI protocol slave helpers and uses an mmap page as the userspace/kernel control block plus RX/TX ring buffer area.

## Important APIs, Types, and Functions
- `struct cs_char` is the global character device state: open flag, HSI client pointer, active `cs_hsi_iface`, notification queues, mmap page, async queue, wait queue, and command/data HSI channel IDs.
- `struct cs_hsi_iface` is the active HSI session: HSI client/master pointers, interface/control/data states, mmap config pointer, buffer sizes and offsets, current RX/TX slots, preallocated command/data messages, data wait queue, PM QoS request, and lock.
- Queue helpers `cs_notify()`, `cs_notify_control()`, `cs_notify_data()`, and `cs_pop_entry()` deliver u32 notifications to blocking reads, poll, and fasync.
- Command message helpers `cs_alloc_cmds()`, `cs_claim_cmd()`, `cs_release_cmd()`, `cs_free_cmds()`, and `cs_cmd_destructor()` maintain a pool of four control messages.
- HSI control path: `cs_hsi_read_on_control()`, `cs_hsi_peek_on_control_complete()`, `cs_hsi_read_on_control_complete()`, `cs_hsi_write_on_control()`, and `cs_hsi_write_on_control_complete()`.
- HSI data path: `cs_hsi_read_on_data()`, `cs_hsi_peek_on_data_complete()`, `cs_hsi_read_on_data_complete()`, `cs_hsi_write_on_data()`, and `cs_hsi_write_on_data_complete()`.
- Buffer/session management: `cs_hsi_buf_config()`, `check_buf_params()`, `set_buffer_sizes()`, `cs_hsi_data_enable()`, `cs_hsi_data_disable()`, `cs_hsi_data_sync()`, `cs_hsi_start()`, and `cs_hsi_stop()`.
- Character device operations: `cs_char_open()`, `cs_char_release()`, `cs_char_read()`, `cs_char_write()`, `cs_char_poll()`, `cs_char_ioctl()`, `cs_char_mmap()`, and `cs_char_fasync()`.
- Driver entry points: `cs_hsi_client_probe()`, `cs_hsi_client_remove()`, `cs_char_init()`, and `cs_char_exit()`.

## Control Flow
Probe initializes global `cs_char_data`, resolves HSI channel IDs by name, and registers the misc device. `open()` is exclusive: it allocates one zeroed page, starts the HSI session, claims the HSI port, gets the SSI master client, verifies it is running, and starts a pending control read. Userspace then `mmap()`s the one-page shared area, configures buffers with `CS_CONFIG_BUFS`, uses `write()` to send u32 commands, and reads u32 notifications.

Control reads use a zero-length "peek" async read first, then a real one-word read. Completion releases the command message back to the pool, optionally timestamps RX control messages, enqueues a notification, and immediately re-arms the control read. Control writes are serialized by `SSI_CHANNEL_STATE_WRITING`; the command target bits decide whether a userspace write goes to remote control or local TX-data handling.

Data reads also use a peek read followed by a read into the current RX slot inside the mmap page. On completion, the driver increments `rx_slot`, updates `mmap_cfg->rx_ptr`, wakes data waiters, enqueues `CS_RX_DATA_RECEIVED | slot`, and re-arms reads. Data writes use a TX slot selected by the low command parameter and write `buf_size` bytes from the mmap page.

`CS_CONFIG_BUFS` temporarily moves a configured interface back to opened state, waits for active transfers to finish or time out, validates buffer counts and total mmap size, lays out cache-aligned RX/TX slots after the config block, and starts/stops data reads and CPU latency QoS depending on configured state.

## State and Persistence
State is global and single-open. The misc device only permits one active session via `cs_char_data.opened`. Runtime state includes list-backed control and data notification queues, `dataind_pending`, HSI state bitmasks, mmap config contents visible to userspace, precomputed RX/TX offsets, current slots, wake line state, and PM QoS request. Nothing persists after close; `release()` stops HSI, frees the page, clears queues, and resets `opened`.

## Dependencies and Integration Points
The driver depends on HSI core APIs (`hsi_claim_port`, `hsi_async_read/write`, `hsi_release_port`, `hsi_get_channel_id_by_name`), SSI protocol slave APIs (`ssip_slave_get_master`, `ssip_slave_running`, `ssip_slave_start_tx`, `ssip_slave_stop_tx`, `ssip_slave_put_master`), CMT speech UAPI definitions from `linux/hsi/cs-protocol.h`, miscdevice, mmap VM operations, wait queues, fasync, spinlocks, and CPU latency QoS. It binds as an HSI client named `cmt-speech` with module alias `hsi:cmt-speech`.

## Risks and Edge Cases
- `cs_char_data` is a single global, so multiple CMT speech HSI clients would collide.
- The mmap area is only one page; buffer validation must remain correct or userspace-selected sizes can overlap the config block or exceed the page.
- HSI callbacks and file operations share state under spinlocks and bottom-half disabling; destructor/error paths must release message ownership exactly once.
- `cs_hsi_write_on_control()` returns 0 even after an immediate async write submission error path has called the error handler, which may hide errors from userspace.
- Data reconfiguration depends on `cs_hsi_data_sync()` timing out after 500 ms; slow or stuck controllers can force `-EIO`.
- Notification queue overrun handling drops oldest data indications beyond RX buffer count, so userspace must keep up with reads.

## Test Signals
- Module load should register `/dev/cmt_speech` after the HSI child named `cmt-speech` probes and finds both named channels.
- ABI tests should cover exclusive open, one-page mmap, `CS_GET_STATE`, `CS_GET_IF_VERSION`, `CS_SET_WAKELINE`, `CS_CONFIG_BUFS`, blocking/nonblocking read, poll, fasync, and write command routing.
- HSI tests should verify control read re-arming, remote command writes, data RX slot advancement, TX slot writes, PM QoS activation only while configured, and clean close after pending transfers.
- Fault tests should cover missing channel names, missing SSI master, async read/write errors, signal interruption, buffer overrun, and remove while open.
