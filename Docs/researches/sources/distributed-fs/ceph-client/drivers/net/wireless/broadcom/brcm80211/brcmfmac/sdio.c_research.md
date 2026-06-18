# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/sdio.c

## Purpose
`sdio.c` is the main SDIO bus backend for `brcmfmac`. It initializes SDIO chips, downloads firmware/NVRAM/CLM, implements SDPCM framing over function 2, manages interrupts and deferred processing, handles control/data TX/RX, glomming, flow control, clock and sleep state, watchdog polling, debug forensics, reset/remove, and integration with the BCDC protocol.

## Important APIs, types, and functions
- `struct brcmf_sdio` is the central runtime state: SDIO device pointer, chip/core metadata, interrupt masks/status atomics, TX queue and flow control, SDPCM sequence/window state, RX header/control buffers, glom queues, clock/sleep state, control-frame wait queues, watchdog timer/thread, ordered workqueue, counters, SR state, and alignment/glomming configuration.
- `struct brcmf_sdio_count` holds debug counters for interrupts, polling, register failures, TX/RX errors, flow control, glomming, frame transfers, control frames, and readahead.
- SDPCM helpers `brcmf_sdio_hdparse()`, `brcmf_sdio_hdpack()`, `brcmf_sdio_update_hwhdr()`, and `brcmf_sdio_getdatoffset()` parse and construct the hardware/software packet headers.
- RX path: `brcmf_sdio_dpc()` -> `brcmf_sdio_readframes()` -> `brcmf_sdio_read_control()`, `brcmf_sdio_rxglom()`, `brcmf_rx_event()`, or `brcmf_rx_frame()`.
- TX path: `brcmf_sdio_bus_txdata()` enqueues priority packets; `brcmf_sdio_sendfromq()` dequeues under firmware window/flow-control limits; `brcmf_sdio_txpkt()` prepares headers/alignment and calls `brcmf_sdiod_send_pkt()`; `brcmf_sdio_bus_txctl()` sends synchronous control frames via the DPC.
- Clock/power helpers include `brcmf_sdio_kso_control()`, `brcmf_sdio_htclk()`, `brcmf_sdio_clkctl()`, `brcmf_sdio_bus_sleep()`, `brcmf_sdio_sr_init()`, `brcmf_sdio_sleep()`, and watchdog timer helpers.
- Probe/setup functions include `brcmf_sdio_probe()`, `brcmf_sdio_probe_attach()`, `brcmf_sdio_prepare_fw_request()`, `brcmf_sdio_firmware_callback()`, `brcmf_sdio_bus_preinit()`, and `brcmf_sdio_remove()`.
- Bus integration is through `brcmf_sdio_bus_ops`, which supplies stop, preinit, tx/rx control, tx data, tx queue lookup, WoWL, RAM size/memdump, blob retrieval, debugfs, reset, and remove hooks.

## Control flow
`brcmf_sdio_probe()` allocates `struct brcmf_sdio`, creates an ordered high-priority workqueue, attaches chip/core state, sets alignments and drive strength, prepares queues/buffers/wait queues/watchdog, disables function 2 to clear stale device state, initializes clock state, then requests firmware. The firmware callback downloads firmware and NVRAM, starts the ARM core, enables the watchdog, forces clocks, enables function 2, programs host interrupt mask and chip-specific watermarks, optionally enables SaveRestore/KSO behavior, registers interrupts, marks the SDIO device data-ready, then calls `brcmf_alloc()` and `brcmf_attach()`.

Runtime interrupts call `brcmf_sdio_isr()`, which records pending interrupt state and queues `brcmf_sdio_dataworker()`. The worker loops while `dpc_triggered` is set, calling `brcmf_sdio_dpc()`. DPC wakes the bus, reads and acknowledges interrupt status, handles mailbox data such as firmware ready, flow-control, NAK completion, and firmware halt, processes RX frame indications, transmits pending control frames, drains data TX queue within firmware credit windows, and reschedules itself if more work remains.

RX reads parse SDPCM headers, validate checksum/length/channel/offset/sequence/window fields, update firmware TX window and flow-control bits, and dispatch control frames to the dcmd response waiter or data/event frames upward. Glom descriptor frames allocate a packet chain, read the superframe, validate each subframe, then deliver each subpacket. RX failures may abort function 2, terminate frames, and optionally NAK to request event/control retransmission.

TX data pushes SDPCM header room, maps skb priority to a precedence queue, applies high/low water flow blocking to the protocol layer, and triggers DPC. DPC dequeues packets not blocked by firmware flow-control bits, supports optional TX glomming with scatter-gather alignment and tail padding, sends via SDIO CMD53, updates sequence numbers, postprocesses skbs back to their original layout, and completes them to BCDC.

## State and persistence behavior
All runtime state is volatile and tied to the SDIO device lifetime. Firmware/NVRAM are loaded into dongle RAM during setup; CLM firmware is retained in `sdiodev->clm_fw` until the common layer asks for it via `get_blob`. TX/RX sequence numbers, flow-control masks, firmware credit window, glom descriptors, control response buffers, counters, and clock/sleep state persist across runtime operations but are reset on bus stop/remove. The watchdog timer and thread periodically poll interrupts, firmware console output in debug builds, idle clock transitions, and freezer state.

The driver also mutates device-side persistent-for-session state: CCCR card control, function 1 misc registers, SB address windows, PMU drive strength, F2 watermarks, host interrupt masks, mailbox data, firmware RAM, NVRAM placement, and SaveRestore/KSO registers.

## Dependencies and integration points
The file depends on Linux MMC/SDIO APIs, firmware loading, kthreads, workqueues, timers, debugfs, Broadcom chipcore and firmware helpers, `brcmf_sdiod_*` low-level SDIO accessors from other files, `bcdc.h`, `bus.h`, `core.h`, `common.h`, `tracepoint.h`, and protocol/common attach functions. It integrates upward as a `brcmf_bus_ops` provider for BCDC and downward through SDIO function 0/1/2 register and buffer transfers.

## Risks and edge cases
- SDPCM header parsing is a major trust boundary. Length checksum, data offset, channel, next-frame length, and sequence checks protect against desynchronization, but bad firmware/device data still drives abort/NAK behavior.
- Control TX/RX is wait-queue based with timeouts; missed wakeups, stale `rxctl`, or DPC halt can surface as dcmd timeouts.
- Glomming is allocation- and alignment-heavy. Descriptor length errors, SG entry misalignment, or partial read failures require careful cleanup of queued skbs.
- Clock/KSO/SR transitions are timing-sensitive and chip-specific, including special CY43012 behavior when clearing KSO.
- The DPC uses atomics plus an ordered workqueue; correctness depends on careful setting/clearing of `dpc_triggered`, `intstatus`, `ipend`, and `fcstate`.
- `brcmf_sdio_bus_txdata()` pushes header room before enqueue and must pull it back on enqueue failure; later TX postprocessing must restore skb shape after padding/glomming.
- Firmware callback failure releases both SDIO function drivers, so partial setup paths must avoid leaked IRQs, workqueues, firmware, buffers, or clocks.
- Probe has many chip-specific watermarks and drive-strength settings; regressions may be device-ID specific.

## Test signals
Useful signals include successful SDIO probe, firmware/NVRAM download and optional verify, F2 enable, interrupt registration, `Dongle ready` mailbox, `brcmf_attach()` success, stable TX/RX under flow control, dcmd round trips, glommed and non-glommed RX, watchdog idle sleep/wake, WoWL/sleep behavior, memdump and CLM blob handoff, debugfs counters/forensics, firmware halt handling, injected CMD52/CMD53 failures, malformed SDPCM headers, control timeout, and remove/reset under active traffic.
