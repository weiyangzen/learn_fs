# sources/distributed-fs/ceph-client/drivers/hsi/clients/hsi_char.c

## Purpose
`hsi_char.c` implements a generic HSI/SSI character driver. For each bound HSI client, it registers 16 character-device minors, one per HSI channel, and lets userspace perform aligned blocking reads/writes, configure RX/TX HSI parameters, send/receive break frames, and control the wake line.

## Important APIs, Types, and Functions
- Constants: `HSC_DEVS` is 16 channels; `HSC_MSGS` preallocates four messages per opened channel; `max_data_size` module parameter bounds transfer size and must be a power of two from 4 to 65536.
- Minor layout: `HSC_BASEMINOR(id, port_id)` packs HSI controller and port IDs into the base minor; low 4 bits select channel.
- `struct hsc_channel` stores per-channel flags, free/RX/TX message queues, spinlock, HSI client pointer, parent client data, and read/write wait queues.
- `struct hsc_client_data` stores the cdev, open/close mutex, port flags, port use count, HSI client pointer, and all 16 channels.
- Message lifecycle helpers: `hsc_msg_alloc()`, `hsc_msgs_alloc()`, `hsc_msg_free()`, `hsc_free_list()`, `hsc_reset_list()`, `hsc_add_tail()`, and `hsc_get_first_msg()`.
- Completion/destructor callbacks: `hsc_rx_completed()`, `hsc_rx_msg_destructor()`, `hsc_tx_completed()`, `hsc_tx_msg_destructor()`, `hsc_break_received()`, and `hsc_break_req_destructor()`.
- HSI configuration helpers: `hsc_rx_set()`, `hsc_rx_get()`, `hsc_tx_set()`, `hsc_tx_get()`, `hsc_break_request()`, and `hsc_break_send()`.
- File operations: `hsc_open()`, `hsc_release()`, `hsc_read()`, `hsc_write()`, and `hsc_ioctl()`.
- Driver entry points: `hsc_probe()`, `hsc_remove()`, `hsc_init()`, and `hsc_exit()`.

## Control Flow
Module init validates `max_data_size` and registers the HSI client driver named `hsi_char`. Probe allocates `hsc_client_data`, allocates a char-device region for 16 minors based on HSI ID and port ID, initializes channels, and adds a cdev spanning all channels.

Opening a minor selects the channel from the low minor bits, serializes with the parent mutex, enforces exclusive open per channel, claims and sets up the HSI port on first open, increments a use count, and preallocates four scatterlist-backed HSI messages. Reads and writes each allow only one in-flight operation per channel using `HSC_CH_READ`/`HSC_CH_WRITE`. A read takes a free message, sets length and callbacks, submits `hsi_async_read()`, waits for completion queue, copies data to userspace, and returns the message to the free list. A write copies userspace data into a free message, submits `hsi_async_write()`, waits for TX completion, and recycles the message.

`HSC_SET_RX` and `HSC_SET_TX` ioctls validate mode/channel/flow/arbitration values, update the HSI client config, call `hsi_setup()`, and roll back on setup failure. RX frame mode arms break detection. `HSC_SEND_BREAK` sends a break frame. `HSC_SET_PM` starts or stops TX using `hsi_start_tx()` / `hsi_stop_tx()` and tracks wake-line state with `HSC_CH_WLINE`.

Release stops TX if enabled, decrements the port use count, flushes/releases the HSI port on last close, frees all pending/free messages, clears flags, and wakes wait queues.

## State and Persistence
State is per bound HSI client and per opened channel. The major number is global and allocated on first probe. Each channel tracks open/read/write/wake-line bits and list-backed free/RX/TX message pools. The parent use count keeps the HSI port claimed while any channel is open. No state persists after module unload or device removal.

## Dependencies and Integration Points
The driver depends on HSI core async I/O, HSI config structures, the `linux/hsi/hsi_char.h` ioctl ABI, cdev/chrdev registration, wait queues, spinlocks, mutexes, scatterlists, and uaccess. It binds to HSI clients named `hsi_char` through `MODULE_ALIAS("hsi:hsi_char")`.

## Risks and Edge Cases
- Probe/remove do not appear to prevent removal while channels are open; cdev deletion with live file references needs careful lifetime assumptions.
- Blocking reads/writes flush the whole HSI client on signal interruption, which may disrupt other open channels sharing the same port.
- `hsi_flush()` is per client/port rather than per channel, so reset and break handling can affect all channels.
- The global major allocation plus per-port minor packing supports only masked ID/port ranges; IDs beyond the masks collide.
- Reads/writes silently clamp length to `max_data_size`; userspace may need to infer short transfer limits.
- All transfers require 32-bit alignment; unaligned userspace sizes return `-EINVAL`.

## Test Signals
- Module parameter validation should reject non-power-of-two, too-small, and too-large `max_data_size`.
- Device-node tests should verify 16 minors per HSI client and correct channel selection from minor number.
- Functional tests should cover aligned read/write, simultaneous channel opens, exclusive same-channel open, signal interruption, break receive broadcast, `HSC_RESET`, PM wake-line toggling, and RX/TX config rollback on `hsi_setup()` failure.
- Stress tests should exercise message pool exhaustion, port use counting across multiple channels, and controller removal during blocked I/O.
