# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/Makefile

## Purpose
Builds Tulip-family Ethernet driver modules and declares the multipart object composition for the main `tulip` driver.

## Important APIs, Types, and Functions
Sets `ccflags-$(CONFIG_NET_TULIP) := -DDEBUG`, maps config symbols to objects (`xircom_cb.o`, `dmfe.o`, `winbond-840.o`, `de2104x.o`, `tulip.o`, `uli526x.o`), and defines `tulip-objs` as `eeprom.o interrupt.o media.o timer.o tulip_core.o 21142.o pnic.o pnic2.o`.

## Control Flow and State
No runtime flow. Build-time state determines which modules are produced and which translation units are linked into `tulip.o`.

## Dependencies and Integration Points
Integrated with the child Kconfig symbols. The multipart `tulip.o` links the source files that share `tulip.h` and the common `struct tulip_private` runtime state, while standalone drivers such as `dmfe.o` and `de2104x.o` build separately.

## Risks and Test Signals
Risks include omitting a required object from `tulip-objs`, compiling stale DEBUG flags unexpectedly, or mapping a config symbol to the wrong module. Test signals are successful modular and built-in builds for every symbol, symbol resolution across `tulip-objs`, and expected module file names.
