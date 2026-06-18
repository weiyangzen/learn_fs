# sources/distributed-fs/ceph-client/drivers/misc/mei/Makefile

## Purpose
The MEI Makefile maps Kconfig symbols to the core MEI module, hardware transport modules, optional trace/debug pieces, graphics service clients, and VSC/LB modules.

## Important APIs, Types, and Functions
`mei.o` is composed from `init.o`, `hbm.o`, `interrupt.o`, `client.o`, `main.o`, `dma-ring.o`, `bus.o`, and `bus-fixup.o`, with `debugfs.o` and `mei-trace.o` conditional. Hardware modules include `mei-me.o`, `mei-gsc.o`, `mei-csc.o`, `mei-txe.o`, and VSC modules.

## Control Flow
Kbuild includes objects according to selected `CONFIG_INTEL_MEI*` options and descends into `hdcp/`, `pxp/`, and `gsc_proxy/` directories when their client drivers are enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates core MEI, PCI/TXE/GSC hardware, event tracing include flags, and client subdirectories with the kernel build.

## Risks
Object composition is part of the MEI internal ABI; omitting `client.o`, `bus.o`, or `bus-fixup.o` breaks exported MEI client functionality. Trace CFLAGS must stay aligned with generated trace headers.

## Test Signals
Signals are successful modular and built-in builds for each selected transport/client combination and correct module names such as `mei`, `mei-me`, `mei-gsc`, and `mei_gsc_proxy`.
