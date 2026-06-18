# sources/distributed-fs/ceph-client/drivers/dma/tegra20-apb-dma.c

## Purpose
This is the DMAengine provider for NVIDIA Tegra20-family APB DMA controllers. It exposes slave SG and cyclic DMA channels for APB peripherals, registers an OF DMA controller, and abstracts SoC differences for Tegra20, Tegra30, Tegra114, and Tegra148.

## Important APIs, Types, and Functions
Key state types are `struct tegra_dma`, `struct tegra_dma_channel`, `struct tegra_dma_desc`, and `struct tegra_dma_sg_req`. `struct tegra_dma_chip_data` captures per-SoC channel count, register stride, maximum count, pause support, and separate word-count support. DMAengine entry points include `tegra_dma_slave_config()`, `tegra_dma_prep_slave_sg()`, `tegra_dma_prep_dma_cyclic()`, `tegra_dma_issue_pending()`, `tegra_dma_terminate_all()`, `tegra_dma_synchronize()`, and `tegra_dma_tx_status()`. Hardware access is isolated through `tdma_write()`, `tdc_write()`, and `tdc_read()`.

## Control Flow
Probe obtains the memory resource, clock, reset, per-channel IRQs, initializes channel lists/tasklets, registers the DMAengine device, and registers OF translation through `tegra_dma_of_xlate()`. A client configures slave properties, prepares either SG or cyclic descriptors, submits them through `tegra_dma_tx_submit()`, and starts work with `issue_pending()`. `tdc_start_head_req()` programs channel registers and enables the channel. Interrupts clear EOC status, call the active ISR handler (`handle_once_dma_done()` or `handle_cont_sngl_cycle_dma_done()`), wake synchronizers, and schedule the tasklet for callbacks.

## State and Persistence
Per-channel state is held in pending SG requests, reusable SG request and descriptor freelists, callback descriptors, `busy`, `cyclic`, `config_init`, and the current slave ID. Transfer progress is tracked by descriptor byte counters and per-SG `words_xferred`. Runtime PM gates the DMA clock while active transfers take references. System suspend kills tasklets and refuses suspend if any channel is busy. Resume reinitializes hardware through reset and global enable.

## Dependencies and Integration Points
The driver depends on Linux DMAengine, runtime PM, clocks, resets, OF DMA, IRQs, tasklets, and Tegra tracepoints. Device tree supplies compatible strings and DMA request IDs. Clients receive private slave channels via `dma_get_any_slave_channel()` and the OF xlate path sets `tdc->slave_id`.

## Risks
The driver has delicate races around pausing, EOC status, and programming the next cyclic segment. Older SoCs use a global pause counter, so one channel pause can affect global controller state. Transfer lengths and addresses must be 4-byte aligned and within `max_dma_count`; callers that violate this fail at prepare time. Cyclic residue is approximate around counter wrap and EOC timing. Suspend during active DMA returns `-EBUSY`.

## Test Signals
Useful checks include DMAengine slave SG loopback/peripheral tests, ALSA cyclic audio playback/capture, DT xlate with valid and invalid request IDs, suspend/resume with idle and busy channels, runtime PM clock toggling, and tracepoint/callback ordering under multi-period cyclic load. Error tests should cover unaligned buffers, overlarge SG segments, termination while EOC is pending, and callback synchronization.
