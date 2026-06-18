# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/cppi_dma.h

Purpose: defines data structures and descriptor bit fields for TI CPPI and CPPI 4.1 DMA integration used by MUSB platforms. It is a private header shared by DMA backend implementation and platform glue that need CPPI channel/controller state.

Important APIs, types, and symbols: hardware state-RAM structures are `struct cppi_tx_stateram` and `struct cppi_rx_stateram`. Descriptor flags include `CPPI_SOP_SET`, `CPPI_EOP_SET`, `CPPI_OWN_SET`, `CPPI_EOQ_MASK`, `CPPI_ZERO_SET`, `CPPI_RXABT_MASK`, masks for packet/buffer length, and `CPPI_TEAR_READY`. `struct cppi_descriptor` models a CPPI buffer descriptor with hardware overlay fields plus software next pointer, DMA address, and original RX buffer length. `struct cppi_channel` wraps the generic `struct dma_channel` with MUSB endpoint, direction, RNDIS mode, buffer progress, state RAM, descriptor free/active lists, and TX completion list. `struct cppi` is the controller state for older CPPI channels. `struct cppi41_dma_channel` is the per-channel state used by the DMAengine-based CPPI 4.1 backend.

Control flow: older CPPI code uses descriptor/state-RAM definitions to program linked buffer descriptors and track active TX/RX channels. CPPI41 code uses `cppi41_dma_channel` with DMAengine channels, cookies, programmed/actual lengths, packet size, TX FIFO recheck list, ZLP flag, and saved USB toggle state.

State and persistence: no persistent storage. Runtime state is DMA descriptor memory, DMAengine channel state, CPPI state RAM registers, per-channel progress counters, allocation flags, and endpoint references. Descriptor alignment is fixed at 16 bytes for hardware consumption.

Dependencies and integration points: includes Linux list, slab, errno, DMA pool, DMAengine, and MUSB core/DMA abstraction headers. It connects MUSB's generic `dma_controller`/`dma_channel` interfaces to TI CPPI hardware and CPPI41 DMAengine plumbing used by DA8xx and DSPS glue.

Risks: hardware overlay structs must match CPPI state RAM and descriptor layout exactly. Descriptor ownership flags and teardown bits are hardware-visible, so endian/layout mistakes corrupt DMA. `struct cppi41_dma_channel` mixes generic DMA abstraction state and DMAengine state; lifecycle mismatches can leak DMA channels or complete stale transfers. The header exposes both older CPPI and CPPI41 models, so changes must avoid assuming one backend's fields apply to the other.

Test signals: compile CPPI41 and older CPPI users, validate descriptor alignment and field offsets against hardware documentation, run DMA TX/RX bulk traffic, exercise teardown/abort, RNDIS mode, ZLP generation, RX short packets, and channel allocation/release under repeated endpoint enable/disable.
