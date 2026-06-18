# subset-b-000746 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/vz.c -->
# sources/distributed-fs/ceph-client/arch/mips/kvm/vz.c

Purpose: implements the MIPS KVM backend for CPUs with VZ hardware virtualization. It wires KVM's MIPS callback table to VZ-specific CP0 context management, guest interrupt injection, guest timer handling, guest-exit emulation, TLB/GuestID maintenance, vCPU load/put/run paths, and module initialization.

Important APIs/functions: exposes `kvm_mips_callbacks`, `kvm_mips_emulation_init`, `kvm_vz_acquire_htimer`, and `kvm_vz_lose_htimer`; callback methods include `kvm_vz_vcpu_setup`, `kvm_vz_vcpu_load`, `kvm_vz_vcpu_put`, `kvm_vz_vcpu_run`, `kvm_vz_get_one_reg`, `kvm_vz_set_one_reg`, `kvm_trap_vz_handle_guest_exit`, and TLB-miss handlers. The code maintains CP0 config write masks, guest register index lists, MAAR handling, Loongson CPUCFG/Diag special cases, GuestCtl interrupt state, and guest VTLB sizing.

Control flow: initialization checks `cpu_has_vz` and registers the callback table. Per-vCPU setup seeds reset-state CP0 registers and timer frequency. CPU virtualization enable resizes/partitions guest TLB resources, configures GuestCtl0/1/2, GuestID caches, and CPU-specific Octeon/Loongson quirks. On vCPU entry, state is restored, interrupts are delivered, htimer may be acquired, GuestID/TLB state is refreshed, wired entries are loaded, and the low-level run function is invoked. Exits dispatch by guest exception code to GPSI, GSFC, hypercall, guest mode-change, MMIO load/store, coprocessor, and MSA paths.

State and persistence: persistent per-CPU state lives in `last_vcpu`, `last_exec_vcpu`, `cpu_data[].guestid_cache`, and `kvm_vz_guest_vtlb_size`; per-vCPU state includes software CP0 shadow registers, MAAR array, wired TLB backup, guest IDs per CPU, count/timer fields, pending exception bitmaps, and last scheduled/executed CPU. Hardware CP0 guest registers are saved/restored across scheduling and preemption boundaries; no disk persistence exists.

Dependencies and integration: depends on MIPS CP0 helpers, KVM MIPS common code, TLB helpers, hrtimer count emulation, FPU/MSA ownership code, tracepoints, kernel user-copy APIs, and CPU feature flags. It integrates with KVM ioctls through one-reg get/set/copy callbacks and with VM memory through GPA TLB handling and MMIO emulation.

Risks: correctness is highly sensitive to CP0 hazard ordering, guest timer handoff races, GuestID wrap/flushing, CPU feature asymmetry, writable Config masks, MMIO badvaddr GVA-to-GPA conversion, and failure paths that roll back guest PC. Wired TLB allocation uses `GFP_ATOMIC` and may preserve partial state on failure. Mismatched guest VTLB size across CPUs is treated as an error.

Test signals: build `CONFIG_KVM_MIPS_VZ` on supported MIPS variants, boot VZ guests, exercise KVM one-reg get/set ioctls, timer migration/preemption, SMP vCPU migration, MMIO load/store exits, FPU/MSA lazy ownership, GuestID wrap/TLB flush paths, Loongson-specific CPUCFG/Diag exits, and negative tests on CPUs without VZ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/vz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/Kconfig

Purpose: defines Lantiq MIPS SoC configuration choices, covering XWAY-family, Amazon SE, and Falcon targets plus optional built-in device tree and PCI support.

Important APIs/types/functions: Kconfig symbols include `SOC_TYPE_XWAY`, `SOC_AMAZON_SE`, `SOC_XWAY`, `SOC_FALCON`, `LANTIQ_DT_NONE`, `DT_EASY50712`, and `PCI_LANTIQ`. Selections pull in pinctrl, MFD syscon/core, PCI capability, and built-in DTB support.

Control flow: under `if LANTIQ`, the first choice selects one SoC family, and the second selects whether to embed a fallback DTB. `PCI_LANTIQ` is only available for XWAY with generic PCI enabled.

State and persistence: build-time configuration only; it persists as `.config` symbols and drives compilation.

Dependencies and integration: feeds `arch/mips/lantiq/Makefile`, board DTS inclusion, pinctrl drivers, and PCI support.

Risks: selecting a SoC without the matching device tree or required pinctrl/syscon support can produce an unbootable kernel. Built-in DTB is only a fallback when firmware does not pass one.

Test signals: Kconfig dependency checks, defconfig coverage for XWAY/Falcon, and boot tests with both firmware-supplied and built-in DTB paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/Makefile

Purpose: selects core Lantiq platform objects and descends into SoC-family subdirectories.

Important APIs/types/functions: always builds `irq.o`, `clk.o`, and `prom.o`; conditionally builds `early_printk.o`, `xway/`, and `falcon/`.

Control flow: object inclusion follows `CONFIG_EARLY_PRINTK`, `CONFIG_SOC_TYPE_XWAY`, and `CONFIG_SOC_FALCON`.

State and persistence: build-system state only.

Dependencies and integration: ties Kconfig selections to platform initialization, interrupt controller, clock, PROM, and SoC-specific sysctrl/reset code.

Risks: missing directory selection prevents `ltq_soc_detect()` or `ltq_soc_init()` providers from linking.

Test signals: Lantiq allmod/allyes builds and per-SoC defconfig link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.c

Purpose: provides a small legacy clock implementation for Lantiq MIPS platforms and initializes the MIPS high-precision timer frequency.

Important APIs/functions: `clkdev_add_static`, `clk_get_cpu`, `clk_get_fpi`, `clk_get_io`, `clk_get_ppe`, `clk_get_rate`, `clk_set_rate`, `clk_round_rate`, `clk_enable`, `clk_disable`, `clk_activate`, `clk_deactivate`, and `plat_time_init`. `get_counter_resolution()` reads hardware register `$3` via `rdhwr`.

Control flow: SoC-specific code calls `clkdev_add_static()` to seed CPU/FPI/IO/PPE rates. Generic clock accessors validate `struct clk`, then return stored rates or call callbacks. `plat_time_init()` calls `ltq_soc_init()`, computes `mips_hpt_frequency` from CPU rate and counter resolution, resets compare, and prints CPU clock.

State and persistence: static `cpu_clk_generic[4]` holds clock rates for the booted SoC; no dynamic parent tree or persistence exists.

Dependencies and integration: integrates with Linux `clkdev`, MIPS timer setup, and Lantiq SoC init code in XWAY/Falcon.

Risks: invalid clocks often return `0` or `-1` instead of standard errno. `clk_set_parent()` and `clk_get_parent()` are stubs. Timer frequency depends on correct CPU rate and counter resolution.

Test signals: boot log CPU clock value, timer tick stability, driver clock lookup for FPI/IO/PPE, and build checks with Lantiq SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.h -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.h

Purpose: declares the Lantiq legacy `struct clk`, common clock-rate constants, static clock registration API, and SoC-specific rate calculation functions.

Important APIs/types/functions: `struct clk` embeds `struct clk_lookup`, rate/rate-table fields, module/bits metadata, and optional callbacks for rate, enable, disable, activate, deactivate, and reboot. It declares XWAY-family rate helpers such as `ltq_danube_cpu_hz`, `ltq_vr9_fpi_hz`, `ltq_ar10_pp32_hz`, and `ltq_grx390_cpu_hz`.

Control flow: used by generic and SoC-specific clock providers to create `clkdev` entries and expose fixed or register-derived rates.

State and persistence: state is per allocated `struct clk`, usually static or early-allocated and registered with clkdev.

Dependencies and integration: consumed by `lantiq/clk.c`, `xway/clk.c`, `xway/sysctrl.c`, `falcon/sysctrl.c`, and GPTU clock registration.

Risks: duplicate `CLOCK_60M` macro definition is benign but noisy. The custom clock model lacks modern common-clk semantics.

Test signals: compile warnings, clock lookup behavior, and SoC boot rate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/early_printk.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/early_printk.c

Purpose: implements early console output for Lantiq ASC UARTs through `prom_putchar`.

Important APIs/functions: `prom_putchar(char c)` waits for the ASC TX FIFO to empty, optionally emits carriage return before newline, and writes a byte to the transmit buffer. Register addresses account for endianness.

Control flow: disables local IRQs, polls `LTQ_ASC_FSTAT`, writes `\r` for `\n`, writes the character, and restores IRQ state.

State and persistence: stateless except for hardware UART FIFO state.

Dependencies and integration: used by generic early printk paths when `CONFIG_EARLY_PRINTK`; depends on `LTQ_EARLY_ASC` and `ltq_r32/ltq_w8`.

Risks: busy-wait can hang if the UART base is wrong or hardware is wedged. It assumes early MMIO mappings and no locking beyond IRQ masking.

Test signals: early boot characters before full console init and correct CRLF handling on serial terminals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/Makefile

Purpose: builds Falcon-specific platform support.

Important APIs/types/functions: includes `prom.o`, `reset.o`, and `sysctrl.o`.

Control flow: unconditional within the Falcon subdirectory selected by parent Makefile.

State and persistence: build-system only.

Dependencies and integration: supplies Falcon `ltq_soc_detect()`, reboot hooks, and clock/sysctrl initialization.

Risks: omitting any object breaks Falcon boot or reset behavior.

Test signals: Falcon defconfig link and boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/prom.c

Purpose: detects Falcon SoC identity and installs NMI/EJTAG exception vector setup hooks.

Important APIs/functions: `ltq_soc_detect`, `ltq_soc_nmi_setup`, and `ltq_soc_ejtag_setup`. It decodes chip ID/config/type registers into part number, revision, subrevision, name, type, compatible string, and revision text.

Control flow: reads `FALCON_CHIPID`, `FALCON_CHIPCONF`, and `FALCON_CHIPTYPE`; maps Falcon subtype values to Falcon-D/V/M/default names; assigns board-level NMI and EJTAG setup callbacks that write handler addresses into boot-vector registers.

State and persistence: fills caller-owned `struct ltq_soc_info`; writes boot exception-vector MMIO registers.

Dependencies and integration: called by generic Lantiq `prom_init()` and depends on `lantiq_soc.h` register definitions plus MIPS trap handler symbols.

Risks: unknown part numbers call `unreachable()`. Incorrect vector writes can break debug/NMI handling.

Test signals: boot log SoC string, Falcon variant detection, NMI/EJTAG handler entry tests, and DT compatibility matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/reset.c

Purpose: provides Falcon reboot, halt, poweroff, and boot-source query support.

Important APIs/functions: `ltq_boot_select`, `machine_restart`, `machine_halt`, `machine_power_off`, and `mips_reboot_setup`.

Control flow: `arch_initcall` installs `_machine_restart`, `_machine_halt`, and `pm_power_off`. Restart disables interrupts, writes boot password registers and reset vector, then enables watchdog reset with magic values. Halt/poweroff disable interrupts and spin via `unreachable()`.

State and persistence: writes boot and watchdog MMIO registers; no software persistence.

Dependencies and integration: integrates with `asm/reboot.h` hooks and platform reset paths.

Risks: `ltq_boot_select()` is a dummy always returning SPI, so consumers cannot infer real boot media. Restart relies on magic register sequences.

Test signals: reboot command resets hardware, poweroff/halt paths stop execution, and watchdog reset is visible on Falcon boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/sysctrl.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/sysctrl.c

Purpose: maps Falcon system-control register blocks, initializes core clocks, enables the GPE/ONU core, and registers clkdev gates for platform devices.

Important APIs/functions: `ltq_soc_init`, `sysctl_activate`, `sysctl_deactivate`, `sysctl_clken`, `sysctl_clkdis`, `sysctl_reboot`, `falcon_gpe_enable`, and `clkdev_add_sys`. Global MMIO bases include `ltq_sys1_membase` and `ltq_ebu_membase`.

Control flow: `ltq_soc_init()` locates required DT nodes (`status`, `ebu`, `sys1`, `syseth`, `sysgpe`), requests/remaps resources, enables the GPE frequency path based on fuses, registers static CPU/FPI/IO clocks based on CPU divider, and adds device-specific clock gates for GPIO, pad, serial, and other modules.

State and persistence: stores ioremapped base pointers and early-allocated `struct clk` objects in clkdev. Register writes persist in SoC clock/reset hardware until reset.

Dependencies and integration: called by `plat_time_init()`; depends on OF resources, Lantiq MMIO helpers, `clkdev`, and Falcon DT compatible strings.

Risks: missing DT core nodes or failed remaps panic. Activation wait loops are fixed-count busy waits. Allocated clock structures are intentionally never freed.

Test signals: Falcon boot reaches timer init, clk lookups for registered device names succeed, GPE clock comes up, and system-control operations do not timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/sysctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/irq.c

Purpose: implements Lantiq ICU/EIU interrupt-controller support and hooks it into irqchip/irqdomain and MIPS CPU interrupt handling.

Important APIs/functions: `ltq_eiu_get_irq`, `ltq_enable_irq`, `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_eiu_settype`, `ltq_startup_eiu_irq`, `ltq_shutdown_eiu_irq`, `ltq_hw_irq_handler`, `icu_map`, `icu_of_init`, `get_c0_perfcount_int`, `get_c0_compare_int`, and `arch_init_irq`.

Control flow: `IRQCHIP_DECLARE` invokes `icu_of_init()` for `lantiq,icu`; it maps per-CPU ICU resources, disables and clears interrupts, initializes MIPS CPU IRQs, installs chained handlers for CPU IRQs 2.., creates a linear irqdomain, maps perfcount IRQ, and optionally maps EIU resources from DT. Chained handling reads ICU pending bits, applies silicon-bug `__fls()` filtering, translates to hwirq, and calls `generic_handle_domain_irq()`.

State and persistence: global state includes ICU/EIU MMIO bases, irqdomain pointer, EIU hwirq list, perfcount mapping, and spinlocks. Hardware interrupt enable, type, pending, and resend registers hold runtime state.

Dependencies and integration: depends on OF irq/address APIs, generic irqdomain, MIPS CPU IRQ controller, Lantiq EBU ack registers, and SMP affinity masks.

Risks: incorrect DT EIU lists break external IRQs. The handler trusts only the highest pending bit due to silicon behavior. EBU IRQs need special ack to avoid deadlock. Affinity fallback during hotplug can route to the current CPU.

Test signals: interrupt storm tests, GPIO/EIU edge/level type tests, SMP affinity changes, perf counter IRQ mapping, EBU device IRQ acking, and DT probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.c

Purpose: provides generic Lantiq PROM/platform initialization, command-line extraction, DT setup, system type reporting, and MIPS MT SMP override.

Important APIs/functions: exports `ebu_lock`; implements `get_system_type`, `ltq_soc_type`, `prom_init_cmdline`, `plat_mem_setup`, and `prom_init`.

Control flow: `prom_init()` calls SoC-specific `ltq_soc_detect()`, formats the system type, initializes firmware command line from `fw_arg0/fw_arg1`, and optionally registers SMP ops with a custom secondary init. `plat_mem_setup()` configures IO resources, sets KSEG1 IO port base, obtains FDT, and calls `__dt_setup_arch()`.

State and persistence: static `soc_info` holds detected platform data; `arcs_cmdline` is populated from firmware arguments; `ebu_lock` coordinates EBU users.

Dependencies and integration: depends on SoC-specific PROM code in XWAY/Falcon, MIPS bootinfo/prom APIs, memblock/OF FDT parsing, and clock/timer init.

Risks: missing DTB panics. Firmware command-line pointers are assumed valid after KSEG1 translation. SMP interrupt enabling is broad via `ST0_IM`.

Test signals: boot command line contents, system type string, DT memory discovery, and SMP secondary CPU startup on MIPS MT systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.h -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.h

Purpose: defines common Lantiq SoC information structures and declarations shared by generic and SoC-specific PROM code.

Important APIs/types/functions: `struct ltq_soc_info` carries `name`, revision fields, `partnum`, `type`, `sys_type`, and `compatible`; declarations for `ltq_soc_detect()` and `ltq_soc_init()`.

Control flow: SoC-specific detection fills this structure; generic `prom_init()` formats and exposes it.

State and persistence: the structure is caller-owned and typically stored in generic `prom.c` static state.

Dependencies and integration: included by XWAY/Falcon PROM and sysctrl code.

Risks: fixed-size revision/system strings require bounded formatting by callers.

Test signals: compile checks for all SoC providers and boot log system type correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/Makefile

Purpose: builds XWAY-family platform support.

Important APIs/types/functions: includes `prom.o`, `sysctrl.o`, `clk.o`, `dma.o`, `gptu.o`, `dcdc.o`, and `vmmc.o`.

Control flow: unconditional within the XWAY subdirectory selected by the parent Makefile.

State and persistence: build-system only.

Dependencies and integration: supplies SoC detection, clocks, PMU/sysctrl, DMA, timers, regulator log probe, and VMMC memory reservation.

Risks: broad unconditional object inclusion means DT compatibility and initcall ordering must keep unused devices harmless.

Test signals: XWAY defconfig link and boot tests across Danube/AR9/VR9/AR10/GRX390 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/clk.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/clk.c

Purpose: derives CPU, FPI/OCP, and PPE/PP32 clock rates for XWAY-family Lantiq SoCs from CGU registers.

Important APIs/functions: `ltq_danube_cpu_hz`, `ltq_danube_fpi_hz`, `ltq_danube_pp32_hz`, `ltq_ar9_cpu_hz`, `ltq_ar9_fpi_hz`, `ltq_vr9_cpu_hz`, `ltq_vr9_fpi_hz`, `ltq_vr9_pp32_hz`, `ltq_ar10_cpu_hz`, `ltq_ar10_fpi_hz`, `ltq_ar10_pp32_hz`, `ltq_grx390_cpu_hz`, `ltq_grx390_fpi_hz`, and `ltq_grx390_pp32_hz`.

Control flow: each function reads `ltq_cgu_r32()` at SoC-specific offsets, decodes selector/divider bitfields, and returns a fixed frequency constant or divided frequency. Danube derives CPU/FPI from DDR clock, newer XRX paths use `CGU_SYS_XRX` and `CGU_IF_CLK_AR10`.

State and persistence: stateless; all state comes from CGU hardware registers.

Dependencies and integration: declared in `clk.h` and consumed by `xway/sysctrl.c` when registering static clocks.

Risks: unknown selector values often return `0` or a default rate. Some comments note unresolved XTAL-frequency assumptions elsewhere.

Test signals: boot-time CPU clock print, measured timer frequency, and per-SoC CGU selector coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dcdc.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dcdc.c

Purpose: probes XRX200 DCDC regulator registers and logs core voltage.

Important APIs/functions: `dcdc_probe`, `dcdc_init`, `dcdc_match`, and `dcdc_driver`.

Control flow: `arch_initcall` registers a platform driver for `lantiq,dcdc-xrx200`; probe maps the first resource with devm helpers and reports `DCDC_BIAS_VREG1 * 8` millivolts.

State and persistence: static `dcdc_membase` stores mapped MMIO; no regulator state is modified.

Dependencies and integration: depends on OF platform binding and Lantiq MMIO helpers.

Risks: this is informational only and does not register with the regulator framework. Wrong DT resource prevents logging.

Test signals: DT match, successful resource mapping, and expected voltage line in boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dcdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dma.c

Purpose: provides low-level XWAY DMA engine setup and exported channel/port helper APIs for Lantiq drivers.

Important APIs/functions: `ltq_dma_enable_irq`, `ltq_dma_disable_irq`, `ltq_dma_ack_irq`, `ltq_dma_open`, `ltq_dma_close`, `ltq_dma_alloc_tx`, `ltq_dma_alloc_rx`, `ltq_dma_free`, `ltq_dma_init_port`, `ltq_dma_init`, and `dma_init`.

Control flow: platform probe maps DMA registers, enables/reset the DMA clock, disables interrupts, discovers channel count from `LTQ_DMA_ID`, resets each channel, and enables polling. Channel allocation allocates coherent descriptors, programs descriptor base/length, resets channel state, configures TX/RX direction, and enables descriptor interrupts.

State and persistence: global `ltq_dma_membase` and `ltq_dma_lock`; per-channel descriptor base, physical address, channel number, and device pointer live in `struct ltq_dma_channel`. Hardware registers persist channel configuration.

Dependencies and integration: exports symbols for Ethernet/PCI/peripheral drivers; uses Linux DMA coherent API, clk API, OF platform matching `lantiq,dma-xway`, and `xway_dma.h`.

Risks: probe panics on mapping or clock failure. Descriptor allocation uses `GFP_ATOMIC`; failure is not checked before programming hardware. Busy waits and global channel select register require locking.

Test signals: DMA probe log, descriptor IRQ delivery, TX/RX data-path tests, port burst/endian settings, and channel reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/gptu.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/gptu.c

Purpose: exposes the XWAY GPTU six-timer block as clkdev-controllable timer clocks.

Important APIs/functions: `gptu_probe`, `gptu_enable`, `gptu_disable`, `timer_irq_handler`, `gptu_hwinit`, `gptu_hwexit`, `clkdev_add_gptu`, and `gptu_init`.

Control flow: `arch_initcall` registers a `lantiq,gptu-xway` platform driver. Probe collects six IRQ resources, maps MMIO, enables the parent clock, powers the GPTU, validates the magic ID byte, then registers six named clocks `timer1a` through `timer3b`. Enabling a timer requests its IRQ, configures count/edge/sync/internal clock mode, enables IRQ bit, and starts auto reload; disabling reverses those steps.

State and persistence: static MMIO base and six IRQ resources; per-timer state lives in GPTU registers and clkdev objects.

Dependencies and integration: depends on platform DT IRQ/resource tables, parent clock support from XWAY sysctrl, and the generic IRQ layer.

Risks: driver structure is named `dma_driver`, a misleading local name. `request_irq()` uses NULL dev_id, so shared IRQ use would be unsafe. Magic-ID failure disables hardware and returns `-ENAVAIL`.

Test signals: GPTU probe log, successful clk_get/enable for timer names, IRQ ack behavior, and timer disable cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/gptu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/prom.c

Purpose: detects XWAY-family SoC IDs and maps them to human-readable names, Lantiq type constants, and DT compatible strings.

Important APIs/functions: `ltq_soc_detect`.

Control flow: reads `LTQ_MPS_CHIPID`, extracts part number and revision, formats `rev_type`, and switches over many Danube/Twinpass/Amazon SE/AR9/GR9/VR9/VRX220/AR10/GRX390 part IDs. Amazon SE panics if built with PCI.

State and persistence: fills the supplied `struct ltq_soc_info`; no persistent state beyond caller storage.

Dependencies and integration: called by generic Lantiq `prom_init()`; depends on SoC ID macros and MMIO register helpers from `lantiq_soc.h`.

Risks: unknown IDs call `unreachable()`. Multiple GR/VR variants share compatible strings and type constants, so downstream code must tolerate family grouping.

Test signals: boot SoC name/revision string for each supported chip ID and correct machine compatibility branches in `xway/sysctrl.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/sysctrl.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/sysctrl.c

Purpose: initializes XWAY-family PMU/CGU/EBU system-control blocks, registers clock gates and static clocks, and provides legacy PMU enable/disable exports.

Important APIs/functions: `ltq_soc_init`, `ltq_pmu_enable`, `ltq_pmu_disable`, `pmu_enable`, `pmu_disable`, `cgu_enable`, `cgu_disable`, `pci_enable`, `pci_ext_enable`, `pci_ext_disable`, `clkout_enable`, `clkdev_add_pmu`, `clkdev_add_cgu`, `clkdev_add_pci`, and `clkdev_add_clkout`.

Control flow: `ltq_soc_init()` finds DT core nodes for PMU/CGU/EBU, maps resources, clears EBU flash write-protect, registers generic clocks, selects VR9 register offsets if needed, conditionally adds PCI, then branches by machine compatibility to add SoC-specific static rates and PMU clock gates for USB, PCIe, Ethernet/PPE/switch, SDIO, DEU, USIF, MEI, GPHY, analog PHYs, and other blocks. `usb_set_clock()` adjusts USB CGU source bits.

State and persistence: global MMIO bases `pmu_membase`, `ltq_cgu_membase`, `ltq_ebu_membase`, mutable CGU offset variables, and a PMU spinlock. Registered clkdev objects persist for the kernel lifetime.

Dependencies and integration: called during Lantiq timer init; consumed by many platform drivers through `clk_get`; depends on OF matching, `clkdev`, Lantiq MMIO helpers, and SoC-specific rate helpers.

Risks: missing DT nodes or remaps panic. PMU enable failure panics, while disable failure only warns. Clock names are DT-address-string sensitive, and several `con_id` values use literal `"NULL"` rather than NULL.

Test signals: boot across all compatible strings, clk lookup for each platform device, PCI/USB/Ethernet probe success, PMU timeout absence, and static clock rate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/sysctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/vmmc.c -->
# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/vmmc.c

Purpose: reserves coherent memory for the Lantiq VMMC/CP1 voice processor and configures optional relay GPIOs.

Important APIs/functions: `ltq_get_cp1_base`, `vmmc_probe`, `vmmc_match`, and `vmmc_driver`.

Control flow: built-in platform driver probes `lantiq,vmmc-xway`, allocates 1 MiB coherent memory, stores its physical address as `cp1_base`, requests all unnamed GPIOs as output-high relays, names them `vmmc-relay`, and logs the reservation. Consumers call `ltq_get_cp1_base()` and panic if probe has not set the base.

State and persistence: static `cp1_base` persists after probe; coherent DMA allocation is kernel-lifetime.

Dependencies and integration: exports CP1 base to voice/firmware users; uses DMA coherent and GPIO descriptor APIs.

Risks: allocation failure is not checked before `CPHYSADDR`. Panicking accessor makes probe ordering important. GPIO failures are logged but not fatal.

Test signals: VMMC DT probe, non-null CP1 base export, relay GPIO state, and voice firmware users accessing the reserved region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/vmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/lib/Makefile

Purpose: selects MIPS-specific library objects for bit operations, checksum, delay, memory/string operations, atomic IRQ helpers, IO mapping, TLB dump support, and libgcc-style compiler intrinsics.

Important APIs/types/functions: builds `bitops.o`, `csum_partial.o`, `delay.o`, `memcpy.o`, `memset.o`, `mips-atomic.o`, `strncpy_user.o`, `strnlen_user.o`, `uncached.o`, `iomap_copy.o`, optional `iomap-pci.o`, `dump_tlb.o`, `r3k_dump_tlb.o`, and `bswapsi.o/bswapdi.o/multi3.o`.

Control flow: `CONFIG_GENERIC_CSUM` filters out assembly checksum; CPU/config symbols select PCI and TLB dump variants.

State and persistence: build-system only.

Dependencies and integration: feeds core kernel architecture library symbols and compiler runtime helpers.

Risks: wrong object selection can duplicate or omit fundamental symbols such as `memcpy`, checksum, or TLB dump routines.

Test signals: architecture build/link, boot smoke tests, network checksum tests, user-copy tests, and config matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/bitops.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/bitops.c

Purpose: provides fallback atomic bit operations for MIPS configurations without faster inline LL/SC implementations.

Important APIs/functions: exports `__mips_set_bit`, `__mips_clear_bit`, `__mips_change_bit`, `__mips_test_and_set_bit_lock`, `__mips_test_and_clear_bit`, and `__mips_test_and_change_bit`; also defines `__mips_xor_is_negative_byte`.

Control flow: each operation computes the target word and bit mask, disables local IRQs, updates memory, optionally captures old bit state, then restores IRQs.

State and persistence: mutates caller-provided memory only; no global state.

Dependencies and integration: used by generic bitops macros when no faster MIPS path is available; exports support modules and core code.

Risks: IRQ masking gives local atomicity but not cross-CPU atomicity unless these routines are only selected for appropriate uniprocessor/no-LLSC contexts. Volatile memory operations are intentionally simple.

Test signals: bitops selftests, lock bit behavior, SMP configuration review, and module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/bitops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/bswapdi.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/bswapdi.c

Purpose: supplies GCC/libgcc 64-bit byte-swap helper `__bswapdi2`.

Important APIs/functions: exports `notrace unsigned long long __bswapdi2(unsigned long long u)`.

Control flow: returns `___constant_swab64(u)`.

State and persistence: stateless.

Dependencies and integration: used when compiler emits a libgcc byte-swap call inside the kernel; includes swab and compiler headers.

Risks: must remain `notrace` and exported to satisfy early/runtime compiler-generated calls without recursion surprises.

Test signals: MIPS builds with compilers that emit `__bswapdi2`, byte-swap correctness, and symbol export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/bswapdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/bswapsi.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/bswapsi.c

Purpose: supplies GCC/libgcc 32-bit byte-swap helper `__bswapsi2`.

Important APIs/functions: exports `notrace unsigned int __bswapsi2(unsigned int u)`.

Control flow: returns `___constant_swab32(u)`.

State and persistence: stateless.

Dependencies and integration: used for compiler-generated byte-swap calls in kernel code.

Risks: same runtime-helper constraints as `bswapdi`: no tracing recursion and stable export.

Test signals: compiler/link tests and byte-swap unit coverage through users of `__builtin_bswap32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/bswapsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/csum_partial.S -->
# sources/distributed-fs/ceph-client/arch/mips/lib/csum_partial.S

Purpose: implements optimized MIPS IP checksum and checksum-copy routines, including user/kernel copy variants.

Important APIs/functions: exports `csum_partial`, `__csum_partial_copy_nocheck`, `__csum_partial_copy_to_user`, and `__csum_partial_copy_from_user`. Core macros include `ADDC`, `ADDC32`, `CSUM_BIGCHUNK`, and `__BUILD_CSUM_PARTIAL_COPY_USER`.

Control flow: `csum_partial` aligns the source, processes large 128/64/32-byte chunks with carry accumulation, handles tail bytes with endian-aware shifts, folds 64-bit sums when needed, handles odd starting alignment, then adds the incoming partial checksum. Copy variants combine aligned/unaligned copy loops with checksum accumulation and exception-table fixups for user/EVA accesses.

State and persistence: stateless except writes to destination buffers and exception fixup return values.

Dependencies and integration: used by networking checksums and copy/checksum helpers; depends on MIPS ABI register conventions, EVA support, exception tables, endian macros, and exported kernel checksum ABI.

Risks: assembly is sensitive to alignment, endianness, 32/64-bit mode, CPU errata workarounds, exception fixups, and carry propagation. Any incorrect tail handling corrupts network checksums.

Test signals: network stack checksum tests, ping/TCP/UDP data integrity, usercopy fault injection, EVA build/run coverage, and big/little endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/csum_partial.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/delay.c

Purpose: implements busy-wait delay loops for MIPS.

Important APIs/functions: exports `__delay`, `__udelay`, and `__ndelay`; internal arithmetic uses `lpj_fine`/`loops_per_jiffy`, `HZ`, `USEC_PER_SEC`, `NSEC_PER_SEC`, and `__delay`.

Control flow: `__delay()` loops until the requested loop count decrements to zero. Microsecond/nanosecond helpers scale time units into loop counts and call `__delay()`.

State and persistence: reads global loop calibration values; no local persistent state.

Dependencies and integration: used by `udelay`/`ndelay` architecture delay APIs and early platform code.

Risks: correctness depends on calibrated loops and overflow-safe arithmetic. CPU frequency changes can skew busy waits.

Test signals: delay calibration, timer-based delay measurements, and boot code using `udelay()` in hardware init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/dump_tlb.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/dump_tlb.c

Purpose: dumps R4x00-style MIPS TLB registers and active entries for debugging.

Important APIs/functions: `dump_tlb_regs`, `dump_tlb_all`, and internal `dump_tlb`/`msk2str`.

Control flow: saves current TLB-related CP0 state, iterates requested TLB indices, performs `tlb_read`, skips invalid/unused/unrelated ASID/MMID entries, formats page mask, VA, ASID/MMID, optional GuestID, RI/XI bits, physical addresses, cache attributes, dirty/valid/global bits, then restores saved CP0 state.

State and persistence: temporarily changes CP0 Index/PageMask/EntryHi and optional GuestCtl1, then restores them.

Dependencies and integration: used by MIPS TLB debug paths; depends on CP0 helpers, CPU feature flags, XPA/RI/XI/HTW support, and printk.

Risks: debug code touches privileged TLB state and must restore it exactly. Formatting assumes feature-dependent widths and entry layouts.

Test signals: manual TLB dump output on supported CPUs, no state corruption after dump, and config builds with GuestID/XPA/HTW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/dump_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/iomap-pci.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/iomap-pci.c

Purpose: implements legacy PCI IO port mapping helpers for MIPS.

Important APIs/functions: `__pci_ioport_map` and exported `pci_iounmap` under `CONFIG_PCI_DRIVERS_LEGACY`.

Control flow: IO port mapping derives the host controller from `dev->bus->sysdata`, uses `io_map_base`, and warns/falls back to `mips_io_port_base` if unset; multiple PCI domains can panic to avoid corruption. `pci_iounmap()` only calls `iounmap()` for addresses outside the controller IO resource window.

State and persistence: may initialize `ctrl->io_map_base` as a fallback.

Dependencies and integration: used by legacy PCI drivers and MIPS PCI controller structures.

Risks: fallback mapping is explicitly unsafe for multiple domains. Incorrect resource bounds can leak or unmap wrong IO regions.

Test signals: legacy PCI IO driver probe, multi-domain panic path review, and IO resource mapping/unmapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/iomap-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/iomap_copy.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/iomap_copy.c

Purpose: provides `__ioread64_copy` for copying MMIO data into memory in 64-bit units.

Important APIs/functions: exports `__ioread64_copy`.

Control flow: on 64-bit kernels, loops from source to end and copies via `__raw_readq`; on 32-bit kernels, delegates to `__ioread32_copy` with doubled count.

State and persistence: writes destination buffer only.

Dependencies and integration: used by generic IO copy helpers and device drivers reading MMIO FIFOs or buffers.

Risks: access order is not guaranteed and no barrier is issued. Caller must provide 64-bit aligned pointers and correct count.

Test signals: driver IO-copy tests, 32/64-bit build coverage, and device-specific data integrity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/iomap_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/libgcc.h -->
# sources/distributed-fs/ceph-client/arch/mips/lib/libgcc.h

Purpose: declares endian-aware unions and integer-mode typedefs used by MIPS in-kernel libgcc helper implementations.

Important APIs/types/functions: defines `word_type`, `struct DWstruct`, `DWunion`, and for 64-bit MIPS R6 `ti_type`, `struct TWstruct`, and `TWunion`.

Control flow: compile-time endian branches place high/low words in ABI-correct order; unsupported endian emits preprocessor error.

State and persistence: type definitions only.

Dependencies and integration: included by `multi3.c` and potentially other compiler-runtime helpers.

Risks: field order must match target endian/ABI, or compiler helper arithmetic returns incorrect values.

Test signals: endian build coverage and helper tests for multiword arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/libgcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/mips/lib/memcpy.S

Purpose: implements optimized MIPS `memcpy`, `memmove`, reverse copy, and raw user-copy routines with exception-table handling.

Important APIs/functions: exports `memmove`, `memcpy`, `__raw_copy_from_user`, and `__raw_copy_to_user`; internal `__rmemcpy` handles backward overlap. The `__BUILD_COPY_USER` macro generates legacy and EVA copy bodies with load/store fixups.

Control flow: forward copy aligns destination/source, uses prefetch and unrolled word/dword loops for aligned and unaligned cases, then handles tail bytes. `memmove` selects forward or reverse copy based on overlap. User-copy variants return remaining bytes after faults using exception handlers and task bad-address state.

State and persistence: mutates destination memory; no global state. Fault fixups report incomplete byte counts.

Dependencies and integration: fundamental kernel memory and usercopy ABI; depends on MIPS 32/64-bit mode, endian-specific unaligned load/store pairs, EVA instructions, exception tables, and CPU errata workarounds.

Risks: extremely sensitive to overlap direction, fault accounting, alignment, prefetch safety, and endian-specific first/rest load-store ordering. A bug can corrupt arbitrary kernel/user memory.

Test signals: lib/string tests, usercopy fault injection, overlap memmove tests, EVA builds, 32/64-bit and endian matrix builds, and boot stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/mips/lib/memset.S

Purpose: implements optimized MIPS `memset` and `__bzero` with user/EVA exception fixups.

Important APIs/functions: exports `memset` and `__bzero`; macros include `f_fill64`, `__BUILD_BZERO`, and exception wrapper `EX`.

Control flow: `memset` expands byte fill into a word/dword pattern, then the generated bzero/fill body handles small regions bytewise, aligns the destination, writes unrolled 64-byte blocks, writes partial words, and handles tail bytes. Exception fixups return remaining unset byte counts for bzero/user-style paths.

State and persistence: mutates destination memory only.

Dependencies and integration: core kernel memory primitive; depends on MIPS store-left/right support or byte fallback, microMIPS handling, EVA, exception tables, and R10K barriers.

Risks: alignment and fixup accounting are subtle. Incorrect fill expansion or store-left/right use corrupts memory; missing barriers can affect affected CPUs.

Test signals: string/memory selftests, fault-injection for bzero/user mappings, microMIPS and EVA builds, and boot memory initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/mips-atomic.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/mips-atomic.c

Purpose: implements local IRQ disable/save/restore for MIPS CPUs lacking the `di/ei` instruction support selected by `CONFIG_CPU_HAS_DIEI`.

Important APIs/functions: exports `arch_local_irq_disable`, `arch_local_irq_save`, and `arch_local_irq_restore`.

Control flow: each function disables preemption for the notrace sequence, manipulates CP0 Status IE bits via inline assembly, applies IRQ hazard barriers, and reenables preemption. Save returns prior Status; restore merges requested IE state back into CP0 Status.

State and persistence: mutates CP0 Status interrupt-enable state.

Dependencies and integration: used by low-level IRQ flag helpers and fallback bitops; depends on CP0 hazards and TX49 errata comments.

Risks: inline assembly must preserve only intended Status bits and respect hazards. Incorrect restore can enable interrupts too early or lose exception-level bits.

Test signals: IRQ enable/disable nesting tests, lockdep/interrupt tracing sanity, affected CPU boot tests, and preemption notrace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/mips-atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/multi3.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/multi3.c

Purpose: supplies `__multi3` for GCC 9 and older on 64-bit MIPS R6 when the compiler may emit suboptimal 128-bit multiply helper calls.

Important APIs/functions: conditional exported `__multi3`, with inline `dmulu` and `dmuhu` wrappers.

Control flow: splits operands into high/low 64-bit halves with `TWunion`, computes low product, high product, and cross terms, and returns the low 128 bits.

State and persistence: stateless.

Dependencies and integration: depends on `libgcc.h`, MIPS R6 `dmulu/dmuhu`, 64-bit mode, and GCC version guard.

Risks: conditional compilation must match compiler behavior. Endian union layout and signedness of low/high operations must remain correct.

Test signals: 128-bit multiplication tests on MIPS64R6 GCC < 10 and symbol absence on unsupported configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/multi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/r3k_dump_tlb.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/r3k_dump_tlb.c

Purpose: dumps R3000-style TLB registers and active entries for debugging.

Important APIs/functions: `dump_tlb_regs`, `dump_tlb_all`, and internal `dump_tlb`.

Control flow: saves current ASID from EntryHi, iterates indexed TLB entries with `tlbr`, skips unused KSEG0 entries and entries outside current ASID unless global, prints VA/ASID and EntryLo flags, then restores EntryHi ASID.

State and persistence: temporarily writes CP0 Index/EntryHi while dumping.

Dependencies and integration: selected by `CONFIG_CPU_R3000`; uses R3K EntryLo flag definitions and printk.

Risks: old TLB format differs from modern MIPS; using this on wrong CPU class would be invalid. Debug output lacks locking around concurrent context changes.

Test signals: R3000 build coverage and manual TLB dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/r3k_dump_tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/strncpy_user.S -->
# sources/distributed-fs/ceph-client/arch/mips/lib/strncpy_user.S

Purpose: implements assembly backend for copying a NUL-terminated string from user space.

Important APIs/functions: exports `__strncpy_from_user_asm`; uses exception macro `EX` and EVA `lbue` when configured.

Control flow: loops byte-by-byte from user source to kernel destination until NUL or count limit, increments copied count, checks for pointer wrap into kernel space, returns copied length/count, or returns `-EFAULT` via exception-table fixup.

State and persistence: writes destination buffer; no global state.

Dependencies and integration: used by MIPS `strncpy_from_user`; depends on exception tables, EVA user-load instruction, and R10K barrier macro.

Risks: user pointer wrap handling is a special-case guard; faults after partial copy return `-EFAULT` rather than partial length. Byte loop favors correctness over speed.

Test signals: usercopy string tests, fault injection on invalid user pointers, limit-boundary behavior, and EVA build/run coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/strncpy_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/strnlen_user.S -->
# sources/distributed-fs/ceph-client/arch/mips/lib/strnlen_user.S

Purpose: implements assembly backend for bounded user-string length calculation.

Important APIs/functions: exports `__strnlen_user_asm`; uses exception macro `EX` and EVA `lbe` when configured.

Control flow: computes stop pointer from start plus max length, scans one byte at a time until limit or NUL, returns length including the terminating NUL, and returns zero on fault.

State and persistence: reads user memory only.

Dependencies and integration: used by MIPS `strnlen_user`/`strlen_user`; depends on exception tables, EVA, and CPU DADDI workarounds.

Risks: comments note deliberate limited access into low KSEG0 for performance. Address wrap and 64-bit boundary behavior are delicate.

Test signals: user-string length tests for NUL, no-NUL limit, invalid pointer, and EVA/non-EVA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/strnlen_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/uncached.c -->
# sources/distributed-fs/ceph-client/arch/mips/lib/uncached.c

Purpose: runs a function through an uncached virtual mapping of both function address and stack.

Important APIs/functions: `run_uncached(void *func)`.

Control flow: reads current stack pointer, maps stack and target function from CKSEG0/CKSEG1 to CKSEG1 or from XKPHYS to uncached XKPHYS on 64-bit, BUGs on unsupported address ranges, then switches `$sp`, `jalr`s to the uncached function, restores `$sp`, and returns `$2`.

State and persistence: temporarily changes the CPU stack pointer during the call; no global state.

Dependencies and integration: used by cache/MMU-sensitive code that must execute uncached; depends on MIPS address-space macros.

Risks: only works for simple functions without stack arguments or complex return values. Unsupported addresses trigger `BUG()`. Caller must ensure cache coherency and interrupt expectations.

Test signals: platform cache init paths using `run_uncached`, 32/64-bit address mapping tests, and no stack corruption after return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/lib/uncached.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Kconfig

Purpose: defines machine choices and support options for Loongson 2E/2F Lemote platforms.

Important APIs/types/functions: symbols include `LEMOTE_FULOONG2E`, `LEMOTE_MACH2F`, `CS5536`, `CS5536_MFGPT`, `LOONGSON_UART_BASE`, and `LOONGSON_MC146818`.

Control flow: under `MACH_LOONGSON2EF`, a machine choice selects either Fuloong 2E or Loongson 2F family and pulls in CPU, PCI/ISA, early printk, DMA, endian, highmem, and timer dependencies. `CS5536_MFGPT` depends on CS5536 and disables high-res timer compatibility.

State and persistence: build-time `.config` state only.

Dependencies and integration: drives Loongson2EF Makefiles, CS5536 VSM inclusion, UART/RTC support, and timer source selection.

Risks: MFGPT timer selection is incompatible with high-resolution timers and required for some CPUFreq correctness per help text.

Test signals: defconfig coverage for 2E/2F boards, Kconfig dependency resolution, and boot timer correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Makefile

Purpose: selects common and machine-specific Loongson2EF platform directories.

Important APIs/types/functions: builds `common/` for `CONFIG_MACH_LOONGSON2EF`, `fuloong-2e/` for `CONFIG_LEMOTE_FULOONG2E`, and `lemote-2f/` for `CONFIG_LEMOTE_MACH2F`.

Control flow: object recursion follows machine Kconfig selections.

State and persistence: build-system only.

Dependencies and integration: connects Kconfig machine choice to common platform setup and board-specific reset/IRQ/DMA code.

Risks: wrong selection causes missing board hooks at link or boot.

Test signals: machine defconfig builds and board boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/Makefile

Purpose: builds shared Loongson2EF platform support and optional CS5536, serial, RTC, PCI, and suspend components.

Important APIs/types/functions: always includes setup/init/env/time/reset/irq/bonito-irq/mem/machtype/platform; optional objects include `pci.o`, `serial.o`, `uart_base.o`, `rtc.o`, `cs5536/`, and `pm.o`.

Control flow: object inclusion follows `CONFIG_PCI`, `CONFIG_LOONGSON_UART_BASE`, `CONFIG_EARLY_PRINTK`, `CONFIG_LOONGSON_MC146818`, `CONFIG_CS5536`, and `CONFIG_SUSPEND`.

State and persistence: build-system only.

Dependencies and integration: provides common boot, interrupt, memory, PCI, and platform-device infrastructure for board subdirectories.

Risks: `serial.o` can be selected by two symbols, so kbuild de-duplication matters. CS5536 VSM directory is required for 2F southbridge PCI config virtualization.

Test signals: Loongson2E/2F config link checks and optional feature matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/bonito-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/bonito-irq.c

Purpose: implements IRQ chip support for the Bonito/Loongson interrupt block.

Important APIs/functions: `bonito_irq_enable`, `bonito_irq_disable`, `bonito_irq_type`, and `bonito_irq_init`.

Control flow: init assigns `bonito_irq_type` and `handle_level_irq` to 32 IRQs starting at `LOONGSON_IRQ_BASE`; Loongson2E additionally requests the DMA timeout IRQ with `no_action`. Enable/disable write bit masks to `LOONGSON_INTENSET`/`LOONGSON_INTENCLR` and flush with `mmiowb()`.

State and persistence: hardware interrupt enable registers hold state.

Dependencies and integration: used by Loongson common IRQ init; depends on `loongson.h` register macros and generic IRQ APIs.

Risks: IRQ arithmetic uses `d->irq - LOONGSON_IRQ_BASE`; wrong IRQ numbering writes wrong bits. The DMA timeout IRQ is reserved only by a no-op handler.

Test signals: interrupt enable/disable tests, DMA timeout reservation log, and level IRQ handling on Loongson2E/2F.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/bonito-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/Makefile

Purpose: builds AMD CS5536 southbridge Virtual Support Module components for Loongson2F platforms.

Important APIs/types/functions: `CONFIG_CS5536` builds PCI, IDE, ACC, OHCI, ISA, and EHCI VSM objects; `CONFIG_CS5536_MFGPT` builds MFGPT timer support.

Control flow: object inclusion follows CS5536 Kconfig symbols.

State and persistence: build-system only.

Dependencies and integration: VSM objects virtualize CS5536 PCI config space through MSR-backed register emulation.

Risks: omitting a VSM object can make southbridge functions invisible or unconfigurable.

Test signals: CS5536 PCI enumeration, USB/IDE/ISA function config accesses, and optional MFGPT timer boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_acc.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_acc.c

Purpose: virtualizes PCI configuration space for the CS5536 ACC function using MSR-backed hardware state.

Important APIs/functions: `pci_acc_write_reg` and `pci_acc_read_reg`.

Control flow: writes handle PCI command bus mastering through `GLIU_PAE`, parity status clearing through `SB_ERROR`, BAR probing/allocation through soft BAR flag and `GLIU_IOD_BM1`, and interrupt routing through `PIC_YSEL_LOW`. Reads synthesize vendor/device, command/status, class revision, BAR, subsystem, ROM, capability, and interrupt-line values.

State and persistence: hardware MSRs hold BAR, error, bus-master, and interrupt-routing state; soft BAR probe flags are stored in `GLCP_SOFT_COM`.

Dependencies and integration: called by CS5536 PCI config virtualization layer; depends on `cs5536.h` and `cs5536_pci.h` macros and `_rdmsr/_wrmsr`.

Risks: BAR probing uses side-effect soft flags that are cleared on read. Incorrect MSR bit packing breaks IO decoding or interrupts.

Test signals: PCI config-space reads/writes for ACC, BAR sizing, bus-master enable toggles, parity clear behavior, and interrupt line reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_acc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ehci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ehci.c

Purpose: virtualizes PCI configuration space for the CS5536 EHCI USB function.

Important APIs/functions: `pci_ehci_write_reg` and `pci_ehci_read_reg`.

Control flow: command writes update EHCI MSR memory/bus-master bits; status writes clear parity error flags; BAR0 writes either set the soft sizing flag or program EHCI base and GLIU P2D mapping; EHCI legacy SMI and frame-length adjustment registers map into EHCI MSR high bits. Reads synthesize standard PCI header fields plus EHCI-specific legacy status and FLADJ values.

State and persistence: EHCI USB MSRs, GLIU mapping registers, southbridge error state, and soft BAR flags.

Dependencies and integration: used by CS5536 VSM PCI dispatcher for the EHCI function; integrates with USB EHCI driver enumeration.

Risks: memory BAR handling must preserve MMIO vs IO-space semantics. Legacy SMI bit masks are partial and must match hardware layout.

Test signals: EHCI PCI enumeration, BAR sizing/programming, USB host controller probe, parity status clearing, and legacy register access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ehci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ide.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ide.c

Purpose: virtualizes PCI configuration space for the CS5536 IDE controller.

Important APIs/functions: `pci_ide_write_reg` and `pci_ide_read_reg`.

Control flow: command writes control bus mastering through `GLIU_PAE`; BAR4 writes support sizing through soft flags or program IDE IO BAR plus GLIU IOD mapping; IDE config/timing/control/power registers map directly to IDE MSRs; a flash signature write toggles DIVIL ball options. Reads synthesize PCI identity/status/class/cache/BAR/capability/interrupt fields and return IDE MSR-backed control registers.

State and persistence: IDE, GLIU, GLCP, DIVIL, and SB MSRs store emulated PCI state.

Dependencies and integration: used by CS5536 VSM for IDE PCI config; integrates with Linux IDE/ATA probing.

Risks: only BAR4 is meaningful; incorrect IO range packing can break IDE register decoding. Flash-signature special case has hidden hardware side effects.

Test signals: IDE PCI config enumeration, BAR sizing/programming, timing register read/write, bus-master enable, and storage probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_isa.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_isa.c

Purpose: virtualizes PCI configuration space and local BARs for the CS5536 ISA bridge.

Important APIs/functions: `pci_isa_write_bar`, `pci_isa_read_bar`, `pci_isa_write_reg`, `pci_isa_read_reg`, and `cs5536_isa_mmio_always_on`.

Control flow: BAR helpers handle sizing via soft flags or program DIVIL LBARs and SB RCONF mappings. PCI command IO enable toggles DIVIL LBAR enablement. Status writes clear selected SB error flags. UART interrupt pseudo-registers program PIC route selectors. Reads synthesize standard bridge config fields, BARs, error-derived status, class revision, and interrupt-line values. A PCI fixup marks ISA MMIO always-on to protect early MFGPT timer interrupts.

State and persistence: static arrays map BAR indexes to MSR registers, soft flags, ranges, and lengths; hardware MSRs persist BAR/error/interrupt routing state.

Dependencies and integration: part of CS5536 VSM; depends on PCI fixup framework and MSR helpers. Supports SMB, GPIO, MFGPT, IRQ, PMS, and ACPI local bars.

Risks: BAR index validity is assumed by callers. The MMIO-always-on fixup prevents timer hangs during PCI config races and must not be removed without replacing that guarantee.

Test signals: ISA bridge PCI enumeration, BAR sizing/programming, UART interrupt routing, error status clear tests, and MFGPT timer operation during PCI probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_mfgpt.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_mfgpt.c

Purpose: implements CS5536 MFGPT0 timer as a periodic clock event and optional low-rated clocksource.

Important APIs/functions: exports `disable_mfgpt0_counter` and `enable_mfgpt0_counter`; defines `mfgpt_timer_set_periodic`, `mfgpt_timer_shutdown`, `timer_interrupt`, `setup_mfgpt0_timer`, `mfgpt_read`, `clocksource_mfgpt`, and `init_mfgpt_clocksource`.

Control flow: setup configures clockevent parameters, routes comparator 2 through interrupt mapper/gate, reads MFGPT base, registers the clockevent, and requests the timer IRQ. The IRQ handler refreshes variable base, acknowledges comparator status, and calls the event handler. The clocksource emulates a free-running counter from `jiffies * COMPARE + count`, clamping count if an underflow has not yet advanced jiffies.

State and persistence: raw spinlock protects timer access; static `mfgpt_base`, `old_count`, and `old_jifs` track hardware base and monotonic read smoothing. Hardware counter/setup registers persist timer mode.

Dependencies and integration: selected by `CONFIG_CS5536_MFGPT`; depends on CS5536 MSR/IO port definitions, clockevents, clocksource, jiffies, and IRQ framework.

Risks: oneshot mode is intentionally unsupported due to high deviation. Clocksource is not registered on SMP because MFGPT does not scale. Read function has side effects under seqlock retry, documented and lock-protected.

Test signals: periodic tick delivery, suspend/resume timer reenable, clocksource registration only on UP, CPUFreq/system time stability, and IRQ ack behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_mfgpt.c -->
