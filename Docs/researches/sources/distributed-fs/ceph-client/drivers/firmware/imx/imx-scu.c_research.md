# sources/distributed-fs/ceph-client/drivers/firmware/imx/imx-scu.c

Purpose: Implements the core i.MX System Controller Unit mailbox RPC transport over MU channels.

Important APIs/types/functions: `imx_sc_ipc` stores channels, lock, completions, response buffer, and fast-IPC flag. Exports `imx_scu_get_handle()` and `imx_scu_call_rpc()`. Internal callbacks `imx_scu_tx_done()` and `imx_scu_rx_callback()` coordinate mailbox send/receive. `imx_scu_ipc_write()` sends RPC words sequentially.

Control flow: Probe detects fast IPC from mailbox controller compatible, requests TX/RX mailbox channels, initializes completions and mutex, publishes the global IPC handle, initializes SoC info and general IRQ channel, then populates child OF devices. RPC calls lock the IPC, install the message pointer, send all words, wait up to 3 seconds for response if requested, translate SCU error code in `hdr->func`, clear state, and unlock.

State and persistence behavior: Global `imx_sc_ipc_handle` represents the default SCU channel. Per-call transient state includes `msg`, `rx_size`, and `count`; these are protected by the mutex.

Dependencies and integration points: Depends on mailbox framework, SCU firmware RPC headers, OF platform population, SoC init helper, IRQ helper, and downstream SCU service helpers (`misc.c`, `rm.c`).

Risks and test signals: RX before `msg` is set is ignored; timeouts must leave state consistent. Fast IPC receives all words in one callback; non-fast IPC relies on per-word channel ordering enforced by completions. Test normal RPCs, timeouts, firmware error mapping, fast/non-fast controllers, probe deferral, and child device population.
