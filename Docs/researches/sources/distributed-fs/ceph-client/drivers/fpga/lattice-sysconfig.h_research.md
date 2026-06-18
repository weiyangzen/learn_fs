# sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig.h

Purpose: private interface shared by the Lattice sysCONFIG common core and transport drivers. It defines sysCONFIG command bytes, status bits, polling constants, transport callback structure, and the common `sysconfig_probe` entry point.

Important APIs and types: command macros include ISC enable/disable/erase, read status, check busy, refresh, init address, and bitstream burst. Status macros cover DONE, BUSY, FAIL, and ERR fields. Poll constants set 30 microsecond intervals, one-second busy timeout, and 100 millisecond GPIO timeout. `struct sysconfig_priv` stores optional PROGRAM/INIT/DONE GPIOs, the owning device, command-transfer callback, and bitstream burst init/write/complete callbacks.

Control flow role: transport drivers allocate and fill `struct sysconfig_priv`, then call `sysconfig_probe`. The common core uses the callbacks to issue commands and stream bitstreams while using the optional GPIOs and status bits defined here to decide state and completion.

State and persistence: no storage is allocated in the header. It defines the in-memory state contract between common and transport code and encodes hardware command/status values for persistent or SRAM configuration on Lattice devices.

Dependencies and integration points: relies on `BIT`, `GENMASK`, `struct gpio_desc`, and `struct device` declarations being available through included users. It is included by `lattice-sysconfig.c` and `lattice-sysconfig-spi.c`.

Risks and test signals: risks include stale opcode/status definitions, callback contract drift, and timeout constants being inappropriate for some boards. Test signals are compile coverage for common and SPI modules, successful callback validation, correct status-bit interpretation, and transport-specific tests that verify command byte sequences.
