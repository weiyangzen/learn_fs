# Group Research: group_3_9front_sources_os_plan9_9front_sys_src_9_cycv_mmu_c_sources_os_plan9_9_9fdc32477749

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/mmu.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/mmu.c

Role: ARM Cyclone V MMU support for per-process L1/L2 page tables, TLB switching, kernel temporary mappings, `kmap`, direct physical/virtual address translation, and uncached allocation.

Key responsibilities:
- Initializes the CPU's current L1 table from `ttbget()` and installs a per-CPU temporary mapping L2 page at `TMAP`.
- Allocates, caches, switches, and frees per-process `L1` structures, with ASID rollover causing full TLB flush.
- Allocates L2 page-table pages lazily in `putmmu()`, installs user mappings, flushes old mappings, and handles text-cache coherency.
- Implements `flushmmu()` and `mmurelease()` cleanup for process address spaces, including per-process `KMAP` tables.
- Provides `paddr()`, `kaddr()`, and `cankaddr()` for direct-mapped kernel/peripheral address handling.
- Implements per-process `kmap()`/`kunmap()` and per-CPU `tmpmap()`/`tmpunmap()` for physical pages not directly addressable.
- Provides `ucalloc()` from a descending uncached/OCRAM region.

Dependencies:
- Relies on ARMv7-ish page-table constants/macros from `mem.h` and low-level TLB/cache functions from assembly.
- Uses Plan 9 `Proc`, `Page`, `Mach`, `Ref`, `newpage`, `freepages`, `smalloc`, and interrupt priority primitives.

Notes and risks:
- Many paths panic on misuse, including low interrupt level use in `l1free()`/`tmpmap()`, invalid direct address conversion, and exhausted kmap/tmpmap space.
- `l2free()` unlinks all used L2 pages into `mmufree` and clears four L1 entries per recorded `daddr`, matching 4-entry section coverage.
- `tmpmap()` also mirrors the kernel TMAP L1 entry into the current process L1 when needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/timer.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/timer.c

Role: Cyclone V timer and delay support using MPCore global/local timers and clock-manager PLL values.

Key responsibilities:
- Implements `microdelay()`, `delay()`, `µs()`, and `fastticks()` over the global timer registers.
- Reads a stable 64-bit global timer value by sampling high/low/high.
- Programs the local timer compare interval in `timerset()` with range clamping.
- Handles local timer interrupts in `timerirq()` and delegates to `timerintr()`.
- Initializes CPU frequency from clock-manager VCO fields and enables global/local timers.
- Registers `TIMERIRQ` as the clock interrupt.

Dependencies:
- Uses `CLOCKMGR_BASE`, `mpcore`, `HPS_CLK`, timer IRQ constants, and Plan 9 timer core callbacks.
- `synccycles()` is intentionally empty on this platform.

Notes:
- `timerhz` is set to `m->cpuhz / 4`, matching global timer control divider setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/timer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/trap.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/trap.c

Role: Cyclone V ARM trap, syscall, fault, notification, floating-point, process-save, and register setup code.

Key responsibilities:
- Dumps stacks and registers for debugging, including a `ktrace /arm/9cycv` script fragment.
- Decodes ARM fault status values and routes translation/access/domain/permission faults to `fault()`.
- Converts unrecoverable kernel faults into panics and user faults into Plan 9 notes via `faultnote()`.
- Handles undefined-instruction traps, including lazy FPU initialization/restoration for coprocessor 10/11 opcodes.
- Dispatches IRQ traps through `intr()` and syscalls through `dosyscall()`.
- Builds and validates user notification frames in `notify()`/`noted()`.
- Saves/restores FPU state around notes and process switches.
- Sets initial kernel/user register state for fork, exec, and kernel process children.

Dependencies:
- Uses ARM Ureg layout, fault status registers (`getifsr`, `getdfsr`, etc.), FPU helpers, Plan 9 note/syscall/fault machinery, and scheduler entry points.

Notes and risks:
- `faulterr[0x01]` string says "alignement fault" as in source.
- `notefpsave()` returns nil, so note-time FPU save exposure is not implemented here.
- `procsave()` always switches back to the kernel L1 table after saving active FPU state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/uartcycv.c -->
# File Research: sources/os/plan9/9front/sys/src/9/cycv/uartcycv.c

Role: Cyclone V console UART driver for a single 16550-like UART instance.

Key responsibilities:
- Defines UART register offsets and line/status bits.
- Instantiates one controller at `UART_BASE` with `UART0IRQ`.
- Registers one Plan 9 `Uart` named `UART1`, default 115200 baud, console enabled.
- Implements polling `getc`/`putc`, interrupt receive/transmit handling, and staged output kicking.
- Enables UART interrupts and basic 8-bit line/fifo setup in `vuartenable()`.
- Supports word size and parity changes by mutating `LCR`; baud changes only print requested baud and return success.
- Exposes `PhysUart cycvphysuart`.

Dependencies:
- Uses common Plan 9 UART framework (`uartrecv`, `uartstageoutput`, `consuart`) and platform interrupt registration.

Notes:
- Stop bits, RTS/DTR/break/fifo/power/modem control are no-op or unsupported.
- Transmit writes through `RBR` offset, matching 16550 THR/RBR shared register layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/cycv/uartcycv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/ccm.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/ccm.c

Role: i.MX8 clock-control module support: named input clocks, root clock slices, module gates, PLL programming, and public clock rate/gate APIs.

Key responsibilities:
- Defines input clock IDs/frequencies/names for ARM/GPU/VPU/DRAM/system/audio/video PLLs, oscillator refs, and external refs.
- Defines root clock IDs/names for CPU, buses, display, USB, PCIe, SAI, ENET, I2C, UART, PWM, GPT, MIPI, CSI, and HDMI domains.
- Provides a large `root_clk_input_mux` table mapping each root clock to its valid mux inputs.
- Provides a large `clocks[]` module table mapping named module clocks to root slices and optional CCGR gate numbers.
- Programs fractional PLLs by searching divider/fraction settings, bypassing while changing, waiting for lock, then unbypassing.
- Supports analog PLL monitor output via special `ccm_analog_pllout` handling.
- Reads and writes CCGR gate state and root target registers, preserving active gates during root-clock reconfiguration.
- Computes current root rates including disabled-state negative return convention.
- Chooses pre/post divider values that do not exceed requested frequency, then enables the source PLL when needed.
- Exposes `setclkgate()`, `setclkrate()`, and `getclkrate()` by string name.

Dependencies:
- Hard-wired CCM MMIO at `VIRTIO + 0x380000` and analog top at `VIRTIO + 0x360000`.
- Used by nearly every i.MX8 driver to gate clocks and set bus/peripheral/display/USB/PCIe rates.

Notes and risks:
- Unknown clock or input names panic, so driver string names must match tables exactly.
- IPG-derived roots are special-cased and may be disabled in target writes.
- Some table entries are duplicated or commented with uncertainty, for example USB root comments and duplicated ECSPI2/perfmon naming, but behavior is table-driven.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/ccm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/clock.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/clock.c

Role: i.MX8 AArch64 generic timer, performance counter setup, delays, and CPU frequency measurement.

Key responsibilities:
- Enables PMU cycle counter and user access to virtual counter.
- Enables the physical timer and registers `IRQcntpns` as the clock interrupt.
- On CPU 0, reads `CNTFRQ_EL0`, prints timer frequency, and raises A53 root clock from 25 MHz to 1.6 GHz via CCM.
- Measures `m->cpuhz` from PMCCNTR over 1/100 second of generic counter time.
- Uses `CNTVCT_EL0` as user-visible cycle source frequency.
- Implements `timerset()`, `fastticks()`, `perfticks()`, `µs()`, `microdelay()`, and `delay()`.
- Synchronizes CPUs in `synccycles()` with two `Ref` barriers.

Dependencies:
- Uses ARM64 system registers, `setclkrate()`, and Plan 9 timer interrupt core.

Notes:
- `clockshutdown()` is empty.
- `timerset()` writes the raw signed interval to `CNTP_TVAL_EL0` without explicit lower/upper clamping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/dat.h

Role: i.MX8 platform data declarations and machine/process structures for the 9front ARM64 kernel.

Key contents:
- Defines time constants (`HZ`, `MS2HZ`, `TK2SEC`) and GPIO interrupt mode constants.
- Declares platform typedefs including `Conf`, `Mach`, `Proc`, `Page`, `PTE`, `Tval`, and `KMap`.
- Defines A.OUT magic, saved label format, FPU save/allocation state, and FP state values.
- Defines memory configuration structures and the global `Conf`.
- Defines `MMMU` with top-level user page-table pointer and `PMMU` with per-process page-table free/head/tail arrays, ASID, and TPIDR.
- Includes shared `portdat.h`, then defines `Mach` with fields known to assembly followed by `PMach`.
- Declares global `active` CPU state, `MACHP()`, and register globals `m`/`up`.
- Defines parsed ISA configuration and device-port structures.

Dependencies:
- Paired with `mem.h` and `l.s`; early `Mach` field offsets are assembly-sensitive.
- Pulls in the common Plan 9 port data model.

Notes:
- `NCOLOR` is fixed to 1; cache virtual color issues are ignored on this platform.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/devrtc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/devrtc.c

Role: Plan 9 `#r/rtc` device for an NXP PCF8523 RTC on I2C.

Key responsibilities:
- Attaches to `i2c3` address `0x68`, configures 1-byte subaddresses, and exposes a single `rtc` file.
- Reads PCF8523 BCD time registers seconds through year.
- Converts BCD fields to seconds since 1970 with 1970/2000 century split.
- Performs stable reads by requiring two consecutive equal second values, retrying up to 100 times.
- Allows only `eve` to write non-read mode.
- Parses written numeric seconds, converts to RTC fields, BCD-encodes them, and writes the clock registers.
- Implements local `rtc2sec()`, `sec2rtc()`, and leap-year helpers.

Dependencies:
- Uses Plan 9 device framework, `../port/i2c.h`, `i2cdev`, `i2crecv`, `i2csend`, and common device helpers.

Notes and risks:
- Write path stores `rtc.year` directly via `PUTBCD`, so the full year is reduced by decimal digit operations into the two BCD year digits.
- The diagnostic message on unstable reads is informal in the original source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/devrtc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/etherimx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/etherimx.c

Role: i.MX8 ENET Ethernet MAC driver with RGMII PHY/MII support and descriptor-ring DMA.

Key responsibilities:
- Defines ENET register layout, interrupt bits, MAC controls, MII management, FIFO, coalescing, and descriptor status bits.
- Uses uncached descriptor rings and a block pool for 256 RX and 256 TX descriptors.
- Implements MDIO read/write using ENET MMFR and MII interrupt/completion rendezvous.
- Interrupt handler wakes RX, TX, MII I/O, and link waiters and clears event bits.
- Resets/shuts down MAC via `ECR_RESET`, masks/clears events, and initializes RGMII/max frame settings.
- `attach()` probes PHY, sets MAC address/filter tables, allocates/replenishes RX buffers, initializes TX descriptors, enables coalescing, and starts RX/TX/free/link kernel processes.
- `txproc()` dequeues outgoing blocks, maps them to descriptors, cleans cache, and activates TX DMA.
- `frproc()` reclaims completed TX descriptors and frees blocks.
- `rxproc()` receives complete non-error frames, invalidates cache, strips FCS, delivers to `etheriq`, and replenishes descriptors.
- `linkproc()` negotiates PHY, updates ENET speed/duplex/flow-control bits, and updates Plan 9 link state.
- `pnp()` sets pad muxing, clock rates/gates, MAC address from OCOTP fuses, and interrupt registrations.

Dependencies:
- Uses Plan 9 `etherif`, `ethermii`, `netif`, block pool, kernel process, and cache DMA helpers.
- Depends on `iomuxpad`, `setclkrate`, `setclkgate`, `dmaflush`, and GIC interrupts.

Notes and risks:
- Descriptor memory comes from `ucalloc()` to avoid cache-coherency issues.
- Multicast hash is rebuilt from `edev->maddr`.
- RX replenish waits indefinitely through `resrcwait()` if buffer allocation fails.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/etherimx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/fns.h

Role: i.MX8 platform function declarations tying C code to common port code, assembly routines, and platform drivers.

Key contents:
- Includes common `portfns.h`.
- Declares assembly functions from `l.s`: barriers, atomics, interrupt priority, user transition, FPU register access, SMC call, TLB operations, cache maintenance, cycle counters, TTBR/FAR access.
- Declares MMU/memory APIs such as `paddr`, `kaddr`, `kmap`, `mmukmap`, `vmap`, `mmuidmap`, `mmu0init`, `meminit`, and `ucalloc`.
- Declares clock/timer, FPU, trap, IRQ, sysreg, UART, DMA, main/config, CCM, GPC, LCD, IOMUX, GPIO, and PCIe APIs.
- Defines `GPIO_PIN(n, m)` encoding as bank shifted by 5 plus pin.

Dependencies:
- Signature contract used across all i.MX8 files and port code.

Notes:
- The function declarations for GPIO interrupt enable/disable omit `extern` but are still declarations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/gic.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/gic.c

Role: GICv3 interrupt controller driver for i.MX8, including distributor, redistributor, CPU interface, shared interrupt dispatch, FIQ, and PCI interrupt forwarding.

Key responsibilities:
- Defines GICD/GICR register offsets and stores interrupt handlers in per-CPU hash buckets by `intid % 32`.
- Locates each CPU redistributor by matching `GICR_TYPER` affinity bits.
- Disables CPU interrupt groups and the distributor during shutdown.
- Initializes distributor on CPU 0: clears/enables groups, disables/clears interrupts, priorities, targets, configs, then enables distributor groups.
- Initializes per-CPU redistributor state and CPU interface registers.
- `irq()` reads `ICC_IAR1_EL1`, skips spurious IDs, calls matching handlers, notes clock IRQ, and writes EOI.
- `fiq()` dispatches a single registered FIQ handler on CPU 0.
- `intrenable()` routes PCI `tbdf` interrupt requests to `pciintrenable()`, otherwise allocates a `Vctl`, chooses CPU target, enables ICC group 1, and enables GICR/GICD interrupt.
- `intrdisable()` delegates PCI disables and otherwise has no non-PCI removal logic.

Dependencies:
- ARM64 system registers, `sysrd/syswr`, PCI shim, Plan 9 `Vctl`-style interrupt interface.

Notes and risks:
- Non-PCI `intrdisable()` does not remove handlers or mask GIC lines.
- FIQ registration uses special `IRQfiq` and a single global `vfiq`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/gic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/gpc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/gpc.c

Role: i.MX8 power gating controller helper for powering up named power domains.

Key responsibilities:
- Defines GPC power-up/down request and CPU mapping registers.
- Maps domain names such as `mipi`, `pcie`, `usb_otg1`, `gpu`, `vpu`, `hdmi`, `disp`, and `pcie2` to request bits.
- `powerup()` matches a name case-insensitively, temporarily maps PGCs to CPUs, sets the PUP request bit, waits until hardware clears it, then clears CPU mapping.

Dependencies:
- Hard-wired GPC MMIO at `VIRTIO + 0x3A0000`.
- Used by LCD, USB, and PCIe initialization.

Notes:
- Unknown domain names panic.
- There is no public power-down helper in this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/gpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/gpio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/gpio.c

Role: i.MX8 GPIO bank driver with input/output helpers and callback-based interrupt dispatch.

Key responsibilities:
- Defines GPIO data, direction, interrupt config, mask/status, and edge-select register offsets.
- Models five GPIO banks with MMIO base and clock-gate name.
- Lazily enables each bank clock, disables its interrupt mask, caches direction, and marks it enabled.
- `gpioout()` switches a pin to output and sets/clears the data bit.
- `gpioin()` switches a pin to input and reads the data register.
- `gpiointrenable()` configures pin input mode, edge/level trigger registers, stores callback, and unmasks the pin.
- `gpiointrdisable()` masks a pin and clears its callback.
- `gpiointerrupt()` acknowledges pending status and invokes callbacks with encoded pin IDs.
- `gpiolink()` registers low/high IRQs for all five banks.

Dependencies:
- Uses `setclkgate`, GIC interrupts, `GPIO_PIN`, and platform GPIO mode constants.

Notes and risks:
- Pin bank encoding is one-based in callers (`GPIO_PIN(1, 14)`), and `enable()` rejects bank 0.
- In `gpiointrenable()`, the code compares and shifts using `bit` rather than pin index for ICR1/ICR2 selection; this is source behavior and should be treated carefully if modifying interrupt modes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/gpio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/i2cimx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/i2cimx.c

Role: i.MX8 I2C controller driver integrated with Plan 9 `I2Cbus`.

Key responsibilities:
- Defines i.MX I2C registers/status/control bits and four controller MMIO/IRQ structs.
- Provides interrupt wakeup and `waitsr()` that can poll at high priority or sleep on a rendezvous in process context.
- Implements combined write/read transfers with start, repeated start, ACK/NACK handling, dummy read, stop, arbitration-lost handling, and byte count return.
- Supports 7-bit and apparent extended address prefix sizing via `alen`.
- Selects IFDR divider index from a hardware divider table.
- Enables module clocks by setting `<bus>.ipg_clk_patref` to 25 MHz and gating it.
- Registers I2C1, I2C3, and I2C4 at 400 kHz and configures their pads.

Dependencies:
- Plan 9 `../port/i2c.h`, `iomuxpad`, CCM, GIC interrupt registration.

Notes:
- I2C2 controller struct exists but is not registered by `i2cimxlink()`.
- `waitsr()` clears interrupt/arbitration bits as part of polling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/i2cimx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/io.h -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/io.h

Role: i.MX8 interrupt-number and PCI bus helper definitions.

Key contents:
- Defines `IRQfiq`, PPI/SPI bases, generic timer IRQs, LCD/VPU/uSDHC/UART/I2C/RDC/USB/SCTR/GPIO/PCI/SAI/ENET interrupt numbers.
- Defines `BUSUNKNOWN` as `-1`.
- Defines `PCIWADDR(x)` as physical address plus `PCIWINDOW`, with `PCIWINDOW` currently zero.

Dependencies:
- Included broadly by i.MX8 C files for IRQ constants and bus sentinel values.

Notes:
- IRQ numbering matches GIC SPI/PPI scheme with `SPI` offset 32.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/iomux.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/iomux.c

Role: Table-driven i.MX8 IOMUXC pad, signal, daisy-chain, pad-control, and GPR configuration.

Key responsibilities:
- Defines pad IDs, signal IDs, daisy selector encoding, pad mux alternatives, pad names, and signal names.
- Tracks input daisy selectors for signals like MDIO, PCIe CLKREQ, SAI, and UART RX/RTS.
- Provides pad-control option parsing for voltage select, LVTTL, hysteresis, pull enable, open drain, slew rate, and drive strength.
- `iomuxpad()` resolves pad name, optional signal name, and optional config string, then updates pad control, mux mode/SION, and daisy select registers.
- Supports negated options using `~` in the config string.
- `iomuxgpr()` updates or reads IOMUXC GPR registers.

Dependencies:
- Hard-wired IOMUXC MMIO at `VIRTIO + 0x330000`.
- Used by every board-level peripheral setup file.

Notes and risks:
- Unknown pad/signal names or unmuxable combinations panic.
- Table includes source spelling quirks such as `SAY6_TX_SYNC` and `RANWNAD_DATA04`; callers must use the corresponding string table names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/iomux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/l.s -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/l.s

Role: i.MX8 ARM64 bootstrap, low-level CPU/MMU/cache/TLB/FPU/syscall/trap assembly, and SMC bridge.

Key responsibilities:
- `_start` preserves boot argument, sets SB, enters EL1 from EL2 if needed, disables MMU, flushes caches, computes `machno`, sets `Mach` pointer/stack, clears L1/BSS on CPU 0, builds initial maps, enables MMU, sets `TPIDR_EL1`, then calls `main`.
- `svcmode` configures EL2 state, timer offset, HCR, SCTLR_EL2, VTTBR, and returns to EL1.
- `mmuenable` sets MAIR/TCR, TTBR0/TTBR1, enables SCTLR MMU/cache bits, switches stack/LR to high virtual addresses, and invalidates I-cache.
- Provides atomics (`cmpswap`, `tas`), barriers (`coherence`), interrupt priority (`spl*`, `islo`), idle `WFE`, cycle counters, labels, FAR/TTBR access.
- Provides broadcast/local TLB maintenance entry points.
- Provides FPU enable/disable and raw vector register save/load.
- Implements EL0 syscall fast path, trap path, fork/notereturn, EL1 trap return, and vector stubs patched to user/kernel handlers.
- Provides fault-proof byte copy `peek` and `smccall()` for PSCI/SMC calls.

Dependencies:
- Tightly coupled to `mem.h` constants, `Mach` offsets from `dat.h`, ARM64 sysreg definitions, and C functions `main`, `trap`, `syscall`, `mmuidmap`, `mmu0init`.

Notes:
- Exception vectors store a trap frame of `TRAPFRAMESIZE` and route through C with `Ureg`.
- Several vector branch sites are self-loop placeholders intended to be patched elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/l.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/lcd.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/lcd.c

Role: i.MX8 LCDIF + MIPI DSI + SN65DSI86 bridge + PWM backlight display initialization and blanking.

Key responsibilities:
- Defines reset-controller, PWM2, MIPI DPHY, DSI host, and LCDIF register bits.
- Models video timing and derived DSI timing configuration.
- Computes DSI/DPHY timing parameters from lane count, HS clock, ref clock, and escape clocks.
- Resets and initializes LCDIF for 24-bit dotclock mode, framebuffer address, sync timings, and frame-done interrupt.
- Initializes SN65DSI86 bridge over I2C, including reset, PLL clock selection, lane/rate setup, ASSR, link training, detailed timing registers, and stream enable.
- Reads EDID through bridge AUX passthrough and parses the first detailed timing descriptor.
- Programs DPHY magic/timing/PLL settings and waits for lock.
- Programs DSI host lane, clock, timeout, and DPI video parameters.
- Sets up backlight GPIO and PWM2.
- Implements `blankscreen()` by toggling LCDIF clocks/run state, PWM/backlight GPIO, and bridge video output.
- `lcdinit()` sequences IRQ setup, GPR display mux, backlight, bridge enable, MIPI power/reset/clock setup, EDID, framebuffer allocation, pixel clock, bridge, and LCDIF start.

Dependencies:
- Uses I2C, IOMUX, GPIO, CCM, GPC, screen framebuffer API, Plan 9 draw/memdraw, and GIC interrupts.

Notes and risks:
- DSI HS clock is fixed for the bridge at `2*486 MHz`.
- `dpiinit()` comments that VSYNC/HSYNC polarity programming "seems wrong"; it writes zero regardless of EDID polarity.
- Failure paths print `lcdinit: <reason>` and leave display unavailable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/lcd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/main.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/main.c

Role: i.MX8 kernel entry orchestration, boot argument parsing, configuration, SMP bring-up, reboot, and DMA cache maintenance.

Key responsibilities:
- Parses `BOOTARGS`/plan9.ini-style text into `confname`/`confval`, stripping CR and mapping tabs to spaces.
- Exposes configuration through `getconf()`, `setconfenv()`, and `writeconf()`.
- Starts first user process in `init0()`, initializes devices/environment, starts alarm kproc, builds `boot` argv, exits FPU kernel state, and calls `touser()`.
- Computes memory/process/swap/image configuration in `confinit()`.
- Initializes per-CPU `Mach` state and active CPU bitmap.
- Starts secondary CPUs using PSCI `CPU_ON` SMC with MPID mapping and `_start` entry.
- Adds physical segments for TMU and ECSPI2, configuring pads/clocks for LPC SPI.
- `main()` handles separate secondary CPU path and primary boot path through memory, console, trap, FPU, interrupt, clock, page/proc/device/display/user/SMP/MMU/scheduler initialization.
- `exit()` powers off CPUs or system-resets CPU 0 through PSCI after clearing secrets.
- `reboot()` rewrites config, migrates to CPU 0, shuts devices/timer/interrupts, clears secrets, installs reboot trampoline, and jumps with identity map.
- `dmaflush()` performs clean/invalidate maintenance with `BLOCKALIGN` handling for DMA buffers.

Dependencies:
- Uses `rebootcode.i`, ARM64 SMC/sysreg support, Plan 9 core init functions, CCM/IOMUX, LCD, and memory/cache helpers.

Notes:
- `conf.nmach` defaults to `MAXMACH`.
- `dmaflush(clean=0)` preserves dirty partial cache lines around unaligned DMA receive ranges.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/mem.c

Role: i.MX8 early page-table setup, physical memory discovery, kernel RAM mapping, and uncached allocation.

Key responsibilities:
- `mmuidmap()` builds initial TTBR0 identity blocks for VDRAM until physical `-KZERO`.
- `mmu0init()` builds shared TTBR1 kernel mappings for initial DRAM and VIRTIO device space, using blocks where aligned and pages for unaligned tail.
- Installs higher-level page-table links for configured `PTLEVELS`.
- `meminit()` defines three memory banks: kernel-after-end to `UCRAMBASE`, post-uncached area to 4 GiB, and 4 GiB to 5 GiB quad-A53 memory.
- Calls `kmapram()` for all memory ranges and computes per-bank page counts.
- `ucramalloc()` allocates descending aligned memory from the reserved uncached region and maps pages uncached when allocation crosses page boundaries.
- `ucalloc()` wraps `ucramalloc()` with 8-byte alignment and `PTEUNCACHED`.

Dependencies:
- Relies on `mem.h` address layout, `end`, `mmukmap`, `kmapram`, and page-table macros.

Notes:
- The reserved uncached region is excluded from normal memory in `meminit()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/mem.h -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/mem.h

Role: i.MX8 ARM64 memory layout, page-table geometry, virtual address constants, and PTE attribute definitions.

Key contents:
- Defines KiB/MiB/GiB, 64 KiB pages (`PGSHIFT=16`), effective VA bits (`EVASHIFT=34`), page-table level math, and L1 table sizing.
- Defines CPU/stack constants: `MAXMACH=4`, `MACHSIZE=8 KiB`, `KSTACK=8 KiB`, and `TRAPFRAMESIZE`.
- Defines reserved uncached DRAM at the end of `KZERO` physical space.
- Defines kernel virtual layout: `VDRAM`, `KTZERO`, `VIRTIO`, `KZERO`, `VMAP`, `KMAP`, `KSEG0`, L1/L1BOT/L1TOP, `MACHADDR`, `CONFADDR`, `BOOTARGS`, and `REBOOTADDR`.
- Defines user layout: `UZERO`, `UTZERO`, `USTKTOP`, `USTKSIZE`.
- Defines word/block alignment and map constants.
- Defines shareability, cache memory attributes, MAIR indices, PTE valid/table/page/block bits, AP/SH fields, AF/NG/PXN/UXN bits, and common PTE attribute combinations.
- Defines physical DRAM base and local `MIN`/`MAX`.

Dependencies:
- Used by both C and assembly; changes affect bootstrap, MMU, and trap frame layout.

Notes:
- Comments document physical ranges implied by virtual constants, especially VDRAM and VIRTIO.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/pciimx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/pciimx.c

Role: i.MX8 PCIe root-complex driver for two DesignWare PCIe controllers, config-space access, iATU windows, and MSI dispatch.

Key responsibilities:
- Describes two controllers with memory/config/I/O windows, bus ranges, IRQ bases, and DBI MMIO bases.
- Disables and configures iATU outbound regions for config, I/O, and memory transactions.
- Maps `tbdf` to controller and returns DBI or config-window addresses for 8/16/32-bit config reads/writes.
- Maintains 32 MSI vectors per controller, using a static `msimsg` target address.
- Initializes MSI controller registers, target address, status/mask/enable, and GIC interrupt lines.
- `pciintrenable()` finds device, disables old MSI state, assigns a vector slot, enables controller bit, and programs device MSI.
- `pciintrdisable()` removes matching vector callbacks.
- `rootinit()` maps config space, enables DBI RO writes, sets bridge bus numbers/command/class, scans the bus, initializes MSI, maps I/O/memory windows, assigns resources, and prints hierarchy.
- `pciimxlink()` resets/powers/configures both PCIe blocks, configures reset GPIOs, GPRs, clock rates/gates, releases resets, scans config, and applies QoS magic.

Dependencies:
- Uses Plan 9 PCI framework, `vmap`, `pciscan`, `pcibusmap`, `pcimsienable`, `pcimsidisable`, `iomuxpad`, `iomuxgpr`, `gpioout`, `powerup`, CCM, and GIC.

Notes and risks:
- `qosmagic()` writes undocumented QoS registers to avoid LCDIF/PCIe interference.
- PCIe reset GPIOs are board-specific (`gpio5_io07`, `gpio3_io23`).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/pciimx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/sai.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/sai.c

Role: i.MX8 SAI2 transmit-only audio driver for Plan 9 audio output with ring buffering and headphone sense.

Key responsibilities:
- Defines SAI transmit registers/control bits and a software ring buffer.
- Tracks buffered/available bytes in a circular buffer with one sample-sized gap.
- `saiwrite()` copies user audio into the ring, starts hardware when enough delay-buffered data exists, and sleeps for room/output pacing.
- `saireset()` resets FIFO/software state and configures I2S-style 16-bit packed stereo transmit framing.
- `fifo()` drains ring data into the SAI transmit FIFO in 32-bit words.
- Interrupt handler responds to FIFO error/request/warn, stops on underrun, fills FIFO, acknowledges, and wakes writers.
- Exposes audio control command `reset`, status reporting, buffered count, close behavior, and card probe.
- `saiprobe()` allocates controller/ring state, configures SAI2 pads, gates clock, registers IRQ, configures headphone-detect GPIO interrupt, and registers audio callbacks.
- `sailink()` registers the card type `sai`.

Dependencies:
- Plan 9 audio interface, GPIO, IOMUX, CCM, GIC.

Notes:
- Only controller 0 is accepted.
- Ring size is `44100 * 4 * 2` bytes.
- Headphone sense is sampled from `GPIO_PIN(4, 21)` and stored as `hp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/sai.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/screen.c

Role: Software framebuffer console and draw attachment support for i.MX8 display.

Key responsibilities:
- Maintains `gscreen` as a `Memimage`, raw framebuffer pointer `fbraw`, default font, console colors, screen lock, cursor position, and text window.
- Provides mouse control commands for accelerated/linear mouse mode.
- Uses software cursor helpers for cursor on/off/load and avoids cursor overlap in `hwdraw()`.
- `screeninit()` initializes memdraw, allocates `gscreen`, allocates uncached framebuffer memory, draws the console window, replays kernel message buffer, installs `screenputs`, and initializes software cursor.
- `flushmemscreen()` clips a rectangle and copies changed pixels from `gscreen` to raw framebuffer.
- `attachscreen()` returns the `Memdata` backing `gscreen` for `devdraw` with `softscreen=1`.
- `myscreenputs()` decodes UTF-8 runes under `screenlock` and delegates character rendering.
- `screenwin()` draws a simple Plan 9 console UI and initializes text bounds.
- `screenputc()` handles newline, carriage return, tab, backspace, and glyph rendering with scrolling.

Dependencies:
- Plan 9 draw/memdraw/cursor libraries, `ucalloc`, `kmesg`, software cursor code, and common devdraw hooks.

Notes:
- `hwdraw()` does no acceleration; it only manages software cursor avoidance and returns 0.
- `getcolor()` and `setcolor()` are stubs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/screen.h

Role: Shared display/mouse/draw declarations for the i.MX8 screen stack.

Key contents:
- Declares mouse state/control hooks from `devmouse.c`.
- Declares screen functions: initialization, blanking, flushing, attach, cursor control, cursor loading, mouse control/resizing/redraw.
- Declares global `drawlock`.
- Defines `ishwimage(i)` as always true for `devdraw.c`.
- Declares software cursor helper functions.

Dependencies:
- Included by `lcd.c` and `screen.c`, and used with Plan 9 draw/devdraw code.

Notes:
- `screeninit` parameter name is misspelled `hight` in the prototype but implementation uses `height`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/uartimx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/uartimx.c

Role: i.MX8 UART1 driver integrated with Plan 9 `PhysUart`.

Key responsibilities:
- Defines UART register layout and control/status bits.
- Instantiates one UART at `VIRTIO + 0x860000`, default 115200 baud, 25 MHz source.
- Implements transmit kicking with staged output and TRDY interrupt enable/disable.
- Configures UART enable, parity, stop bits, word size, RX/TX enable, FIFO thresholds, and baud modulator registers.
- Supports `bits`, `stop`, `parity`, and `baud` control by updating the `Uart` state then reconfiguring hardware.
- Interrupt handler drains RX chars and kicks TX.
- Clock helper programs `<uart>.ipg_perclk` from oscillator and gates it.
- `enable()` optionally registers `IRQuart1` interrupt, enables clock, and configures hardware.
- `disable()` avoids disabling the console UART to prevent glitches.
- Provides polling console `getc`/`putc` and `uartconsinit()`.

Dependencies:
- Plan 9 UART framework, CCM, GIC, `VIRTIO` MMIO mapping.

Notes:
- Only UART1 is exposed by `pnp()`.
- RTS, DTR, FIFO, modem control, and break are no-op.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/uartimx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/usbxhciimx.c -->
# File Research: sources/os/plan9/9front/sys/src/9/imx8/usbxhciimx.c

Role: i.MX8 USB xHCI host glue for clocks, PHY/core initialization, power domains, and Plan 9 xHCI registration.

Key responsibilities:
- Gates per-controller `usbN.ctrl` and `usbN.phy` clocks.
- Initializes USB PHY control registers: reset/ATE reset, reference SSP enable, TX enable, and clears resets.
- Initializes Synopsys DWC3 core registers for host mode, power-down scale, auto retry, and 30 MHz frame adjustment.
- `reset()` allocates up to two xHCI controllers at fixed MMIO bases, assigns IRQs, and links them to Plan 9 xHCI core.
- First-controller setup configures USB1 overcurrent/reset pads, toggles hub reset GPIO, disables both clocks, and programs shared USB bus/core/phy root rates.
- Powers up per-controller GPC domains `usb_otg1`/`usb_otg2`, gates clocks, initializes PHY and core.
- `usbxhciimxlink()` registers the `xhci` HCI type.

Dependencies:
- Plan 9 USB/xHCI core, GPC, CCM, GPIO, IOMUX, GIC.

Notes:
- Controller allocation is sequential; each `reset()` call claims the first nil slot.
- USB1 hub reset uses board-specific `gpio1_io14`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/imx8/usbxhciimx.c -->