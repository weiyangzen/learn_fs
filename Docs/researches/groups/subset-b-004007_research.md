# subset-b-004007 Research

Grouped research for Linux irqchip source files under the ceph-client source tree. Each section preserves the original source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sg2042-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sg2042-msi.c

## Purpose
Implements the Sophgo SG2042/SG2044 MSI parent/middle irq domain used to terminate PCI MSI/MSI-X writes into SoC general-purpose interrupt registers and forward them to the RISC-V PLIC parent domain. It is a platform irqchip driver, not a Ceph-specific component.

## Important APIs, Types, And Functions
`struct sg204x_msi_chipdata` stores the clear register, doorbell physical address, first parent IRQ, vector count, interrupt type, allocation bitmap, mutex, and SoC-specific `sg204x_msi_chip_info`. The middle-domain callbacks are `sg204x_msi_middle_domain_alloc()` and `sg204x_msi_middle_domain_free()`, backed by bitmap allocation helpers. SG2042 and SG2044 have separate `irq_chip` instances and MSI parent ops because SG2044 supports multi-MSI/MSI-X and uses per-vector doorbell/clear semantics.

## Control Flow
Probe reads match data, maps the `clr` MMIO resource, records the `doorbell` resource start, parses `msi-ranges` to find the PLIC fwnode, base IRQ, type, and vector count, allocates the vector bitmap, then creates a parent MSI irq domain. MSI allocation finds a free contiguous bitmap region, allocates one parent PLIC IRQ per vector, installs the middle chip, and composes MSI messages using either SG2042 bit data or SG2044 doorbell-bank plus bit-index data. Ack clears the controller latch and then acks the parent.

## State And Persistence
Mutable state is the in-memory MSI allocation bitmap protected by `msi_map_lock`; hardware state is the clear register write, parent PLIC enable/type state, and MSI doorbell target programmed into PCI devices. Managed allocation keeps chipdata and bitmap alive for device lifetime.

## Dependencies And Integration Points
Depends on generic MSI parent-domain support, `irq-msi-lib`, Linux irqdomain hierarchy APIs, platform resource parsing, firmware properties, and the PLIC parent domain. Integration is through `sophgo,sg2042-msi` and `sophgo,sg2044-msi` compatible strings plus `msi-ranges`, `clr`, and `doorbell` resources.

## Risks
`1 << d->hwirq` limits SG2042-style operations to word-sized vector positions and depends on DT-provided vector count matching hardware. `msi-ranges` parsing is subtle because the code reads separate base and count reference entries. Allocation failure cleanup must release both parent IRQs and bitmap regions. Incorrect supported MSI flags can make PCI endpoints request unsupported MSI-X or multi-MSI modes.

## Test Signals
Build with the Sophgo MSI driver enabled, boot on SG2042 and SG2044 DTs, verify the MSI parent domain registers, and exercise PCI endpoints with single MSI, multi-MSI, and MSI-X where supported. Useful failures include PLIC parent lookup errors, exhausted vector bitmap paths, correct interrupt ack/clear behavior, and endpoint stress with repeated enable/disable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sg2042-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sifive-plic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sifive-plic.c

## Purpose
Implements the RISC-V Platform-Level Interrupt Controller for DT and ACPI systems. It maps external device interrupt sources to per-hart contexts, handles claim/complete cycles, supports edge-capable variants, saves state for suspend, and carries a workaround path for the UltraRISC CP100 claim-register erratum.

## Important APIs, Types, And Functions
`struct plic_priv` owns MMIO base, fwnode, irqdomain, local CPU mask, quirk bits, priority-save bitmap, interrupt count, and ACPI GSI metadata. Per-CPU `struct plic_handler` owns hart context base, enable bitmap registers, saved enable words, and a lock. Core operations include `plic_irq_enable()`, `plic_irq_disable()`, `plic_irq_eoi()`, `plic_set_affinity()`, `plic_irq_set_type()`, `plic_handle_irq()`, `plic_handle_irq_cp100()`, and `plic_probe()`.

## Control Flow
Probe maps registers, parses interrupt counts and contexts from DT or ACPI, creates one handler per usable `RV_IRQ_EXT` context, disables per-source enables, sets priorities, and creates a linear domain. Once all online CPUs have handlers, it maps the parent RISC-V external interrupt, installs the chained handler, registers CPU hotplug callbacks, and registers syscore suspend/resume. Runtime handling repeatedly reads the claim register, dispatches the domain hwirq, and completes in EOI. CP100 handling temporarily isolates one pending enabled interrupt before reading claim.

## State And Persistence
State is split between global setup flags, the parent IRQ, per-CPU handler data, enable-save arrays, and priority-save bitmap. Suspend saves priority and enable registers; resume restores them for all present handlers. Hardware priorities are hardwired to one when unmasked and zero when masked.

## Dependencies And Integration Points
Depends on RISC-V hart/INTC helpers, CPU hotplug, syscore PM, DT `riscv,ndev` and interrupt-parent data, ACPI RINTC/GSI helpers, and generic irqdomain allocation. Compatible strings include SiFive, generic RISC-V, Andes, T-Head, UltraRISC, and Allwinner early PLIC declarations.

## Risks
Context parsing is platform-critical: wrong hart/context IDs leave CPUs without interrupt handlers. Hardware IRQ 0 is reserved and must stay unmapped. Affinity changes write multiple context enable registers and rely on saved masks being coherent. CP100 isolation temporarily rewrites enables and must restore them exactly. M-mode/S-mode context ordering is acknowledged as fragile in comments.

## Test Signals
Boot DT and ACPI RISC-V systems, confirm the logged interrupt/context counts, verify per-CPU external interrupts, affinity changes, CPU hotplug, suspend/resume, and edge-versus-level triggering on quirked controllers. Erratum coverage should stress simultaneous pending interrupts on CP100-compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sifive-plic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sl28cpld.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sl28cpld.c

## Purpose
Provides a compact interrupt-controller driver for the Kontron SL28 CPLD. It exposes eight CPLD interrupt bits through the regmap-irq framework with status, enable, and ack registers derived from the device's `reg` property.

## Important APIs, Types, And Functions
`sl28cpld_irqs` declares eight `REGMAP_IRQ_REG_LINE()` entries. `struct sl28cpld_intc` stores the parent regmap, a mutable `regmap_irq_chip`, and returned regmap IRQ chip data. `sl28cpld_intc_probe()` wires the regmap IRQ chip into the platform IRQ.

## Control Flow
Probe requires a parent MFD device, obtains its regmap, gets the parent IRQ, reads the register base offset, populates `regmap_irq_chip` fields, and calls `devm_regmap_add_irq_chip_fwnode()` with shared oneshot flags. Runtime masking, acking, status reads, and nested interrupt dispatch are handled by regmap-irq core.

## State And Persistence
The driver has no custom runtime state beyond the allocated chip descriptor. Persistent hardware state is the CPLD enable and pending registers managed by regmap-irq. Device-managed resources remove the registration with the platform device.

## Dependencies And Integration Points
Depends on the parent SL28 CPLD MFD regmap, Linux platform-device APIs, generic interrupt flags, firmware properties, and compatible `kontron,sl28cpld-intc`.

## Risks
The `reg` property must point at the correct CPLD interrupt block because all register offsets are derived from it. Parent IRQ flags are shared/oneshot, so interrupt lines must tolerate threaded handling. Any change to CPLD register layout requires updating status/unmask/ack offsets together.

## Test Signals
Probe under the SL28 CPLD parent, verify eight child IRQs appear, and trigger each CPLD source while checking mask, unmask, and ack behavior. Regression tests should include missing parent regmap, missing parent IRQ, and incorrect `reg` property handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sl28cpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sni-exiu.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sni-exiu.c

## Purpose
Implements the Socionext SynQuacer External Interrupt Unit, a 32-line interrupt translator in front of a parent GIC. It supports DT early irqchip initialization and ACPI platform probing, translating EXIU local lines to parent SPI lines while programming level/edge and polarity registers.

## Important APIs, Types, And Functions
`struct exiu_irq_data` stores MMIO base and the parent SPI base. The irq chip implements ack, eoi, enable, mask, unmask, affinity forwarding, and type configuration. Domain callbacks `exiu_domain_translate()` and `exiu_domain_alloc()` convert DT GIC-style or ACPI two-cell specifiers into EXIU hwirqs and parent fwspecs.

## Control Flow
Initialization reads `socionext,spi-base`, maps MMIO, clears and masks all EXIU interrupts, then creates a hierarchical domain under the parent. Allocation validates SPI specifiers, maps the local hwirq, installs the EXIU chip, and allocates the parent GIC IRQ. Type setting programs EILVL/EIEDG, selects fasteoi or fasteoi-ack handlers, clears stale latch state, and forces the parent to level-high.

## State And Persistence
Persistent state is register-backed: mask bits, level/polarity/edge bits, and latched request status. The driver stores only the base pointer and SPI base. There is no suspend state cache, so correctness after low-power states depends on EXIU registers being retained or firmware restoring them.

## Dependencies And Integration Points
Depends on parent irqdomain lookup, GIC DT binding constants, OF address/IRQ parsing, ACPI resource/platform-device support, and compatible `socionext,synquacer-exiu` or ACPI HID `SCX0008`.

## Risks
`spi_base` translation must match firmware; otherwise child IRQs are routed to the wrong parent SPI. Level-triggered lines require EOI-time clearing to avoid stuck interrupts. The parent is always programmed as level-high, so EXIU polarity conversion must remain correct. ACPI and DT fwspec formats differ and must be kept in sync.

## Test Signals
Validate DT and ACPI boot paths, all four trigger types, affinity forwarding, mask/unmask ordering, and level lines that remain asserted across EOI. Firmware tests should confirm `socionext,spi-base` and parent interrupt ranges map to the expected GIC SPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sni-exiu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sp7021-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sp7021-intc.c

## Purpose
Implements the Sunplus SP7021 interrupt controller, exposing 224 child interrupts through two cascaded external parent IRQ lines. It includes a hardware workaround for GPIO_INT0-7 edge triggering by emulating edge behavior with level mode and polarity toggling.

## Important APIs, Types, And Functions
The global `sp_intc` holds two MMIO register groups, irqdomain, raw spinlock, and GPIO workaround state bitmap. Key functions are `sp_intc_assign_bit()`, chip callbacks for ack/mask/unmask/type, `sp_intc_get_ext_irq()`, cascaded handler `sp_intc_handle_ext_cascaded()`, and `sp_intc_init_dt()`.

## Control Flow
Initialization maps both register blocks, maps two parent interrupts, programs all child interrupts masked, edge, high-active, routed to EXT_INT0, and cleared, then creates a linear two-cell domain. The chained handler reads pending groups for EXT_INT0 or EXT_INT1, resolves the highest pending line, handles the child IRQ, and performs GPIO edge workaround polarity restoration when needed.

## State And Persistence
State is mostly hardware registers plus the static bitmap tracking whether each affected GPIO line is edge, low/falling, and currently active. The global singleton design assumes one SP7021 controller instance.

## Dependencies And Integration Points
Depends on OF MMIO/IRQ parsing, chained irqchip helpers, linear irqdomains, and compatible `sunplus,sp7021-intc`. Parent interrupts are consumed from the controller node as EXT_INT0 and EXT_INT1.

## Risks
The GPIO workaround is timing-sensitive because ack toggles polarity and the cascaded handler later restores it. Register group and pending-group layout constants must match silicon. `irq_set_chip_data()` stores `&sp_intc_chip` rather than controller data, which is harmless for current callbacks but fragile if chip data is later consumed differently.

## Test Signals
Exercise normal non-GPIO interrupts and GPIO_INT0-7 rising/falling edge cases, including repeated pulses and active-level transitions. Boot tests should confirm both parent IRQs are chained, 224 hwirqs map, and initial masking/clearing prevents stale interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sp7021-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-st.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-st.c

## Purpose
Programs STiH407 syscfg routing for selected Cortex-A9 IRQ/FIQ inputs. This is a syscfg helper rather than a full irqdomain provider: it enables and selects sources for two IRQ and two FIQ channels through a syscon regmap.

## Important APIs, Types, And Functions
`struct st_irq_syscfg` caches the syscon regmap, register offset, and computed configuration word. `st_irq_xlate()` translates DT binding device IDs into enable and channel-select bits. `st_irq_syscfg_enable()` parses `st,irq-device`, `st,fiq-device`, and `st,invert-ext`, then writes the masked syscfg register.

## Control Flow
Probe allocates state, obtains match-data register offset, looks up the `st,syscfg` phandle regmap, stores drvdata, and programs the syscfg. Resume rewrites the cached configuration using the same mask, restoring routing after system sleep.

## State And Persistence
The only persistent driver state is the computed `config` value; hardware state is the syscfg register. There is no dynamic interrupt allocation or per-line mask state.

## Dependencies And Integration Points
Depends on ST interrupt-controller DT binding constants, syscon/regmap, platform driver registration via `core_initcall`, and compatible `st,stih407-irq-syscfg`.

## Risks
Incorrect DT arrays silently route devices to the wrong IRQ/FIQ channel. The driver requires exactly two entries for both IRQ and FIQ device arrays. Because it rewrites a masked syscfg field, mask definitions must match hardware or unrelated syscfg bits could be altered.

## Test Signals
Validate probe with complete DT properties, invalid device IDs, resume restore, and functional routing of PMU, CTI, PL310, and external interrupt sources to the selected IRQ/FIQ channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-starfive-jh8100-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-starfive-jh8100-intc.c

## Purpose
Implements the StarFive JH8100 external interrupt controller as a 32-line cascaded interrupt controller. It masks/unmasks child lines in local registers and dispatches pending status from one parent IRQ.

## Important APIs, Types, And Functions
`struct starfive_irq_chip` owns MMIO base, child domain, and raw spinlock. `starfive_intc_bit_set()` and `_clear()` perform register read-modify-write. The irq chip has mask/unmask callbacks, while `starfive_intc_irq_handler()` reads `SRC0_INT`, dispatches child hwirqs, and pulses `SRC0_CLEAR`.

## Control Flow
Probe allocates state, maps registers, gets and deasserts reset, enables the clock, creates a one-cell linear domain, obtains the parent IRQ, and installs the chained handler. Runtime dispatch iterates over set pending bits, calls `generic_handle_domain_irq()`, then sets and clears the corresponding clear bit.

## State And Persistence
The controller keeps persistent clock/reset enablement, MMIO base, domain, and a lock for mask register updates. There is no suspend/resume cache. Cleanup paths exist only for probe failure because successful initialization is early/platform irqchip lifetime.

## Dependencies And Integration Points
Depends on OF MMIO, clock, reset, chained irqchip, one-cell irqdomain APIs, and compatible `starfive,jh8100-intc` through `IRQCHIP_PLATFORM_DRIVER`.

## Risks
Missing runtime removal means clock/reset resources remain intentionally owned for the lifetime of the controller. Pending clear is a pulse sequence and must match hardware. All lines use `handle_level_irq`; edge-like sources would need upstream conditioning.

## Test Signals
Boot with clock and reset providers, verify 32 child hwirqs map, toggle mask/unmask, and trigger multiple simultaneous pending bits. Probe-failure tests should cover missing reset, clock, parent IRQ, and domain allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-starfive-jh8100-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32-exti.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32-exti.c

## Purpose
Implements STM32 F4/H7 EXTI edge interrupt controllers using generic irq chips. It supports one-bank F4 and three-bank H7 register layouts, cascaded parent interrupts, wake masks, and trigger configuration.

## Important APIs, Types, And Functions
`stm32_exti_bank` describes per-bank register offsets; `stm32_exti_drv_data` selects the bank table; `stm32_exti_chip_data` caches wake/mask and trigger registers. `stm32_irq_handler()` scans bank pending registers. `stm32_irq_set_type()`, `stm32_irq_ack()`, `stm32_irq_suspend()`, and `stm32_irq_resume()` are installed in generic chip callbacks.

## Control Flow
Early OF init maps MMIO, creates a linear domain covering all banks, allocates one generic chip per bank, clears mask/event registers after hot reboot, assigns register offsets and callbacks, then chains every parent IRQ declared by the node. Dispatch loops over each bank and handles all pending bits. Type setting updates RTSR/FTSR under the generic chip lock.

## State And Persistence
Per-bank chip data caches rising/falling trigger registers during suspend and uses generic chip mask/wake caches to restore interrupt mask state. Hardware state is otherwise the IMR, RTSR, FTSR, SWIER, and pending registers.

## Dependencies And Integration Points
Depends on OF init, chained irqchips, generic irq chips, one/two-cell irqdomain translation, and compatible strings `st,stm32-exti` and `st,stm32h7-exti`.

## Risks
Only edge trigger types are accepted; level requests fail. Parent IRQ count and bank layout must match the SoC. Since the IP has no reset, hot reboot residue is handled by clearing IMR/EMR; missing this can produce stale interrupts.

## Test Signals
Test F4 and H7 DTs, rising/falling/both-edge inputs, multiple pending bits per bank, wake-enabled suspend/resume, and hot reboot without stale pending events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32-exti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32mp-exti.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32mp-exti.c

## Purpose
Implements STM32MP EXTI as a hierarchical interrupt controller in front of a parent GIC or interrupt router. It supports direct parent-forwarded interrupts, locally latched EXTI events, secure/reserved event detection, optional hwspinlock coordination, and wake state across system sleep.

## Important APIs, Types, And Functions
`stm32mp_exti_bank` describes offsets including rising/falling pending and security config. `stm32mp_exti_host_data` owns MMIO base, drvdata, optional hwspinlock, and bank data. Two irq chips are used: `stm32mp_exti_chip` for locally managed events and `stm32mp_exti_chip_direct` for direct parent-backed events. Allocation is handled by `stm32mp_exti_domain_alloc()`.

## Control Flow
Probe gets optional hwspinlock, match data, bank data, MMIO, initializes bank state, checks secure/RIF ownership, finds the parent domain, and creates a hierarchy. Allocation validates hwirq, rejects secure events, chooses local or direct chip based on trigger routing, then either parses `interrupts-extended` or uses static descriptor arrays to allocate the parent IRQ. Runtime mask/unmask updates EXTI IMR and parent state; EOI clears rising/falling pending and then EOIs the parent when present.

## State And Persistence
Per-bank state tracks mask cache, wake-active mask, saved RTSR/FTSR, secure event reservation, and a raw lock. Suspend programs IMR to wake-active only and resume restores trigger and mask caches. Optional hwspinlock protects trigger programming shared with another processor.

## Dependencies And Integration Points
Depends on OF platform probing, GIC binding constants, hierarchical irqdomains, hwspinlock framework, noirq PM ops, and compatible `st,stm32mp1-exti` or `st,stm32mp13-exti`.

## Risks
Static descriptor arrays must match SoC interrupt wiring unless DT supplies `interrupts-extended`. Secure/RIF detection can make events unavailable with `-EPERM`. Trigger reconfiguration in atomic context may fail if the hwspinlock cannot be acquired. Direct versus local chip selection depends on hardware routing bits.

## Test Signals
Probe STM32MP1 and STM32MP13, verify secure events are rejected, exercise direct and local lines, all supported edge types, software retrigger, wake-only suspend/resume, and systems with and without hwspinlock. DT tests should validate both descriptor-array and `interrupts-extended` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32mp-exti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun4i.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun4i.c

## Purpose
Implements the legacy Allwinner A1X/SUNIV root interrupt controller. It is a primary ARM irqchip that installs the global `handle_irq` entry and exposes 96 hwirqs through a one-cell linear domain.

## Important APIs, Types, And Functions
`struct sun4i_irq_chip_data` stores MMIO base, domain, and SoC-specific enable/mask register offsets. The irq chip implements ack for NMI hwirq 0, mask/unmask through enable registers, and fasteoi handling. `sun4i_handle_irq()` reads the vector register and dispatches domain hwirqs.

## Control Flow
OF init allocates singleton state, chooses register offsets for A10 or SUNIV, maps MMIO, disables all interrupts, unmasks mask registers, clears pending bits, enables protection, configures NMI source type, creates the domain, and installs `set_handle_irq()`. Runtime reads the vector, special-cases hwirq 0 by checking pending status, and loops until no vector remains.

## State And Persistence
State is a global singleton pointer plus register state. There is no suspend/resume cache; this controller is expected to remain configured or be restored by platform code.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/init, irqdomain, and compatible `allwinner,sun4i-a10-ic` or `allwinner,suniv-f1c100s-ic`.

## Risks
Global singleton design excludes multiple instances. Vector value zero is ambiguous and requires the pending-register check; incorrect handling could drop hwirq 0 or spin on spurious interrupts. Register offsets differ between variants and must match compatible selection.

## Test Signals
Boot on supported Allwinner SoCs, verify root handler installation, hwirq 0/NMI delivery, normal peripheral interrupts across all three banks, and no stale pending interrupts after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun4i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun6i-r.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun6i-r.c

## Purpose
Implements Allwinner R_INTC wakeup/NMI interrupt control for A31/H6-class SoCs as a hierarchical domain above the GIC. It handles NMI trigger conversion, wake-enabled direct and muxed IRQs during suspend/shutdown, and old two-cell NMI bindings.

## Important APIs, Types, And Functions
`struct sun6i_r_intc_variant` describes mux range and valid mux bitmap. Global bitmaps track wake-enabled top-level and mux interrupts. `sun6i_r_intc_nmi_chip` manages NMI-specific ack/eoi/type/state; `sun6i_r_intc_wakeup_chip` forwards regular IRQ operations to the parent while providing wake programming.

## Control Flow
Initialization parses the parent NMI GIC SPI, seeds wake bitmaps from variant data, maps MMIO, creates a zero-size hierarchy domain, registers syscore ops, clears NMI pending state, and enables normal NMI-only operation. Allocation accepts either old two-cell NMI specifiers or GIC-style three-cell specifiers, allocates the parent GIC IRQ, and installs the NMI or wakeup chip. Suspend writes wake bitmaps into IRQ and mux enable registers; resume restores normal NMI-only enables.

## State And Persistence
Persistent state consists of global base pointer, NMI hwirq, wake bitmaps, valid mux bitmap, and syscore PM hooks. NMI level ack may be deferred in `chip_data` until unmask/EOI for oneshot behavior.

## Dependencies And Integration Points
Depends on OF parent domain, GIC binding constants, hierarchical irqdomain APIs, syscore suspend/resume/shutdown, and compatible `allwinner,sun6i-a31-r-intc` or `allwinner,sun50i-h6-r-intc`.

## Risks
Wake capability is constrained by variant bitmaps; invalid wake requests return `-EPERM`. NMI parent specifier must be level-high GIC SPI. Deferred NMI ack logic must avoid losing oneshot-level wake interrupts. The domain accepts old and new bindings, so translation must remain compatible.

## Test Signals
Test NMI rising/falling/level modes, old two-cell binding, GIC-style child specifiers, suspend/shutdown wake from direct and muxed sources, and H6 full 128-bit mux coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun6i-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sunxi-nmi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sunxi-nmi.c

## Purpose
Implements standalone Allwinner NMI controllers for several SoC generations. It exposes a single child interrupt and configures controller-specific control, pending, and enable offsets using generic irq chips.

## Important APIs, Types, And Functions
`struct sunxi_sc_nmi_data` supplies register offsets and optional enable value. The generic chip has separate level and edge chip types. `sunxi_sc_nmi_set_type()` converts Linux trigger flags to hardware source-type values and switches between level and edge handlers.

## Control Flow
Initialization creates a one-IRQ domain, allocates two generic chip types, maps the parent IRQ and MMIO resource, programs level and edge chip callbacks/register offsets, disables the NMI, clears pending state, then installs a chained handler that always dispatches child hwirq 0.

## State And Persistence
State lives in generic irq chip register and mask caches plus MMIO state. There is no custom suspend/resume storage. Hardware source type, mask, and pending registers persist while powered.

## Dependencies And Integration Points
Depends on OF early irqchip init, generic irq chips, chained IRQ helpers, and compatible strings for sun6i A31, sun7i A20, sun9i A80, and sun55i A523 NMI blocks.

## Risks
Register offset ordering differs by generation, and sun55i uses a nonzero enable disable value. Unsupported mixed trigger modes return `-EBADR`. Since only one child hwirq exists, parent mapping failures make the entire controller unusable.

## Test Signals
Validate each compatible's offsets, single child IRQ mapping, all supported trigger types, pending clear, enable/disable polarity, and chained dispatch under repeated NMI assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sunxi-nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-tb10x.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-tb10x.c

## Purpose
Implements the Abilis TB10x interrupt controller as a 32-line generic-chip domain with chained parent interrupts. It supports both level and edge trigger programming using source mode/polarity registers.

## Important APIs, Types, And Functions
`tb10x_irq_set_type()` computes source mode and polarity bits from Linux trigger flags and switches generic-chip type handlers. `of_tb10x_init_irq()` maps resources, creates the domain, allocates level and edge generic chip types, and chains all parent IRQs listed in DT.

## Control Flow
Initialization requests and maps MMIO, creates a 32-line domain, allocates generic chips, populates level and edge callbacks/register offsets, chains each parent IRQ to `tb10x_irq_cascade()`, disables all interrupts, clears modes/polarities, and acks pending status. The cascaded handler dispatches the parent IRQ number into the domain.

## State And Persistence
Generic chip mask cache and MMIO source configuration provide state. There is no explicit PM handling. MMIO resource ownership is manual and cleaned up only on init failure.

## Dependencies And Integration Points
Depends on OF address/IRQ parsing, generic irq chips, chained handlers, and compatible `abilis,tb10x-ictl`.

## Risks
The cascade handler uses the Linux parent IRQ number as the hwirq, so platform mapping must align with expected domain entries. Trigger programming starts from register reads ORed with the bit and then toggles per case, making polarity/mode definitions easy to regress. Manual resource acquisition requires careful error cleanup.

## Test Signals
Boot with one or more parent interrupts, test level-low/high and edge-rising/falling lines, verify initial disable/ack state, and run invalid mixed trigger requests to confirm `-EBADR` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-tb10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-tegra.c

## Purpose
Implements NVIDIA Tegra legacy interrupt controllers as hierarchical filters above the GIC. It manages up to six 32-line ICTLR blocks, local enable/EOI/retrigger registers, and wake state for suspend.

## Important APIs, Types, And Functions
`struct tegra_ictlr_info` stores per-controller MMIO bases and, under PM, saved CPU/COP enable/class registers plus wake masks. The irq chip wraps parent mask/unmask/eoi/retrigger/type/affinity and overrides wake handling. Domain callbacks translate GIC-style DT specifiers and allocate parent IRQs.

## Control Flow
OF init locates the parent GIC domain, matches the expected controller count, maps each ICTLR region, disables CPU interrupts, selects IRQ class, creates a hierarchy domain, and registers syscore PM when enabled. Allocation validates SPI specifiers, installs the Tegra chip with the relevant block base as chip data, then allocates the same parent GIC interrupt.

## State And Persistence
Global `lic` and `num_ictlrs` describe the singleton controller set. Suspend saves CPU/COP enable and class registers, disables all interrupts, and enables only wake masks. Resume restores saved class and enable state. Wake masks are driver state only and intentionally do not call into the parent GIC.

## Dependencies And Integration Points
Depends on OF address matching for `nvidia,tegra20-ictlr`, `tegra30`, and `tegra210`, GIC binding constants, hierarchy domains, and syscore PM.

## Risks
DT region count mismatches expected SoC data are only warnings, so wrong DT can still boot with missing interrupt lines. Wake support bypasses the GIC and relies on ICTLR wake capability. The singleton design assumes one controller node.

## Test Signals
Verify controller count on Tegra20/30/210, child interrupt delivery through GIC, mask/unmask/EOI/retrigger behavior, CPU affinity forwarding, and suspend/resume wake masks per ICTLR block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-inta.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-inta.c

## Purpose
Implements the TI K3 Interrupt Aggregator as an MSI-capable irq domain backed by TI SCI resource management. It allocates virtual interrupts, global events, and event-to-vint mappings on demand and dispatches MSI events from VINT status registers.

## Important APIs, Types, And Functions
`ti_sci_inta_irq_domain` owns the TI SCI handle, VINT/global-event resources, VINT list, mutex, MMIO base, device ID, and unmapped event-source list. `ti_sci_inta_vint_desc` tracks one VINT, parent virq, and up to 64 event descriptors. Resource allocation is deferred to `irq_request_resources()` via `ti_sci_inta_request_resources()`. The MSI layer uses `ti_sci_inta_msi_domain_info` and `ti_sci_inta_msi_set_desc()`.

## Control Flow
Probe gets the parent domain, TI SCI handle, device ID, VINT/global event resource pools, MMIO base, unmapped event sources, creates the IRQ domain, then creates an MSI domain. MSI allocation stores a packed source device/index hwirq. Requesting resources finds or allocates a VINT parent IRQ, allocates a global event, calls TI SCI `set_event_map`, and stores the event descriptor. The chained VINT handler reads masked status and dispatches the hwirq stored in each set bit.

## State And Persistence
State persists in the VINT list, event bitmaps, TI SCI resource allocations, event descriptors, and hardware VINT enable/status registers. Releasing resources frees TI SCI event maps, global events, parent VINT IRQs, and resource pool entries when a VINT becomes empty.

## Dependencies And Integration Points
Depends on TI SCI protocol/resource APIs, `ti_sci_inta_msi`, generic MSI infrastructure, OF interrupt ranges, parent GIC or interrupt-router domains, and compatible `ti,sci-inta`.

## Risks
Resource lifecycle is split between domain allocation and request_resources to avoid deadlock; regressions can leak VINTs or global events. `ti,interrupt-ranges` and unmapped-event-source handling must match firmware. Affinity is unsupported and returns `-EINVAL`. Level MSI handling depends on trigger type selection and ack suppression for high-level events.

## Test Signals
Exercise MSI consumers with rising and level-high MSIs, allocate more than 64 events to force multiple VINTs, release all events to free VINTs, validate unmapped event sources, and test parent paths through both GIC and TI interrupt router. TI SCI set/free event map failures should clean up resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-inta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-intr.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-intr.c

## Purpose
Implements the TI K3 Interrupt Router hierarchy over TI SCI. It routes input hwirqs to allocated output interrupts, then forwards those to a parent GIC or another TI interrupt router.

## Important APIs, Types, And Functions
`struct ti_sci_intr_irq_domain` stores the TI SCI handle, output IRQ resource pool, device pointer, TI SCI device ID, and optional global trigger type. `ti_sci_intr_irq_domain_translate()` supports one-cell global-type and two-cell per-line bindings. `ti_sci_intr_alloc_parent_irq()` allocates output resources and programs TI SCI `set_irq`.

## Control Flow
Probe finds the parent domain, reads `ti,intr-trigger-type` if present, gets the TI SCI handle and device ID, obtains the IR output resource pool, and creates a hierarchy domain. Allocation translates the child fwspec, gets a free output IRQ, maps it through optional `ti,interrupt-ranges`, builds a parent fwspec for GIC or another INTR, allocates parent IRQs, calls TI SCI `set_irq`, and stores the output IRQ in chip data. Free reverses the SCI route, releases the resource, frees the parent, and resets irq_data.

## State And Persistence
Driver state is per-domain and resource-pool backed. Runtime route state is held by system firmware through TI SCI plus parent irqdomain mappings. There is no explicit suspend/resume state in this source.

## Dependencies And Integration Points
Depends on TI SCI protocol/resource APIs, OF parent domains, optional `ti,interrupt-ranges`, optional global trigger property, GIC-v3 formatting, and compatible `ti,sci-intr`.

## Risks
Incorrect interrupt ranges route to wrong parent hwirqs. Parent INTR nodes may expect one-cell or two-cell specifiers depending on their trigger-type property. Freeing must call TI SCI before resource release to avoid stale firmware routes. The module author string has a typo but does not affect behavior.

## Test Signals
Test direct GIC parent and chained INTR parent configurations, one-cell global trigger and two-cell per-line trigger DT forms, output resource exhaustion, route free/reallocation, and TI SCI set/free failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ts4800.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ts4800.c

## Purpose
Implements the Technologic Systems TS-4800 FPGA multiplexed interrupt controller. It exposes eight child IRQs behind one parent interrupt and masks/unmasks them through 16-bit FPGA registers.

## Important APIs, Types, And Functions
`struct ts4800_irq_data` stores MMIO base, platform device, and domain. The irq chip supplies mask/unmask and `irq_print_chip()`. `ts4800_ic_chained_handle_irq()` reads the FPGA status register and dispatches each set bit.

## Control Flow
Probe maps MMIO, masks all child IRQs, parses the parent IRQ, creates an eight-line one-cell domain, installs the chained handler, and saves drvdata. Runtime dispatch handles all set status bits or calls `handle_bad_irq()` if the parent fires with no status.

## State And Persistence
State is the domain and MMIO base, plus hardware mask bits. Remove removes the domain but does not explicitly clear the chained handler. Device-managed allocation covers memory and MMIO lifetime.

## Dependencies And Integration Points
Depends on platform-device probing, OF address/IRQ parsing, chained irqchip helpers, seq_file chip printing, and compatible `technologic,ts4800-irqc`.

## Risks
The hardware has only eight child bits but uses 16-bit masks/status reads; invalid DT child hwirqs beyond eight are not explicitly rejected in map. Parent spurious interrupts are treated as bad IRQs. Remove should be audited if hot-unbind matters.

## Test Signals
Trigger each of eight FPGA IRQs, verify mask/unmask bits, spurious parent interrupt handling, `/proc/interrupts` chip naming, and module remove/probe cycles if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ts4800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-uniphier-aidet.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-uniphier-aidet.c

## Purpose
Implements Socionext UniPhier AIDET, an interrupt detector/polarity inverter in front of a GIC. It lets active-low and falling-edge child requests be represented while the parent sees active-high/rising signals.

## Important APIs, Types, And Functions
`struct uniphier_aidet_priv` stores the hierarchy domain, MMIO base, spinlock, and saved DETCONF registers. `uniphier_aidet_irq_set_type()` programs inverter bits and converts low/falling types to parent high/rising. Domain allocation validates one IRQ, sets the child chip, and allocates a GIC SPI parent fwspec.

## Control Flow
Probe finds the parent domain, maps MMIO, initializes the lock, and creates a 256-line hierarchy domain. Allocation translates two-cell child specifiers, validates hwirq and type, installs the AIDET chip, builds a GIC SPI fwspec, and allocates the parent. Suspend saves eight DETCONF words; resume restores them.

## State And Persistence
State is one device-managed private structure and saved DETCONF values for noirq PM. Runtime polarity state is the DETCONF inverter register. Mask/unmask/eoi/affinity operations are delegated to the parent.

## Dependencies And Integration Points
Depends on OF platform probing, parent irqdomain lookup, GIC-style parent semantics, noirq PM, and UniPhier compatible strings from LD4 through NX1.

## Risks
The parent is hard-coded as GIC SPI with hwirq equal to child hwirq. Type conversion must match hardware inverter behavior or low/falling signals will be lost. Multi-IRQ allocation is rejected. PM save/restore only covers DETCONF, not parent state.

## Test Signals
Validate all supported UniPhier compatibles, high/low level and rising/falling edge conversions, parent SPI allocation, suspend/resume retention of DETCONF, and invalid hwirq/type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-uniphier-aidet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-versatile-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-versatile-fpga.c

## Purpose
Supports ARM Versatile FPGA-based interrupt controllers, either as primary root controllers or cascaded secondary controllers. It registers valid interrupt masks, dispatches pending status, and supports the Versatile SIC pass-through register.

## Important APIs, Types, And Functions
`struct fpga_irq_data` stores MMIO base, valid mask, domain, and active IRQ count. Static `fpga_irq_devices` avoids allocation during early init. The irq chip masks by writing enable-clear, unmasks by writing enable-set, and prints the OF node name.

## Control Flow
OF init maps MMIO, reads `clear-mask` and `valid-mask`, clears IRQ/FIQ enables, maps an optional parent IRQ, and either installs a chained handler or the global root `fpga_handle_irq()`. Registration creates a linear domain sized by `fls(valid)`, pre-creates mappings for valid bits, and enables SIC pass-through bits for `arm,versatile-sic`.

## State And Persistence
State is static per-controller array entries and hardware enable registers. There is no PM state. Valid mask determines which hwirqs can map for the controller lifetime.

## Dependencies And Integration Points
Depends on early OF irqchip init, ARM exception handling, chained irq helpers, `CONFIG_VERSATILE_FPGA_IRQ_NR`, and compatible `arm,versatile-fpga-irq` or `arm,versatile-sic`.

## Risks
The static controller array can overflow if Kconfig is too small. Invalid-mask mistakes produce `-EPERM` mappings or missing child interrupts. Root-mode polling loops over all registered FPGA controllers until none is pending, so stale status can spin.

## Test Signals
Boot primary and cascaded configurations, confirm valid-mask mapping count, test mask/unmask, trigger simultaneous child bits, verify SIC pass-through behavior, and validate Kconfig controller-count coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-versatile-fpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-vf610-mscm-ir.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-vf610-mscm-ir.c

## Purpose
Implements the Freescale/NXP VF610 MSCM interrupt router hierarchy. It routes peripheral interrupts to the CPU running Linux, supports GIC and NVIC parents, and saves router state around CPU cluster power transitions.

## Important APIs, Types, And Functions
`struct vf610_mscm_ir_chip_data` stores MMIO base, CPU routing mask, saved IRSPRC registers, and whether the parent is NVIC. Chip callbacks wrap parent operations and program `MSCM_IRSPRC()` on enable/disable. Domain callbacks translate two-cell specifiers and allocate GIC or NVIC parent fwspecs.

## Control Flow
OF init finds the parent domain, maps MSCM IR registers, reads the current CPU number from the `fsl,cpucfg` syscon, creates a hierarchy domain for 112 lines, detects NVIC parent compatibility, and registers a CPU PM notifier. Enabling a child IRQ writes the local CPU mask into its route register before enabling the parent; disabling clears it.

## State And Persistence
Global singleton `mscm_ir_data` holds routing state. CPU cluster PM enter saves all 112 route registers; failed enter or exit restores them. Runtime route state is entirely hardware-backed per interrupt.

## Dependencies And Integration Points
Depends on OF address, syscon/regmap, CPU PM notifier, GIC binding constants, hierarchy domains, and compatible `fsl,vf610-mscm-ir`.

## Risks
CPU mask comes from hardware CPU ID and must match Linux's running core. Route registers are 16-bit and only low two bits are valid. Parent fwspec formatting diverges for NVIC versus GIC. PM notifier is global and assumes one controller.

## Test Signals
Validate single-core and dual-core VF610 configurations, interrupt delivery after enable, route clearing after disable, GIC and NVIC parent paths, and CPU cluster suspend/resume preserving IRSPRC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-vf610-mscm-ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-vic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-vic.c

## Purpose
Implements ARM PL190/PL192 Vectored Interrupt Controller support for legacy ARM platforms. It can operate as a root controller or cascaded controller, supports valid/wakeup source masks, and saves/restores VIC registers for PM.

## Important APIs, Types, And Functions
`struct vic_device` stores MMIO base, base IRQ, valid and resume source masks, saved registers, and domain. Static `vic_devices` holds early controllers. Core functions include `vic_register()`, `vic_handle_irq()`, `vic_handle_irq_cascaded()`, `vic_ack_irq()`, `vic_mask_irq()`, `vic_unmask_irq()`, and vendor-aware `__vic_init()`.

## Control Flow
OF init maps registers, reads `valid-mask` and `valid-wakeup-mask`, gets an optional parent IRQ, then calls `__vic_init()`. Initialization identifies the AMBA vendor, disables and clears interrupts, initializes vector registers, creates a simple domain, pre-creates valid mappings, and installs either root or chained handling. PM late init registers syscore ops when any VIC exists.

## State And Persistence
Static device records persist for the kernel lifetime. PM saves interrupt select, enable, soft interrupt, and protect registers; suspend enables only resume IRQs, and resume restores saved state. Wake configuration is maintained as `resume_irqs` filtered by `resume_sources`.

## Dependencies And Integration Points
Depends on ARM exception entry, AMBA vendor IDs, OF irqchip init, simple irqdomains, syscore PM, and compatible strings `arm,pl190-vic`, `arm,pl192-vic`, and `arm,versatile-vic`.

## Risks
Static array size is controlled by `CONFIG_ARM_VIC_NR`. Vendor-specific ST 64-interrupt behavior uses offset-sensitive initialization. Wake source validation depends on correct base IRQ calculation. Root handler polling can spin if status never clears.

## Test Signals
Boot ARM and ST VIC variants, verify valid-mask mapping, root and cascaded handling, soft interrupt ack clearing, wake-mask suspend/resume, and multiple VIC ordering during resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-vic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-vt8500.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-vt8500.c

## Purpose
Implements VIA/WonderMedia VT8500 interrupt controller support for primary and cascaded controllers. It exposes 64 hwirqs per instance with destination control, ack, mask/unmask, and trigger type programming.

## Important APIs, Types, And Functions
`struct vt8500_irq_data` stores MMIO base and domain. The irq chip implements ack by writing status, mask/unmask through destination control bytes, and trigger type selection for high level, rising edge, and falling edge. `vt8500_handle_irq_common()` dispatches the current highest-priority interrupt.

## Control Flow
OF init allocates state, maps MMIO, creates a 64-line one-cell domain, initializes hardware by enabling rotating priority and disabling/routing all lines to IRQ, then either chains parent interrupts or installs the global primary handler. Runtime reads the priority/current register, validates special hwirq 63 using status bit 31, and dispatches one domain IRQ.

## State And Persistence
State is per-controller domain/base plus global `primary_intc` for root mode. Hardware destination-control bytes carry enabled, route, and trigger state. There is no PM state cache.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/IRQ parsing, chained irq helpers, and compatible `via,vt8500-intc`.

## Risks
Low-level trigger is unsupported. The hwirq 63 special case relies on status register interpretation. Multiple controllers are supported only with exactly one primary and optional cascaded children. No explicit cleanup exists after successful early init.

## Test Signals
Boot primary-only and chained configurations, test hwirq 63 handling, mask/unmask, rising/falling/high trigger setup, and multiple parent IRQs on chained controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-vt8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-wpcm450-aic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-wpcm450-aic.c

## Purpose
Implements the Nuvoton WPCM450 Advanced Interrupt Controller as a 32-line root irqchip. It initializes source priorities/types, reads the priority encoding register to identify active interrupts, and EOIs through the end-of-service register.

## Important APIs, Types, And Functions
`struct wpcm450_aic` stores MMIO base and domain. `wpcm450_aic_init_hw()` masks all lines, primes IPER/EOSCR, and sets every source to high-level priority 7. The irq chip supports eoi, mask, unmask, and a restricted set_type accepting only level-high.

## Control Flow
OF init requires no parent, allocates singleton state, maps MMIO, initializes hardware, installs `set_handle_irq()`, and creates a 32-line two-cell domain. Runtime reads IPER, divides by four to get the hwirq, dispatches it, and EOIs after handler completion.

## State And Persistence
Global singleton `aic` holds controller state. Hardware mask/source/priority/EOS registers persist. There is no PM state or multi-instance support.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/init, irqdomain, and compatible `nuvoton,wpcm450-aic`.

## Risks
Only level-high interrupts are accepted despite hardware supporting more modes, so DTs using edge/low types fail. No parent is allowed. Domain creation return is not checked after initialization, so allocation failure would leave a partially installed root handler.

## Test Signals
Boot WPCM450, verify all 32 hwirqs map, level-high interrupt delivery and EOI, mask/unmask command registers, rejection of non-level-high DT trigger types, and no-parent enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-wpcm450-aic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-xilinx-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-xilinx-intc.c

## Purpose
Implements Xilinx OPB/XPS interrupt controller support for primary and cascaded use. It handles configurable endianness, edge-versus-level input classification, vector-register dispatch, and master enable setup.

## Important APIs, Types, And Functions
`struct xintc_irq_chip` stores MMIO base, root domain, edge mask, and number of inputs. `xintc_read()`/`xintc_write()` switch to big-endian access if MER readback indicates endian mismatch. Chip callbacks mask, unmask, ack, and mask-ack. `xil_intc_handle_irq()` and `xil_intc_irq_handler()` serve primary and chained modes.

## Control Flow
OF init maps registers, reads `xlnx,num-intr-inputs` and optional `xlnx,kind-of-intr`, disables inputs, acks pending bits, enables hardware interrupt/master bits, probes endianness, creates a linear domain, then either chains a parent IRQ or installs the primary handler/default domain. Dispatch reads IVR until the spurious value appears.

## State And Persistence
Per-controller state is allocated at init; primary mode is stored globally. Hardware state includes IER/IAR/MER and edge/level behavior configured by DT. There is no suspend/resume cache.

## Dependencies And Integration Points
Depends on OF address/IRQ parsing, irqdomain, chained handlers, jump labels for endian mode, and compatible `xlnx,xps-intc-1.00.a` or `xlnx,opb-intc-1.00.c`.

## Risks
`xintc_is_be` is a global static key, so mixed-endian instances are not supported. Edge mask width is 32 bits and must not exceed `nr_irq`. `BUG_ON(!base)` makes missing MMIO fatal. Level IRQ ack-on-unmask behavior is hardware-specific.

## Test Signals
Validate little- and big-endian hardware, primary and cascaded modes, edge and level inputs from `xlnx,kind-of-intr`, spurious IVR exit, master enable readback, and invalid DT properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-xilinx-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-mx.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-mx.c

## Purpose
Implements the Xtensa MX interrupt distributor, extending the built-in Xtensa interrupt controller with external interrupt routing, per-CPU mask caching, IPIs, and affinity programming.

## Important APIs, Types, And Functions
Per-CPU `cached_irq_mask` mirrors enabled local interrupt bits. `xtensa_mx_irq_map()` treats hardware IRQs 0-1 as per-CPU IPIs and delegates others to common Xtensa mapping. Mask/unmask either updates external MX enable registers (`MIENG`/`MIENGSET`) or the local `intenable` special register. Affinity writes `MIROUT()`.

## Control Flow
Legacy or DT init creates an irqdomain using MX ops, sets it as default, initializes this CPU's external interrupt mask, enables external edge/level bits, and routes all external interrupts to CPU0. Runtime mask/unmask checks whether an interrupt is an external MX line or a local core line, then updates the appropriate register. Retrigger only supports software interrupt types.

## State And Persistence
State is per-CPU cached mask plus MX routing registers. There is no explicit PM cache. Secondary CPU initialization re-establishes local external interrupt enable state.

## Dependencies And Integration Points
Depends on Xtensa architecture registers/helpers, common `xtensa_irq_map()` and `xtensa_irq_domain_xlate()`, SMP affinity, and compatible `cdns,xtensa-mx`.

## Risks
External interrupt numbering offsets are subtle: one/two-cell DT translation maps external specifiers with `HW_IRQ_EXTERN_BASE`. Affinity uses `cpumask_any_and()` without explicit no-CPU error handling. Local cached masks must remain in sync with `intenable`.

## Test Signals
Boot DT and legacy paths, verify IPI hwirqs 0-1, external interrupt mask/unmask through MX registers, local interrupt mask cache, affinity routing to online CPUs, secondary CPU init, and software retrigger validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-mx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-pic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-pic.c

## Purpose
Implements the built-in Xtensa programmable interrupt controller. It provides the default irqdomain and simple mask/unmask/ack/retrigger operations over Xtensa special registers.

## Important APIs, Types, And Functions
`xtensa_pic_irq_domain_xlate()` handles one- or two-cell specifiers using common Xtensa translation. The irq chip updates `intenable`, clears pending bits through `intclear`, and retriggers software interrupts through `intset`.

## Control Flow
Legacy or DT init creates a domain, installs common Xtensa map ops, and sets it as the default domain. Runtime masking clears a bit in `intenable`, unmasking sets it, ack writes the hwirq bit to `intclear`, and retrigger rejects non-software interrupt types.

## State And Persistence
State is CPU-local special registers and the default domain. The file keeps no private heap or MMIO state and has no suspend/resume hooks.

## Dependencies And Integration Points
Depends on Xtensa architecture macros, common Xtensa irqchip helpers, irqdomain APIs, and compatible `cdns,xtensa-pic`.

## Risks
The controller directly manipulates special registers, so callers must respect CPU-local semantics. Retrigger only works for software interrupts. DT specifier translation must distinguish internal versus external numbering consistently with other Xtensa controllers.

## Test Signals
Boot legacy and DT platforms, verify default domain setup, mask/unmask/ack on internal interrupts, software retrigger behavior, and rejection of non-software retrigger attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-zevio.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-zevio.c

## Purpose
Implements the Zevio/TI-Nspire classic root interrupt controller. It initializes IRQ/FIQ priority blocks, exposes 32 IRQ lines through a generic-chip domain, and dispatches the current interrupt from hardware registers.

## Important APIs, Types, And Functions
Global `zevio_irq_domain` and `zevio_irq_io` store singleton state. `zevio_init_irq_base()` disables, sets max priority, and resets each IRQ/FIQ block. `zevio_irq_ack()` acks by reading the reset register. Generic-chip callbacks handle enable/disable mask registers.

## Control Flow
OF init rejects multiple instances, maps MMIO, programs non-inverted non-sticky highest-priority operation, initializes IRQ and FIQ blocks, creates a 32-line generic-chip domain, configures mask/enable/disable/ack offsets, installs the root handler, and logs controller presence. Runtime loops while status is nonzero, reads `IO_CURRENT`, and dispatches that hwirq.

## State And Persistence
State is global singleton domain/MMIO and generic chip mask cache. Hardware priority, invert, sticky, enable, and reset registers persist. There is no PM handling.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/init, generic irq chips, and compatible `lsi,zevio-intc`.

## Risks
The code uses `BUG_ON` for critical allocation/mapping failures. FIQ is initialized but not exposed as a separate domain. Ack by read from reset register is unusual and hardware-specific. Singleton guard rejects additional controllers.

## Test Signals
Boot supported hardware, confirm root handler installation, dispatch all 32 IRQs, verify priority/status loop exits, mask/unmask via generic chip, and ensure no second controller node is accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-zevio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irqchip.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irqchip.c

## Purpose
Provides the common irqchip initialization entry points. It invokes linker-table based OF irqchip initialization and ACPI irqchip table probing, and exports the helper used by platform irqchip drivers to defer until their parent domains exist.

## Important APIs, Types, And Functions
`irqchip_init()` calls `of_irq_init(__irqchip_of_table)` and `acpi_probe_device_table(irqchip)`. `platform_irqchip_probe()` retrieves the matched probe callback, finds the OF parent, defers when the parent domain is not ready, and invokes the platform irqchip probe with the parent node.

## Control Flow
Early boot calls `irqchip_init()` to initialize statically declared irqchips. Platform irqchip drivers using `IRQCHIP_PLATFORM_DRIVER` later call `platform_irqchip_probe()` through their probe path. The helper normalizes a self-parent node to `NULL`, checks parent domain readiness, and returns `-EPROBE_DEFER` when ordering is not yet satisfied.

## State And Persistence
The file owns no mutable runtime state except the linker-table sentinel symbol. It coordinates initialization rather than representing hardware.

## Dependencies And Integration Points
Depends on OF irq initialization, ACPI probing, platform devices, match data carrying `platform_irq_probe_t`, and the special `__irqchip_of_table` linker section.

## Risks
Missing match data returns `-EINVAL`, so platform irqchip declarations must provide probe callbacks. Parent-domain checks use `DOMAIN_BUS_ANY`; specialized domains may still require additional checks in the driver. Incorrect handling of self-parent nodes could cause false defers.

## Test Signals
Boot systems with OF-only, ACPI-only, and platform irqchip drivers, verify parent-probe deferral ordering, and test platform irqchip nodes whose parent is not yet registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irqchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/qcom-irq-combiner.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/qcom-irq-combiner.c

## Purpose
Implements an ACPI-only Qualcomm TCSR interrupt combiner. It ORs read-only status registers behind one parent interrupt and exposes individual child status bits as Linux IRQs with software-maintained enable masks.

## Important APIs, Types, And Functions
`struct combiner` stores the child domain, parent IRQ, total IRQ count, register count, and flexible array of `combiner_reg` entries. Each register stores an MMIO address and enabled bitmask. ACPI helpers count and map Generic Register resources from `_CRS`.

## Control Flow
Probe counts ACPI generic-register resources, allocates the combiner, maps each register, sums bit widths into `nirqs`, obtains the parent IRQ, creates a linear domain, and installs a chained handler. The handler reads each status register, ANDs with the software enabled mask, warns for unexpected disabled pending bits, and dispatches each enabled child bit.

## State And Persistence
Mutable state is only the per-register `enabled` bitmask; hardware status registers are read-only. There is no suspend/resume state. Device-managed allocation covers mappings and combiner storage.

## Dependencies And Integration Points
Depends on ACPI `_CRS` generic-register resources, platform IRQ acquisition, chained irqchip helpers, irqdomain translation for ACPI fwspecs, and HID `QCOM80B1`.

## Risks
Only ACPI fwspecs are accepted; DT is intentionally unsupported. Resource validation rejects non-memory, nonzero bit-offset, or wider-than-32-bit registers. Since masking is software-only, disabled hardware sources can still assert the parent and produce warnings. Edge trigger flags are rejected.

## Test Signals
Boot ACPI systems with QCOM80B1, validate register count/mapping, child IRQ translation, software mask/unmask behavior, warning path for disabled pending bits, and level-trigger dispatch for all declared register bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/qcom-irq-combiner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/qcom-pdc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/qcom-pdc.c

## Purpose
Implements Qualcomm Power Domain Controller wakeup interrupts as a hierarchy above the GIC. It maps GPIO/PDC wake pins to parent GIC SPIs, controls PDC enable bits, converts polarity/edge types for the GIC, and handles version- and X1E-specific register layouts.

## Important APIs, Types, And Functions
`struct pdc_pin_region` maps PDC pin ranges to parent hwirq ranges. Global state stores PDC MMIO bases, region table, version, and X1E quirk flag. `qcom_pdc_gic_set_type()` programs PDC type bits and converts low/falling/both to parent-supported high/rising. `pdc_setup_pin_mapping()` parses `qcom,pdc-ranges` and disables all mapped PDC interrupts.

## Control Flow
Platform probe maps the current PDC region and, on X1E, the previous DRV region needed for an enable-bank write workaround. It reads PDC version, finds the parent domain, parses pin mappings, creates a wakeup hierarchy domain, and marks it `DOMAIN_BUS_WAKEUP`. Allocation translates two-cell child specifiers, handles `GPIO_NO_WAKE_IRQ` disconnects, installs the PDC chip, finds the pin region, normalizes parent trigger type, and allocates the parent GIC IRQ.

## State And Persistence
State is global because the PDC is treated as a singleton: MMIO bases, region table, version, lock, and quirk. Hardware state is IRQ enable banks or per-IRQ config enable bits plus type bits. There is no explicit PM cache; wake behavior is represented by irqchip flags and the wakeup domain token.

## Dependencies And Integration Points
Depends on OF platform irqchip probing, GIC parent domain, Qualcomm GPIO wake constants, raw spinlock protection, `qcom,pdc-ranges`, compatible `qcom,pdc`, and special compatible `qcom,x1e80100-pdc`.

## Risks
Pin-region mappings are safety-critical; missing regions disconnect hierarchy allocation. Hardware versions before and after 3.2 use different enable layouts. X1E remaps enable-bank writes across DRV regions, and incorrect bank shifting can enable the wrong wake line. Type changes may generate phantom interrupts, so pending parent state is cleared after reconfiguration.

## Test Signals
Validate old and new PDC versions, X1E quirk bank remapping, GPIO wake/no-wake allocations, all trigger types, suspend wake from PDC lines, `qcom,pdc-ranges` parsing failures, and phantom interrupt clearing after type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/qcom-pdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/spear-shirq.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/spear-shirq.c

## Purpose
Implements shared interrupt demultiplexing for ST SPEAr300/310/320 platforms. It maps SoC-specific shared IRQ blocks into legacy Linux IRQ descriptors and dispatches child interrupts from shared status bits.

## Important APIs, Types, And Functions
`struct spear_shirq` describes each block's MMIO base, status/mask registers, bit mask, virtual IRQ base, number of IRQs, bit offset, and chip. Static block tables define SPEAr300/310/320 layouts. `shirq_irq_mask()` and `_unmask()` update mask registers under a global raw spinlock, while `shirq_handler()` dispatches pending child bits.

## Control Flow
Variant OF init calls `shirq_init()`, which maps MMIO, totals child counts, allocates a contiguous descriptor range, creates a legacy domain, assigns each block base and virq base, parses the matching parent IRQ, and registers a chained handler plus per-child chip/handler. Runtime masks status with the block mask, shifts by offset, and calls `generic_handle_irq()` for each pending child virq.

## State And Persistence
Static block descriptors are mutated with base and virq base at init. Hardware mask/status registers persist. There is no PM state, and cleanup exists only for early init failure.

## Dependencies And Integration Points
Depends on OF early irqchip init, legacy irq descriptor allocation, simple legacy irqdomains, chained handlers, and compatibles `st,spear300-shirq`, `st,spear310-shirq`, and `st,spear320-shirq`.

## Risks
Uses legacy virq allocation instead of hierarchical domains, so descriptor base stability matters. Some blocks use `dummy_irq_chip`, meaning mask/unmask is not available for all variants. Parent IRQ count/order must match the static block table. Global spinlock serializes mask changes across all blocks.

## Test Signals
Boot each SPEAr variant, verify contiguous descriptor allocation and domain mappings, trigger every shared block bit, test mask/unmask on SPEAr300, validate dummy-chip blocks dispatch correctly, and check failure cleanup for descriptor/domain allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/spear-shirq.c -->
