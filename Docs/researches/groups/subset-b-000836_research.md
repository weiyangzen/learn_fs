# subset-b-000836 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7723.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7723.h

Purpose: defines the SH7723 GPIO, hardware-block, and pin function namespace used by board and driver code.

Important APIs/types/functions: GPIO_PTA6, GPIO_PTA5, GPIO_PTA4, GPIO_PTA3, GPIO_PTA2, GPIO_PTA1, GPIO_PTA0, GPIO_PTB6, GPIO_PTB5, GPIO_PTB4, GPIO_PTB3, GPIO_PTB2, GPIO_PTB1, GPIO_PTB0, GPIO_PTC6, GPIO_PTC5, GPIO_PTC4, GPIO_PTC3, GPIO_PTC2, GPIO_PTC1.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7723.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7724.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7724.h

Purpose: defines the SH7724 GPIO, hardware-block, and DMA slave namespace used by board and driver code.

Important APIs/types/functions: GPIO_PTA6, GPIO_PTA5, GPIO_PTA4, GPIO_PTA3, GPIO_PTA2, GPIO_PTA1, GPIO_PTA0, GPIO_PTB6, GPIO_PTB5, GPIO_PTB4, GPIO_PTB3, GPIO_PTB2, GPIO_PTB1, GPIO_PTB0, GPIO_PTC6, GPIO_PTC5, GPIO_PTC4, GPIO_PTC3, GPIO_PTC2, GPIO_PTC1.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7724.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7734.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7734.h

Purpose: defines the SH7734 GPIO bank and pin-function namespace used by board and driver code.

Important APIs/types/functions: GPIO_GP_0_0, GPIO_GP_0_1, GPIO_GP_0_2, GPIO_GP_0_3, GPIO_GP_0_4, GPIO_GP_0_5, GPIO_GP_0_6, GPIO_GP_0_7, GPIO_GP_0_8, GPIO_GP_0_9, GPIO_GP_0_10, GPIO_GP_0_11, GPIO_GP_0_12, GPIO_GP_0_13, GPIO_GP_0_14, GPIO_GP_0_15, GPIO_GP_0_16, GPIO_GP_0_17, GPIO_GP_0_18, GPIO_GP_0_19.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7734.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7757.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7757.h

Purpose: defines the SH7757 GPIO and DMA slave namespace used by board and driver code.

Important APIs/types/functions: GPIO_PTA1, GPIO_PTA2, GPIO_PTA3, GPIO_PTA4, GPIO_PTA5, GPIO_PTA6, GPIO_PTA7, GPIO_PTB1, GPIO_PTB2, GPIO_PTB3, GPIO_PTB4, GPIO_PTB5, GPIO_PTB6, GPIO_PTB7, GPIO_PTC1, GPIO_PTC2, GPIO_PTC3, GPIO_PTC4, GPIO_PTC5, GPIO_PTC6.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7757.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7785.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7785.h

Purpose: defines the SH7785 GPIO and pin-function namespace used by board and driver code.

Important APIs/types/functions: GPIO_PA6, GPIO_PA5, GPIO_PA4, GPIO_PA3, GPIO_PA2, GPIO_PA1, GPIO_PA0, GPIO_PB6, GPIO_PB5, GPIO_PB4, GPIO_PB3, GPIO_PB2, GPIO_PB1, GPIO_PB0, GPIO_PC6, GPIO_PC5, GPIO_PC4, GPIO_PC3, GPIO_PC2, GPIO_PC1.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7785.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7786.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7786.h

Purpose: defines the SH7786 GPIO/pin-function namespace plus memory-mode selector declaration used by board and driver code.

Important APIs/types/functions: GPIO_PA6, GPIO_PA5, GPIO_PA4, GPIO_PA3, GPIO_PA2, GPIO_PA1, GPIO_PA0, GPIO_PB6, GPIO_PB5, GPIO_PB4, GPIO_PB3, GPIO_PB2, GPIO_PB1, GPIO_PB0, GPIO_PC6, GPIO_PC5, GPIO_PC4, GPIO_PC3, GPIO_PC2, GPIO_PC1, sh7786_mm_sel.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sh7786.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/shx3.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/shx3.h

Purpose: defines the SH-X3 GPIO and pin-function namespace used by board and driver code.

Important APIs/types/functions: GPIO_PA6, GPIO_PA5, GPIO_PA4, GPIO_PA3, GPIO_PA2, GPIO_PA1, GPIO_PA0, GPIO_PB6, GPIO_PB5, GPIO_PB4, GPIO_PB3, GPIO_PB2, GPIO_PB1, GPIO_PB0, GPIO_PC6, GPIO_PC5, GPIO_PC4, GPIO_PC3, GPIO_PC2, GPIO_PC1.

Control flow: there is no executable flow; platform code includes the enumerations when requesting GPIOs, pin functions, hardware-block clock/power gates, or DMA slave IDs.

State and persistence: no software state is stored here; the constants name SoC pins, module-stop domains, DMA request lines, and fixed hardware capabilities.

Dependencies/integration: integrates CPU subtype pinmux, GPIO, clock/power, DMA, and board setup code that must share stable numeric identifiers.

Risks: enum order is an ABI-like in-kernel contract for pinctrl/GPIO tables; inserting values in the wrong place misroutes pins or DMA request IDs.

Test signals: build the matching CPU subtype, probe pinctrl/GPIO users, and test peripherals using listed pins, hardware blocks, or DMA slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/shx3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sigcontext.h

Purpose: declares the SH-4 CPU-local `struct sigcontext` layout used by signal delivery and restore code.

Important APIs/types/functions: `struct sigcontext` with oldmask, regs[16], pc, pr, sr, gbr, mach, macl, fpregs[16], xfpregs[16], fpscr, fpul, ownedfp.

Control flow: the file is a pure ABI type declaration; signal setup copies register/FPU state into this shape and sigreturn consumes the same offsets.

State and persistence: no persistence; the state is user-visible process signal-frame data and must stay layout-compatible.

Dependencies/integration: included by architecture signal code and mirrors the UAPI signal context expectations for SH-4 FPU state.

Risks: any field reorder or type-width change breaks signal ABI and user-space unwind/sigreturn.

Test signals: build asm offsets and run signal/FPU context save-restore tests on SH-4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sq.h

Purpose: defines SH-4 store-queue geometry and control register addresses.

Important APIs/types/functions: `SQ_SIZE`, `SQ_ALIGN_MASK`, `SQ_ALIGN()`, `SQ_QACR0`, `SQ_QACR1`, and `SQ_ADDRMAX`.

Control flow: callers align addresses and program QACR registers before issuing store-queue writes.

State and persistence: state lives in CPU store-queue/QACR registers, not in this header.

Dependencies/integration: used by cache/DMA/memcpy-style optimized SH-4 paths needing store queues.

Risks: bad alignment or address-range assumptions can corrupt uncached/write-combining accesses.

Test signals: compile users and exercise store-queue copy paths with aligned and unaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/sq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/watchdog.h

Purpose: maps SH-4 watchdog registers and bit meanings.

Important APIs/types/functions: `WTCNT`, `WTCSR`, `WTST`, `WTBST`, `WTCSR_TME`, `WTCSR_WT`, `WTCSR_RSTS`, `WTCSR_WOVF`, `WTCSR_IOVF` with endian/CPU conditional addresses.

Control flow: watchdog drivers read/write these addresses to start, refresh, stop, and inspect overflow/reset state.

State and persistence: state persists only in watchdog hardware registers across kernel code paths and possibly reset causes.

Dependencies/integration: integrates with SH watchdog driver code and CPU subtype/endian configuration.

Risks: register aliases differ across subtypes and byte order, so one wrong address can disable or accidentally reset the machine.

Test signals: verify watchdog probe, ping, timeout interrupt/reset, and endian-specific register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/dma.h

Purpose: selects SH-4A DMAC base addresses and IRQ numbers for supported CPU subtypes.

Important APIs/types/functions: `DMTE*_IRQ`, `DMAE*_IRQ`, `SH_DMAC_BASE0`, and optional `SH_DMAC_BASE1` guarded by subtype config.

Control flow: DMAC platform code includes this header and instantiates channels from the chosen constants.

State and persistence: no software state; it describes fixed interrupt and MMIO topology.

Dependencies/integration: depends on `CONFIG_CPU_SUBTYPE_*` and feeds SH DMA engine registration.

Risks: subtype guard mistakes misroute DMA completion/error interrupts or point at the wrong controller bank.

Test signals: build every enabled subtype and test DMA memcpy/peripheral transfers plus error IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/serial.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/serial.h

Purpose: provides the SH-4A CPU serial include guard placeholder.

Important APIs/types/functions: no public symbols beyond `__CPU_SH4A_SERIAL_H`.

Control flow: there is no runtime control flow; platform serial resources are declared elsewhere.

State and persistence: no state or persistence.

Dependencies/integration: included by generic SH serial plumbing when CPU-local serial declarations are expected.

Risks: empty compatibility headers can hide missing subtype serial definitions if callers assume symbols exist.

Test signals: compile serial users for SH-4A subtypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/highlander.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/highlander.h

Purpose: provides the Renesas Highlander/R7780RP board register map.

Important APIs/types/functions: PA_NORFLASH_ADDR, PA_NORFLASH_SIZE, PA_BCR, PA_SDPOW, PA_IRLMSK, PA_IRLMON, PA_IRLPRI1, PA_IRLPRI2, PA_IRLPRI3, defined, highlander_plat_pinmux_setup.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/highlander.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/hp6xx.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/hp6xx.h

Purpose: provides the HP Jornada HP6xx handheld GPIO/ADC/HD64461 constants.

Important APIs/types/functions: HP680_BTN_IRQ, HP680_TS_IRQ, HP680_HD64461_IRQ, DAC_LCD_BRIGHTNESS, DAC_SPEAKER_VOLUME, PGDR_OPENED, PGDR_MAIN_BATTERY_OUT, PGDR_PLAY_BUTTON, PGDR_REWIND_BUTTON.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/hp6xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/lboxre2.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/lboxre2.h

Purpose: provides the L-BOX RE2 interrupt and I/O prefix definitions.

Important APIs/types/functions: IRQ_CF1, IRQ_CF0, IRQ_INTD, IRQ_ETH1, IRQ_ETH0, IRQ_INTA, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/lboxre2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/magicpanelr2.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/magicpanelr2.h

Purpose: provides the MagicPanel R2 board control and bus/register macros.

Important APIs/types/functions: SETBITS_OUTB(mask,, SETBITS_OUTW(mask,, SETBITS_OUTL(mask,, CLRBITS_OUTB(mask,, CLRBITS_OUTW(mask,, CLRBITS_OUTL(mask,, PA_LED, CMNCR, CS0BCR.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/magicpanelr2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/mangle-port.h

Purpose: sets the common machine port-mangling hook contract.

Important APIs/types/functions: only the `__MACH_COMMON_MANGLE_PORT_H` guard; no address transformation macros are defined here.

Control flow: generic I/O code includes it when a machine does not need custom port address mangling.

State and persistence: no state.

Dependencies/integration: integrates with SH `io.h` include layering and machine-specific `__IO_PREFIX` handling.

Risks: future machines needing byte/word port translation must not rely on this empty default.

Test signals: compile I/O accessors for boards using mach-common defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/mangle-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/r2d.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/r2d.h

Purpose: provides the Renesas RTS7751R2D board FPGA/IRQ/resource map.

Important APIs/types/functions: PA_BCR, PA_IRLMON, PA_CFCTL, PA_CFPOW, PA_DISPCTL, PA_SDMPOW, PA_RTCCE, PA_PCICD, PA_VOYAGERRTS, Copyright, rts7751r2d_irq_demux.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/r2d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/romimage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/romimage.h

Purpose: declares the common ROM-image progress hook.

Important APIs/types/functions: `mmcif_update_progress(int nr)` prototype.

Control flow: early ROM/image loaders can call the hook while copying/loading storage blocks.

State and persistence: no state in this common declaration.

Dependencies/integration: implemented by board ROM headers or platform ROM code that can signal progress.

Risks: signature mismatch would break early boot builds where normal driver infrastructure is unavailable.

Test signals: build ROM image configurations and check progress hook references resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/romimage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sdk7780.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sdk7780.h

Purpose: provides the Renesas SDK7780 board memory/FPGA register map.

Important APIs/types/functions: SE_AREA0_WIDTH, PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_EXT1, PA_EXT1_SIZE, PA_SDRAM, PA_SDRAM_SIZE, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sdk7780.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/secureedge5410.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/secureedge5410.h

Purpose: provides the SnapGear SecureEdge5410 I/O port access helpers.

Important APIs/types/functions: _ASM_SH_IO_SNAPGEAR_H, SECUREEDGE_IOPORT_ADDR, SECUREEDGE_WRITE_IOPORT(val,, SECUREEDGE_READ_IOPORT().

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/secureedge5410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh2007.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh2007.h

Purpose: provides the SH2007 bus/PCMCIA timing register bit definitions.

Important APIs/types/functions: CS5BCR, CS5WCR, CS5PCR, BUS_SZ8, BUS_SZ16, BUS_SZ32, PCMCIA_IODYN, PCMCIA_ATA, PCMCIA_IO8.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh2007.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7763rdp.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7763rdp.h

Purpose: provides the SH7763RDP MSTP/port/CPLD/USB register definitions.

Important APIs/types/functions: MSTPCR1, PORT_PSEL0, PORT_PSEL1, PORT_PSEL2, PORT_PSEL3, PORT_PSEL4, PORT_PACR, PORT_PCCR, PORT_PFCR, Copyright, sh7763rdp_irq_demux.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7763rdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7785lcr.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7785lcr.h

Purpose: provides the SH7785LCR board device address map.

Important APIs/types/functions: NOR_FLASH_ADDR, NOR_FLASH_SIZE, PLD_BASE_ADDR, PLD_PCICR, PLD_LCD_BK_CONTR, PLD_LOCALCR, PLD_POFCR, PLD_LEDCR, PLD_SWSR.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/sh7785lcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/shmin.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/shmin.h

Purpose: provides the SHMIN minimal board NE2000 I/O constants.

Important APIs/types/functions: SHMIN_IO_BASE, SHMIN_NE_IRQ, SHMIN_NE_BASE.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/shmin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/titan.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/titan.h

Purpose: provides the Titan board external IRQ definitions.

Important APIs/types/functions: _ASM_SH_TITAN_H, TITAN_IRQ_WAN, TITAN_IRQ_LAN, TITAN_IRQ_MPCIA, TITAN_IRQ_MPCIB, TITAN_IRQ_USB.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/titan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/urquell.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/urquell.h

Purpose: provides the Urquell board NOR/FPGA register map.

Important APIs/types/functions: NOR_FLASH_ADDR, NOR_FLASH_SIZE, CS1_BASE, CS5_BASE, FPGA_BASE, BOARDREG(ofs), UBOARDREG(ofs), SRSTR_OFS, BDMR_OFS.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/urquell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/dma.h

Purpose: provides the Dreamcast DMA channel and register map.

Important APIs/types/functions: G2_NR_DMA_CHANNELS, PVR2_CASCADE_CHAN, G2_CASCADE_CHAN, PVR2_DMA_BASE, PVR2_DMA_ADDR, PVR2_DMA_COUNT, PVR2_DMA_MODE, PVR2_DMA_LMMODE0, PVR2_DMA_LMMODE1.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/maple.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/maple.h

Purpose: provides the Dreamcast Maple bus constants and function codes.

Important APIs/types/functions: MAPLE_PORTS, MAPLE_PNP_INTERVAL, MAPLE_MAXPACKETS, MAPLE_DMA_ORDER, MAPLE_DMA_SIZE, MAPLE_DMA_PAGES, MAPLE_BASE, MAPLE_DMAADDR, MAPLE_TRIGTYPE.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/maple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/pci.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/pci.h

Purpose: provides the Dreamcast GAPS PCI aperture constants.

Important APIs/types/functions: GAPSPCI_REGS, GAPSPCI_DMA_BASE, GAPSPCI_DMA_SIZE, GAPSPCI_BBA_CONFIG, GAPSPCI_BBA_CONFIG_SIZE, GAPSPCI_IRQ.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/sysasic.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/sysasic.h

Purpose: provides the Dreamcast System ASIC hardware event IRQ definitions.

Important APIs/types/functions: HW_EVENT_IRQ_BASE, HW_EVENT_VSYNC, HW_EVENT_MAPLE_DMA, HW_EVENT_GDROM_DMA, HW_EVENT_G2_DMA, HW_EVENT_PVR2_DMA, HW_EVENT_GDROM_CMD, HW_EVENT_AICA_SYS, HW_EVENT_EXTERNAL, Copyright, systemasic_irq_init.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-dreamcast/mach/sysasic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-ecovec24/mach/romimage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-ecovec24/mach/romimage.h

Purpose: implements an Ecovec24 ROM-image MMCIF progress indicator.

Important APIs/types/functions: `mmcif_update_progress()` writes board GPIO/port registers such as `HIZCRA` and `PGDR`.

Control flow: the hook toggles/updates board-visible progress state from early boot code.

State and persistence: state is direct hardware latch/GPIO output only.

Dependencies/integration: depends on early raw I/O helpers and Ecovec24 port register layout before full drivers exist.

Risks: raw register writes during early boot can conflict with later pinmux/GPIO setup if values drift.

Test signals: boot an Ecovec24 ROM image and verify progress indication and later GPIO state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-ecovec24/mach/romimage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/kfr2r09.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/kfr2r09.h

Purpose: declares KFR2R09 LCDC system-bus callbacks.

Important APIs/types/functions: `kfr2r09_lcdc_setup()`/teardown-style prototypes taking `sh_mobile_lcdc_sys_bus_ops`.

Control flow: board LCD setup code provides bus operations to the LCDC driver through these declarations.

State and persistence: no persistent state in the header; LCD controller state is managed by board/display code.

Dependencies/integration: depends on `video/sh_mobile_lcdc.h` style system bus operations.

Risks: prototype drift breaks board display bring-up at compile time or through wrong callbacks.

Test signals: build KFR2R09 display support and test panel enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/kfr2r09.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/romimage.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/romimage.h

Purpose: implements the KFR2R09 ROM-image progress hook in early assembly/C style.

Important APIs/types/functions: `mmcif_update_progress()` and inline label-based delay/control sequence.

Control flow: called repeatedly by MMCIF boot-copy code to show load progress on board hardware.

State and persistence: state is only the board display/GPIO latch touched by raw writes.

Dependencies/integration: integrates with KFR2R09 early boot before platform devices and LCD drivers are available.

Risks: timing-sensitive raw I/O and label flow can break if compiler assumptions change.

Test signals: test KFR2R09 ROM boot and confirm progress signaling does not disturb later device init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-kfr2r09/mach/romimage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-landisk/mach/gio.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-landisk/mach/gio.h

Purpose: provides the LANDISK GIO user ioctl constants.

Important APIs/types/functions: VERSION_STR, GIO_DRIVER_NAME, GIODRV_IOC_MAGIC, GIODRV_IOCRESET, GIODRV_IOCSGIODATA1, GIODRV_IOCGGIODATA1, GIODRV_IOCSGIODATA2, GIODRV_IOCGGIODATA2, GIODRV_IOCSGIODATA4.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-landisk/mach/gio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-landisk/mach/iodata_landisk.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-landisk/mach/iodata_landisk.h

Purpose: provides the I-O DATA LANDISK board register and IRQ map.

Important APIs/types/functions: PA_USB, PA_ATARST, PA_LED, PA_STATUS, PA_SHUTDOWN, PA_PCIPME, PA_IMASK, PA_PWRINT_CLR, PA_PIDE_OFFSET, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-landisk/mach/iodata_landisk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-migor/mach/migor.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-migor/mach/migor.h

Purpose: defines Migor board pin/control register addresses and LCDC setup callback declaration.

Important APIs/types/functions: `PORT_MSELCRA`, `PORT_MSELCRB`, `BSC_CS*`, and `migor_lcdc_setup()`-style LCDC bus op prototype.

Control flow: board setup uses constants to configure bus/pin state and hands system bus ops to LCDC.

State and persistence: state is hardware register configuration done by board code.

Dependencies/integration: integrates with SuperH board setup, BSC, pinmux, and sh_mobile_lcdc.

Risks: wrong bus width/timing registers can break flash/LCD access early in boot.

Test signals: build Migor board support and test LCD plus external memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-migor/mach/migor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/fpga.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/fpga.h

Purpose: provides the SDK7786 FPGA register accessors and bit definitions.

Important APIs/types/functions: SRSTR, SRSTR_MAGIC, INTASR, INTAMR, MODSWR, INTTESTR, SYSSR, NRGPR, NMISR, sdk7786_fpga_init, sdk7786_nmi_init, ioread16, fpga_write_reg, iowrite16.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/fpga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/irq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/irq.h

Purpose: provides the SDK7786 IRQ include guard placeholder.

Important APIs/types/functions: no IRQ symbols beyond `__MACH_SDK7786_IRQ_H`.

Control flow: no runtime flow in this file.

State and persistence: no state.

Dependencies/integration: included by SDK7786 board code that may provide IRQ definitions elsewhere.

Risks: empty header can mask missing board IRQ definitions if assumed complete.

Test signals: compile SDK7786 IRQ and board setup code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sdk7786/mach/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/mrshpc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/mrshpc.h

Purpose: declares SolutionEngine MR-SHPC PCMCIA window setup.

Important APIs/types/functions: `mrshpc_setup_windows()`.

Control flow: board PCMCIA setup calls this helper after MR-SHPC register mappings are available.

State and persistence: state lives in MR-SHPC memory and I/O window registers, not the header.

Dependencies/integration: integrates with SE board headers and PCMCIA/CF resource setup.

Risks: incorrect window setup prevents card detection or maps attribute/common memory incorrectly.

Test signals: boot SE PCMCIA-capable boards and test CF/card insertion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/mrshpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se.h

Purpose: provides the Hitachi SolutionEngine common memory/MR-SHPC/IRQ map.

Important APIs/types/functions: PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_EXT1, PA_EXT1_SIZE, PA_EXT2, PA_EXT2_SIZE, PA_SDRAM, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7206.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7206.h

Purpose: provides the SolutionEngine 7206 board I/O constants.

Important APIs/types/functions: PA_SMSC, PA_MRSHPC, PA_LED, init_se7206_IRQ.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7206.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7343.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7343.h

Purpose: provides the SolutionEngine 7343 memory/MR-SHPC/IRQ declarations.

Important APIs/types/functions: PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_SRAM, PA_EXT1, PA_EXT1_SIZE, PA_EXT2, init_7343se_IRQ.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7343.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7721.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7721.h

Purpose: provides the SolutionEngine 7721 memory/FPGA/MR-SHPC map.

Important APIs/types/functions: SE_AREA0_WIDTH, PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_EXT1, PA_EXT1_SIZE, PA_SDRAM, PA_SDRAM_SIZE, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7721.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7722.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7722.h

Purpose: provides the SolutionEngine 7722 memory/FPGA/LAN/pin map.

Important APIs/types/functions: SE_AREA0_WIDTH, PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_EXT1, PA_EXT1_SIZE, PA_SDRAM, PA_SDRAM_SIZE, init_se7722_IRQ.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7722.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7724.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7724.h

Purpose: provides the SolutionEngine 7724 FPGA IRQ and Ethernet constants.

Important APIs/types/functions: SH_ETH_ADDR, SH_ETH_MAHR, SH_ETH_MALR, PA_LED, IRQ_MODE, IRQ0_SR, IRQ1_SR, IRQ2_SR, IRQ0_MR, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7724.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7751.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7751.h

Purpose: provides the SolutionEngine 7751 memory/MR-SHPC/BCR map.

Important APIs/types/functions: PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_EXT1, PA_EXT1_SIZE, PA_EXT2, PA_EXT2_SIZE, PA_SDRAM, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7751.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7780.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7780.h

Purpose: provides the SolutionEngine 7780 memory/FPGA/display/SM501 map.

Important APIs/types/functions: SE_AREA0_WIDTH, PA_ROM, PA_ROM_SIZE, PA_FROM, PA_FROM_SIZE, PA_EXT1, PA_EXT1_SIZE, PA_SM501, PA_SM501_SIZE, Copyright.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-se/mach/se7780.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/io.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/io.h

Purpose: defines SH03 external interrupt line priorities.

Important APIs/types/functions: `IRL0_IRQ`..`IRL3_IRQ` and matching priority macros.

Control flow: board IRQ setup consumes these constants to configure external interrupt routing.

State and persistence: state is interrupt controller priority programming performed elsewhere.

Dependencies/integration: integrates with SH03 machine vector and irq setup.

Risks: priority mismatch can starve or invert external device interrupts.

Test signals: verify external IRQ delivery and priority masking on SH03.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/sh03.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/sh03.h

Purpose: defines SH03 PCI aperture and config-address registers.

Important APIs/types/functions: `PA_PCI_IO`, `PA_PCI_MEM`, `PCIPAR`, `PCIPDR`.

Control flow: PCI setup uses these constants for config cycles and I/O/memory windows.

State and persistence: state is PCI controller register programming outside this header.

Dependencies/integration: integrates with SH03 PCI and generic PCI accessors.

Risks: wrong apertures produce invalid config cycles or overlapping MMIO.

Test signals: enumerate PCI devices and test config-space reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-sh03/mach/sh03.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/hardware.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/hardware.h

Purpose: declares X3PROTO baseboard GPIO capacity and gpio chip type.

Important APIs/types/functions: `NR_BASEBOARD_GPIOS` and forward declaration of `struct gpio_chip`.

Control flow: board GPIO code sizes its GPIO range from this constant.

State and persistence: GPIO state is owned by gpiolib and board registers elsewhere.

Dependencies/integration: integrates X3PROTO baseboard support with Linux gpiolib.

Risks: wrong GPIO count breaks descriptor allocation and IRQ mapping.

Test signals: probe all baseboard GPIOs and validate line numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/ilsel.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/ilsel.h

Purpose: defines the X3PROTO interrupt line selector interface constants.

Important APIs/types/functions: ILSEL-related include guard and selector declarations/macros in the header.

Control flow: board IRQ setup programs line selectors before registering interrupt sources.

State and persistence: state is selector register contents in board hardware.

Dependencies/integration: integrates with X3PROTO FPGA/baseboard interrupt routing.

Risks: wrong selector mapping makes valid devices appear interrupt-dead.

Test signals: test every routed baseboard interrupt source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/ilsel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/Kbuild

Purpose: controls exported generated/generic UAPI headers for SH.

Important APIs/types/functions: `generated-y += unistd_32.h` and `generic-y += ucontext.h`.

Control flow: Kbuild exports a generated syscall header and reuses generic ucontext during headers install.

State and persistence: no runtime state; this affects installed kernel headers.

Dependencies/integration: integrates arch SH UAPI with scripts/headers_install and syscall generation.

Risks: missing generated header breaks libc builds; wrong generic header changes user ABI.

Test signals: run `make headers_install` for SH and compile a minimal userspace program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/auxvec.h

Purpose: defines SH architecture-specific ELF auxiliary vector tags.

Important APIs/types/functions: `AT_FPUCW`, `AT_SYSINFO_EHDR`, cache-shape auxv tags, and `AT_VECTOR_SIZE_ARCH`.

Control flow: ELF loader fills these auxv entries for userspace startup.

State and persistence: state is process startup metadata copied to user stack.

Dependencies/integration: depends on CPU cache-shape globals set during CPU init and generic ELF binfmt.

Risks: tag renumbering breaks dynamic loaders and runtime cache probes.

Test signals: inspect auxv in SH userspace and verify cache shape values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/byteorder.h

Purpose: selects SH user ABI byte-order helpers.

Important APIs/types/functions: includes little- or big-endian linux byteorder headers based on `__LITTLE_ENDIAN__`.

Control flow: compile-time dispatch only.

State and persistence: no runtime state.

Dependencies/integration: used by userspace and kernel UAPI consumers for endian conversions.

Risks: incorrect endian macro selection corrupts protocol and structure interpretation.

Test signals: compile headers for little and big endian SH targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cachectl.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cachectl.h

Purpose: defines SH cacheflush syscall operation flags.

Important APIs/types/functions: `CACHEFLUSH_D_INVAL`, `CACHEFLUSH_D_WB`, `CACHEFLUSH_D_PURGE`, `CACHEFLUSH_I`, `ICACHE`, `DCACHE`, `BCACHE`.

Control flow: userspace passes these flags to cacheflush/cache control entry points.

State and persistence: state is CPU cache contents affected by syscall handlers elsewhere.

Dependencies/integration: integrates UAPI with SH cacheflush implementation and JIT/self-modifying-code users.

Risks: flag value changes break existing binaries.

Test signals: run userspace cacheflush tests for D/I/both cache cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cachectl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cpu-features.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cpu-features.h

Purpose: publishes SH CPU feature bit positions.

Important APIs/types/functions: `CPU_HAS_FPU`, `P2_FLUSH_BUG`, `MMU_PAGE_ASSOC`, `DSP`, `PERF_COUNTER`, `PTEA`, `LLSC`, `L2_CACHE`, `OP32`, `PTEAEX`, `CAS_L`.

Control flow: kernel CPU detection sets these bits and proc/ELF code interprets them.

State and persistence: state is in `current_cpu_data.flags` and exposed indirectly to procfs/userspace.

Dependencies/integration: must stay in sync with proc flag strings and CPU probe code.

Risks: bit renumbering silently changes feature meaning.

Test signals: compare `/proc/cpuinfo` flags against detected CPU subtype capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/cpu-features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/hw_breakpoint.h

Purpose: marks SH hardware-breakpoint UAPI as empty/unsupported in this tree.

Important APIs/types/functions: no structs or ioctls are declared.

Control flow: ptrace/perf breakpoint features cannot rely on arch-specific UAPI from this header.

State and persistence: no state.

Dependencies/integration: included by generic perf/ptrace headers to satisfy architecture layout.

Risks: adding fields later is ABI-sensitive and must align with perf_event expectations.

Test signals: build perf/ptrace headers and confirm unsupported breakpoint paths fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ioctls.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ioctls.h

Purpose: defines SH terminal and file ioctl command numbers.

Important APIs/types/functions: `FIOCLEX`, `TCGETS`, `TCSETS*`, `TIOCGWINSZ`, `TIOC*`, `FIONREAD`, and socket/group tty ioctls.

Control flow: drivers and libc use fixed numbers for ioctl dispatch across the syscall boundary.

State and persistence: no kernel state here, but each number selects stateful tty/socket behavior in drivers.

Dependencies/integration: integrates with generic termios, tty, serial, and libc ABI.

Risks: renumbering any ioctl breaks existing binaries and device tools.

Test signals: run headers ABI checks and tty ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ioctls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types.h

Purpose: delegates SH POSIX type definitions to the 32-bit header.

Important APIs/types/functions: includes `posix_types_32.h`.

Control flow: compile-time include routing only.

State and persistence: no runtime state.

Dependencies/integration: used by libc and kernel UAPI headers needing `__kernel_*` types.

Risks: wrong include breaks all userspace ABI type widths.

Test signals: headers_install and compile stat/ioctl/signal users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types_32.h

Purpose: defines 32-bit SH kernel POSIX base types.

Important APIs/types/functions: `__kernel_mode_t`, pid/ipc ids, uid/gid old types, old dev type, and generic posix include handoff.

Control flow: userspace sees these typedefs through installed headers.

State and persistence: no runtime state.

Dependencies/integration: integrates with generic `asm-generic/posix_types.h` and libc.

Risks: type-width changes are ABI breaks for syscalls and file formats.

Test signals: run UAPI type-size checks against known SH ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace.h

Purpose: defines SH ptrace request numbers and FDPIC/DSP selectors.

Important APIs/types/functions: `PTRACE_GETREGS`, `SETREGS`, `GETFPREGS`, `GETFDPIC`, DSP requests, and `PT_*` addresses.

Control flow: ptrace syscall switches on these request IDs to copy register/process metadata.

State and persistence: state is traced task register/FDPIC state manipulated elsewhere.

Dependencies/integration: integrates debuggers, strace, gdb, and arch ptrace code.

Risks: request-number drift breaks debugger compatibility.

Test signals: run gdb/ptrace register get/set tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace_32.h

Purpose: defines the 32-bit SH userspace register frame layout.

Important APIs/types/functions: `struct pt_regs`, `struct pt_dspregs`, register index macros for GPR, PC/PR/SR/GBR/MAC/FPU/FPSCR/FPUL.

Control flow: exception and ptrace code save/restore registers according to this layout and expose it to userspace.

State and persistence: per-task register state is copied into these structs on traps and ptrace calls.

Dependencies/integration: must match assembly offsets and signal context handling.

Risks: layout/index changes break debuggers, core dumps, signal frames, and syscall tracing.

Test signals: validate asm offsets, core dump notes, gdb register access, and signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/ptrace_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sigcontext.h

Purpose: defines the user-visible SH signal context layout.

Important APIs/types/functions: `struct sigcontext` with GPRs, PC/PR/SR/GBR/MAC, FPU, xFPU, FPSCR/FPUL, and ownedfp.

Control flow: signal delivery writes this frame and sigreturn restores it.

State and persistence: state is user-stack signal-frame CPU context.

Dependencies/integration: integrates signal_32, ptrace register layouts, and libc signal trampolines.

Risks: any field movement or type change breaks old binaries.

Test signals: run signal frame ABI and FPU preservation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/signal.h

Purpose: adds SH-specific signal action ABI details.

Important APIs/types/functions: `SA_RESTORER` and `struct old_sigaction`.

Control flow: sigaction syscalls translate between old/new action layouts and optional restorer trampoline.

State and persistence: state is per-process signal disposition stored by generic signal code.

Dependencies/integration: integrates with libc signal handling and arch signal delivery.

Risks: incorrect restorer semantics break signal return on old userspace.

Test signals: test old and new sigaction paths including custom restorer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sockios.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sockios.h

Purpose: defines SH socket ioctl command numbers.

Important APIs/types/functions: `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, old timestamp ioctls.

Control flow: socket ioctl syscall dispatches these values to networking state handlers.

State and persistence: state is socket ownership, process group, mark, and timestamps outside this header.

Dependencies/integration: integrates libc networking headers and kernel socket ioctl handling.

Risks: number drift breaks network tools compiled for SH.

Test signals: run socket ioctl ABI smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sockios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/stat.h

Purpose: defines SH old/new stat structures and flags.

Important APIs/types/functions: `struct __old_kernel_stat`, `struct stat`, `struct stat64`, `STAT64_HAS_BROKEN_ST_INO`, `STAT_HAVE_NSEC`.

Control flow: stat-family syscalls fill these layouts for userspace.

State and persistence: state is filesystem inode metadata serialized through fixed ABI fields.

Dependencies/integration: integrates VFS stat translation, libc, and compat old-stat users.

Risks: padding/order changes corrupt userspace file metadata interpretation.

Test signals: run stat/stat64 ABI size-offset checks and filesystem stat tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/swab.h

Purpose: provides SH inline byte-swap implementations.

Important APIs/types/functions: `__arch_swab16`, `__arch_swab32`, optional `__arch_swab64` using `swap.b`/`swap.w`/`xtrct` assembly.

Control flow: compile-time inlines emit SH instructions for endian conversion.

State and persistence: no persistent state.

Dependencies/integration: used by UAPI and kernel byteorder helpers when architecture swab is enabled.

Risks: inline assembly constraints must be correct for compiler/register allocation and endian semantics.

Test signals: compile optimized byte-swap tests and compare outputs for 16/32/64-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/unistd.h

Purpose: routes SH syscall number declarations to the generated 32-bit table.

Important APIs/types/functions: includes `unistd_32.h` through generated UAPI flow.

Control flow: syscall numbers are consumed by libc and kernel syscall dispatch code.

State and persistence: no runtime state in this file.

Dependencies/integration: depends on Kbuild generating `unistd_32.h`.

Risks: missing generation breaks all userspace syscall builds.

Test signals: run headers_install and compile syscall-number users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/Makefile

Purpose: builds the SH kernel core object set.

Important APIs/types/functions: object lists for head, traps, IRQ, process, ptrace, signal, syscall, time, topology, cache/TLB, SMP, ftrace, DWARF unwind, PCI, PM, kprobes, kgdb, perf, and platform sections.

Control flow: Kbuild selects objects from config symbols and removes `-pg` from ftrace/return-address files when needed.

State and persistence: build state only; no runtime persistence.

Dependencies/integration: integrates the whole SH architecture kernel with config-driven object inclusion and linker script generation.

Risks: wrong object selection causes missing boot entry, trap, or syscall code only for some configs.

Test signals: build representative SH configs including SMP, MMU, ftrace, PCI, PM, and kprobes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/asm-offsets.c

Purpose: generates assembly offsets for SH low-level code.

Important APIs/types/functions: `main()` emits `DEFINE()` constants for thread, task, pt_regs, sigframe, CPU context, and FPU/DSP offsets.

Control flow: build system compiles and runs this during offset generation; assembly includes the generated header.

State and persistence: no runtime state; it serializes C layout into assembly constants.

Dependencies/integration: must match `thread_info`, `task_struct`, `pt_regs`, signal, xstate, and CPU context layouts.

Risks: missing or stale offsets break exception entry, context switch, signal, and FPU save/restore.

Test signals: rebuild after struct changes and verify assembly compiles plus context-switch/signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/Makefile

Purpose: selects SH CPU-family support objects.

Important APIs/types/functions: routes `CONFIG_CPU_SH2`, `SH2A`, `SH3`, `SH4`, `SH4A`, shmobile, ADC, legacy CPG clock, IRQ, init, clock, fpu, pfc, proc.

Control flow: Kbuild descends into subtype folders and links common CPU services.

State and persistence: build-time state only.

Dependencies/integration: integrates CPU subtype support with generic SH kernel init.

Risks: wrong config expression can omit the only CPU probe or clock implementation for a platform.

Test signals: build each CPU family config and confirm expected objects are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/adc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/adc.c

Purpose: implements a simple SH ADC single-conversion helper.

Important APIs/types/functions: `adc_single(unsigned int channel)`.

Control flow: selects a channel, starts conversion by programming ADC registers, waits for completion, clears status, and returns the sampled value.

State and persistence: ADC hardware registers hold channel, start, status, and result state.

Dependencies/integration: depends on SH ADC register definitions and callers that serialize/pace conversions.

Risks: busy-wait conversion can hang if hardware clock/reset is wrong; no rich error reporting.

Test signals: test valid channels, timeout behavior if added, and known voltage readings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock-cpg.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock-cpg.c

Purpose: provides the deprecated legacy CPG clock registration path.

Important APIs/types/functions: `cpg_clk_init()`, weak `arch_clk_init()`, master/peripheral/bus/cpu clocks and clkdev aliases.

Control flow: registers on-chip clocks, attaches subtype ops via `arch_init_clk_ops`, adds timer/peripheral aliases, and returns combined registration status.

State and persistence: clock rates and enable flags live in legacy `struct clk` objects.

Dependencies/integration: integrates old SH clock framework with TMU/CMT/MTU and subtype clock ops.

Risks: clock ordering is explicitly significant; alias drift breaks timer/serial clock lookup.

Test signals: boot legacy CPG platforms and verify timer and serial clocks resolve/rate correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock.c

Purpose: coordinates SH architecture clock initialization.

Important APIs/types/functions: `clk_init()`.

Control flow: calls `arch_clk_init()` unless common-clk is used, then machine-vector `mv_clk_init`, recalculates root clocks, and enables init clocks.

State and persistence: clock framework state persists in registered clock objects.

Dependencies/integration: integrates CPU clock code, machine vector clock hooks, and legacy/common clock configuration.

Risks: failure ordering can leave partially registered clocks; missing init clocks breaks timer/console early.

Test signals: boot with and without common-clk and verify clock lookup/rates for timers and serial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/fpu.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/fpu.c

Purpose: handles generic SH FPU state initialization and lazy restore.

Important APIs/types/functions: `init_fpu()`, `__fpu_state_restore()`, `fpu_state_restore()`.

Control flow: initializes hard or soft FPU save area, enables FPU when restoring current task, restores state, disables as appropriate, and marks TS_USEDFPU.

State and persistence: per-task FPU state is stored in `thread.xstate`; CPU FPU enable status is transient.

Dependencies/integration: integrates scheduler lazy FPU handling, traps, and hard/soft FPU layouts.

Risks: incorrect lazy flags leak FPU state across tasks or fault recursively.

Test signals: test context switching with FPU users, signal FPU preservation, and no-FPU configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/init.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/init.c

Purpose: performs early per-CPU SH processor initialization.

Important APIs/types/functions: `cpu_init()`, `cache_init()`, `detect_cache_shape()`, `fpu_init()`, `dsp_init()`, weak `l2_cache_init()`, setup handlers for `nofpu`/`nodsp`.

Control flow: probes CPU, computes cache geometry, purges/enables caches, initializes FPU/DSP feature flags, sets ASID cache and physical address bits, programs speculative/expmask registers, initializes VBR and xstate on boot CPU.

State and persistence: persistent kernel state includes `current_cpu_data`, cache shape auxv globals, ASID cache, feature flags, and thread xstate metadata.

Dependencies/integration: depends on CPU probe, cacheflush, SMP, SH BIOS, trap setup, MMU context, and command-line setup.

Risks: early raw cache/register operations are fragile; wrong geometry can corrupt boot data or user ABI cache shapes.

Test signals: boot representative subtypes with nofpu/nodsp, cache modes, SMP, and verify `/proc/cpuinfo`, auxv, and trap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/Makefile

Purpose: builds SH CPU IRQ helper objects.

Important APIs/types/functions: `imask.o` always and `ipr.o` when `CONFIG_CPU_HAS_IPR_IRQ` is enabled.

Control flow: Kbuild includes the right interrupt-controller helpers for the CPU.

State and persistence: build-time only.

Dependencies/integration: integrates CPU IRQ controller support with platform IRQ setup files.

Risks: omitting `ipr.o` breaks platforms whose vectors depend on IPR priority registers.

Test signals: build configs with and without CPU_HAS_IPR_IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/imask.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/imask.c

Purpose: implements IRQ masking through the SR.IMASK priority field.

Important APIs/types/functions: `make_imask_irq()`, `mask_imask_irq()`, `unmask_imask_irq()`, `set_interrupt_registers()`.

Control flow: registers a level irq_chip; mask/unmask update a bitmap, compute current interrupt priority, and write SR IMASK using inline assembly.

State and persistence: state is `imask_mask`, `interrupt_priority`, and the CPU SR priority bits.

Dependencies/integration: integrates with generic irq_desc handling and SH external IRQ priority model.

Risks: not valid for level 15; priority computation is global and assembly-sensitive.

Test signals: test nested IRQ mask/unmask ordering, level IRQ handling, and CLI-ed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/imask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/ipr.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/ipr.c

Purpose: implements priority-register based IRQ chips.

Important APIs/types/functions: `register_ipr_controller()`, `enable_ipr_irq()`, `disable_ipr_irq()`.

Control flow: controller registration allocates descriptors, installs a level irq_chip, stores per-IRQ IPR data, disables each IRQ, and later mask/unmask writes 4-bit priorities into IPR registers.

State and persistence: state is per-IRQ `ipr_data`, irq_desc chip data, and hardware IPR register fields.

Dependencies/integration: used by many SH platform setup files that declare `ipr_desc`/intc data.

Risks: bad shifts or offsets silently mask wrong interrupt sources; BUG_ON catches invalid descriptor tables only at boot.

Test signals: boot platforms with each IPR table and verify device interrupt enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/ipr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/pfc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/pfc.c

Purpose: registers SH pin-function-controller resources.

Important APIs/types/functions: `plat_pinmux_setup()` weak/default path and `platform_device` resource registration.

Control flow: subtype pinmux files provide resources; setup registers the PFC platform device for the pinctrl driver.

State and persistence: pinmux state is hardware register programming later performed by PFC driver.

Dependencies/integration: integrates CPU subtype pinmux resource tables with platform bus/pinctrl.

Risks: missing or wrong resources prevent GPIO/peripheral muxing while compiling cleanly.

Test signals: boot pinmux subtypes and verify serial/GPIO/peripheral pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/pfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/proc.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/proc.c

Purpose: provides SH CPU identification and `/proc/cpuinfo` output.

Important APIs/types/functions: `get_cpu_subtype()`, `cpuinfo_op`, `show_cpuinfo()`, cache/flag formatting helpers.

Control flow: seq_file iteration walks `cpu_data`, skips offline CPUs, prints machine, subtype, cut, flags, cache geometry, physical bits, and bogomips.

State and persistence: state read from `cpu_data`, online CPU mask, UTS machine, and machvec system type.

Dependencies/integration: integrates CPU probe data, procfs, SMP, cache detection, and exported subtype lookup.

Risks: cpu flag strings must stay aligned with UAPI feature bits; out-of-range type indexes would mislabel CPUs.

Test signals: compare `/proc/cpuinfo` across subtypes, SMP/offline CPUs, cache variants, and feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/Makefile

Purpose: builds SH-2 CPU support.

Important APIs/types/functions: `ex.o`, `probe.o`, `entry.o`, SH7619 setup/clock, and optional J2 SMP support.

Control flow: Kbuild selects subtype setup and SMP object based on config.

State and persistence: build-time only.

Dependencies/integration: integrates SH-2 exception entry, CPU probe, subtype platform devices, and SMP hooks.

Risks: wrong object selection prevents boot or secondary CPU bring-up.

Test signals: build SH7619, J2, SMP and non-SMP configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/clock-sh7619.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/clock-sh7619.c

Purpose: defines SH7619 legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: uses `CONFIG_SH_PCLK_FREQ` as root, derives module/bus clocks, and supplies ops to legacy CPG registration.

State and persistence: clock rates live in registered legacy `struct clk` instances.

Dependencies/integration: integrates with `clock-cpg.c` and SH7619 timer/serial/ether devices.

Risks: wrong divisors break serial baud and timer tick.

Test signals: verify clock rates for CMT, SCIF, and Ethernet on SH7619.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/clock-sh7619.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/entry.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/entry.S

Purpose: implements SH-2 exception, interrupt, and trap entry.

Important APIs/types/functions: `exception_handler`, `interrupt_entry`, `trap_entry`, `restore_all`, BIOS handler paths, stack offset constants.

Control flow: saves interrupted registers, switches from user to kernel stack when needed, dispatches vectors <31 to exception table, >=64 to `do_IRQ`, and trap range to syscall handling, then returns through common ret paths.

State and persistence: state is pt_regs frame, per-CPU mode/thread-info variables, SR.MD, PR/GBR/MAC registers.

Dependencies/integration: depends on generated asm offsets, entry macros, syscall and IRQ common code, SMP cpuid support.

Risks: frame layout must match C `pt_regs`; any stack arithmetic bug corrupts returns or ptrace/signal state.

Test signals: run syscall, IRQ, nested exception, ptrace, and user/kernel trap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/ex.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/ex.S

Purpose: builds the SH-2 exception vector trampoline table.

Important APIs/types/functions: `vbr_base`, `exception_entry`, `exception_trampoline`.

Control flow: generates 256 vector stubs that save r0/r1, encode the vector number, and jump to `exception_handler`.

State and persistence: state is CPU VBR pointing at this table and the temporary exception stack frame.

Dependencies/integration: integrates with `per_cpu_trap_init()` and SH-2 entry.S.

Risks: stub size and vector arithmetic must match VBR table assumptions.

Test signals: trigger representative exceptions/IRQs and verify vector numbers reach handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/ex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/probe.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/probe.c

Purpose: identifies SH-2 CPU subtype and cache shape.

Important APIs/types/functions: `cpu_probe()`.

Control flow: sets `current_cpu_data` type/family/cache fields for configured SH7619 or J2-like CPUs.

State and persistence: persistent CPU metadata is later consumed by cpu_init and procfs.

Dependencies/integration: integrates early CPU init, cache setup, and subtype config.

Risks: incorrect probe data corrupts cache maintenance and CPU reporting.

Test signals: boot each SH-2 subtype and verify cache geometry and `/proc/cpuinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/setup-sh7619.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/setup-sh7619.c

Purpose: declares SH7619 interrupt table and core platform devices.

Important APIs/types/functions: INTC vectors/priorities, SCIF0-2, Ethernet, CMT resources, `sh7619_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: arch initcall registers devices; IRQ setup registers the INTC descriptor; early setup enables CMT clock and adds early console/timer devices.

State and persistence: state is platform-device registry, INTC programming, and STBCR3 clock bit.

Dependencies/integration: integrates serial, sh_eth, sh-cmt, INTC, and early platform infrastructure.

Risks: wrong vector/resource addresses break console, timer, or Ethernet; early clock gating is critical.

Test signals: boot SH7619 with console/timer/network interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/setup-sh7619.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/smp-j2.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/smp-j2.c

Purpose: implements J2 device-tree based SMP/IPI support.

Important APIs/types/functions: `j2_prepare_cpus()`, `j2_start_cpu()`, `j2_smp_processor_id()`, `j2_send_ipi()`, IPI handler, `CPU_METHOD_OF_DECLARE`.

Control flow: maps IPI controller and cpuid MMIO from DT, requests per-CPU IPI IRQ, disables unavailable CPUs, writes release/initpc addresses for secondary boot, and sends messages through per-CPU bitmasks plus MMIO trigger.

State and persistence: state includes per-CPU `j2_ipi_messages`, mapped MMIO pointers, IRQ number, and CPU possible/present masks.

Dependencies/integration: integrates OF CPU spin-table binding, generic SMP message handling, and native CPU hotplug hooks.

Risks: missing DT resources silently limits to one CPU; IPI bitmask races rely on cmpxchg correctness.

Test signals: boot SMP J2 DT, send reschedule/call-function IPIs, and test CPU hotplug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/smp-j2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/Makefile

Purpose: builds SH-2A CPU support.

Important APIs/types/functions: common `ex.o`/`entry.o`, probe/opcode helper, optional FPU, subtype setup/clock files, and pinmux resources.

Control flow: Kbuild maps subtype configs to setup/clock/pinmux object files.

State and persistence: build-time only.

Dependencies/integration: integrates SH-2A entry, FPU emulation, clocks, pinmux, and platform-device setup.

Risks: shared files for SH7203/SH7263 and MX-G can be omitted by config mistakes.

Test signals: build all listed SH2A subtype configs with and without FPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7201.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7201.c

Purpose: defines SH7201 legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `cpu_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: reads mode/frequency configuration and derives module, bus, and CPU clock rates for the legacy clock framework.

State and persistence: state is registered clock rates and hardware mode bits.

Dependencies/integration: integrates with SH7201 setup devices, timer, and serial drivers.

Risks: bad divisor tables break baud/timer calibration.

Test signals: boot SH7201 and verify cpu/peripheral/bus clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7203.c

Purpose: defines SH7203/SH7263 legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: derives legacy master/module/bus clocks from mode pins/register values for SH7203-family devices.

State and persistence: clock framework stores derived rates after registration.

Dependencies/integration: integrates with setup-sh7203 SCIF/CMT/MTU/USB resources.

Risks: wrong base rate or divisor gives broken console and timers.

Test signals: verify early console baud, CMT tick, and peripheral clock aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7206.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7206.c

Purpose: defines SH7206/MX-G legacy clock operations.

Important APIs/types/functions: `master_clk_init()`, `module_clk_recalc()`, `bus_clk_recalc()`, `cpu_clk_recalc()`, `arch_init_clk_ops()`.

Control flow: calculates CPU, bus, and module clocks from FRQ/mode settings and supplies ops to CPG init.

State and persistence: state lives in legacy clock objects and source hardware frequency registers.

Dependencies/integration: used by SH7206 and MX-G setup through Kbuild selection.

Risks: shared use by MX-G means subtype assumptions must be checked carefully.

Test signals: test both SH7206 and MX-G clock rates and timer serial behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7206.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7264.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7264.c

Purpose: registers SH7264 modern legacy-clock objects.

Important APIs/types/functions: `arch_clk_init()`, `pll_recalc()`, main clocks, div4 clocks, MSTP clocks, clkdev lookup table.

Control flow: derives PLL from FRQCR and mode pins, registers root/divider/module-stop clocks, and maps device fck aliases to MSTP gates.

State and persistence: clock state is registered clk objects plus STBCR gate bits and FRQCR divisor fields.

Dependencies/integration: integrates SCIF, VDC, CMT, USB, MTU2, SDHI, ADC, RTC clock lookup.

Risks: wrong mode-pin divisor or MSTP bit disables devices or skews rates.

Test signals: verify clock tree rates and enable/disable for each listed peripheral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7269.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7269.c

Purpose: registers SH7269 modern legacy-clock objects.

Important APIs/types/functions: `arch_clk_init()`, `pll_recalc()`, peripheral recalc helpers, div4 and MSTP clock arrays.

Control flow: registers root/extal/PLL/peripheral clocks, DIV4 CPU/bus clocks, and per-device MSTP gates for SCIF0-7, CMT, USB, MTU2, ADC, RTC.

State and persistence: state is clock framework objects and FRQCR/STBCR hardware fields.

Dependencies/integration: integrates SH7269 platform devices with clkdev aliases.

Risks: fixed PLL/peripheral divisors must match board oscillator or timers and baud rates drift.

Test signals: verify extal override, clock rates, and gated peripheral resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/clock-sh7269.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/entry.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/entry.S

Purpose: implements SH-2A exception, interrupt, and syscall entry.

Important APIs/types/functions: `exception_handler`, `interrupt_entry`, `trap_entry`, BIOS handler path, movmu/movml frame save logic.

Control flow: uses SH-2A instructions to save registers, manage SR.MD/kernel stack switching, dispatch interrupt/trap/exception vectors, and return through common paths.

State and persistence: state is pt_regs, CPU mode byte, thread-info stack pointer, SR/PR/GBR/MAC registers.

Dependencies/integration: depends on asm offsets, SH-2A exception vector table, `do_IRQ`, syscall entry, and trap table.

Risks: SH-2A compact save/restore instructions make offset accuracy critical.

Test signals: test interrupts, syscalls, branch-delay traps, ptrace, and signal frames on SH-2A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/ex.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/ex.S

Purpose: builds SH-2A 512-entry exception vector table.

Important APIs/types/functions: `exception_entry0`, `exception_entry1`, `exception_trampoline0/1`, `vbr_base`.

Control flow: emits two banks of 256 stubs, extends vector number to 0-511, and jumps to `exception_handler`.

State and persistence: state is CPU VBR table and temporary saved r0/r1.

Dependencies/integration: integrates with SH-2A entry code and trap initialization.

Risks: stub spacing and vector-bank math must match hardware exception numbering.

Test signals: trigger low and high vector exceptions and verify handler vector numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/ex.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/fpu.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/fpu.c

Purpose: saves/restores SH-2A FPU state and emulates denormal arithmetic traps.

Important APIs/types/functions: `save_fpu()`, `restore_fpu()`, denormal float/double helpers, `ieee_fpe_handler()`, `BUILD_TRAP_HANDLER(fpu_error)`.

Control flow: trap handler un-lazies FPU state, decodes the faulting or delay-slot instruction, emulates denormal fcnvsd/fmul/fadd/fsub when possible, clears FPSCR cause/flag bits, restores FPU, or sends SIGFPE.

State and persistence: per-task hardfpu registers/fpscr/fpul are persistent scheduler state; hardware FPU enable is transient.

Dependencies/integration: depends on trap framework, task xstate, instruction encodings, branch-delay PC rules, and FPU control helpers.

Risks: manual IEEE emulation has precision FIXME notes and fragile instruction decoding for delay slots.

Test signals: test denormal single/double multiply/add/sub, branch-delay FPU traps, context switch, and SIGFPE fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/opcode_helper.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/opcode_helper.c

Purpose: returns SH-2A instruction length for exception fixups.

Important APIs/types/functions: `instruction_size(unsigned short insn)`.

Control flow: decodes known 32-bit prefixes and returns 4 or default 2 so trap code can advance PC correctly.

State and persistence: no persistent state.

Dependencies/integration: integrates with exception/trap emulation that needs variable instruction sizes.

Risks: missing an opcode class advances PC incorrectly after emulation.

Test signals: unit-test representative 16-bit and 32-bit SH-2A opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/opcode_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7203.c

Purpose: registers SH7203 pinmux resources.

Important APIs/types/functions: `plat_pinmux_setup()` with SH7203 PFC resource data.

Control flow: calls generic PFC platform registration for this subtype.

State and persistence: state is later PFC driver register programming.

Dependencies/integration: integrates SH7203 board setup with pinctrl/GPIO.

Risks: wrong resource range prevents serial/peripheral pin muxing.

Test signals: boot SH7203 and verify GPIO and SCIF pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7203.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7264.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7264.c

Purpose: registers SH7264 pinmux resources.

Important APIs/types/functions: `plat_pinmux_setup()` with SH7264 PFC resource data.

Control flow: registers subtype-specific PFC resources for the pinctrl driver.

State and persistence: state is hardware mux configuration owned by PFC driver.

Dependencies/integration: integrates SH7264 peripherals such as SCIF, CMT, SDHI, USB, ADC with pinctrl.

Risks: resource mistakes break peripheral pins without obvious compile errors.

Test signals: boot SH7264 and validate enabled peripheral pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7269.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7269.c

Purpose: registers SH7269 pinmux resources.

Important APIs/types/functions: `plat_pinmux_setup()` with SH7269 PFC resource data.

Control flow: hands subtype resources to generic PFC registration.

State and persistence: state is pin configuration managed after platform-device probe.

Dependencies/integration: integrates SH7269 SCIF/CMT/USB/ADC pinmux with platform bus.

Risks: wrong resource base/size makes GPIO or alternate functions unavailable.

Test signals: boot SH7269 and test serial, GPIO, and selected peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/pinmux-sh7269.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/probe.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/probe.c

Purpose: identifies SH-2A CPU subtype and capabilities.

Important APIs/types/functions: `cpu_probe()`.

Control flow: fills `current_cpu_data` with subtype, family, cache, and feature information based on config/CPU.

State and persistence: persistent metadata drives cache init, procfs, and feature-dependent code.

Dependencies/integration: integrates with `cpu_init()`, FPU support, and subtype setup files.

Risks: wrong cache or feature flags break cache maintenance/FPU reporting.

Test signals: boot each SH2A subtype and check cpuinfo/cache/FPU behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-mxg.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-mxg.c

Purpose: declares Renesas MX-G interrupt table and platform devices.

Important APIs/types/functions: INTC vectors/priorities/masks, SCIF0 and MTU2 resources, `mxg_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: arch initcall registers SCIF/MTU2; IRQ setup registers INTC; early setup registers early console/timer devices.

State and persistence: state is platform-device registry and INTC priority/mask registers.

Dependencies/integration: integrates MX-G serial/timer with generic SH INTC and early platform framework.

Risks: empty priority slots and exact vector numbers are hardware contracts.

Test signals: boot MX-G with console/timer interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-mxg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7201.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7201.c

Purpose: declares SH7201 interrupt table and core platform devices.

Important APIs/types/functions: large INTC vector/group/priority/mask tables, SCIF0-7, CMT/MTU2 resources, `sh7201_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: arch initcall adds serial/timer devices; early setup enables required clocks and registers early devices; IRQ setup registers the INTC descriptor.

State and persistence: state is platform-device registry, interrupt controller registers, and clock-gating bits.

Dependencies/integration: integrates sh-sci, CMT/MTU2, INTC, and early console/timer infrastructure.

Risks: vector/resource mismatches break specific serial ports or timer channels.

Test signals: boot with each SCIF, CMT/MTU interrupts, and early console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7203.c

Purpose: declares SH7203/SH7263 interrupt table and platform devices.

Important APIs/types/functions: INTC vectors/groups/priorities/masks, conditional SH7263-only vectors, SCIF0-3, timer resources, `sh7203_devices_setup()`, `plat_irq_setup()`, `plat_early_device_setup()`.

Control flow: registers devices by arch initcall, registers INTC at IRQ setup, and exposes early console/timer devices before normal driver probing.

State and persistence: state is platform-device registry, INTC priority/mask registers, and subtype clock-gate bits.

Dependencies/integration: integrates SH7203/SH7263 serial, timers, optional SH7263 devices, and generic SH INTC.

Risks: conditional SH7203 vs SH7263 tables can misassign vectors if config is wrong.

Test signals: boot both subtypes and test SCIF, timers, USB/LCDC/SDHI/RTC where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7203.c -->
