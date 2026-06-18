# sources/distributed-fs/ceph-client/drivers/parport/Kconfig

## Purpose
This Kconfig file defines the Linux parallel-port feature hierarchy. It exposes core parport support, PC-style and platform-specific low-level drivers, optional PCMCIA and serial-card integration, and optional IEEE 1284 advanced transfer support.

## Important APIs, Types, and Functions
The central symbol is `PARPORT`, a tristate gated by `HAS_IOMEM`. Driver symbols include `PARPORT_PC`, `PARPORT_SERIAL`, `PARPORT_PC_FIFO`, `PARPORT_PC_SUPERIO`, `PARPORT_PC_PCMCIA`, `PARPORT_IP32`, `PARPORT_AMIGA`, `PARPORT_MFC3`, `PARPORT_ATARI`, `PARPORT_GSC`, and `PARPORT_SUNBPP`. `PARPORT_1284` controls advanced IEEE 1284 negotiation, daisy-chain discovery, probing, and enhanced transfer modes. `PARPORT_NOT_PC` is a helper selected by non-PC implementations.

## Control Flow
Configuration starts with an architecture opt-in helper `ARCH_MIGHT_HAVE_PC_PARPORT`, then presents `menuconfig PARPORT`. All subordinate symbols live inside `if PARPORT`, so no low-level driver builds without the core. Dependencies narrow each driver to relevant buses or architectures: for example `PARPORT_IP32` depends on `SGI_IP32`, Amiga drivers depend on `AMIGA` or `ZORRO`, and `PARPORT_GSC` defaults to `GSC`.

## State and Persistence
The file contributes build-time state only. Selected symbols determine which objects compile and which runtime features are available. No runtime persistence exists here.

## Dependencies and Integration Points
It integrates with kbuild through the symbols consumed by `drivers/parport/Makefile`. It also connects to architecture Kconfig through `ARCH_MIGHT_HAVE_PC_PARPORT` and to subsystem configs such as `PCI`, `PCMCIA`, `SERIAL_8250_PCI`, `HAS_IOPORT`, `SBUS`, and platform architecture symbols.

## Risks
Feature availability depends on accurate architecture selection. Enabling generic PC-style support on platforms with incompatible I/O mappings can produce unusable drivers, while disabling `PARPORT_1284` removes daisy-chain probing and advanced readback behavior. `PARPORT_GSC` has no prompt and follows `GSC`, so PA-RISC coverage depends on that platform symbol.

## Test Signals
Useful checks are generated `.config` combinations and object inclusion: `CONFIG_PARPORT=m/y` should build core `parport`, non-PC drivers should select `PARPORT_NOT_PC`, and `CONFIG_PARPORT_1284=y` should cause daisy/probe support to be compiled into the core.
