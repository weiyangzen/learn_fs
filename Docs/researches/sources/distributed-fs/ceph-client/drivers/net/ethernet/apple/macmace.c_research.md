## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/macmace.c

Purpose: platform driver for Macintosh 68k onboard MACE Ethernet, using PSC Ethernet DMA rather than macio/DBDMA.

Important APIs/types: `struct mace_data` stores fixed MACE base, coherent TX/RX ring buffers and DMA addresses, PSC DMA slot/tail counters, chip id, and owning device. `struct mace_frame` describes PSC receive frame layout with padded MACE status bytes. Main operations are `mace_probe()`, `mace_open()`, `mace_close()`, `mace_xmit_start()`, `mace_interrupt()`, `mace_dma_intr()`, `mace_tx_timeout()`, and PSC DMA reset/load helpers.

Control flow: probe allocates netdev, uses fixed `MACE_BASE` and `MACE_PROM`, reads a bit-reversed PROM MAC address with checksum, sets IRQs, and registers. Open requests normal and DMA IRQs, allocates coherent TX/RX rings, disables/resets PSC DMA, arms both RX DMA sets, resets TX DMA, enables MAC, and masks receive-chip interrupts. TX copies the SKB into the coherent TX ring buffer, programs PSC write address/length/command, toggles the slot, frees the SKB, and relies on DMA/MACE interrupts to free capacity. RX DMA interrupt checks PSC status, resets on error, walks completed ring entries, converts `mace_frame` records into SKBs, and reloads or restarts the active PSC set. Normal MACE interrupt handles transmit status and error accounting.

State and persistence: no persistent state. Coherent DMA rings are allocated on open and freed on device remove; close disables DMA/MAC but does not free rings in this file’s close path, while remove frees them. PSC slot state is reset by `mace_rxdma_reset()` and `mace_txdma_reset()`.

Dependencies/integration: uses m68k Macintosh interrupt IDs, `mac_psc` register helpers, fixed hardware addresses, Linux platform driver model, DMA mapping API, and `mace.h`.

Risks: fixed physical/virtual addresses and PSC magic constants are hardware-specific. TX ring size is one, so queue stop/wake accounting is sensitive. `mace_close()` disables hardware but does not release IRQs or coherent buffers; remove assumes open-time allocations exist. The PSC mystery-status loop and dual-set RX logic are fragile. TX stats increment before DMA completion, so failed transmissions may overcount packets.

Test signals: boot on supported AV Macintosh models, PROM checksum validation, open/close/remove sequencing, one-buffer TX queue wakeups, PSC DMA error reset paths, RX frame status decoding, and watchdog timeout recovery.
