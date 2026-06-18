# sources/distributed-fs/ceph-client/drivers/hsi/clients/ssi_protocol.c

## Purpose
Implements the SSI McSAAB protocol as an HSI client driver and exposes it as a Phonet point-to-point net_device named `phonet%d`. It translates Phonet sk_buffs into HSI data-channel messages, drives a command-channel handshake with the modem/CMT, and provides exported helpers for sibling HSI slave clients that need to coordinate use of the shared SSI wake line.

## Important APIs, Types, and Functions
- `struct ssi_protocol` is the main per-client state object. It tracks `main_state`, `send_state`, `recv_state`, TX/RX message IDs, watchdog timers, keep-alive timer, command/data HSI channel IDs, command pool, TX queue, and Phonet netdev.
- Exported helpers: `ssip_slave_get_master()`, `ssip_slave_start_tx()`, `ssip_slave_stop_tx()`, `ssip_slave_running()`, and `ssip_reset_event()`.
- Netdev operations: `ssip_pn_open()`, `ssip_pn_stop()`, `ssip_pn_xmit()`.
- HSI callbacks: `ssip_rxcmd_complete()`, `ssip_rx_data_complete()`, `ssip_tx_data_complete()`, `ssip_swbreak_complete()`, and `ssip_port_event()`.

## Control Flow
Probe allocates `struct ssi_protocol`, resolves `mcsaab-control` and `mcsaab-data` channel IDs, preallocates command messages, registers a Phonet netdev, and links the instance on `ssip_list`. Opening the netdev claims the HSI port shared, registers wake-line event handling, configures the port, starts a wake test, enters `HANDSHAKE`, sends `BOOTINFO_REQ`, and posts a command read. Command completions re-arm the command read before dispatching command IDs. Handshake moves through boot-info request/response and `WAKETEST_RESULT`; a successful wake test marks `ACTIVE`, enables carrier, and wakes the TX queue. TX queues Phonet packets as HSI data messages, raises wake with `hsi_start_tx()`, waits for `READY`, sends `START_TRANS`, writes data, then sends `SWBREAK` before returning to idle or ready. RX wake events send `READY`; `START_TRANS` allocates an skb and reads the data payload, then injects it into the Phonet stack.

## State and Persistence
State is in memory only: lists, timers, atomics, message IDs, and carrier state. There is no persistent storage. `ssip_reset()` flushes HSI transfers, stops wake usage, cancels timers/work, clears state, and frees queued TX messages. Command messages are pooled and recycled through destructors.

## Dependencies and Integration Points
Depends on the HSI core API (`hsi_claim_port`, `hsi_async_read/write`, `hsi_start_tx`, `hsi_stop_tx`, events), OMAP SSI's exported `ssi_waketest()` workaround, Linux netdev/Phonet APIs, sk_buff scatter-gather helpers, timers, workqueues, and spinlocks.

## Risks and Test Signals
Key risks are async completion ordering, watchdog reset during callbacks, command-pool exhaustion if destructors are bypassed, wake-line reference imbalance through slave helper users, and assumptions about host/modem endianness. Test signals include Phonet netdev registration, successful boot/wake-test transition to carrier on, TX queue stop/wake behavior near `SSIP_TXQUEUE_LEN`, watchdog-triggered reset recovery, RX/TX ID mismatch handling, and module unload after active traffic.
