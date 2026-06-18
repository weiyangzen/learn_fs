# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spi.h

Purpose: declares the OCTEON SPI4 packet-interface initialization API and callback hooks.

Important APIs/types/functions: `cvmx_spi_mode_t` defines unknown, TX halfplex, RX halfplex, and duplex modes. `cvmx_spi_callbacks_t` contains reset, calendar setup, clock detection, training, calendar synchronization, and interface-up callbacks. Inline helpers are `cvmx_spi_is_spi_interface`, `cvmx_spi4000_is_present`, `cvmx_spi4000_initialize`, and `cvmx_spi4000_check_speed`. External functions include `cvmx_spi_start_interface`, `cvmx_spi_restart_interface`, callback get/set APIs, and default callback implementations.

Control flow: callers detect SPI mode by reading `CVMX_GMXX_INF_MODE(interface)` and checking mode bits. Interface start/restart is implemented elsewhere through the callback sequence: reset DLL, configure calendar, detect clocks, train link, synchronize calendars, then mark interface up. SPI4000 helpers are stubs returning no device or zeroed status.

State and persistence: callback configuration is external state managed by the implementation file. Hardware state lives in GMX/SPI CSRs and link-training state. The header itself holds no state.

Dependencies and integration points: includes `cvmx-gmxx-defs.h` and uses `cvmx_read_csr`. It integrates with SPI4 network-interface bring-up, board-specific callback overrides, and GMX in-band status structures.

Risks: the SPI4000 functions are stubbed, so code that expects real SPI4000 support will silently see no device. Callback failures abort initialization, and timeout units differ between clock detection/training/calendar synchronization comments. The typo "corespondant" is harmless but indicates older SDK text.

Test signals: hardware tests should cover SPI interface detection, start/restart callback ordering, timeout behavior, and link-up state. Unit coverage can mock callbacks to verify abort and sequencing logic in the implementation.
