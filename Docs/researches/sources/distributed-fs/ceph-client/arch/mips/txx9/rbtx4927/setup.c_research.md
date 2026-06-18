# sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/setup.c

Purpose: RBTX4927/RBTX4937 board setup for PCI, GPIO, restart, memory, clocks, RTC, Ethernet, flash, LEDs, and platform devices.

Important APIs/types/functions: `tx4927_pci_setup`, `tx4937_pci_setup`, `rbtx4927_gpio_init`, `rbtx4927_arch_init`, `toshiba_rbtx4927_restart`, `rbtx4927_mem_setup`, clock/time/RTC/NE/MTD/GPIO LED/device init helpers, board vectors.

Control flow and state: board vector delegates from generic TXX9 setup to initialize board-specific clocks, memory size, PCI windows and IRQ map, RTC platform device, network and flash resources, and GPIO LEDs.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: variant differences are numerous; PCI clock auto-detection can change bus timing; restart uses watchdog/reset registers; fixed flash/network resources must match board straps.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
