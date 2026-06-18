# sources/distributed-fs/ceph-client/drivers/leds/leds-sun50i-a100.c

Purpose: Allwinner A100 LED controller driver for addressable RGB LED strings. It exposes each LED as a multicolor LED class device and transfers packed RGB data to hardware through PIO or DMA.

Important APIs, types, and functions: `struct sun50i_a100_ledc` stores MMIO base, clocks, reset, DMA resources, transfer buffer, spinlock-protected transfer state, format/timing, and LED array. `sun50i_a100_ledc_brightness_set()` computes color components and schedules transfers. `sun50i_a100_ledc_start_xfer()`, `_pio_xfer()`, `_dma_xfer()`, and IRQ handler implement the data path. Parse helpers read `allwinner,pixel-format` and timing properties.

Control flow: probe validates child `reg` and RGB color, allocates state, maps registers, gets clocks/reset, optionally configures DMA, requests IRQ, resumes hardware, then registers each multicolor LED. Brightness updates write one buffer word and either start a transfer or extend the pending transfer length. The IRQ completes transfers and starts any queued transfer.

State and persistence: the transfer buffer mirrors LED color state across writes. `xfer_active` and `next_length` persist scheduling state under spinlock. Suspend waits for active transfers to finish, then disables clocks and asserts reset; resume restores format/timing/interrupt setup.

Dependencies and integration points: platform resources, MMIO, clocks, reset controller, DMA engine, IRQs, LED multicolor class, OF/fwnode properties, and PM ops.

Risks and test signals: validate DMA fallback to PIO, interrupt-driven queueing, suspend waiting without deadlock, address gaps, pixel-format mapping, timing calculations with zero clock rate, and cleanup after partial multicolor registration failure. Hardware tests should inspect actual color order and reset timing.
