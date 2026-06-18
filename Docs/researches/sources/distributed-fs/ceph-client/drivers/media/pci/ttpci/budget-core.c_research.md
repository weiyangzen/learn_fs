
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-core.c

## Purpose
This is the common SAA7146 "budget" DVB support layer used by board-specific TT/Hauppauge/Siemens budget drivers. It allocates the transport-stream DMA buffer, registers the DVB adapter/demux/dmxdev/network frontend plumbing, drives SAA7146 DMA3 capture, dispatches received MPEG-TS packets into the software demux, and exports helper APIs for DEBI access and video-port switching.

## Important APIs, Types, And Functions
The file operates on `struct budget` from `budget.h` and exports `budget_debug`, `ttpci_budget_init`, `ttpci_budget_init_hooks`, `ttpci_budget_deinit`, `ttpci_budget_irq10_handler`, `ttpci_budget_set_video_port`, `ttpci_budget_debiread`, and `ttpci_budget_debiwrite`. Internal capture functions are `start_ts_capture` and `stop_ts_capture`; DVB feed callbacks are `budget_start_feed` and `budget_stop_feed`; registration helpers are `budget_register` and `budget_unregister`. `budget_read_fe_status` wraps the frontend `read_status` callback to gate DMA on frontend lock.

## Control Flow
Probe-side callers allocate `struct budget`, set `dev->ext_priv`, and call `ttpci_budget_init`. Initialization selects DMA width/height from board type, clamps the `bufsize` module parameter, registers the DVB adapter, sets SAA7146 DD1/GPIO/I2C state, parses EEPROM MAC, allocates a vmalloc DMA buffer with an SAA7146 page table, initializes VPE bottom-half work, powers the frontend, and registers DVB demux devices. `ttpci_budget_init_hooks` replaces the frontend `read_status` with `budget_read_fe_status`. When demux feeds start, `budget_start_feed` increments `feeding`; capture starts only when a feed exists and `fe_synced` is true. IRQ10 queues `vpeirq`, which syncs the SG buffer for CPU, computes the DMA write pointer from `PCI_VDP3`, slices complete 188-byte packets, and sends them to `dvb_dmx_swfilter_packets`. Feed stop, frontend unlock, deinit, or video-port changes stop/restart DMA as needed.

## State And Persistence
All state is runtime-only kernel driver state: buffer geometry, `feeding`, `fe_synced`, circular DMA pointer `ttbp`, warning counters, DVB adapter/demux objects, I2C adapter, and page table. No persistent storage is written. `feedlock` serializes feed/capture transitions and `debilock` serializes DEBI register transactions. The DMA buffer is explicitly zeroed before capture starts and freed during deinit.

## Dependencies And Integration Points
The file depends on the SAA7146 media bridge API, Linux DVB core (`dvb_register_adapter`, `dvb_dmx_init`, `dvb_dmxdev_init`, `dvb_net_init`), I2C core, `ttpci-eeprom` MAC parsing, workqueues, DMA sync APIs, and board-specific modules that attach a frontend. Its exported symbols are shared by sibling `budget*.c` drivers.

## Risks
Capture correctness depends on frontend lock transitions; a frontend driver whose `read_status` behavior changes can leave DMA stopped or running at the wrong time. Buffer sizing and SAA7146 register programming vary by board type and video port, so regressions are hardware-specific. `vpeirq` silently returns if the DMA pointer is outside the buffer. Overrun detection is only a warning based on the consumed span. DEBI helpers return `0` for invalid counts, which can be ambiguous with a valid read value.

## Test Signals
Useful signals are successful DVB adapter registration, I2C frontend detection by board-specific drivers, valid MPEG-TS demux output under `dvb_dmx_swfilter_packets`, absence of repeated ">80% of buffer" warnings, correct DMA stop on frontend unlock/feed stop, and successful unload without workqueue or DMA mapping leaks. Hardware tests should exercise Activy, DVB-C, and default TS-width paths plus video-port switching while streaming.
