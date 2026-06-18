# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup.c

Purpose: central TXX9 generic platform framework for board selection, early setup, clocks, devices, IRQ/time wrappers, GPIO LEDs, DMA, SRAM sysfs, and helper registration.

Important APIs/types/functions: `prom_init`, `plat_mem_setup`, `arch_init_irq`, `plat_time_init`, `plat_irq_dispatch`, `txx9_reg_res_init`, `txx9_wdt_init/now`, `txx9_spi_init`, `txx9_ethaddr_init`, `txx9_sio_init`, `txx9_physmap_flash_init`, `txx9_ndfmc_init`, `txx9_iocled_init`, `txx9_dmac_init`, `txx9_sramc_init`.

Control flow and state: boot parses firmware args/env for board and clocks, selects a `txx9_board_vec`, applies cache options, installs machine hooks, delegates board memory/IRQ/time/device init, registers fixed clocks, and creates platform devices/sysfs views for SoC peripherals.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: very broad integration surface; command-line parsing mutates `arcs_cmdline`; cache disable options can hurt or save broken hardware; SRAM sysfs exposes raw memory writes to root.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
