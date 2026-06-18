# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.h

Purpose: Hardware register map, firmware download control layout, and typed access helpers for CW1200 I/O.

Important APIs and types: Defines cut-ID constants, download SRAM offsets, `struct download_cntl_t`, bootloader status/error constants, APB address macro, register IDs, control/config bits, and declarations for data/register/APB/AHB accessors. Inline helpers provide 16-bit and 32-bit register/APB/AHB reads/writes.

Control flow: Firmware loading and BH code use these constants to wake the device, configure DPLL, download firmware, switch access modes, and move WSM frames through the queue register.

State and persistence: No host state, but constants represent persistent device register layout and bootloader shared-memory protocol.

Dependencies and integration: Used by `hwio.c`, `fwio.c`, `bh.c`, and bus modules. Register helper inlines convert little-endian device data to CPU-endian values.

Risks: Register constants and bit definitions must match silicon. `cw1200_reg_read_16` masks with `0xfffff`, wider than 16 bits, which is suspicious but usually harmless when assigned to `u16`. Download control comments contain typos but describe critical bootloader protocol.

Test signals: Firmware download, config/control register inspection, indirect APB/AHB reads, queue-mode data movement, and hardware revision detection are the main validation points.
