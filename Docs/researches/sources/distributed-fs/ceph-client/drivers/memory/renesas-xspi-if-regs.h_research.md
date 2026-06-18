# sources/distributed-fs/ceph-client/drivers/memory/renesas-xspi-if-regs.h

Purpose: register definition header for the Renesas RZ xSPI interface used by `renesas-rpc-if.c`. It names wrapper, bridge-map, command-map, command-direct, calibration, interrupt, and protocol-mode bitfields.

Important APIs/types/functions: no functions or types are declared. The important constants are `XSPI_BMCFG_*`, `XSPI_CMCFG*`, `XSPI_LIOCFGCS0`, `XSPI_BMCTL*`, `XSPI_CDCTL0`, `XSPI_CDTBUF0`, command data/address buffer offsets, interrupt bits, `MWRSIZE_MAX`, and protocol encodings such as `PROTO_1S_2S_2S` and `PROTO_4S_4S_4S`.

Control flow: included by the Renesas core driver when programming xSPI hardware. The core combines macros with `regmap_update_bits()` and `regmap_write()` to configure command-map direct reads/writes, manual transfers, protocol width, chip-select timing, interrupt enable/clear, and maximum combined mapped write size.

State and persistence: the header stores no state. It defines the volatile MMIO layout that determines xSPI controller state when written by the driver.

Dependencies and integration: depends only on `<linux/bits.h>`. Integration is private to xSPI-capable Renesas memory-controller code.

Risks: incorrect masks or shifts can silently program invalid command/address/data sizes. `PROTO_1S_4S_4S` and `PROTO_4S_4S_4S` values must match hardware encoding. `MWRSIZE_MAX` is consumed as a write-size limit and affects direct-map write chunking.

Test signals: compile the xSPI path, confirm `max_register = XSPI_INTE` covers the highest used offset, validate manual read/write completion interrupts, and verify direct-map read/write protocol modes with single, dual, and quad bus-width operations.
