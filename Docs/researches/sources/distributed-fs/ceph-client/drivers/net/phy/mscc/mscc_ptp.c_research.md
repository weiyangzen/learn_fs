# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.c

Purpose: implements IEEE 1588/PTP hardware timestamping and PHC support for VSC8584-family PHYs. It configures the PHY's shared 1588 processor, ingress/egress analyzer engines, timestamp FIFO, local time counter, latency compensation, and kernel `mii_timestamper`/`ptp_clock_info` integration.

Important APIs and functions:
- `vsc8584_ptp_probe_once()` initializes package-shared GPIO locking; `vsc8584_ptp_probe()` allocates per-PHY PTP state, queues, GPIO handle, mii timestamper hooks, and registers the PHC.
- `vsc8584_ptp_init()` runs hardware initialization for supported PHY IDs through `__vsc8584_init_ptp()`.
- `vsc8584_ptp_deinit()` unregisters the PHC and purges RX/TX queues.
- `vsc8584_config_ts_intr()` enables timestamp FIFO interrupts; `vsc8584_handle_ts_interrupt()` acknowledges and dispatches FIFO-add and FIFO-overflow events.
- `vsc85xx_hwtstamp_set/get()`, `vsc85xx_txtstamp()`, `vsc85xx_rxtstamp()`, and `vsc85xx_ts_info()` are the kernel timestamping interface.
- `vsc85xx_adjfine()`, `vsc85xx_adjtime()`, `vsc85xx_gettime()`, and `vsc85xx_settime()` implement PHC operations.

Control flow: timestamp CSR access goes through `vsc85xx_ts_read_csr()` and `vsc85xx_ts_write_csr()`, which select the base PHY of a two-port 1588 processor and choose hardware block IDs for ingress, egress, or processor based on whether the current PHY is the base port. Probe sets `phydev->default_timestamp`, installs mii timestamp callbacks, and registers a PTP clock. Hardware init configures the 1588 input clock once for the base pair, disables predictors, selects the 250 MHz internal LTC clock, configures LTC sequence/error, delay FIFO depth, accuracy calibration, rewriter behavior, FIFO signature layout, interface control, latency compensation, analyzer split-flow mode, and default comparators for Ethernet/IP/PTP. HWTSTAMP set disables predictors, bypasses unused ingress/egress paths, resets FIFO, configures L2 or IPv4/UDP comparator chains, enables selected PTP flows, then re-enables predictors.

TX timestamping: `txtstamp` queues outgoing SKBs unless timestamping is disabled or one-step Sync should be rewritten in hardware. Egress FIFO interrupts call `vsc85xx_get_tx_ts()`, which reads FIFO entries, computes a 16-byte signature from the PTP sequence ID/domain/message type/destination MAC, matches queued SKBs, and completes hardware TX timestamps. FIFO overflow purges queued TX SKBs and resets the FIFO.

RX timestamping: ingress hardware writes a nanosecond value into the PTP reserved field. `rxtstamp` extracts the PTP header for L2 or IPv4/UDP mode, stores the nanoseconds in the SKB control block, queues the SKB, and schedules PHC auxiliary work. `vsc85xx_do_aux_work()` snapshots current PHC time, combines seconds with the embedded nanoseconds, handles second wrap, writes `skb_hwtstamps`, and reinjects the SKB through `netif_rx()`.

State and persistence: `struct vsc85xx_ptp` stores the registered PHC, the PHY pointer, TX queue, current TX type/RX filter, and configured flag. `struct vsc8531_private` stores `mii_timestamper`, `phc_lock`, `ts_lock`, `rx_skbs_list`, `load_save` GPIO, `input_clk_init`, and timestamp base address. The shared package state is the GPIO lock. Hardware retains LTC time, comparator configuration, FIFO contents, interrupt masks/status, analyzer mode, latency values, and predictor settings.

Dependencies and integration points: depends on phylib timestamping, `ptp_clock_kernel`, `ptp_classify`, GPIO descriptors, SKB queues, and register definitions from `mscc_ptp.h` and `mscc.h`. `mscc_main.c` calls probe/init/deinit/config interrupt handlers and link-change latency updates. MACsec affects latency tables and delay FIFO depth at compile time through `CONFIG_MACSEC`.

Risks and edge cases:
- CSR read/write polling loops count a small fixed number of BIU polls and do not propagate explicit timeout errors.
- RX timestamp reconstruction only carries nanoseconds in the packet and borrows seconds from current PHC time, so delayed processing near a second boundary is sensitive to the wrap heuristic.
- TX FIFO signature matching can discard SKBs whose PTP header cannot be parsed and can leave unmatched SKBs queued until later FIFO entries.
- Only PTP v2 L2 event and IPv4/UDP L4 event filters are supported; IPv6 and non-event filters return `-ERANGE`.
- `vsc8584_ptp_deinit()` assumes `vsc8531->ptp` exists on devices that install the remove hook.
- Shared load/save GPIO sequencing relies on every user honoring the package `gpio_lock`.

Test signals: use `ethtool -T`, `hwstamp_ctl`, `phc2sys`, and `ptp4l` in L2 and IPv4/UDP modes; validate one-step Sync rewriting and two-step FIFO completion; force FIFO overflow and verify queue purge; test link speed changes and latency reload; verify PHC get/set/adjfine/adjtime; test with and without MACsec compiled in; inspect IRQ handling for FIFO add with global PHY interrupt status equal to zero.
