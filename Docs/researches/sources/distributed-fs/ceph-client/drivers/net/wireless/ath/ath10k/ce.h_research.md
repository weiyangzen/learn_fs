# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/ce.h

Purpose: Public/internal interface for ath10k Copy Engine support. It declares descriptor formats, ring/pipe state, bus operations, CE attributes, operation hooks, ring arithmetic helpers, interrupt summary helpers, host-target pipe configuration structures, and exported CE APIs.

Important APIs/types/functions: `struct ce_desc` and `struct ce_desc_64` define 32-bit and 64-bit descriptors. `struct ath10k_ce_ring` tracks ring sizes, software/write/hardware indices, DMA descriptor bases, optional shadow descriptors, and per-transfer contexts. `struct ath10k_ce_pipe` binds a CE ID to source/destination rings, callbacks, max send size, attrs, and ops. `struct ath10k_ce` holds the global lock, bus ops, CE pipe array, and optional RRI memory. `struct ce_attr` is the caller-provided pipe configuration. `struct ath10k_ce_ops` abstracts 32/64-bit descriptor variants. APIs cover send, receive posting/completion, cancellation, initialization, shutdown, interrupt control, register dump, and RRI allocation.

Control flow: HIF/bus code allocates and initializes pipes from `ce_attr`, then posts RX buffers and sends DMA buffers. Interrupt handlers call CE service functions, which invoke callbacks. Ring helper macros implement power-of-two modular movement and descriptor lookup. `ce_pipe_config` and `ce_service_to_pipe` are shared with firmware during startup to map HTC/WMI/HTT services to CE pipes.

State/persistence: Describes volatile host and hardware ring state only. Per-transfer contexts persist until completion/cancel/revoke. DMA descriptor memory is coherent and visible to device hardware.

Dependencies/integration: Includes `hif.h`, relies on ath10k register constants (`CE0_BASE_ADDRESS`, `CE1_BASE_ADDRESS`, wrapper registers), Linux DMA types, and firmware-facing service/pipe configuration. Bus-specific register access is injected through `ath10k_bus_ops`.

Risks: Structures are used across hardware/firmware boundaries; layout and endian expectations cannot change casually. `nentries` must be a power of two after rounding for masks to work. API users must respect locking distinction between locked and no-lock variants.

Test signals: Cross-bus ath10k boot, service-to-pipe setup, DMA traffic, CE interrupt summaries, and crash dumps validate the header contracts.
