# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-elektor.c

## Purpose
Legacy ISA/optional memory-mapped PCF8584 adapter driver for Elektor-style hardware. It supplies low-level PCF register callbacks to the generic `i2c-algo-pcf` algorithm.

## Important APIs, Types, And Functions
Global module parameters define `base`, `irq`, `clock`, `own`, and `mmapped`. `pcf_isa_data` provides callbacks `pcf_isa_setbyte()`, `pcf_isa_getbyte()`, `pcf_isa_getown()`, `pcf_isa_getclock()`, and `pcf_isa_waitforpin()`. ISA binding uses `elektor_match()`, `elektor_probe()`, and `elektor_remove()`. `pcf_isa_handler()` wakes waiters when IRQ mode is used.

## Control Flow
Match optionally autodetects Alpha UP2000 memory-mapped PCF8584 hardware, validates base settings, and supplies a default I/O base. Probe initializes the wait queue, maps I/O or memory region, requests IRQ if configured, assigns device parent, and calls `i2c_pcf_add_bus()`. The algorithm then uses callbacks to read/write data/control registers and wait for pin events either by IRQ wait or delay polling.

## State And Persistence
This driver supports a single global adapter instance. Register base mapping, pending IRQ flag, wait queue, and spinlock are global. Module parameters are the configuration interface.

## Dependencies And Integration Points
Depends on ISA driver core, PCF8584 algorithm support, I/O port or MMIO resource mapping, optional PCI probing on Alpha, IRQs, and HWMON adapter class.

## Risks
Single-instance global state limits scalability. IRQ request failure silently falls back to polling. Legacy hardware parameters are user supplied and can conflict with real resources. Alpha-specific double writes and autodetect paths are platform-sensitive.

## Test Signals
Test I/O-port and MMIO mapping, module parameter combinations, IRQ and polling wait paths, PCF algorithm adapter registration, resource cleanup on `i2c_pcf_add_bus()` failure, and remove after active registration.
