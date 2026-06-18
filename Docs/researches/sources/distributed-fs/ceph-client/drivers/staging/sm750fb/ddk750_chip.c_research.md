# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.c

Purpose: implements SM750/SM718 chip identification, clock/PLL programming, framebuffer memory size detection, and top-level hardware initialization.

Important APIs/types/functions: exported helpers are `sm750_get_chip_type()`, `sm750_set_chip_type()`, `ddk750_get_vm_size()`, `ddk750_init_hw()`, `sm750_calc_pll_value()`, and `sm750_format_pll_reg()`. Internal helpers set main chip clock, memory clock, and master clock. A static `enum logical_chip_type chip` stores detected chip type.

Control flow: PCI probe code sets chip type from device/revision. Hardware init forces power mode 0, enables display/localmem gates, sets VGA graphics/PLL mode, programs requested chip/memory/master clocks, optionally resets local memory, and optionally disables 2D/video/alpha/DMA engines. PLL calculation searches valid N/M/divider combinations for the closest frequency and formats register fields for PLL control registers.

State and persistence: chip type persists in the file-static `chip`. Clock, gate, reset, and engine state persists in MMIO registers. `ddk750_get_vm_size()` reads local memory size from hardware straps/registers, with SM750LE hardcoded to 64 MiB.

Dependencies and integration: uses `peek32()`/`poke32()` from `ddk750_chip.h`, register masks from `ddk750_reg.h`, power-gate helpers from `ddk750_power.c`, and architecture I/O for SM750LE VGA mode setup under x86.

Risks: global chip type assumes a single active device. Clock programming writes hardware registers directly and must respect chip-specific fixed clocks on SM750LE. PLL search uses integer math and frequency limits; incorrect inputs can produce zero or approximate clocks. Memory reset after clock change can hang if sequenced incorrectly.

Test signals: identify SM718/SM750/SM750LE/unknown devices, verify PLL outputs for common pixel/core clocks, check memory-size detection, run init with reset and engine-off flags, and test SM750LE fixed-clock paths.
