# subset-b-005593 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/msc313e_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/msc313e_wdt.c

## Purpose
`msc313e_wdt.c` is a platform watchdog driver for the MStar MSC313e block. It programs a clock-derived watchdog period into two 16-bit registers, clears the counter to service it, and exposes the device through the Linux watchdog core.

## Important APIs, types, and functions
The private `struct msc313e_wdt_priv` carries the MMIO base, input clock, and embedded `watchdog_device`. Operations are `msc313e_wdt_start`, `msc313e_wdt_stop`, `msc313e_wdt_ping`, and `msc313e_wdt_settimeout`; probe uses `devm_platform_ioremap_resource`, `devm_clk_get`, `watchdog_init_timeout`, `watchdog_stop_on_reboot`, `watchdog_stop_on_unregister`, and `devm_watchdog_register_device`.

## Control flow
Probe maps registers, obtains the clock, computes `max_timeout` from `U32_MAX / clk_rate`, detects a bootloader-running watchdog by checking the period registers, and registers the watchdog. Start enables the clock, writes the requested period split across low/high registers, and clears the counter. Ping only writes the clear register. Stop zeroes period and clear registers and disables the clock. Suspend stops an active watchdog and resume restarts it.

## State and persistence
Runtime state is the watchdog core status plus `timeout`, MMIO registers, and clock enable state. Hardware may persist a nonzero period from firmware, represented with `WDOG_HW_RUNNING`; there is no disk persistence.

## Dependencies and integration points
It depends on platform device probing, OF compatible `mstar,msc313e-wdt`, the clock framework, MMIO accessors, and the watchdog core. Module parameter `timeout` feeds `watchdog_init_timeout`.

## Risks and test signals
Risks include zero or unstable clock rates, overflow in timeout-to-cycle conversion if clock changes after probe, and suspend/resume stopping a watchdog that `nowayout` policy might expect to remain alive. Test signals include DT probe, inherited-running watchdog detection, timeout boundary checks, clock enable failure injection, ping/start/stop sequencing, and suspend/resume with an active watchdog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/msc313e_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mt7621_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/mt7621_wdt.c

## Purpose
`mt7621_wdt.c` drives the Ralink/MediaTek MT7621/MT7628 timer-1 watchdog. It exposes timer load/control registers through the watchdog core and reports watchdog reset cause from the SoC syscon reset-status register.

## Important APIs, types, and functions
`struct mt7621_wdt_data` stores timer MMIO, optional reset control, syscon regmap, and `watchdog_device`. Main operations are `mt7621_wdt_start`, `mt7621_wdt_stop`, `mt7621_wdt_ping`, `mt7621_wdt_set_timeout`, `mt7621_wdt_bootcause`, and `mt7621_wdt_is_running`.

## Control flow
Probe resolves the syscon from `mediatek,sysctl` or the legacy compatible, maps timer registers, deasserts an optional reset, initializes watchdog limits, reads boot cause, applies `nowayout`, and registers the device. If hardware is already enabled, it is stopped then restarted with this driver's 1 ms prescaler and core timeout before `WDOG_HW_RUNNING` is set. Start programs the prescaler, writes the load in milliseconds, pings, and sets enable. Stop pings first, then clears the enable bit. Shutdown always stops the watchdog.

## State and persistence
Persistent hardware state consists of timer control/load bits and syscon reset-cause bits across reboot. Runtime state is in the embedded watchdog device and drvdata; no software state is persisted.

## Dependencies and integration points
The driver depends on OF compatible `mediatek,mt7621-wdt`, regmap/syscon, reset control, platform MMIO, module parameter `nowayout`, and watchdog core bootstatus/status handling.

## Risks and test signals
Risks include changing the prescaler while a bootloader-started watchdog is active, missing syscon phandle fallback, `max_timeout` limited by 16-bit millisecond load, and unconditional stop on shutdown despite nowayout. Test signals include both syscon lookup paths, running-at-boot normalization, timeout load math, reset-control absence, and reboot/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mt7621_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mtk_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/mtk_wdt.c

## Purpose
`mtk_wdt.c` is the common MediaTek watchdog driver. It controls the TOPRGU watchdog, optional bark/pretimeout IRQ mode, system restart, and an integrated reset-controller interface for SoC reset lines.

## Important APIs, types, and functions
`struct mtk_wdt_dev` embeds `watchdog_device`, MMIO base, reset-controller device, lock, and DT option flags. `struct mtk_wdt_data` provides per-compatible reset counts and `WDT_SWSYSRST_EN` support. Key functions are `mtk_wdt_start`, `mtk_wdt_stop`, `mtk_wdt_ping`, `mtk_wdt_set_timeout`, `mtk_wdt_set_pretimeout`, `mtk_wdt_restart`, `mtk_wdt_isr`, and reset-controller callbacks `toprgu_reset_assert/deassert/reset`.

## Control flow
Probe maps registers, optionally requests a bark IRQ, selects watchdog info with or without pretimeout, initializes timeouts and restart priority, detects already-running hardware, registers the watchdog, registers a reset controller when match data exists, then reads DT flags controlling external reset and TOPRGU reset source selection. Start programs length, toggles IRQ/dual mode based on `pretimeout`, applies DT mode bits, and enables the watchdog. Pretimeout mode sets the hardware bark at half timeout. Restart clears IRQ reset mode and loops writing the software-reset key.

## State and persistence
State exists in watchdog length/mode/reset registers, reset-controller software-reset registers, `WDOG_HW_RUNNING`, pretimeout fields, and DT-derived booleans. Hardware state can survive firmware handoff; no nonvolatile software persistence exists. The spinlock protects shared software reset registers.

## Dependencies and integration points
It integrates watchdog core, restart handler priority, OF compatibles for many MediaTek SoCs, DT reset bindings, optional IRQ pretimeout notification, Linux reset-controller consumers, and platform PM suspend/resume.

## Risks and test signals
Risks include global `orion_wdt_info`-style option mutation avoided here but shared hardware reset registers require strict locking, half-timeout pretimeout semantics that ignore requested exact pretimeout values, writing key-protected registers incorrectly, and registering reset controller before DT flags are fully applied. Test signals include IRQ/no-IRQ probe, all compatible match-data reset counts, reset-controller assert/deassert with `has_swsysrst_en`, inherited running watchdog, restart path, suspend/resume, and DT flags `mediatek,disable-extrst` and `mediatek,reset-by-toprgu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mtk_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mtx-1_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/mtx-1_wdt.c

## Purpose
`mtx-1_wdt.c` is a legacy miscdevice watchdog for the MTX-1 board. It toggles a GPIO periodically and exposes `/dev/watchdog` ioctls for keepalive and enable/disable.

## Important APIs, types, and functions
The global `mtx1_wdt_device` stores a GPIO descriptor, timer, completion, spinlock, queue/running counters, timeout ticks, and single-open bit. Important routines are `mtx1_wdt_trigger`, `mtx1_wdt_start`, `mtx1_wdt_stop`, `mtx1_wdt_reset`, `mtx1_wdt_open`, `mtx1_wdt_write`, and `mtx1_wdt_ioctl`.

## Control flow
Probe acquires the watchdog GPIO as output high, initializes state, registers `/dev/watchdog`, and starts the background timer. The timer toggles the GPIO every five seconds while queued, decrements `ticks` if running, and either requeues itself or completes removal. Writes and `WDIOC_KEEPALIVE` reset `ticks`; `WDIOC_SETOPTIONS` starts or stops the timer. Remove disables queueing, waits for completion if needed, and deregisters the miscdevice.

## State and persistence
State is entirely global runtime state. The GPIO level and periodic timer represent the hardware feed signal. There is no bootstatus, no magic-close, and no persistent configuration beyond module lifetime.

## Dependencies and integration points
It depends on platform device alias `mtx1-wdt`, GPIO descriptor APIs, timer/completion primitives, miscdevice `WATCHDOG_MINOR`, and classic watchdog ioctls rather than the watchdog core.

## Risks and test signals
Risks include global singleton behavior, the remove path's noted unlocked queue check, lack of nowayout/magic-close semantics, `ticks` in jiffies but decremented once per timer interval, and timer/GPIO races on removal. Test signals include single-open enforcement, keepalive timeout expiry, enable/disable ioctl behavior, removal while timer queued, GPIO request failure, and userspace write with zero length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mtx-1_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nct6694_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/nct6694_wdt.c

## Purpose
`nct6694_wdt.c` provides watchdog support for the Nuvoton NCT6694 USB-attached MFD device. It sends packed setup and command messages through the parent NCT6694 transport.

## Important APIs, types, and functions
Packed protocol types are `struct nct6694_wdt_setup`, `struct nct6694_wdt_cmd`, and `union nct6694_wdt_msg`. `struct nct6694_wdt_data` stores the watchdog, parent MFD pointer, message buffer, and allocated watchdog index. Operations include `nct6694_wdt_setting`, `start`, `stop`, `ping`, `set_timeout`, `set_pretimeout`, and `get_timeleft`.

## Control flow
Probe gets parent `struct nct6694`, allocates a message buffer, allocates a watchdog slot from `nct6694->wdt_ida`, seeds timeout/pretimeout from module parameter arrays, applies `nowayout`, and registers the watchdog. Start writes setup values in milliseconds with GPO actions. Stop sends command `"WDTC"`; ping sends `"WDTS"`. `get_timeleft` reads the setup message and returns countdown milliseconds divided by 1000.

## State and persistence
Runtime state is per-platform-device but the USB/MFD hardware owns countdown and action state. The IDA allocation persists only for the device lifetime and is devm-freed. There is no bootstatus handling.

## Dependencies and integration points
It depends on `linux/mfd/nct6694.h`, parent driver `nct6694_write_msg/read_msg`, platform child device `nct6694-wdt`, IDA allocation, module parameter arrays for up to two watchdogs, and watchdog pretimeout APIs.

## Risks and test signals
Risks include concurrent reuse of the single message buffer if watchdog core invokes operations concurrently, index values exceeding the two-element module arrays, pretimeout validation only warning on an inverted relationship, and transport errors leaving software timeout fields unchanged or stale. Test signals include dual-device probe, IDA cleanup, USB transport read/write failure, timeout/pretimeout programming, stop/ping command bytes, and countdown readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nct6694_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ni903x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ni903x_wdt.c

## Purpose
`ni903x_wdt.c` drives the National Instruments 903x ACPI watchdog through an I/O port register block. It programs a 24-bit seed counter and services the watchdog by setting a PET control bit.

## Important APIs, types, and functions
`struct ni903x_wdt` stores the device, I/O base, and watchdog object. Key functions are `ni903x_resources`, `ni903x_wdd_start`, `ni903x_wdd_stop`, `ni903x_wdd_ping`, `ni903x_wdd_set_timeout`, `ni903x_wdd_get_timeleft`, `ni903x_acpi_probe`, and `ni903x_acpi_remove`.

## Control flow
Probe walks ACPI `_CRS` to find and reserve exactly one I/O resource of at least eight bytes, initializes watchdog limits, applies module timeout/nowayout, registers the device, then switches hardware from boot mode to user mode. Start resets the controller, enables processor reset, writes the seed derived from `timeout / 30.720 us`, then starts/pets the watchdog. Stop writes reset only. Time-left capture sets `CAPTURECOUNTER` and reads the three counter bytes.

## State and persistence
Hardware state is in control, seed, and counter registers. The ACPI I/O resource reservation persists for device lifetime. No bootstatus is decoded; watchdog timeout persists only in hardware until reprogrammed.

## Dependencies and integration points
It integrates ACPI ID `NIC775C`, ACPI resource walking, x86-style `inb/outb` I/O, watchdog core, and module parameters `timeout` and `nowayout`.

## Risks and test signals
Risks include ACPI resources with extra unsupported I/O ranges, unreported request-region size mismatches, integer truncation of counter math, and stop semantics that may reset but not fully disable depending on hardware. Test signals include `_CRS` parse failure, short I/O region, get-timeleft capture, default and boundary timeout programming, module nowayout, and remove path stop/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ni903x_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nic7018_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/nic7018_wdt.c

## Purpose
`nic7018_wdt.c` supports the National Instruments NIC7018 ACPI watchdog. It chooses between two prescaler periods, programs a compact counter/prescaler register, and exposes time-left readback.

## Important APIs, types, and functions
`struct nic7018_wdt` stores I/O base, active period, and watchdog object. `struct nic7018_config` represents hardware period/divider pairs. Key functions are `nic7018_get_config`, `nic7018_set_timeout`, `nic7018_start`, `nic7018_stop`, `nic7018_ping`, `nic7018_get_timeleft`, `nic7018_probe`, and `nic7018_remove`.

## Control flow
Probe obtains an ACPI-provided I/O resource, reserves it, initializes watchdog limits and module options, unlocks the watchdog register block, and registers the watchdog. Start recalculates timeout, enables reload-port access, writes reload, and enables reset. Stop clears control registers and resets preset/prescaler. Ping writes the reload port. Remove unregisters the watchdog and locks the register block.

## State and persistence
The selected period is cached for `get_timeleft`, while hardware stores the actual counter/prescaler and lock state. No bootstatus is reported. Register lock state is restored on removal.

## Dependencies and integration points
It depends on ACPI ID `NIC7018`, platform I/O resources, watchdog core, and module parameters `timeout`/`nowayout`.

## Risks and test signals
Risks include rounded timeouts not matching user request, global hardware unlock during lifetime, no explicit stop before unregister, and `get_timeleft` using cached period that assumes no external reprogramming. Test signals include ACPI probe, region conflicts, timeout rounding around 16/30 seconds, start/stop lock behavior, reload-port enable, and timeleft register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nic7018_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/npcm_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/npcm_wdt.c

## Purpose
`npcm_wdt.c` drives the Nuvoton WPCM450/NPCM750 watchdog. It maps requested timeouts to the discrete hardware interval table, supports bark/pretimeout IRQ notification, and provides a restart operation.

## Important APIs, types, and functions
`struct npcm_wdt` contains `watchdog_device`, MMIO register pointer, and optional clock. Operations are `npcm_wdt_start`, `npcm_wdt_stop`, `npcm_wdt_ping`, `npcm_wdt_set_timeout`, `npcm_wdt_restart`, `npcm_wdt_interrupt`, and `npcm_is_running`.

## Control flow
Probe maps the register, gets an optional clock, requires an IRQ, initializes limits, normalizes the default/DT timeout to representable hardware values, restarts already-running hardware with the selected timeout, requests the IRQ, and registers the watchdog. Start enables clock, selects the nearest register value, enables reset, interrupt, counter reset, and watchdog. Stop writes zero and disables clock. Interrupt calls `watchdog_notify_pretimeout`. Restart enables the clock and writes the shortest reset-enabled sequence.

## State and persistence
Hardware state is the WTCR register and clock gate. The previous running state can be inherited from firmware and marked `WDOG_HW_RUNNING`. Timeout is rounded to discrete supported values.

## Dependencies and integration points
It depends on OF compatibles `nuvoton,wpcm450-wdt` and `nuvoton,npcm750-wdt`, platform IRQ, optional clock, watchdog core pretimeout notification, and restart callback.

## Risks and test signals
Risks include ignored `clk_prepare_enable` return in start/restart, discrete timeout rounding surprising users, interrupt flag handling without explicit acknowledge beyond watchdog register behavior, and requiring an IRQ even if only reset mode is desired. Test signals include all timeout buckets, active-at-boot restart, IRQ delivery, optional clock absence, restart path, and stop clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/npcm_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.c

## Purpose
`nv_tco.c` is a legacy miscdevice watchdog driver for NVIDIA nForce TCO timers. It discovers supported SMBus PCI functions, derives the TCO I/O base, disables TCO SMI delivery, enables reboot capability, and exposes `/dev/watchdog`.

## Important APIs, types, and functions
Global state includes `tcobase`, `timer_alive`, `tco_expect_close`, `tco_pci`, and a platform device. Hardware helpers are `tco_timer_start`, `tco_timer_stop`, `tco_timer_keepalive`, and `tco_timer_set_heartbeat`. Userspace handlers are `nv_tco_open`, `nv_tco_release`, `nv_tco_write`, and `nv_tco_ioctl`. Discovery and lifecycle are `nv_tco_getdevice`, `nv_tco_init`, `nv_tco_cleanup`, shutdown/remove, and module init/exit.

## Control flow
Module init registers a platform driver and synthetic platform device. Probe scans PCI devices against the TCO table, reads BAR/config registers to compute `tcobase`, reserves the TCO I/O region, sets a safe heartbeat, stops the timer, disables TCO SMI bits, sets the chipset reboot-enable bit, reports watchdog reset status, clears status, validates heartbeat, and registers `/dev/watchdog`. Open keepalives and starts; writes scan for magic `V` and reload; release stops only after magic close, otherwise keepalives. Cleanup stops unless nowayout and attempts to unset reboot capability.

## State and persistence
Hardware status bits survive warm boot and are cleared in probe. Software singleton state tracks single open and magic-close state. PCI config `MCP51_SMBUS_SETUP_B_TCO_REBOOT` is modified during probe, cleanup, and shutdown.

## Dependencies and integration points
It integrates PCI ID matching without binding a PCI driver, platform driver plumbing, I/O port region management, `nv_tco.h` register macros, miscdevice `WATCHDOG_MINOR`, and classic watchdog ioctls.

## Risks and test signals
Risks include global singleton assumptions, direct PCI config manipulation, confusing cleanup that disables future reboot ability, failure to handle shared SMBus ownership beyond not binding PCI driver, and legacy miscdevice behavior outside watchdog core policy. Test signals include supported PCI discovery, region conflicts, SMI disable failure, NO_REBOOT bit verification, heartbeat conversion boundaries, magic close, shutdown cleanup, and warm-boot status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.h

## Purpose
`nv_tco.h` defines the NVIDIA TCO register offsets and chipset-specific control bits used by `nv_tco.c`.

## Important APIs, types, and functions
The header provides address macros `TCO_RLD`, `TCO_TMR`, `TCO_STS`, `TCO_CNT`, and `MCP51_SMI_EN`, plus bit definitions for boot/timeout status, status reset masks, halt control, TCO reboot enable, and TCO SMI enable bits.

## Control flow
There is no executable control flow. The macros are expanded by the TCO driver to reload, configure, stop/start, detect reset cause, clear status, disable SMI, and adjust reboot behavior.

## State and persistence
The header describes hardware state only. `TCO_STS` bits can survive warm boots; `TCO_CNT_TCOHALT`, SMI enable, and reboot-enable bits alter live chipset behavior.

## Dependencies and integration points
It is private to `nv_tco.c` and depends on callers using a valid TCO base derived from chipset PCI config.

## Risks and test signals
Risks are incorrect base arithmetic, especially `MCP51_SMI_EN(base)` subtracting the TCO offset, and stale bit definitions for newer chipsets. Test signals are compile coverage, PCI hardware probe, status clear verification, halt/start behavior, and SMI/reboot bit readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/nv_tco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-main.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-main.c

## Purpose
`octeon-wdt-main.c` implements a Cavium OCTEON per-CPU watchdog. It keeps hardware watchdogs active even before userspace opens the device, supports software countdowns for long heartbeats, and coordinates NMI diagnostics before reset.

## Important APIs, types, and functions
Global state tracks hardware divisor, period/count values, heartbeat, `do_countdown`, per-CPU countdowns, enabled IRQ CPUs, and the OCTEON boot vector. Important functions are `octeon_wdt_cpu_online`, `octeon_wdt_cpu_pre_down`, `octeon_wdt_poke_irq`, `octeon_wdt_ping`, `octeon_wdt_calc_parameters`, `octeon_wdt_set_timeout`, `octeon_wdt_start`, `octeon_wdt_stop`, and `octeon_wdt_nmi_stage3`.

## Control flow
Module init allocates the boot vector, derives the watchdog tick divisor by OCTEON model, computes the largest valid period, registers a watchdog device, and installs CPU hotplug callbacks unless disabled. Each online CPU installs the NMI stage2 vector, requests/affines a watchdog IRQ, clears stale state, and enables interrupt/NMI/soft-reset mode. IRQs either poke hardware and decrement software countdown or disable the IRQ to allow NMI/reset progression. Userspace ping reloads every online CPU and re-enables IRQs if appropriate. NMI stage3 prints saved registers and CP0 state, then may trigger a soft reset on affected OCTEON3 models.

## State and persistence
State is global and per-CPU: hardware CIU watchdog registers, boot-vector entries, per-CPU countdown arrays, and IRQ-enabled masks. It persists only while the module is loaded, but hardware watchdogs remain live across CPU hotplug transitions until disabled by callbacks.

## Dependencies and integration points
It depends on MIPS/OCTEON low-level CSR APIs, CPU hotplug, irqdomain/affinity APIs, watchdog core, boot vector allocation, and `octeon-wdt-nmi.S` for the NMI register-save stage.

## Risks and test signals
Risks include per-CPU global arrays sized by `NR_CPUS`, watchdog IRQ affinity on CIU3 mappings, boot-vector lifetime during module unload, countdown math for very long or non-divisible heartbeats, and panic/reset behavior in NMI context. Test signals include single/SMP OCTEON boot, CPU hotplug online/offline, disable module parameter, heartbeat divisibility changes, userspace open/close, IRQ disable countdown expiry, and NMI register dump on forced hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-nmi.S -->
# sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-nmi.S

## Purpose
`octeon-wdt-nmi.S` is the second-stage OCTEON watchdog NMI handler. It saves MIPS GPR state in CVMSEG, creates a temporary stack, and calls the C diagnostic handler `octeon_wdt_nmi_stage3`.

## Important APIs, types, and functions
The exported symbol is `octeon_wdt_nmi_stage2`. Macros define `CVMSEG_BASE`, `CVMSEG_SIZE`, and `SAVE_REG(r)`. It uses CP0 CVMMEMCTL, debug scratch register `$31`, and the standard MIPS `NESTED`/`END` assembler annotations.

## Control flow
On NMI, the handler clears D-cache state for CVMSEG use, expands CVMSEG, restores `k0` saved by boot-vector code, saves all 32 GPRs at the top of CVMSEG, clears the remaining CVMSEG area, sets `sp` below the saved register frame, calls `octeon_wdt_nmi_stage3(saved_regs)`, and loops forever if the C handler returns.

## State and persistence
It writes volatile per-core CVMSEG memory only. Its saved register frame is consumed immediately by the C stage and is not persistent after reset.

## Dependencies and integration points
It is tightly coupled to `octeon-wdt-main.c`, OCTEON CVMSEG behavior, MIPS CP0 register conventions, and boot-vector stage1 code that branches here.

## Risks and test signals
Risks include corrupting kernel state in NMI context, incorrect CVMSEG sizing, register save layout mismatch with the C handler, and assembler portability across OCTEON/MIPS variants. Test signals include build coverage for OCTEON configs, forced watchdog NMI, register dump sanity, and multi-core simultaneous NMI output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-nmi.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/of_xilinx_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/of_xilinx_wdt.c

## Purpose
`of_xilinx_wdt.c` drives Xilinx AXI/XPS timebase watchdog devices described by devicetree. It starts/stops the two-stage enable sequence, services the timer, and calculates timeout from DT interval and clock frequency.

## Important APIs, types, and functions
`struct xwdt_device` contains MMIO base, interval, spinlock, watchdog device, and optional clock. Operations are `xilinx_wdt_start`, `xilinx_wdt_stop`, `xilinx_wdt_keepalive`, `xwdt_selftest`, `xwdt_probe`, and suspend/resume handlers.

## Control flow
Probe maps MMIO, reads `xlnx,wdt-interval` and `xlnx,wdt-enable-once`, obtains an optional prepared clock or fallback `clock-frequency`, computes timeout as twice the first overflow interval, runs a timebase self-test with the clock enabled, then registers the watchdog. Start enables the clock, clears previous status bits, sets enable bit 1 in CSR0, then enable bit 2 in CSR1. Stop clears both enable bits and disables the clock. Keepalive writes status bits to reset state.

## State and persistence
Hardware CSR bits store enabled and reset-status state. `enable_once` maps to watchdog nowayout. The clock is prepared by devm and enabled only during self-test or active watchdog operation.

## Dependencies and integration points
It depends on OF compatibles `xlnx,xps-timebase-wdt-1.00.a` and `1.01.a`, optional clock framework, DT properties, MMIO access, spinlock serialization, and watchdog core.

## Risks and test signals
Risks include timeout calculation overflow/zero from `1 << wdt_interval`, optional clock paths where `clk_enable(NULL)` behavior must remain valid, self-test false failures, and no set-timeout support because timeout is hardware/DT fixed. Test signals include DT with/without clock, missing properties, enable-once nowayout, self-test behavior, suspend/resume active watchdog, and start/stop register sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/of_xilinx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.c

## Purpose
`omap_wdt.c` controls TI OMAP 16xx/24xx/34xx non-secure 32 kHz watchdogs. It uses the watchdog core with runtime PM, posted-write synchronization, bootstatus reporting, and optional early enable.

## Important APIs, types, and functions
`struct omap_wdt_dev` stores the watchdog object, MMIO base, device, user-active flag, trigger pattern, and mutex. Important helpers are `omap_wdt_reload`, `omap_wdt_enable`, `omap_wdt_disable`, `omap_wdt_set_timer`, plus ops `start`, `stop`, `ping`, `set_timeout`, and `get_timeleft`.

## Control flow
Probe maps registers, sets default/min/max timeouts, initializes runtime PM, optionally reads platform reset sources, disables hardware unless `early_enable` is requested, registers the watchdog, and drops runtime PM. Start takes the mutex, marks users active, resumes the device, disables the watchdog to allow programming, sets prescaler and load, reloads, and enables. Stop disables and runtime-suspends. Set-timeout disables, writes load, enables, reloads, and updates core timeout. Shutdown/suspend disable only when users had started it; resume re-enables and reloads.

## State and persistence
Runtime state tracks active users and trigger pattern. Hardware count/load/control registers persist while powered. Bootstatus is derived from platform reset-source callback. No on-disk persistence exists.

## Dependencies and integration points
It depends on `omap_wdt.h`, platform data `omap-wd-timer`, OF compatible `ti,omap3-wdt`, runtime PM, watchdog core, and module parameters `nowayout`, `timer_margin`, and `early_enable`.

## Risks and test signals
Risks include busy-wait loops on posted-write status, runtime PM reference imbalance on error paths, early-enable double start, set-timeout interactions while inactive, and suspend behavior noted as questionable for nowayout. Test signals include bootstatus callback, early_enable, timeout min/max, runtime PM start/stop balance, suspend/resume active watchdog, and get-timeleft conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.h

## Purpose
`omap_wdt.h` defines OMAP watchdog register offsets, timeout bounds, prescaler value, and conversion macros used by `omap_wdt.c`.

## Important APIs, types, and functions
Key definitions include offsets for `REV`, `CNTRL`, `CRR`, `LDR`, `TGR`, `WPS`, and `SPR`; timeout bounds `TIMER_MARGIN_MIN/DEFAULT/MAX`; prescaler `PTV`; and macros `GET_WLDR_VAL(secs)` and `GET_WCCR_SECS(val)`.

## Control flow
There is no runtime control flow. The driver uses these constants to wait on posted-write status bits, write load/reload/control registers, and convert seconds to/from the 32 kHz counter domain.

## State and persistence
The header describes MMIO state and conversion policy. Timeout limits are software policy, not persistent state.

## Dependencies and integration points
It is private to the OMAP watchdog driver and assumes the non-secure 32 kHz watchdog register layout and `PTV == 0` conversion.

## Risks and test signals
Risks include conversion overflow for future larger timeout limits and mismatch with SoC variants using different prescalers or layouts. Test signals include compile coverage, boundary conversions for min/default/max timeout, and get-timeleft/load round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/orion_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/orion_wdt.c

## Purpose
`orion_wdt.c` supports Marvell Orion, Kirkwood, Dove, Armada 370/375/380/XP watchdogs. It abstracts SoC-specific clock, counter, reset-output, mask, and optional pretimeout behavior behind a shared watchdog core device.

## Important APIs, types, and functions
`struct orion_watchdog_data` provides offsets, enable bits, and SoC-specific callbacks. `struct orion_watchdog` stores watchdog object, timer/reset MMIO, clock, rate, and match data. Important functions are clock init variants, start/stop variants, `orion_wdt_ping`, `orion_wdt_enabled`, `orion_wdt_get_regs`, `orion_wdt_probe`, `orion_wdt_irq`, and `orion_wdt_pre_irq`.

## Control flow
Probe selects match data, maps timer and reset-output registers with backward-compatible fallback for legacy DTs, initializes the clock/rate, computes max timeout from 32-bit cycle count, normalizes module heartbeat, stops hardware unless already enabled, requests optional reset/panic IRQ and optional pretimeout IRQ, applies nowayout, and registers. Start delegates to the SoC variant to write counter, clear status, enable timer and reset output/mask. Ping reloads watchdog and optional timer1 pretimeout counter. Stop disables reset output and timer bits per variant.

## State and persistence
State is in timer counter/control/status registers, reset output registers, optional reset-output mask, clock enable state, and global `orion_wdt_info.options` when pretimeout IRQ exists. Hardware may be inherited running from bootloader and marked `WDOG_HW_RUNNING`.

## Dependencies and integration points
It depends on OF match data for Marvell compatibles, platform MMIO resources, clock framework including named fixed clocks, optional IRQs, watchdog pretimeout notification, and restart/reset output hardware.

## Risks and test signals
Risks include legacy hardcoded RSTOUT fallback, shared mutable `orion_wdt_info` causing pretimeout option leakage across devices, overflow in `clk_rate * timeout` writes, clock cleanup on probe failure, and optional IRQ semantics where primary IRQ panics. Test signals include every compatible mapping, missing second/third resources, fixed-clock fallback, running-at-boot detection, pretimeout IRQ, timeout maximum math, and shutdown stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/orion_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pc87413_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pc87413_wdt.c

## Purpose
`pc87413_wdt.c` is a legacy `/dev/watchdog` driver for National Semiconductor PC87413 super-I/O watchdog hardware. It enters/configures the SWC logical device, programs minute-granularity timeouts, and triggers the watchdog through SWC registers.

## Important APIs, types, and functions
Global state includes configurable index I/O port `io`, discovered `swc_base_addr`, minute `timeout`, single-open bit, magic-close flag, and `io_lock`. Low-level helpers select watchdog pin output, enable SWC, read base address, select bank 3, program WDTO, and toggle watchdog trigger bits. Userspace flow is handled by `pc87413_open`, `release`, `write`, and `ioctl`; lifecycle is `pc87413_init`, reboot notifier, and exit.

## Control flow
Init reserves the super-I/O index ports, registers a reboot notifier and miscdevice, configures the SWC logical device, discovers and reserves the SWC I/O range, enables the watchdog, and releases the index ports. Open enforces single access, optionally pins module if nowayout, and refreshes. Writes scan for magic `V` and refresh. Release disables only after magic close; otherwise it refreshes. Ioctl supports status, enable/disable, keepalive, and seconds API converted to minute hardware units. Reboot notifier disables on halt/down.

## State and persistence
Hardware configuration lives in super-I/O/SWC registers and may remain programmed until reset or driver exit. Software singleton state is global. Bootstatus is not supported.

## Dependencies and integration points
It uses I/O port access, region reservation, reboot notifier, miscdevice `WATCHDOG_MINOR`, classic watchdog ioctls, and module parameters `io`, `timeout`, and `nowayout`.

## Risks and test signals
Risks include fragile super-I/O configuration sequences, timeout conversion allowing zero minutes after small seconds values, enabling hardware during init before userspace opens, unlocked global state around close/open, and nowayout behavior mixed with exit cleanup. Test signals include request-region conflicts, SWC base discovery, magic-close, reboot notifier, timeout conversion boundaries, and enable/disable register readback on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pc87413_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pcwd.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pcwd.c

## Purpose
`pcwd.c` is the Berkshire ISA-PC Watchdog driver. It auto-detects legacy ISA cards by heartbeat bits, handles Rev A and Rev C differences, provides `/dev/watchdog`, and optionally exposes `/dev/temperature`.

## Important APIs, types, and functions
The global `pcwd_private` holds firmware string, revision, temperature support, command mode, boot status, I/O address, lock, timer, and next heartbeat. Important routines include `pcwd_isa_match`, `pcwd_isa_probe`, `send_isa_command`, `set_command_mode`, `pcwd_timer_ping`, `pcwd_start`, `pcwd_stop`, `pcwd_keepalive`, `pcwd_set_heartbeat`, status/temperature helpers, file operations, and ISA remove/shutdown.

## Control flow
ISA match reserves candidate ports and watches Rev A/Rev C heartbeat bits. Probe claims the region, determines revision, reads and clears boot status, initializes a kernel timer, disables the board, probes temperature support, logs firmware/switch info, picks heartbeat from module parameter or DIP switches, registers optional temperature and watchdog miscdevices. Open starts the board and timer; timer pings hardware only while userspace has refreshed `next_heartbeat`; write/ioctl keepalives extend that deadline. Close stops only after magic `V`; otherwise the timer continues toward reset.

## State and persistence
Runtime state is global because `/dev/watchdog` supports one card. Hardware boot/trip bits can survive reset until cleared. The driver keeps a software timer layered over the hardware timer to translate userspace heartbeat policy into frequent hardware pings.

## Dependencies and integration points
It integrates ISA driver probing, I/O ports, timers, miscdevices, classic watchdog ioctls, optional temperature minor, kernel poweroff on temperature panic, and module parameters `debug`, `heartbeat`, and `nowayout`.

## Risks and test signals
Risks include legacy probing false positives, timer-delete races, command-mode/temperature read conflicts, copy-to-user of only one byte for temperature, one-card global state, and `WDIOC_SETOPTIONS` returning `-EINVAL` even after handling options in some paths. Test signals include all ISA port candidates, Rev A vs Rev C, DIP-switch heartbeat, timer heartbeat loss, magic-close, temperature support, bootstatus clear, and remove/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pcwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_pci.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_pci.c

## Purpose
`pcwd_pci.c` is the Berkshire PCI-PC Watchdog driver. It binds a QuickLogic PCI watchdog card, sends command bytes through I/O ports, manages watchdog and temperature miscdevices, and supports time-left/status/temperature ioctls.

## Important APIs, types, and functions
Global `pcipcwd_private` stores temperature support, boot status, I/O base, lock, and PCI device. Key functions are `send_command`, `pcipcwd_start`, `pcipcwd_stop`, `pcipcwd_keepalive`, `pcipcwd_set_heartbeat`, `pcipcwd_get_status`, `pcipcwd_clear_status`, `pcipcwd_get_temperature`, `pcipcwd_get_timeleft`, file operations, reboot notifier, `pcipcwd_card_init`, and `pcipcwd_card_exit`.

## Control flow
PCI probe enables the device, requests BAR regions, reads and clears boot status, disables the card, detects temperature support, reads firmware and DIP switches, selects heartbeat, registers reboot notifier and miscdevices. Commands write data to ports 4/5, command to port 6, poll `WRSP`, then read response bytes. Open starts and keepalives; writes scan for magic `V` and keepalive; release stops only after magic close. Reboot notifier stops on halt/down. Remove stops unless nowayout and tears down miscdevices, notifier, regions, and PCI device.

## State and persistence
Hardware stores watchdog timeout, status, trip, relay, and temperature state. Boot/trip status is cleared at probe. Software single-open and magic-close state is global.

## Dependencies and integration points
It depends on PCI ID `11e3:5030`, I/O BAR access, reboot notifier, miscdevice `WATCHDOG_MINOR` and `TEMP_MINOR`, watchdog ioctl ABI, and module parameters `debug`, `heartbeat`, and `nowayout`.

## Risks and test signals
Risks include one-card global design, command timeout handling that returns boolean rather than errno, temperature byte-size userspace copies, active watchdog behavior on unplug/remove with nowayout, and lack of watchdog core integration. Test signals include PCI enable/region errors, firmware command timeout, DIP heartbeat, status clear/reset count, magic close, reboot notifier, temperature ioctl/device, and time-left command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_usb.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_usb.c

## Purpose
`pcwd_usb.c` drives the Berkshire USB-PC Watchdog HID device. It sends six-byte HID reports for watchdog commands, receives interrupt-in responses, and exposes watchdog and temperature miscdevices.

## Important APIs, types, and functions
`struct usb_pcwd_private` stores USB device/interface, interrupt URB/buffer, last command response, existence flag, and mutex. Important functions include `usb_pcwd_intr_done`, `usb_pcwd_send_command`, start/stop/keepalive/heartbeat/temperature/timeleft helpers, file operations, reboot notifier, `usb_pcwd_probe`, `usb_pcwd_disconnect`, and `usb_pcwd_delete`.

## Control flow
Probe accepts only the supported USB VID/PID HID interface with an interrupt-IN endpoint, allocates the private object, coherent interrupt buffer, and URB, submits the URB, marks the device existing, stops the watchdog, reads firmware and DIP switches, chooses heartbeat, registers reboot notifier, temperature miscdevice, and watchdog miscdevice, then stores interface data. Commands send HID `SET_REPORT`, wait up to 250 ms for the interrupt callback to set `cmd_received`, and copy response bytes. Open starts and keepalives; writes scan for magic `V`; release stops only after magic close. Disconnect stops unless nowayout, marks the device gone, deregisters devices/notifier, frees URB/buffer, and decrements the singleton count.

## State and persistence
Runtime state is global/single-device plus per-USB object state. Hardware stores timeout, watchdog enable, switch, firmware, and temperature state. There is no bootstatus reporting.

## Dependencies and integration points
It integrates USB core, HID report protocol constants, interrupt URBs, coherent DMA buffers, reboot notifier, miscdevice ABI, watchdog ioctl ABI, and module parameters `heartbeat` and `nowayout`.

## Risks and test signals
Risks include global `usb_pcwd_device` dereference after disconnect, races around `is_active` and disconnect despite a disconnect mutex only in disconnect path, command response matching only command byte, allocation via `kzalloc_obj`, and watchdog behavior on USB removal. Test signals include HID class/endpoint validation, URB resubmission errors, command timeout, disconnect while open, magic close, heartbeat from DIP switch, temperature/timeleft ioctls, and reboot notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pic32-dmt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pic32-dmt.c

## Purpose
`pic32-dmt.c` drives the Microchip PIC32 Deadman Timer. It exposes a fixed hardware-programmed timeout and services the timer through a two-step clear sequence gated by the DMT window.

## Important APIs, types, and functions
`struct pic32_dmt` stores MMIO registers and clock. Helpers include `dmt_enable`, `dmt_disable`, `dmt_bad_status`, `dmt_keepalive`, `pic32_dmt_get_timeout_secs`, and `pic32_dmt_bootstatus`. Watchdog ops are `pic32_dmt_start`, `pic32_dmt_stop`, and `pic32_dmt_ping`.

## Control flow
Probe maps DMT registers, enables the clock, reads the timeout from the programmed postscaler count divided by clock rate, maps reset control temporarily to read/clear DMT reset cause, forces nowayout, and registers the global watchdog device. Start sets `DMT_ON` and performs the keepalive sequence. Keepalive writes pre-clear key, waits for `WINOPN`, writes the second key, and checks bad-event bits. Stop clears `DMT_ON` and issues a `nop` before further register access.

## State and persistence
The timeout is determined by hardware registers and is not settable by this driver. Reset cause in the PIC32 reset controller is read and cleared. The global watchdog object means one instance is assumed.

## Dependencies and integration points
It depends on OF compatible `microchip,pic32mzda-dmt`, PIC32 register set/clear address helpers from platform data, clock framework, watchdog core, and reset-controller base constants.

## Risks and test signals
Risks include fixed nowayout, global watchdog object across possible multiple devices, busy waiting for the DMT window without explicit error on timeout beyond bad-status check, and direct `ioremap` of reset base outside devm. Test signals include timeout readback, reset-cause clear, windowed keepalive success/failure, start/stop, clock failure, and nowayout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pic32-dmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pic32-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pic32-wdt.c

## Purpose
`pic32-wdt.c` drives the Microchip PIC32 watchdog timer. It exposes a fixed timeout derived from hardware prescaler/postscaler configuration and services the watchdog with a 16-bit key write.

## Important APIs, types, and functions
`struct pic32_wdt` stores watchdog registers, reset-control base, and clock. Helpers include `pic32_wdt_is_win_enabled`, `pic32_wdt_get_post_scaler`, `pic32_wdt_get_clk_id`, `pic32_wdt_bootstatus`, `pic32_wdt_get_timeout_secs`, and `pic32_wdt_keepalive`. Ops are `pic32_wdt_start`, `stop`, and `ping`.

## Control flow
Probe maps registers and reset-control space, enables the clock, rejects windowed-clear mode, computes timeout from clock/32 and postscaler terminal count, reads/clears WDT reset cause, forces nowayout, and registers the global watchdog device. Start sets `ON` and writes the clear key; stop clears `ON` and executes `nop`; ping writes the clear key to the high halfword of WDTCON.

## State and persistence
Hardware configuration controls timeout and window mode. Reset cause survives until probe clears it. The software watchdog object is global and has no set-timeout path.

## Dependencies and integration points
It depends on OF compatible `microchip,pic32mzda-wdt`, PIC32 platform data macros, clock framework, watchdog core, and MMIO reset base mapping.

## Risks and test signals
Risks include unsupported windowed mode causing probe failure, fixed nowayout, global singleton watchdog, zero timeout if clock/postscaler math underflows, and direct reset-cause clearing during probe. Test signals include windowed-mode rejection, timeout calculation for all postscaler values, bootstatus clear, start/stop/ping key write, and clock/map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pic32-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pika_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pika_wdt.c

## Purpose
`pika_wdt.c` is a legacy miscdevice driver for PIKA FPGA watchdog hardware. It uses a short hardware watchdog timeout and a kernel timer to bridge a longer userspace heartbeat interval.

## Important APIs, types, and functions
Global `pikawdt_private` stores FPGA MMIO, next heartbeat, open bit, magic-close state, bootstatus, and timer. Important functions are `pikawdt_reset`, `pikawdt_ping`, `pikawdt_keepalive`, `pikawdt_start`, file operations, and module init/exit.

## Control flow
Init finds `pika,fpga`, maps it, reads firmware version, maps `pika,fpga-sd` to read POST watchdog reset status, initializes timer, and registers `/dev/watchdog`. Open enforces single access and starts a timer ticking every 500 ms. Timer writes the FPGA reset-control register while userspace heartbeat remains valid, or while not nowayout and the device is closed; otherwise it stops feeding and logs that reset will occur. Writes scan for magic `V` and extend heartbeat. Release deletes the timer when close is not expected, clears open state, and leaves hardware behavior to nowayout/timer state.

## State and persistence
State is global runtime state plus FPGA registers. POST reset cause is read at init. The FPGA watchdog cannot be disabled once enabled according to comments; software controls only whether to keep feeding it.

## Dependencies and integration points
It depends on OF node lookup/mapping, big-endian MMIO accessors, timers, miscdevice `WATCHDOG_MINOR`, classic watchdog ioctls, and module parameters `heartbeat` and `nowayout`.

## Risks and test signals
Risks include nonstandard release semantics where unexpected close deletes the software timer, no validation of `WDIOC_SETTIMEOUT`, hardware timeout comment mismatch with programmed value macro naming, and global singleton assumptions. Test signals include OF mapping failures, POST bootstatus, firmware version read, timer feed expiration, magic close, timeout ioctl validation gaps, and nowayout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pika_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pm8916_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pm8916_wdt.c

## Purpose
`pm8916_wdt.c` drives the Qualcomm PM8916 PON PMIC watchdog. It programs S1/S2 timers, supports optional bark interrupt pretimeout, decodes PMIC power-off reasons, and enables hard reset mode.

## Important APIs, types, and functions
`struct pm8916_wdt` stores parent PMIC regmap, watchdog object, and PON base address. Operations are `pm8916_wdt_start`, `stop`, `ping`, `configure_timers`, `set_timeout`, `set_pretimeout`, ISR, probe, and PM suspend/resume.

## Control flow
Probe gets the grandparent PMIC regmap and parent PON `reg` base, optionally requests the bark IRQ and selects pretimeout-capable info, reads two POFF reason bytes to set `bootstatus`, detects an already-enabled S2 reset bit, configures S2 reset type to hard reset, initializes timeout/pretimeout and timers, then registers the watchdog. Start sets S2 reset enable; stop clears it; ping writes PET. S1 timer is `timeout - pretimeout`; S2 timer is pretimeout. ISR checks bark real-time status and notifies pretimeout.

## State and persistence
PMIC registers hold timers, reset type, enable bit, pet bit, and power-off reason history. Bootstatus bits for watchdog, undervoltage, and overheat are surfaced until hardware clears them externally. Runtime software state is per platform device.

## Dependencies and integration points
It depends on PM8916 MFD/PON device hierarchy, regmap, OF compatible `qcom,pm8916-wdt`, optional IRQ, watchdog core, and PM suspend/resume.

## Risks and test signals
Risks include no validation that `pretimeout <= timeout` before writing `timeout - pretimeout`, reliance on parent/grandparent topology, bark IRQ status not explicitly acknowledged here, and stopping watchdog on suspend. Test signals include PMIC regmap absence, POFF reason combinations, active-at-boot detection, timeout/pretimeout boundary values, IRQ bark notification, hard reset programming failure, and suspend/resume active watchdog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pm8916_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pnx4008_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pnx4008_wdt.c

## Purpose
`pnx4008_wdt.c` drives the NXP PNX4008 watchdog timer and provides a restart handler that can force internal or external resets.

## Important APIs, types, and functions
Global state includes `wdt_base`, `wdt_clk`, `io_lock`, module `heartbeat`, and static `watchdog_device pnx4008_wdd`. Main functions are `pnx4008_wdt_start`, `pnx4008_wdt_stop`, `pnx4008_wdt_set_timeout`, `pnx4008_restart_handler`, and `pnx4008_wdt_probe`.

## Control flow
Probe initializes timeout from module parameter, maps registers, enables the clock, sets bootstatus from reset status, applies nowayout and restart priority, detects already-running hardware, and registers. Start resets the counter, waits for zero, programs match/reset/output/pulse registers, clears interrupt, writes match count from fixed 13 MHz rate, and enables counting with debug stop. Stop clears control. Restart handler interprets optional reboot command first character, then either forces match output/internal reset for soft reset or asserts reset output with a 1 ms pulse for hard reset, then delays for reset.

## State and persistence
Hardware control, match, interrupt, pulse, and reset status registers hold live state. The static watchdog object assumes a single instance. Bootstatus is read from reset status at probe.

## Dependencies and integration points
It depends on OF compatible `nxp,pnx4008-wdt`, clock framework, platform MMIO, watchdog core restart handler, reboot command conventions, and module parameters `heartbeat`/`nowayout`.

## Risks and test signals
Risks include global singleton state, no ping operation despite `WDIOF_KEEPALIVEPING`, fixed counter-rate assumption independent of actual clock, busy wait on counter reset, and restart handler returning after delay if reset fails. Test signals include bootstatus, already-running detection, start register sequence, restart hard/soft command modes, timeout min/max, and clock/map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pnx4008_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_noop.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_noop.c

## Purpose
`pretimeout_noop.c` implements the watchdog pretimeout governor named `noop`. It records a pretimeout event in the kernel log without otherwise changing system state.

## Important APIs, types, and functions
The file defines `pretimeout_noop`, `struct watchdog_governor watchdog_gov_noop`, and module init/exit functions calling `watchdog_register_governor` and `watchdog_unregister_governor`.

## Control flow
Module init registers the governor with the watchdog pretimeout framework. When selected and a driver calls `watchdog_notify_pretimeout`, the governor logs `watchdog%d: pretimeout event`. Module exit unregisters the governor.

## State and persistence
There is no persistent state beyond governor registration. Log output is the only side effect.

## Dependencies and integration points
It depends on `watchdog_pretimeout.h`, watchdog governor APIs, and watchdog devices with pretimeout support.

## Risks and test signals
Risks are minimal, but the module description says "Panic" despite noop behavior, which can confuse users. Test signals include module load/unload, governor selection, pretimeout event logging, and coexistence with other governors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_noop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_panic.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_panic.c

## Purpose
`pretimeout_panic.c` implements the watchdog pretimeout governor named `panic`. It intentionally panics the kernel when a pretimeout event fires.

## Important APIs, types, and functions
The file defines `pretimeout_panic`, `struct watchdog_governor watchdog_gov_panic`, and module init/exit wrappers for governor registration and unregistration.

## Control flow
Module init registers the governor. If selected, any watchdog pretimeout notification calls `panic("watchdog pretimeout event\n")`. Module exit unregisters the governor if the system has not panicked.

## State and persistence
There is no persistent state except framework registration. The side effect is a kernel panic, which may trigger crash dump/reboot policy outside this file.

## Dependencies and integration points
It depends on watchdog pretimeout governor APIs and kernel panic handling. Drivers such as MediaTek, Qualcomm, PM8916, Orion, and NPCM can feed events into this governor.

## Risks and test signals
Risks are deliberate high-impact behavior: selecting this governor turns a bark interrupt into immediate panic. Test signals include module load/unload, governor selection, forced pretimeout, panic notifier/crashdump integration, and ensuring non-selected governors are unaffected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pretimeout_panic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pseries-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/pseries-wdt.c

## Purpose
`pseries-wdt.c` exposes IBM POWER pSeries hypervisor watchdog support through the watchdog core. It uses the `H_WATCHDOG` hypercall to query capabilities, start, and stop a hypervisor-managed timer.

## Important APIs, types, and functions
`struct pseries_wdt` embeds `watchdog_device`, selected timeout action, and one-based watchdog number. Key functions are `pseries_wdt_start`, `pseries_wdt_stop`, `pseries_wdt_probe`, suspend, and resume. Hypercall flags encode start/stop/query and expiry actions.

## Control flow
Probe queries capabilities with `H_WATCHDOG`, allocates driver state, currently selects watchdog number 1, validates module `action`, computes min timeout from hypervisor milliseconds, seeds timeout from module parameter, applies nowayout and stop-on-reboot/unregister, then registers. Start sends `H_WATCHDOG` with start action, watchdog number, and timeout milliseconds. Stop sends stop and accepts `H_NOOP`. Suspend stops if active; resume restarts if active.

## State and persistence
The hypervisor owns actual timer state. The driver keeps selected watchdog number/action and core timeout state. No bootstatus is decoded.

## Dependencies and integration points
It depends on pSeries platform device `pseries-wdt`, POWER `plpar_hcall` APIs, watchdog core, and module parameters `action`, `timeout`, and `nowayout`.

## Risks and test signals
Risks include support for only watchdog number 1, no ping op so core keepalive depends on start/stop semantics, min/max unit conversion, hypervisor busy/hardware errors collapsed to `-EIO`, and advertised pretimeout option without set_pretimeout or event path. Test signals include unsupported hypervisor, action validation, min timeout handling, H_NOOP stop, suspend/resume active watchdog, stop-on-reboot, and hypercall error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/pseries-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/qcom-wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/qcom-wdt.c

## Purpose
`qcom-wdt.c` drives Qualcomm KPSS/APCS/APSS watchdog timer blocks. It supports multiple register layouts, optional bark interrupt pretimeout, bootstatus reporting, and system restart via a short bite timeout.

## Important APIs, types, and functions
`enum wdt_reg` names logical registers. `struct qcom_wdt_match_data` supplies register offsets, pretimeout capability, and max tick count. `struct qcom_wdt` stores watchdog object, clock rate, base, and layout. Operations are `qcom_wdt_start`, `stop`, `ping`, `set_timeout`, `set_pretimeout`, `restart`, ISR, running check, probe, and PM callbacks.

## Control flow
Probe gets OF match data, adjusts MMIO resource by optional `cpu-offset`, maps CPU0 watchdog registers, enables clock, validates rate against hardware max tick count, optionally requests bark IRQ and enables pretimeout info, computes max timeout from ticks/rate, sets default timeout, reads status for watchdog reset bootstatus, restarts already-running hardware with normalized settings, and registers. Start disables, resets, writes bark and bite counts, then enables. Pretimeout changes restart the watchdog with bark at `timeout - pretimeout`. Restart programs both bark and bite to about 128 ms and waits 150 ms.

## State and persistence
Hardware enable/status/bark/bite registers hold live state and reset cause. Runtime state stores the layout and rate. Hardware can be inherited running and marked `WDOG_HW_RUNNING`.

## Dependencies and integration points
It depends on OF compatibles `qcom,kpss-timer`, `qcom,scss-timer`, `qcom,kpss-wdt`, and `qcom,apss-wdt-ipq5424`, clock framework, platform IRQ, watchdog pretimeout APIs, PM callbacks, and restart handler support.

## Risks and test signals
Risks include modifying the platform resource start/end in place for `cpu-offset`, rate validation rejecting high-frequency clocks instead of using prescaling, pretimeout values equal/greater than timeout causing bark underflow, status bit interpretation differences across layouts, and stopping watchdog during suspend. Test signals include each compatible layout, cpu-offset DT, bark IRQ path, active-at-boot reprogramming, restart timing, timeout/pretimeout boundaries, clock-rate validation, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/qcom-wdt.c -->
