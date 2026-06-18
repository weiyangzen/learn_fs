# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.c

## Purpose

This helper implements a reusable COMEDI watchdog subdevice for ADDI-DATA boards that expose a TCW-compatible watchdog register block.

## Important APIs, types, and functions

`struct addi_watchdog_private` stores the watchdog base and cached control value. Exported APIs are `addi_watchdog_reset()` and `addi_watchdog_init()`. Subdevice callbacks are `addi_watchdog_insn_config()`, `addi_watchdog_insn_read()`, and `addi_watchdog_insn_write()`.

## Control Flow

Board drivers call `addi_watchdog_init(s, iobase)`, which allocates subdevice private data, stores the base, and configures the subdevice as a writable one-channel timer with 8-bit maxdata and config/read/write handlers. `INSN_CONFIG_ARM` stores `ADDI_TCW_CTRL_ENA`, masks the reload value to 8 bits, writes the reload register, logs the effective timeout using a 20 ms base, and writes the control register. `INSN_CONFIG_DISARM` clears the cached control and writes it. Writes ping the watchdog by writing cached control ORed with `ADDI_TCW_CTRL_TRIG`; reads return the TCW status register.

## State and Persistence

State is subdevice-private `iobase` and `wdog_ctrl` plus hardware reload/control/status registers. `addi_watchdog_reset()` clears control and reload. There is no persistent storage.

## Dependencies and Integration Points

The helper depends on COMEDI subdevice-private allocation and `addi_tcw.h` register definitions. Board drivers use it for APCI-1516/2016, APCI-1564, APCI-2032, APCI-2200, and similar boards.

## Risks

The helper assumes an 8-bit reload and fixed 20 ms time base for all users. A write while disabled returns `-EINVAL`, so user-space must arm before pinging. The subdevice is marked only `SDF_WRITABLE` even though it installs an `insn_read`; that flag choice may affect discoverability. Since `data[1]` is masked rather than range-checked, too-large reloads silently wrap.

## Test Signals

Validation includes init allocating private data, arm writing reload/control and reporting timeout, read returning status, ping toggling trigger only when armed, disarm clearing control, reset clearing control/reload, and all dependent board drivers probing with watchdog subdevices.
