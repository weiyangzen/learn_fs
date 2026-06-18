# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-hw.h

Purpose: register map and bitfield contract for Intel THC hardware. It names common and per-port MMIO offsets, interrupt/status bits, DMA control fields, SPI/I2C configuration fields, default constants, PIO opcodes, SPI I/O modes/dividers, and I2C sub-IP offsets.

Important APIs/types: this header exports no functions, but it is the authoritative macro set consumed by THC common and DMA code. Key enums include `enum thc_pio_opcode`, `enum thc_spi_iomode`, `enum thc_spi_frq_div`, and `enum THC_I2C_SPEED_MODE`.

Control flow: helper code composes values with `FIELD_PREP()`/`FIELD_GET()` against these masks and writes them through regmap. The register layout separates common LTR control from port-specific control, SPI config, software sequencing, write DMA, RXDMA1/RXDMA2/SWDMA, counters, coalescing, and I2C sub-IP registers.

State and persistence: all persistent state is hardware state described by offsets and W1C/reset bits. Software shadows are held in `struct thc_device`/DMA context, not here.

Dependencies and integration: depends only on `<linux/bits.h>`. It integrates the Intel THC driver with hardware documentation and is included by `intel-thc-dev.c` and `intel-thc-dma.c`.

Risks: macro drift from hardware specification can silently corrupt register programming. Several comments have typos, but the important risk is bit reuse across SPI and I2C modes, such as I2C max-size fields sharing the SPI opcode register offset.

Test signals: compile coverage, regmap trace comparison against hardware programming guides, and device-level smoke tests across SPI/I2C, DMA, interrupt, and PM paths.
