# Research: subset-b-004002

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-misc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-misc.c

## Purpose
Implements the Atheros/QCA AR71xx/AR724x/AR913x MISC interrupt controller as a cascaded IRQ domain beneath a parent interrupt. The controller exposes 32 miscellaneous sources and publishes the CPU performance counter interrupt through `get_c0_perfcount_int()`.

## Important APIs, Types, and Functions
Key entry points are `ath79_misc_intc_of_init()`, `ar7100_misc_intc_of_init()`, and `ar7240_misc_intc_of_init()` through `IRQCHIP_DECLARE`. `ath79_misc_irq_handler()` is the chained handler, `misc_map()` installs `ath79_misc_irq_chip`, and mask/unmask/ack helpers manipulate the MISC enable/status registers. The exported `get_c0_perfcount_int()` integrates with MIPS timer/perf users.

## Control Flow
OF init parses the parent IRQ, maps the register block, creates a linear 32-entry domain, creates the perf-counter mapping for hwirq 5, disables and clears all sources, then attaches the chained handler. On parent IRQ entry, status is ANDed with enable, each set bit is dispatched via `generic_handle_domain_irq()`, and empty pending state is reported as spurious.

## State and Persistence
State is limited to MMIO enable/status bits, `domain->host_data`, and the global `ath79_perfcount_irq`. Chip callbacks flush writes with readbacks. AR7100 and AR7240 variants mutate the static chip callbacks to provide mask-ack or explicit ack behavior.

## Dependencies and Integration Points
Depends on OF address/IRQ parsing, Linux irqdomain, chained IRQ helpers, and raw MMIO access. It is a child of the SoC root interrupt path and feeds generic Linux IRQ handlers as level interrupts.

## Risks and Test Signals
Risks include variant-specific ack semantics, missing parent IRQ/registers, spurious parent interrupts, and global chip callback mutation if multiple incompatible instances were ever described. Test signals are boot logs without init errors, correct perf counter IRQ mapping, `/proc/interrupts` activity for MISC children, and no repeated spurious interrupt reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ath79-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.c

## Purpose
Provides shared support for Atmel AT91 AIC and AIC5 interrupt controllers. It centralizes trigger/priority encoding, generic-chip domain allocation, external interrupt policy, and SoC-specific RTC/RTT interrupt fixups.

## Important APIs, Types, and Functions
`struct aic_chip_data` stores per-generic-chip external IRQ masks. Exported internal helpers include `aic_common_set_type()`, `aic_common_set_priority()`, `aic_common_irq_domain_xlate()`, `aic_common_of_init()`, `aic_common_rtc_irq_fixup()`, and `aic_common_rtt_irq_fixup()`. `aic_common_shutdown()` delegates shutdown to the chip mask callback.

## Control Flow
`aic_common_of_init()` maps the controller, allocates per-chip private data, creates a linear irqdomain sized to 32-entry chip chunks, allocates generic chips with `handle_fasteoi_irq`, initializes generic-chip methods and wake policy, parses `atmel,external-irqs`, and invokes machine fixups selected by `of_machine_get_match_data()`.

## State and Persistence
Persistent state includes mapped controller registers, allocated `aic_chip_data` array, generic-chip `mask_cache`/wake state, and external IRQ bitmasks. RTC/RTT fixups directly clear peripheral interrupt enables to avoid stale interrupt state before the AIC takes over.

## Dependencies and Integration Points
This file is used by `irq-atmel-aic.c` and `irq-atmel-aic5.c`. It depends on generic irqchip infrastructure, OF matching, MMIO, and Atmel DT bindings using three interrupt cells: hwirq, trigger type, and priority.

## Risks and Test Signals
Risks include invalid priorities, unsupported low/falling types on non-external IRQs, memory leaks on partial init failures, and missing peripheral fixups causing boot-time interrupt storms. Test signals are successful AIC/AIC5 domain creation, correct DT xlate rejection for bad cells, wake mask behavior across suspend, and quiet boot on affected RTC/RTT SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.h

## Purpose
Declares the shared AIC helper interface consumed by the AT91 AIC and AIC5 drivers.

## Important APIs, Types, and Functions
The header exposes trigger encoding (`aic_common_set_type()`), priority encoding (`aic_common_set_priority()`), DT interrupt translation (`aic_common_irq_domain_xlate()`), common OF/generic-chip setup (`aic_common_of_init()`), and RTC/RTT fixup hooks.

## Control Flow
There is no runtime control flow in the header. It defines the contract that concrete AIC drivers follow: call common OF init, specialize chip registers/callbacks, then install their root IRQ handler.

## State and Persistence
No state is declared here. State lives in the common C file and in each concrete driver through irqdomains, generic chips, and MMIO state.

## Dependencies and Integration Points
Requires Linux irqdomain, OF device-node, and IRQ type definitions from included translation units. It couples the AIC and AIC5 drivers to a shared three-cell DT interrupt format and common SoC fixup behavior.

## Risks and Test Signals
Risks are ABI-style: changing prototypes or semantics affects both AIC implementations. Test signals are successful builds of both drivers and consistent behavior for trigger, priority, and fixup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic.c

## Purpose
Implements the original 32-line Atmel AT91 Advanced Interrupt Controller as a root interrupt controller for ARM AT91 systems.

## Important APIs, Types, and Functions
`aic_of_init()` is registered for `atmel,at91rm9200-aic`. `aic_handle()` is the root IRQ entry. `aic_retrigger()`, `aic_set_type()`, PM callbacks, `aic_hw_init()`, and `aic_irq_domain_xlate()` specialize common AIC services. SoC fixup functions connect machine compatibles to RTC/RTT cleanup.

## Control Flow
Init rejects duplicate domains, calls `aic_common_of_init()` for a 32-line domain, fills generic-chip register offsets and callbacks, initializes hardware, then installs `set_handle_irq(aic_handle)`. The handler reads IVR/ISR; no active IRQ causes an EOI write, otherwise the domain IRQ matching IVR is dispatched.

## State and Persistence
Global `aic_domain` anchors the controller. Generic-chip mask and wake caches persist across callbacks. Hardware state includes SMR priority/type fields, SVR vector values, enable/disable/clear bits, and EOI state. PM callbacks save runtime mask/wake policy into hardware during suspend/resume or shutdown.

## Dependencies and Integration Points
Depends on `irq-atmel-aic-common`, ARM exception IRQ entry, OF irqchip declaration, and generic irqchip. The DT binding uses hwirq/type/priority cells and machine compatible strings for fixups.

## Risks and Test Signals
Risks include incorrect priority writes during xlate, unsupported trigger types, missed EOI causing locked nIRQ, and stale RTC/RTT sources. Test signals are clean boot with root handler installed, active IRQs reflected in `/proc/interrupts`, suspend/resume wake filtering, and no spurious AIC lockout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic5.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic5.c

## Purpose
Implements newer Atmel/Microchip AIC5 controllers, which can expose up to 128 interrupt lines through a selected-source register interface.

## Important APIs, Types, and Functions
Registered init wrappers cover SAMA5D2, SAMA5D3, SAMA5D4, SAM9X60, and SAM9X7 compatibles. Core logic is in `aic5_of_init()`, `aic5_handle()`, `aic5_mask()`, `aic5_unmask()`, `aic5_retrigger()`, `aic5_set_type()`, PM callbacks, and `aic5_irq_domain_xlate()`.

## Control Flow
Variant init chooses the IRQ count and optionally allocates `smr_cache`. Common init builds the domain/generic chips. The driver fills chip callbacks for each 32-line chunk, initializes every source by selecting it in SSR, programming SVR, disabling, and clearing, then installs the root handler. Dispatch reads IVR/ISR and handles or EOIs like classic AIC.

## State and Persistence
`aic5_domain` is global. AIC5 shared registers require locking on the first generic chip while selecting SSR. PM may persist SMR values in `smr_cache`, and generic-chip `mask_cache`/`wake_active` drive suspend/resume masking.

## Dependencies and Integration Points
Uses common AIC helpers, generic irqchip, OF irqchip declarations, and ARM root IRQ handling. Integrates with SoC fixups for RTC/RTT and with DT three-cell interrupt specs.

## Risks and Test Signals
Risks include SSR races, incorrect per-SoC IRQ counts, missing SMR restore on SAMA5D2, and mask-cache divergence because all chips share one register selector. Test signals include successful boot on each compatible, trigger/priority programming per DT, working wake behavior, and no invalid hwirq access past `revmap_size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2712-mip.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2712-mip.c

## Purpose
Implements the Broadcom BCM2712 MIP MSI-X interrupt controller as an MSI parent domain layered over a parent interrupt domain, typically GIC.

## Important APIs, Types, and Functions
`struct mip_priv` stores MMIO, MSI message address, SPI base/range/offset, bitmap allocator, parent domain, and device. Key functions are `mip_parse_dt()`, `mip_init_domains()`, `mip_middle_domain_alloc()`, `mip_middle_domain_free()`, `mip_compose_msi_msg()`, and platform probe registration through `IRQCHIP_PLATFORM_DRIVER`.

## Control Flow
Probe allocates private data, parses `msi-ranges`, optional `brcm,msi-offset`, and a second `reg` entry as MSI write address, maps MMIO, allocates the hwirq bitmap, then creates an MSI parent domain. Allocation reserves a power-of-two bitmap region, maps it to parent SPI hwirqs, configures parent IRQs as edge rising, installs the MIP middle chip, and marks IRQs single-target/affinity-on-activate.

## State and Persistence
Persistent state includes the allocation bitmap, MMIO mask/config registers, MSI address, parent domain reference, and per-IRQ chip data pointing back to `mip_priv`. Hardware is configured host-unmasked, VPU-masked, edge-triggered.

## Dependencies and Integration Points
Uses `irq-msi-lib`, generic MSI parent ops, OF MSI range parsing, platform irqchip probing, and parent-domain allocation. It serves PCI MSI/MSI-X through `DOMAIN_BUS_GENERIC_MSI` selection.

## Risks and Test Signals
Risks include malformed `msi-ranges`, alignment assumptions in bitmap allocation, hwirq offset/base confusion, and leaked allocations if parent setup partially fails. Test signals are MSI domain creation logs, PCI MSI/MSI-X allocation success, correct composed MSI address/data, and interrupt delivery through parent GIC SPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2712-mip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2835.c

## Purpose
Implements the BCM2835/BCM2836 ARMCTRL interrupt controller handling banked GPU/peripheral interrupts, including BCM2835 root operation and BCM2836 chained operation.

## Important APIs, Types, and Functions
`struct armctrl_ic` stores register pointers and the domain. `armctrl_of_init()` performs setup for both variants, `armctrl_xlate()` maps bank/bit cells to packed hwirqs, and `bcm2835_handle_irq()`/`bcm2836_chained_handle_irq()` dispatch pending interrupts. `get_next_armctrl_hwirq()` handles bank and shortcut quirks.

## Control Flow
Init maps registers, creates a linear domain for three banks, creates mappings for valid bank bits, installs level handlers, disables bootloader-left enabled IRQs/FIQ, and either installs a root handler or chains to a parent IRQ. Dispatch repeatedly reads bank0, resolves shortcuts/bank indicators, and calls `generic_handle_domain_irq()`.

## State and Persistence
State is global `intc`, register pointer arrays, and hardware enable/disable/pending registers. The driver has no software mask cache; mask/unmask writes directly to bank enable/disable registers. Shortcut mapping is static.

## Dependencies and Integration Points
Depends on OF address/IRQ parsing, irqdomain, ARM exception handling, and special BCM2835 bank semantics. It may sit under BCM2836 local interrupt controller for Raspberry Pi 2-style systems.

## Risks and Test Signals
Risks include shortcut interrupts that bypass bank indicators, invalid bank0 bits, boot firmware leaving FIQs enabled, and panics on domain/mapping failures. Test signals are correct DT bank translation, no bootloader-left IRQ warnings after clean firmware setup, and visible banked interrupt counts under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2836.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2836.c

## Purpose
Implements the BCM2836 local root interrupt controller for per-CPU timer, PMU, GPU fast interrupt, mailbox, and SMP IPI delivery.

## Important APIs, Types, and Functions
`struct bcm2836_arm_irqchip_intc` stores the local register base and domain. `bcm2836_map()` assigns chips/handlers by local hwirq. `bcm2836_arm_irqchip_handle_irq()` handles per-CPU pending bits. SMP support includes `ipi_domain`, mailbox chained handling, `bcm2836_arm_irqchip_ipi_send_mask()`, CPU hotplug callbacks, and `set_smp_ipi_range()`.

## Control Flow
OF init maps local registers, programs local timer frequency scaling, creates a wired domain, initializes SMP/IPI support, and installs the root handler. Root dispatch reads the current CPU pending register and handles the first set bit. IPI setup maps mailbox0 as a mux IRQ, creates a separate IPI domain, allocates 32 IPIs, and chains mailbox dispatch.

## State and Persistence
Global `intc` holds base/domain. Per-CPU masks live in local timer/mailbox/PM routing registers. IPI state persists through mailbox set/clear registers and the allocated IPI domain. Timer frequency configuration is persistent hardware state.

## Dependencies and Integration Points
Depends on `irq-bcm2836.h` register definitions, SMP/hotplug infrastructure, irqdomain IPI bus tokens, and ARM exception handling. It integrates with the generic SMP IPI framework via `set_send_ipi` equivalent range setup.

## Risks and Test Signals
Risks include single-bit dispatch if multiple local pending bits are set, CPU-id based register offsets, incorrect affinity for PMU/GPU fast IRQs, and mailbox masking during hotplug. Test signals include working local timers, SMP IPIs, CPU hotplug mailbox mask transitions, and correct `/proc/interrupts` per-CPU counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2836.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm6345-l1.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm6345-l1.c

## Purpose
Implements Broadcom BCM6345-style Level 1 interrupt controllers with per-CPU packed enable/status register windows and a single enable register per word.

## Important APIs, Types, and Functions
`struct bcm6345_l1_chip` tracks lock, word count, domain, CPU mask, and per-CPU data. `struct bcm6345_l1_cpu` stores register mapping, parent IRQ, and enable cache. Core functions are `bcm6345_l1_irq_handle()`, mask/unmask helpers, `bcm6345_l1_set_affinity()`, `bcm6345_l1_init_one()`, and `bcm6345_l1_of_init()`.

## Control Flow
Init iterates possible CPUs, maps each CPU register resource, establishes a parent chained handler, records valid CPU mappings, creates a linear domain sized by register words, and maps children as per-CPU IRQs. Chained dispatch reads pending AND enable for each word and dispatches set bits.

## State and Persistence
Per-CPU `enable_cache[]` mirrors hardware enable registers and is protected by a raw spinlock. Effective affinity chooses which CPU register window owns a child. Register offset helpers differ by CPU endianness.

## Dependencies and Integration Points
Depends on OF multi-resource/multi-parent IRQ descriptions, chained IRQ helpers, cpumask/SMP APIs, and irqdomain one-cell translation. It is a cascaded L1 controller under CPU-local parent IRQs.

## Risks and Test Signals
Risks include inconsistent word counts across CPU resources, endian offset mistakes, affinity migration losing enabled state, and incomplete cleanup on partial per-CPU init failures. Test signals are registration logs per CPU, correct affinity moves, interrupts delivered only on target CPU, and no spurious dispatch for unmapped bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm6345-l1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7038-l1.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7038-l1.c

## Purpose
Implements Broadcom BCM7038-style Level 1 interrupt controllers with status, mask-status, mask-set, and mask-clear registers, including SMP affinity and suspend wake support.

## Important APIs, Types, and Functions
`struct bcm7038_l1_chip` stores lock, word count, domain, per-CPU maps, forwarding mask, affinity table, and optional wake state/list linkage. Core functions include `bcm7038_l1_irq_handle()`, `__bcm7038_l1_mask()/unmask()`, `bcm7038_l1_set_affinity()`, `bcm7038_l1_init_one()`, PM syscore callbacks, and platform probe.

## Control Flow
Probe allocates the chip, initializes each possible CPU window, applies `brcm,int-fwd-mask`, creates a linear domain, optionally registers syscore PM hooks, and logs capacity. The chained handler selects the current CPU window, reads status masked by software mask cache, then dispatches each set child.

## State and Persistence
`mask_cache[]` tracks per-CPU hardware masks. `irq_fwd_mask[]` reserves lines forwarded elsewhere and rejected by map. `affinity[]` stores target CPU per hwirq. PM state includes `wake_mask[]` and a global list of controllers for syscore suspend/resume.

## Dependencies and Integration Points
Uses platform irqchip registration, OF resources/parent IRQs, chained handlers, optional MIPS SMP CPU mapping, generic IRQ domains, and syscore PM.

## Risks and Test Signals
Risks include forwarded IRQs being accidentally mapped, non-atomic affinity migration, boot CPU assumptions during suspend, endianness-specific MMIO access, and partial init cleanup gaps. Test signals include correct `brcm,int-fwd-mask` enforcement, wake-capable suspend/resume behavior, affinity changes on MIPS SMP, and stable mask cache after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7038-l1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7120-l2.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7120-l2.c

## Purpose
Implements Broadcom BCM7120/BCM3380-style Level 2 cascaded interrupt controllers with one or more status/enable word pairs and optional multiple parent IRQ map masks.

## Important APIs, Types, and Functions
`struct bcm7120_l2_intc_data` stores word count, mapped register bases, offsets, domain, wake/fwd masks, parent count, and per-parent L1 data. `bcm7120_l2_intc_probe()` is the common probe; variant iomap functions handle 7120 and 3380 layouts. Generic-chip suspend/resume callbacks restore masks.

## Control Flow
Probe counts parent IRQs, maps registers, parses forwarding and map masks, attaches a chained handler per parent, creates a generic-chip domain, sets each generic chip's register base and enable/status offsets, initializes the enable register with forwarded-mask defaults, and configures wake support if requested.

## State and Persistence
Persistent state includes per-parent `irq_map_mask[]`, `irq_fwd_mask[]`, generic-chip `mask_cache`, wake masks, and mapped register arrays. The handler intersects status with `mask_cache` and the parent-specific map mask before dispatch.

## Dependencies and Integration Points
Uses platform irqchip registration, OF property parsing (`brcm,int-fwd-mask`, `brcm,int-map-mask`, `brcm,irq-can-wake`), generic irqchip, and chained IRQ dispatch. It cascades below parent L1 or CPU interrupt lines.

## Risks and Test Signals
Risks include invalid map-mask dimensions, confusion between enable-as-mask semantics and generic-chip naming, forwarded lines exposed to Linux, and missing cleanup after chained handlers are installed. Test signals are correct per-parent demultiplexing, generic-chip mask cache restoration, wake propagation, and no interrupts from invalid/unmapped bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7120-l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-brcmstb-l2.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-brcmstb-l2.c

## Purpose
Implements generic Broadcom STB Level 2 interrupt controllers in edge-latched and level-sensitive variants.

## Important APIs, Types, and Functions
`struct brcmstb_intc_init_params` describes register layout and flow handler. `l2_edge_intc_init` and `l2_lvl_intc_init` select edge/level behavior. `struct brcmstb_l2_intc_data` stores domain, generic chip, status/mask offsets, wake flag, and saved mask. Probe variants call `brcmstb_l2_intc_probe()`.

## Control Flow
Probe maps MMIO, masks all interrupts, optionally clears latched status, maps the parent IRQ, creates a 32-entry generic-chip domain, installs the chained handler, configures ack/mask/unmask register callbacks by variant, and enables wake support when DT allows. The chained handler reads status AND not-mask-status, dispatches all set bits, and uses a write barrier before returning to the parent.

## State and Persistence
Generic-chip hardware state is the mask register plus optional clear/ack register. `saved_mask` preserves masks across suspend. `wake_active` from generic irqchip determines suspend-time unmasking.

## Dependencies and Integration Points
Depends on platform irqchip registration, OF parent IRQ/address parsing, generic irqchip, and chained IRQ helpers. It integrates with Broadcom STB device tree compatibles for multiple L2 blocks.

## Risks and Test Signals
Risks include wrong variant register layout, bad IRQ if parent fires with no child status, wake mask mishandling, and edge status loss if cleared incorrectly on cold boot. Test signals are per-compatible registration, edge and level interrupt delivery, suspend/resume mask restoration, and absence of `handle_bad_irq` reports under normal operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-brcmstb-l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-clps711x.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-clps711x.c

## Purpose
Implements the Cirrus EP7209/CLPS711X interrupt controller as a legacy ARM root controller with three banks and per-line EOI quirks.

## Important APIs, Types, and Functions
The static `clps711x_irqs[]` table describes valid lines, FIQ-only lines, enableable IRQs, and optional EOI offsets. `clps711x_irqh()` is the root handler. `clps711x_intc_irq_map()` chooses level, fasteoi, or bad handlers. `_clps711x_intc_init()` performs shared resource/domain setup.

## Control Flow
DT init reads the MMIO resource and calls the shared init. Init maps registers, stores status/mask pointers for three banks, masks all sources, allocates legacy descriptors, creates a legacy domain, sets it as default, installs the root handler, and initializes FIQ support when configured. Dispatch scans bank 0 then bank 1 and handles the highest pending bit.

## State and Persistence
Global `clps711x_intc` stores base, register pointers, domain, and ops. Hardware mask registers persist enabled state. Optional EOI writes clear line-specific peripherals. FIQ lines are mapped as bad/noautoen rather than normal IRQs.

## Dependencies and Integration Points
Depends on ARM legacy descriptor allocation, OF address parsing, FIQ support, and irqdomain legacy mapping. It integrates as the platform default IRQ domain for older ARM systems.

## Risks and Test Signals
Risks include only banks 0 and 1 being processed in the handler, FIQ lines accidentally requested as IRQs, invalid table entries without flags, and legacy descriptor base assumptions. Test signals are successful default-domain setup, EOI-cleared timers/UARTs, no normal IRQ handling for FIQ-only lines, and stable interrupt delivery on EP7209 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-crossbar.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-crossbar.c

## Purpose
Implements the TI IRQ crossbar, a hierarchical interrupt router that maps many SoC interrupt sources onto a limited number of parent GIC SPI inputs.

## Important APIs, Types, and Functions
`struct crossbar_device` stores the routing lock, source/IRQ limits, safe map value, allocation map, MMIO base, register offsets, and selected write width. `crossbar_domain_alloc()`, `crossbar_domain_free()`, and `crossbar_domain_translate()` implement the hierarchical domain. `crossbar_of_init()` parses DT properties and initializes hardware safe routes.

## Control Flow
Init locates the parent domain, parses maximum sources and GIC IRQ slots, marks reserved/skipped GIC inputs, computes non-linear register offsets, writes safe-map values to routable entries, then creates a hierarchy above the parent. Allocation validates GIC-style SPI specs, finds a free parent SPI from high to low, allocates the parent IRQ, and writes the crossbar source into the chosen register.

## State and Persistence
Global `cb` owns `irq_map[]` where entries are free, reserved, skipped, or assigned to a source hwirq. Hardware crossbar registers persist routing and are reset to `safe_map` on free.

## Dependencies and Integration Points
Depends on OF properties `ti,max-crossbar-sources`, `ti,max-irqs`, `ti,reg-size`, optional reserved/skip/safe-map lists, hierarchical irqdomains, and GIC parent fwspecs.

## Risks and Test Signals
Risks include global singleton limitations, freeing using source hwirq versus allocated parent slot assumptions, invalid reserved/skip lists, and missing rollback if hierarchy creation fails after hardware init. Test signals are successful allocation of routed SPIs, correct parent GIC fwspecs, safe-map restoration on disposal, and rejection of PPI/non-SPI requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-crossbar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-apb-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-apb-intc.c

## Purpose
Implements C-SKY APB and GX6605S root interrupt controllers with 64-line or dual 128-line support.

## Important APIs, Types, and Functions
Globals `reg_base`, `root_domain`, and `nr_irq` define the singleton controller. `ck_intc_init_comm()` performs common setup. `ck_set_gc()` configures generic chips and optional pulse-signal unmasking via `irq_ck_mask_set_bit()`. `gx_irq_handler()` and `ck_irq_handler()` dispatch pending bits; `setup_irq_channel()` initializes source-channel mapping.

## Control Flow
Init requires root placement, maps registers, creates a linear generic-chip domain, disables all IRQs, configures enable/mask/control registers by variant, initializes source channels with variant magic ordering, configures generic chips per 32-line bank, and installs the root handler. Handlers repeatedly process high then low pending registers until no bit remains.

## State and Persistence
MMIO enable/mask/source registers hold persistent controller state. Generic-chip mask caches track enabled bits. `nr_irq` is mutated for dual-controller mode before common init, and dual mode configures a second register block at `CK_INTC_DUAL_BASE`.

## Dependencies and Integration Points
Depends on C-SKY architecture IRQ entry, OF irqchip declarations, generic irqchip, and one-cell interrupt translation. It is a root interrupt controller and rejects parent nodes.

## Risks and Test Signals
Risks include singleton `nr_irq` mutation, pulse-signal IFR clearing tied to mask offset minus eight, source-channel magic ordering, and repeated handler loops if pending bits are not cleared by devices. Test signals are correct 64/128 domain size, disabled interrupts at boot, pulse-source delivery, and no parent-controller configuration accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-apb-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-mpintc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-mpintc.c

## Purpose
Implements the C-SKY multiprocessor interrupt controller with global/common IRQs, per-CPU local IRQs, trigger configuration, affinity routing, and SMP IPI support.

## Important APIs, Types, and Functions
Global `root_domain`, `INTCG_base`, `INTCL_base`, per-CPU `intcl_reg`, and `__trigger` store controller state. Important functions are `setup_trigger()`, `csky_mpintc_handler()`, mask/unmask/eoi callbacks, `csky_mpintc_set_type()`, `csky_irq_set_affinity()`, `csky_mpintc_send_ipi()`, and `csky_mpintc_init()`.

## Control Flow
Init maps the controller using an architecture control-register physical base, enables global/local blocks, creates a linear domain sized by `csky,num-irqs`, initializes each CPU's local register pointer, installs the root handler, and sets up an IPI mapping on IRQ 15 for SMP. Dispatch reads the current CPU's ready IRQ register and handles that hwirq.

## State and Persistence
`__trigger[]` caches requested trigger mode and is programmed during unmask. Per-CPU local registers control local enable/ack/IPI signaling. Global CIDSTR routing persists external IRQ affinity, using CPU 0 for broadcast/auto delivery and BIT(31) for single CPU mode.

## Dependencies and Integration Points
Depends on C-SKY traps/register ops, SMP cpumasks, irqdomain, OF, and architecture IPI registration. Local IRQs below 32 are per-CPU; common IRQs use fasteoi.

## Risks and Test Signals
Risks include memory leak/error cleanup gaps, `irq_data_update_effective_affinity()` using encoded CPU value after BIT(31), one-ready-IRQ dispatch assumptions, and trigger programming on the current CPU during unmask. Test signals include SMP IPI delivery, correct external IRQ affinity, trigger type changes, and per-CPU interrupt accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-mpintc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-davinci-cp-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-davinci-cp-intc.c

## Purpose
Implements TI DaVinci/Common Platform Interrupt Controller as a legacy root IRQ controller.

## Important APIs, Types, and Functions
Globals store MMIO base and irqdomain. The chip callbacks are `davinci_cp_intc_ack_irq()`, mask/unmask, and `davinci_cp_intc_set_irq_type()`. `davinci_cp_intc_handle_irq()` reads the prioritized interrupt register. `davinci_cp_intc_do_init()` performs hardware and domain initialization.

## Control Flow
OF init reads `ti,intc-size` and MMIO resource. Hardware init requests/maps registers, disables global/host/system interrupts, clears status, sets normal/no-nesting mode, enables host IRQ, maps all priorities to channel 7, allocates legacy descriptors, creates a legacy domain, installs the root handler, and enables global interrupts. Dispatch reads GPIR and handles the indicated IRQ unless the NONE bit signals spurious.

## State and Persistence
Hardware enable, status, polarity, type, channel-map, host, and global registers persist controller configuration. Software state is global base/domain only; no mask cache is kept.

## Dependencies and Integration Points
Depends on OF, legacy irq descriptor allocation, ARM exception handling, and one/two-cell xlate. It integrates as a root controller for TI cp_intc-based SoCs.

## Risks and Test Signals
Risks include unexplained nIRQ disable during mask, fixed edge handler despite programmable level/edge type, missing cleanup after request/map failures, and priority/channel defaults. Test signals are no spurious GPIR NONE messages, correct polarity/type writes for DT/requested triggers, and IRQ counts for cp_intc children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-davinci-cp-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-digicolor.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-digicolor.c

## Purpose
Implements the Conexant Digicolor interrupt controller as a 64-line root controller with two 32-bit banks.

## Important APIs, Types, and Functions
`digicolor_handle_irq()` is the root handler. `digicolor_set_gc()` configures generic chips for each bank. `digicolor_of_init()` maps the interrupt controller, configures a syscon UC register, creates the domain, and installs the handler.

## Control Flow
Init maps the IC, disables both banks, obtains a syscon regmap via `syscon` phandle, selects channel 1 regular IRQ mode, creates a 64-entry generic-chip domain, allocates two 32-line chips, sets ack/mask/unmask registers, and calls `set_handle_irq()`. Dispatch loops reading low bank first, then high bank, handling the first set bit each iteration.

## State and Persistence
Global `digicolor_irq_domain` anchors generic chips. Hardware enable/status/clear registers persist masks and acknowledgements. The UC syscon interrupt-channel selection is persistent platform state.

## Dependencies and Integration Points
Depends on OF, syscon/regmap, generic irqchip, and ARM exception entry. It is the root IRQ path for compatible Digicolor SoCs.

## Risks and Test Signals
Risks include missing syscon phandle, infinite dispatch if a level source is not cleared by its device, low-bank priority starvation, and absent cleanup after partial init failures. Test signals include successful regmap write, active low/high bank IRQ counters, ack register writes clearing latched flags, and no boot errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-digicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-dw-apb-ictl.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-dw-apb-ictl.c

## Purpose
Implements the Synopsys DesignWare APB interrupt controller as either a root controller or a cascaded child controller.

## Important APIs, Types, and Functions
`dw_apb_ictl_init()` handles both root and cascaded init. `dw_apb_ictl_handle_irq()` and `dw_apb_ictl_handle_irq_cascaded()` dispatch root/chained interrupts. `dw_apb_ictl_irq_domain_alloc()` maps generic chips for hierarchical-style root allocation. `dw_apb_ictl_resume()` restores enable/mask registers.

## Control Flow
Init determines whether a parent exists, maps MMIO, writes enable/mask registers to discover synthesized IRQ width, creates a linear domain, allocates generic chips, configures each 32-line bank's register base and mask/unmask callbacks, then either chains to the parent IRQ or installs root `set_handle_irq()`. Dispatch scans all banks' final status bits.

## State and Persistence
Global `dw_apb_ictl_irq_domain` is used only for root mode. Generic-chip mask caches persist software masks and are restored on PM resume. Hardware mask registers use set-bit-to-mask, clear-bit-to-unmask semantics.

## Dependencies and Integration Points
Depends on OF resources/parent IRQs, generic irqchip, chained IRQ helpers, and root ARM IRQ entry. It supports variable IP synthesis widths from 2 to 64 IRQs.

## Risks and Test Signals
Risks include wrong hwirq offset in root handler for banks beyond zero, destructive enable-register probing on live hardware, parent parse failure, and register-bank base offset assumptions. Test signals include discovered IRQ count, chained/root delivery, PM resume mask restoration, and multi-bank interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-dw-apb-ictl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-econet-en751221.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-econet-en751221.c

## Purpose
Implements the EcoNet EN751221 interrupt controller for MIPS 34Kc MT SMP systems, including per-VPE masking through DT-defined shadow interrupts.

## Important APIs, Types, and Functions
Global `econet_intc` stores MMIO and `interrupt_shadows[]` classifications. `get_shadow_interrupts()` parses `econet,shadow-interrupts`. `econet_chmask()` applies real versus shadow mask routing. `econet_intc_from_parent()` is the chained handler, and `econet_intc_map()` selects level versus percpu-devid handlers.

## Control Flow
Init parses shadow pairs, maps the parent IRQ and MMIO resource, requests/remaps memory, masks all sources, creates a 40-entry one-cell domain, and chains to the parent. Parent dispatch reads two pending registers and handles all set bits. Mapping rejects shadow-only hwirqs and marks real per-CPU interrupts with `handle_percpu_devid_irq`.

## State and Persistence
Persistent state is the `interrupt_shadows[]` routing table and hardware mask registers. A raw spinlock serializes read-modify-write register updates. Per-CPU behavior is encoded by using the shadow hwirq when running on VPE1.

## Dependencies and Integration Points
Depends on OF, chained IRQ helpers, MIPS SMP `smp_processor_id()`, and one-cell irqdomain translation. It cascades under a parent CPU interrupt and provides percpu semantics without hardware multicast.

## Risks and Test Signals
Risks include off-by-one validation (`shadow > IRQ_COUNT`), assumptions of at most two VPEs, direct shadow manipulation warnings, and no masking of pending bits in handler. Test signals include rejection of shadow hwirqs, correct per-VPE masking, valid shadow DT parsing logs, and no spurious parent IRQs when pending registers are zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-econet-en751221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ftintc010.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ftintc010.c

## Purpose
Implements the Faraday FTINTC010 interrupt controller, used by Gemini and Moxart variants, as a 32-line ARM root IRQ controller.

## Important APIs, Types, and Functions
`struct ft010_irq_data` stores MMIO base, chip, and domain. Chip callbacks are `ft010_irq_mask()`, `ft010_irq_unmask()`, `ft010_irq_ack()`, and `ft010_irq_set_type()`. `ft010_irqchip_handle_irq()` dispatches status bits. `ft010_of_init_irq()` performs OF initialization.

## Control Flow
Init disables CPU idle polling because of platform idle issues, maps registers, disables IRQ/FIQ masks, creates a simple domain, and installs the root handler. Domain map installs the chip with `handle_bad_irq` until a type is selected. The root handler loops while status is nonzero and handles the lowest pending bit.

## State and Persistence
Static `firq` holds singleton state. Hardware mask, clear, mode, polarity, and status registers persist line configuration. Type setup updates mode/polarity and swaps the Linux flow handler to level or edge.

## Dependencies and Integration Points
Depends on OF irqchip declarations for Faraday/Gemini/Moxart compatibles, ARM root IRQ handling, cpu idle control, and one/two-cell xlate.

## Risks and Test Signals
Risks include `WARN` but continued operation on failed mapping, default bad handlers until type setup, idle polling side effects, and unsupported trigger values returning success after installing bad handler. Test signals are trigger programming per line, status loop draining, IRQ/FIQ masks disabled at boot, and no unexpected idle regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ftintc010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.c

## Purpose
Provides shared helpers for ARM GIC drivers: quirk matching, interrupt trigger configuration, distributor initialization, and CPU-interface private interrupt initialization.

## Important APIs, Types, and Functions
`gic_enable_of_quirks()` and `gic_enable_quirks()` apply workaround tables. `gic_configure_irq()` changes GIC configuration bits with locking. `gic_dist_config()` initializes global SPIs. `gic_cpu_config()` initializes SGI/PPI priority and disabled state.

## Control Flow
Quirk helpers scan sentinel-terminated `struct gic_quirk` arrays and call `init(data)` when OF compatible/property or IIDR mask matches. IRQ configuration locks a global raw spinlock, updates two-bit trigger fields, writes them back, and verifies hardware accepted the new value. Dist/CPU config loops over register groups writing level-trigger defaults, priorities, active-clear, and enable-clear values.

## State and Persistence
Only a file-local raw spinlock is software state. Persistent hardware state is GIC distributor configuration: trigger modes, priorities, active state, and enable bits.

## Dependencies and Integration Points
Depends on ARM GIC register definitions, OF, irqchip users, and common Linux IRQ type flags. Called by GICv2/v3 and platform-specific wrappers.

## Risks and Test Signals
Risks include hardware refusing configuration writes, especially for PPIs/non-secure state, incorrect priority defaults, and quirk init side effects. Test signals are GIC init logs for enabled workarounds, successful set-type operations, and distributor registers reset to disabled/known priority state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.h

## Purpose
Declares shared ARM GIC helper APIs and the quirk descriptor structure used by GIC implementations.

## Important APIs, Types, and Functions
`struct gic_quirk` combines description, OF compatible/property selectors, IIDR mask/value selectors, and an init callback. The header declares `gic_configure_irq()`, `gic_dist_config()`, `gic_cpu_config()`, `gic_enable_quirks()`, and `gic_enable_of_quirks()`. It also defines redistributor flag bits for property-base flushing, preallocated tables, and non-shareable forcing.

## Control Flow
No executable flow lives here. It defines the contract for shared helper calls and quirk tables consumed by GIC source files.

## State and Persistence
No storage is defined. Redistributor flags are bit constants to be stored by consumers in their own state.

## Dependencies and Integration Points
Includes OF, irqdomain, MSI, and ARM GIC common headers. It is a compile-time integration point among ARM GIC drivers and platform-specific quirk implementations.

## Risks and Test Signals
Risks are interface drift and mismatched flag semantics across GIC versions. Test signals are successful builds of all GIC consumers and runtime quirk/redistributor behavior matching the consuming driver expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.c

## Purpose
Provides MSI parent operations for GIC ITS domains, covering GICv3 and GICv5 PCI/platform MSI preparation and teardown.

## Important APIs, Types, and Functions
Exports `gic_v3_its_msi_parent_ops` and `gic_v5_its_msi_parent_ops`. Important helpers include `its_translate_frame_address()`, PCI prepare functions, platform MSI info lookup, `its_pmsi_prepare()`, `its_v5_pmsi_prepare()`, `its_msi_teardown()`, and device MSI info initializers.

## Control Flow
MSI domain creation uses parent ops to initialize per-device MSI info. The initializer delegates to `msi_lib_init_dev_msi_info()`, then overrides `msi_prepare` by bus token. Prepare paths compute the ITS DeviceID from PCI RID, DMA alias, OF `msi-parent`, OF `msi-map`, or ACPI IORT; GICv5 paths also obtain a translate-frame physical address. They round vector counts to powers of two, impose minimums where required, then call the real ITS parent prepare op. Teardown delegates to the parent ITS op.

## State and Persistence
The file has no mutable global state. Per-allocation state is passed through `msi_alloc_info_t` scratchpad fields: DeviceID in slot 0 and GICv5 translate-frame PA in slot 1.

## Dependencies and Integration Points
Depends on PCI MSI, OF, ACPI IORT, `irq-msi-lib`, and ITS parent domain ops. It is selected by GIC ITS irqdomains to expose PCI and platform MSI bus domains.

## Risks and Test Signals
Risks include incorrect alias sizing, DevID 0 workaround over-allocation, missing GICv5 `ns-translate` resources, and failure to match OF/ACPI controller nodes. Test signals include PCI MSI/MSI-X allocation on aliased buses, platform MSI DeviceID mapping, GICv5 translate PA propagation, and successful teardown delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.h

## Purpose
Declares GIC ITS MSI parent operation tables for GICv3 and GICv5 users.

## Important APIs, Types, and Functions
The header exports `gic_v3_its_msi_parent_ops` and `gic_v5_its_msi_parent_ops` as `extern const struct msi_parent_ops`.

## Control Flow
No runtime logic exists in the header. Consumers include it to pass the appropriate parent ops when creating ITS-backed MSI parent domains.

## State and Persistence
No state is declared. The referenced const operation tables live in `irq-gic-its-msi-parent.c`.

## Dependencies and Integration Points
Depends on `struct msi_parent_ops` being available through including translation units. It is a narrow integration boundary for GIC ITS MSI setup.

## Risks and Test Signals
Risks are limited to declaration/definition mismatch or missing include coverage. Test signals are successful linkage and creation of GICv3/GICv5 ITS MSI domains using the declared symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-pm.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-pm.c

## Purpose
Wraps a child ARM GIC instance with runtime PM and clock management, used for NVIDIA Tegra AGIC-style controllers.

## Important APIs, Types, and Functions
`struct gic_clk_data` describes required clocks. `struct gic_chip_pm` stores GIC data, clock metadata, and bulk clock handles. Runtime PM callbacks are `gic_runtime_resume()` and `gic_runtime_suspend()`. `gic_probe()` initializes clocks, PM, and the child GIC via `gic_of_init_child()`.

## Control Flow
Probe matches clock data, maps a parent IRQ, allocates clock descriptors, enables runtime PM, resumes to turn clocks on, initializes the child GIC, then releases the runtime PM reference. Runtime suspend saves distributor/CPU interface state and disables clocks. Runtime resume enables clocks and restores saved GIC state after the first initialization pass.

## State and Persistence
Device-managed `gic_chip_pm` persists as driver data. `chip_data` is intentionally NULL during first resume to avoid restoring before initialization. GIC save/restore state is held by core GIC data. Clock enable state follows runtime PM.

## Dependencies and Integration Points
Depends on platform driver probing, OF match data, clock bulk APIs, runtime PM, parent IRQ parsing, and ARM GIC child initialization/save/restore helpers.

## Risks and Test Signals
Risks include clock enable failures, parent IRQ mapping leaks, restore-before-init ordering, and runtime PM imbalance. Test signals include AGIC registration log, clocks toggling around runtime suspend/resume, interrupts surviving PM cycles, and no `irq_dispose_mapping` leak on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-realview.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-realview.c

## Purpose
Applies ARM RealView platform syscon configuration before initializing the GIC on TC11MP/EB11MP systems.

## Important APIs, Types, and Functions
`syscon_pldset_of_match[]` selects the PLD control register offset by syscon compatible. `realview_gic_of_init()` unlocks the system control block, programs interrupt mode, relocks it, and then calls `gic_of_init()`.

## Control Flow
During irqchip init, the driver finds a matching syscon node, obtains its regmap, writes the unlock value, updates PLD interrupt mode bits to "new no DCC", locks the syscon, logs the configuration, and delegates normal GIC initialization to the common ARM GIC driver.

## State and Persistence
Persistent state is the syscon PLD interrupt mode field. No driver-private state remains after init.

## Dependencies and Integration Points
Depends on OF matching, syscon/regmap, ARM GIC OF init, and RealView-specific system-control register definitions. Registered for `arm,tc11mp-gic` and `arm,eb11mp-gic`.

## Risks and Test Signals
Risks include missing/incorrect syscon compatible, wrong PLD offset for board revision, and failure to unlock/relock the syscon. Test signals are the RealView mode setup log, successful subsequent GIC init, and functional interrupt routing without legacy DCC mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-realview.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v2m.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v2m.c

## Purpose
Implements ARM GICv2m MSI/MSI-X support by exposing MSI parent domains backed by GIC SPI ranges and v2m frame registers.

## Important APIs, Types, and Functions
`struct v2m_data` stores frame resource, fwnode, base, SPI range, bitmap, and quirks. Key functions include `gicv2m_init()`, OF/ACPI init helpers, `gicv2m_init_one()`, `gicv2m_allocate_domains()`, `gicv2m_irq_domain_alloc()/free()`, `gicv2m_compose_msi_msg()`, and quirk/teardown helpers.

## Control Flow
OF or ACPI discovery creates one or more `v2m_data` frames, reads or overrides SPI base/count, applies IIDR/Graviton quirks, allocates bitmaps, and creates an MSI parent domain. Allocation searches all frames for an aligned free SPI range, prepares DMA MSI addressing, allocates parent GIC IRQs as edge-rising SPIs, and installs a v2m chip whose MSI message writes either SETSPI_NS or quirked address/data.

## State and Persistence
Global `v2m_nodes` and `v2m_lock` protect frame list and bitmap allocation. Hardware state includes mapped v2m frame registers and parent GIC SPI configuration. ACPI may register an MSI fwnode provider for PCI.

## Dependencies and Integration Points
Depends on ARM GIC parent domains, PCI/platform MSI infrastructure, OF child frame nodes, ACPI MADT/IORT, IOMMU DMA MSI preparation, and `irq-msi-lib`.

## Risks and Test Signals
Risks include SPI range validation, multi-frame domain host-data representing only the first frame while allocation scans all frames, quirked message data/addressing, bitmap leak on `iommu_dma_prepare_msi()` failure, and ACPI Graviton range handling. Test signals include v2m range logs, MSI allocation/free under PCI/MSI-X, correct edge SPI configuration, and working X-Gene/NS2/Graviton quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its-fsl-mc-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its-fsl-mc-msi.c

## Purpose
Creates Freescale Management Complex bus MSI domains backed by GICv3 ITS domains.

## Important APIs, Types, and Functions
`its_msi_irq_chip` forwards mask/unmask/eoi/affinity to the parent MSI stack. `fsl_mc_msi_domain_get_msi_id()` maps an MC device ICID to an ITS DeviceID via OF MSI translation or ACPI IORT. `its_fsl_mc_msi_prepare()` validates DPRC devices and prepares parent allocation. Discovery uses `its_fsl_mc_of_msi_init()`, ACPI MADT parsing, and `early_initcall()`.

## Control Flow
Early init scans OF ITS nodes with `msi-controller` and ACPI generic translator entries. For each ITS fwnode it finds the DOMAIN_BUS_NEXUS parent and creates an FSL-MC MSI irqdomain. During allocation prepare, only FSL-MC DPRC devices are accepted; their ICID-derived DeviceID is placed in scratchpad slot 0, vector count is rounded up with a minimum of 32, and parent ITS prepare is invoked.

## State and Persistence
The MSI domain info and ops are static, with ops marked `__ro_after_init`. No mutable global list is maintained here; created domains are owned by MSI/irqdomain core. Per-allocation DeviceID state is passed through `msi_alloc_info_t`.

## Dependencies and Integration Points
Depends on FSL-MC bus helpers, GICv3 ITS parent MSI domains, OF MSI xlate, ACPI IORT, MADT generic translator parsing, and generic MSI domain infrastructure.

## Risks and Test Signals
Risks include accepting only DPRC devices, missing ITS parent domains at early init, ICID translation mismatches, and ACPI node-name allocation failure paths. Test signals include "fsl-mc MSI domain created" logs, successful DPRC MSI allocation, correct ICID-to-DeviceID mapping in OF and ACPI boots, and parent ITS teardown/allocation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its-fsl-mc-msi.c -->
