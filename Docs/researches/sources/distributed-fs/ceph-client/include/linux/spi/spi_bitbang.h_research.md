<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_bitbang.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/spi_bitbang.h

Purpose: This header defines the helper framework for SPI controllers implemented by bit-banging GPIO or similar software-controlled lines.

Important APIs/types/functions: `spi_bb_txrx_word_fn` is the per-mode word shift function type. `spi_bitbang` stores a mutex, busy/use_dma flags, extra mode flags, controller pointer, setup-transfer hook, chipselect hook, optional MOSI idle setter, buffer TX/RX hook, per-mode word functions, and optional line-direction hook. Helpers include setup/cleanup/setup_transfer and queue start/init/stop APIs.

Control flow: A bitbang driver fills callbacks, initializes/starts the helper, and the framework sequences chipselect, setup, and transfer functions for queued SPI messages.

State and persistence: `lock` and `busy` serialize controller state. Callback tables and `ctlr` persist for the controller lifetime.

Dependencies/integration: Depends on workqueues and SPI core types. Used by GPIO and other simple software SPI controllers.

Risks and test signals: Risks include timing jitter, wrong mode-specific shift functions, direction errors for 3-wire modes, and chipselect polarity mistakes. Test all SPI modes, different word sizes, half-duplex transfers, queue start/stop, and logic analyzer timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/spi_bitbang.h -->
