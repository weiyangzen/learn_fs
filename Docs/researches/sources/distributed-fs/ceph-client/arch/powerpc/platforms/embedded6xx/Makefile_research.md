# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Makefile

Purpose: build mapping from embedded6xx Kconfig symbols to board, interrupt, UART, and debug objects.

Important APIs and control flow: Linkstation builds `linkstation.o` and `ls_uart.o`; StorCenter, Holly, GameCube, Wii, and MVME5100 select their board files. `GAMECUBE_COMMON` always builds `flipper-pic.o`; Wii additionally builds `hlwd-pic.o`; `USBGECKO_UDBG` builds the EXI debug console.

State, dependencies, and risks: state is object inclusion order at build time. Dependencies are Kconfig symbols and link-time machine descriptor registration. Risks are missing common objects when symbols are misconfigured and board code depending on prototypes from `mpc10x.h` or PIC headers without matching object inclusion. Test signals are per-board kernel link success and absence of unresolved `flipper_*`, `hlwd_*`, or AVR UART symbols.
