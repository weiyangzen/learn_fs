# sources/distributed-fs/ceph-client/drivers/hsi/controllers/omap_ssi_port.c

## Purpose
Implements the per-port OMAP SSI HSI controller operations: async transfer queuing, PIO and GDD-DMA transfer setup, wake-line handling, HSI port setup/flush/release, per-port IRQs, runtime PM context save/restore, and port debugfs.

## Important APIs, Types, and Functions
- HSI port callbacks assigned in probe: `ssi_async()`, `ssi_setup()`, `ssi_flush()`, `ssi_start_tx()`, `ssi_stop_tx()`, and `ssi_release()`.
- Transfer helpers: `ssi_start_transfer()`, `ssi_start_dma()`, `ssi_start_pio()`, `ssi_pio_complete()`, and `ssi_transfer()`.
- Interrupt threads: `ssi_pio_thread()` for data/error/break interrupts and `ssi_wake_thread()` for CAWAKE changes.
- Cleanup helpers: `ssi_cleanup_gdd()`, `ssi_cleanup_queues()`, `ssi_flush_queue()`, and `ssi_process_errqueue()`.
- Runtime PM helpers save/restore SST/SSR and MPU interrupt context.

## Control Flow
Port probe picks the first uninitialized port slot from the parent controller, obtains the CAWAKE GPIO, allocates port private data, maps TX/RX MMIO, requests the data IRQ and wake IRQ, initializes queues/locks/work, enables autosuspend runtime PM, creates debugfs, and registers DT-described HSI clients. Async transfers are queued per TX/RX channel. Single-word transfers use PIO interrupt bits; larger single-entry scatterlists claim a GDD logical channel and program DMA registers. PIO IRQ loops through enabled pending status, completing TX/RX frames, break events, and error handling. Wake IRQ toggles runtime PM references and notifies HSI clients with start/stop RX events. Release and flush cancel DMA, clear buffers/status, drain queues, and reset port mode when the last client exits.

## State and Persistence
Per-port state includes queue contents, wake refcount, wake-in flag, SST/SSR shadow context, active GDD linkage through the controller, error queue work, and debugfs state. Runtime suspend writes modules to sleep and saves registers; resume restores divisor, mode, and context when needed. No persistent storage.

## Dependencies and Integration Points
Depends on the HSI framework, parent OMAP SSI controller data, GDD registers, pm_runtime, GPIO descriptors, pinctrl sleep/default states, IRQ threading, DMA mapping, scatterlists, debugfs, and DT child client registration.

## Risks and Test Signals
Risks include PM reference imbalance between PIO, DMA, wake, and flush paths; list manipulation during callbacks; partial scatter-gather support (`nents > 1` returns `-ENOSYS`); BUG_ON on invalid channels; and teardown races with IRQ/work. Test signals include PIO and DMA transfer completion, break receive/send in frame mode, error IRQ recovery, wake transitions with rapid high-low-high changes, flush during active DMA, autosuspend/resume preserving register state, and DT child client creation.
