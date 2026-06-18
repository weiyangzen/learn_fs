# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus_regs.h

Purpose: defines MMIO offsets and bitfields for Intel GPIO DDC pins and GMBUS controller registers.

Important APIs/types/functions: `GPIO(display, gpio)` maps GPIO line registers with clock/data direction/value/pull-up bits. `GMBUS0` selects pin, clock rate, Aksv source, hold time, and byte-count override. `GMBUS1` encodes commands, cycle type, byte count, slave index/address, read/write, software ready, and clear interrupt. `GMBUS2` exposes status bits such as active, SATOER/NAK, ready, wait phase, interrupt, and timeout. `GMBUS3` is data, `GMBUS4` interrupt enables, and `GMBUS5` 2-byte index support.

Control flow: no executable code. `intel_gmbus.c` uses these macros to implement hardware I2C transactions and GPIO bit-banging fallback.

State and persistence: the header holds no state; it describes hardware register state that persists across transfers until reset/clear.

Dependencies and integration: depends on `intel_display_reg_defs.h` and `display->gmbus.mmio_base`.

Risks: wrong byte-count limits, status bits, or command encodings can wedge the DDC bus or corrupt EDID/HDCP transactions. GPIO mask/value semantics are subtle because writes include direction/value mask bits.

Test signals: MMIO trace short/long reads, indexed writes, NAK/timeout clearing, STOP generation, byte-count override, and GPIO bit-bang line toggling.
