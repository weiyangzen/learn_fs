# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpts.c

## Purpose
Implements the TI K3 AM65 Common Platform Time Sync driver. It provides a PTP hardware clock, timestamp FIFO handling, RX/TX PTP packet timestamp matching, external timestamp and periodic output support, PPS generation, ESTF outputs for TAPRIO schedules, refclk mux setup, platform probe, and suspend/resume context save/restore.

## Important APIs, Types, and Functions
Exported APIs are `am65_cpts_create`, `am65_cpts_release`, `am65_cpts_phc_index`, `am65_cpts_rx_timestamp`, `am65_cpts_tx_timestamp`, `am65_cpts_prep_tx_timestamp`, `am65_cpts_ns_gettime`, `am65_cpts_estf_enable`, `am65_cpts_estf_disable`, `am65_cpts_suspend`, and `am65_cpts_resume`. Key internal types are register-layout structs `am65_cpts_regs` and `am65_genf_regs`, `struct am65_cpts_event`, `struct am65_cpts`, and skb control block `am65_cpts_skb_cb_data`. The PTP ops are in `am65_ptp_info`.

## Control Flow
Creation allocates state, obtains the `cpts` IRQ, parses DT for external timestamp inputs, periodic outputs, PPS indexes, and optional refclk mux, initializes event pools/lists/locks/txq, gets and enables the refclk, configures add value and control/int registers, initializes PHC time to realtime, registers the PTP clock, and requests a threaded IRQ. Interrupts and explicit reads drain the hardware event FIFO into a small software pool, classifying events as push, RX, TX, hardware timestamp, host, rollover, half rollover, or compare. RX/TX events are queued with timeouts; hardware events are emitted to the PTP core as EXTS or PPS events.

PTP gettime temporarily disables interrupts, triggers a timestamp push, records system pre/post timestamps, drains FIFO, then re-enables interrupts. Adjfine computes PPM adjustment periods from scaled ppm and refclk, updates CPTS and active GenF/ESTF compensation registers under mutex plus spinlock. RX timestamping parses the skb PTP header before `eth_type_trans`, adds port and RX event bits, searches queued RX events, and writes skb hwtstamp. TX preparation parses PTP metadata and marks `SKBTX_IN_PROGRESS`; TX completion queues a referenced skb; auxiliary work matches queued TX events against skbs by message type/sequence/port or expires them.

## State and Persistence
Persistent software state includes PHC registration, refclk frequency/add value, event pool and TX/RX event lists, skb TX timestamp queue, ext-ts/genf/pps/estf enable bitmaps, last pushed timestamp, and saved suspend context. Persistent hardware state includes CPTS control, interrupt enable, refclk select, PPM registers, GenF/ESTF compare/length/control/PPM registers, and timestamp counter value. Suspend saves control, interrupt, refclk, ppm, current CPTS time plus realtime anchor, and GenF/ESTF register blocks, then disables CPTS/refclk. Resume restores clock selection, add value, controls, time advanced by suspend duration, PPM, and GenF/ESTF blocks using the documented length-zero sequence.

## Dependencies and Integration Points
Depends on Linux PTP clock APIs, PTP packet parsing/classification, net timestamping, IRQ/platform/OF/clk APIs, clock provider mux registration, PM runtime consumers, skbuff queues, and kernel timekeeping. It integrates with `am65-cpsw-nuss.c` for hwtstamp get/set, RX/TX timestamp hooks, PHC index, and PM; with `am65-cpsw-qos.c` for ESTF periodic outputs; and can also probe standalone as `ti,am65-cpts`/`ti,j721e-cpts`.

## Risks and Test Signals
Risks include FIFO pool exhaustion, timestamp event/skb matching ambiguity, event timeout tuning, lock ordering between FIFO spinlock, txq lock, and PTP mutex, PHC adjfine divide-by-zero style edge cases for zero ppb, PPS index validation, refclk mux lifetime, double clock disable on failed create/release paths, and context drift across suspend. Test signals include PHC registration and `phc_ctl`, `ptp4l`/`phc2sys`, hardware TX/RX timestamp accuracy, PPS/EXTTS/PEROUT requests, TAPRIO ESTF enable/disable, high timestamp load to stress FIFO pool, suspend/resume with active PHC, and IRQ/error-path injection.
