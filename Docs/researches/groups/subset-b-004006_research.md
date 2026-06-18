# subset-b-004006 research

This grouped report covers Linux irqchip drivers under `sources/distributed-fs/ceph-client/drivers/irqchip`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-or1k-pic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-or1k-pic.c

## Purpose
`irq-or1k-pic.c` implements the OpenRISC/OpenCores CPU-local programmable interrupt controller. It is the root interrupt controller for OR1K CPU exceptions and supports generic level, generic edge, and OR1200-specific latch behavior.

## Important APIs, Types, and Functions
`struct or1k_pic_dev` couples an `irq_chip`, flow handler, and status flags. The chip callbacks are `or1k_pic_mask()`, `or1k_pic_unmask()`, `or1k_pic_ack()`, `or1k_pic_mask_ack()`, plus OR1200 variants that clear `SPR_PICSR` by writing a zeroed bit. `pic_get_irq()` scans `SPR_PICSR`, `or1k_pic_handle_irq()` dispatches through `generic_handle_domain_irq()`, and `or1k_map()` installs the chip and handler. Init entry points are declared with `IRQCHIP_DECLARE()` for `opencores,or1200-pic`, `opencores,or1k-pic`, `opencores,or1k-pic-level`, and `opencores,or1k-pic-edge`.

## Control Flow
Initialization disables all PIC sources by clearing `SPR_PICMR`, creates a 32-entry linear root domain, and installs `or1k_pic_handle_irq()` via `set_handle_irq()`. On each CPU IRQ exception, pending bits in `SPR_PICSR` are scanned from low to high and dispatched into the domain. Mapping selects `handle_level_irq`, `handle_edge_irq`, or an SMP wrapper that delegates per-CPU requested interrupts to `handle_percpu_devid_irq()`.

## State and Persistence
State is CPU SPR backed: `SPR_PICMR` holds masks and `SPR_PICSR` holds pending/latch bits. The only global software state is `root_domain` and static chip descriptors. There is no persistent storage or suspend cache here.

## Dependencies and Integration Points
The driver depends on OR1K `mfspr()`/`mtspr()` accessors, Linux irqdomain, OF irqchip declaration, and the architecture root IRQ handler hook. It integrates directly with generic IRQ flow handlers and SMP per-CPU IRQ semantics.

## Risks and Edge Cases
The OR1200 clear-by-zero behavior differs from the OR1K spec, so choosing the wrong compatible can leave latched level interrupts stuck. `root_domain` is a singleton and assumes one root PIC. `or1k_pic_edge.flags` uses `IRQ_LEVEL`, which is unusual for an edge chip and should be treated as an inherited platform convention.

## Test Signals
Useful signals are successful boot root-domain creation, correct `/proc/interrupts` increments for all 32 hardware lines, masking/unmasking via `SPR_PICMR`, edge ACK behavior, OR1200 level-latch clearing, SMP per-CPU interrupt handling, and absence of repeated stuck interrupts after handler return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-or1k-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-orion.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-orion.c

## Purpose
`irq-orion.c` supports Marvell Orion interrupt controllers. It contains a root controller for SoC interrupt cause/mask banks and a cascaded bridge controller used behind a parent interrupt.

## Important APIs, Types, and Functions
The main controller uses `orion_handle_irq()` and `orion_irq_init()`. It creates a generic-chip linear domain, one 32-bit generic chip per MMIO resource, and uses `irq_gc_mask_clr_bit`/`irq_gc_mask_set_bit` over `ORION_IRQ_MASK`. The bridge path uses `orion_bridge_irq_handler()`, `orion_bridge_irq_startup()`, and `orion_bridge_irq_init()` with `ORION_BRIDGE_IRQ_CAUSE` and `ORION_BRIDGE_IRQ_MASK`.

## Control Flow
For the root controller, OF address count determines how many 32-source banks exist. Probe creates the domain, maps each resource, masks every source, and installs `orion_handle_irq()` as the architecture handler. The handler iterates all banks, intersects cause with `mask_cache`, takes the highest set bit with `__fls()`, and dispatches it. The bridge controller creates a 32-source or DT-sized domain, maps its parent IRQ, masks and clears all child sources, then installs a chained handler that demultiplexes pending bridge bits.

## State and Persistence
Runtime state is the global `orion_irq_domain`, generic-chip `mask_cache`, and mapped MMIO registers. The driver does not save/restore state explicitly and relies on platform-level retention or boot-time reinitialization.

## Dependencies and Integration Points
It uses OF address and IRQ parsing, `irq_generic_chip_ops`, generic-chip helpers, `request_mem_region()`, `ioremap()`, `set_handle_irq()`, and chained IRQ handling. It is declared for `marvell,orion-intc` and `marvell,orion-bridge-intc`.

## Risks and Edge Cases
The root init path panics on allocation or mapping failures because no interrupt controller is recoverable during early boot. Bridge `IRQ_CAUSE` can assert even while masked, so startup ACKs stale causes before unmasking; missing that ordering would deliver old events. Bridge cleanup paths do not undo prior allocations on later failures because this is early irqchip setup.

## Test Signals
Test by booting with multiple register banks, checking masked sources remain silent, validating bridge startup does not replay stale pending bits, exercising chained parent IRQ delivery, and confirming DT `marvell,#interrupts` sizes the bridge domain correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-owl-sirq.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-owl-sirq.c

## Purpose
`irq-owl-sirq.c` implements the Actions Semi Owl SIRQ controller, a small hierarchical controller that adapts three external interrupt lines into parent GIC SPIs while handling polarity and edge conversion in Owl-specific registers.

## Important APIs, Types, and Functions
`struct owl_sirq_params` describes whether SIRQ control fields share one register or use separate offsets. `struct owl_sirq_chip_data` stores mapped registers, the spinlock, and parent SPI numbers. Register helpers include `owl_field_get()`, `owl_field_prep()`, `owl_sirq_read_extctl()`, `owl_sirq_write_extctl()`, and `owl_sirq_clear_set_extctl()`. IRQ operations are `owl_sirq_mask()`, `owl_sirq_unmask()`, `owl_sirq_eoi()`, and `owl_sirq_set_type()`. Domain callbacks are `owl_sirq_domain_translate()` and `owl_sirq_domain_alloc()`.

## Control Flow
Init locates the parent domain, allocates chip data, maps the register block, parses three parent interrupts, records each parent SPI, and selects a 24 MHz external interrupt clock. A hierarchical domain is then created for three child IRQs. Allocation validates a two-cell child spec, converts falling/low child requests into rising/high parent semantics, installs `owl_sirq_chip`, and allocates the corresponding GIC SPI from the parent.

## State and Persistence
State lives in the chip data and the SIRQ control registers. The raw spinlock serializes shared-register read/modify/write operations. No suspend cache exists; register contents must survive power management or be restored by platform setup.

## Dependencies and Integration Points
The driver depends on OF irq parsing, parent irqdomains, GIC binding cell layout, hierarchical IRQ APIs, `irq_chip_*_parent()` helpers, and `dt-bindings/interrupt-controller/arm-gic.h`. Compatibles cover `actions,s500-sirq`, `actions,s700-sirq`, and `actions,s900-sirq`.

## Risks and Edge Cases
Only three SIRQ lines are valid; wrong DT cell counts or parent interrupt cells fail allocation/init. Because GIC cannot directly represent falling edge or active-low here, the child controller must correctly invert/convert signals. Edge EOI clears pending only for non-level interrupts, so incorrect trigger typing can cause missed or repeated interrupts.

## Test Signals
Validate all three SIRQ lines, S500/S700 shared-field packing, S900 independent offsets, low/falling conversion to parent high/rising, edge pending clear on EOI, SMP affinity pass-through, and failure reporting for malformed DT interrupt specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-owl-sirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pic32-evic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-pic32-evic.c

## Purpose
`irq-pic32-evic.c` drives the Microchip PIC32MZDA EVIC interrupt controller. It maps the controller's linear interrupt list into Linux IRQs, separates persistent and non-persistent interrupts into level and edge generic-chip types, and handles external IRQ polarity.

## Important APIs, Types, and Functions
`struct evic_chip_data` caches per-hwirq trigger types and up to eight externally polarity-programmable hwirqs. `plat_irq_dispatch()` reads `REG_INTSTAT` and invokes `do_domain_IRQ()` on MIPS. Type and configuration helpers are `pic32_set_ext_polarity()`, `pic32_set_type_edge()`, `pic32_bind_evic_interrupt()`, and `pic32_set_irq_priority()`. Domain operations are `pic32_irq_domain_xlate()` and `pic32_irq_domain_map()`, with setup in `pic32_of_init()`.

## Control Flow
Probe maps EVIC MMIO, allocates private data and a linear domain sized to `NR_IRQS`, then allocates two generic-chip types per 32-bit bank. DT translation records each hwirq's sense type. Mapping invokes `irq_map_generic_chip()`, switches to the edge chip when the recorded type indicates an edge interrupt, masks and clears the source, and programs a default priority. External IRQ numbers from `microchip,external-irqs` are used to permit rising/falling polarity changes through `INTCON`.

## State and Persistence
The global `evic_base` and `evic_irq_domain` back a single controller. Trigger type choices are cached in `evic_chip_data.irq_types` so mapping can select the right generic chip. EVIC enable, flag, priority, offset, and polarity registers are volatile hardware state without explicit suspend persistence.

## Dependencies and Integration Points
The file integrates with MIPS trap dispatch, Microchip PIC32 register helper macros, OF address parsing, Linux generic IRQ chips, default irqdomain selection, and optional board EIC binding through `board_bind_eic_interrupt`.

## Risks and Edge Cases
The driver assumes all interrupts are described through DT so `xlate()` can pre-cache trigger types before mapping. External interrupts support only one edge polarity, not both. `NR_IRQS` bounds hwirq validation; mismatched kernel configuration and hardware interrupt count can reject valid hardware or expose unused slots.

## Test Signals
Useful tests include DT-triggered level and edge mappings, external rising/falling polarity, EVIC priority programming, MIPS dispatch from `REG_INTSTAT`, masking and flag clearing during map, and boot logs/errors for invalid hwirqs or oversized external IRQ lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pic32-evic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pruss-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-pruss-intc.c

## Purpose
`irq-pruss-intc.c` is the TI PRU-ICSS/ICSSG interrupt controller driver. It maps PRU system events to PRU channels and host interrupts, then demultiplexes host interrupt lines presented to the MPU.

## Important APIs, Types, and Functions
`struct pruss_intc` owns event-to-channel and channel-to-host reference-counted maps, host IRQs, MMIO base, domain, SoC limits, device pointer, and a mutex. `struct pruss_intc_map_record` tracks a mapped value and refcount. Hardware helpers update CMR/HMR registers. Mapping lifecycle is `pruss_intc_validate_mapping()`, `pruss_intc_map()`, and `pruss_intc_unmap()`. IRQ callbacks include ACK/mask/unmask, request/release resources, pending get/set state, domain xlate/map/unmap, and the chained `pruss_intc_irq_handler()`.

## Control Flow
Probe reads SoC match data, maps registers, optionally reads `ti,irqs-reserved`, initializes all system events as active-high level, clears CMR/HMR, enables global interrupts, creates a linear domain, and attaches chained handlers for available host interrupt resources. DT interrupt cells specify system event, channel, and host. Translation validates ranges and conflicting mappings. Mapping writes CMR/ESR/SECR, enables the host mapping on first channel user, and installs a level IRQ chip. The chained handler repeatedly reads `HIPIR(host)` for the highest-priority pending system event and dispatches the domain IRQ, ACKing unmapped events defensively.

## State and Persistence
The driver maintains non-persistent runtime allocation state in the event/channel refcount arrays. Module references are held while child IRQ resources are requested. Hardware mappings are undone when IRQs are unmapped and fully cleared on driver initialization.

## Dependencies and Integration Points
It is a platform driver for `ti,pruss-intc` and `ti,icssg-intc`, depends on OF IRQ resources named `host_intr0` through `host_intr7`, chained IRQ helpers, irqdomain, and PRU firmware/client DT mappings.

## Risks and Edge Cases
Conflicting reuse of a system event or channel returns `-EBUSY`. The host numbering exposed to hardware is offset by `FIRST_PRU_HOST_INT`; DT cells and named platform IRQs must agree. Reserved host IRQ bits skip platform IRQ acquisition. Unmapped pending events are manually cleared to avoid interrupt storms.

## Test Signals
Exercise multiple clients sharing a mapping, conflict rejection, domain unmap refcount teardown, software pending set/clear via irqchip state, all host interrupt names, `ti,irqs-reserved`, and chained dispatch loops under simultaneous PRU system events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pruss-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-qcom-mpm.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-qcom-mpm.c

## Purpose
`irq-qcom-mpm.c` implements the Qualcomm MSM Power Manager wakeup interrupt controller. It programs a shared vMPM register image used by the application processor while awake and handed to RPM firmware during deep power collapse.

## Important APIs, Types, and Functions
`struct qcom_mpm_priv` stores the vMPM base, lock, mailbox client/channel, MPM-to-GIC pin map, register stride, wakeup domain, and generic PM domain. Register helpers `qcom_mpm_read()` and `qcom_mpm_write()` access enable, edge, polarity, and status banks. IRQ operations are `qcom_mpm_mask()`, `qcom_mpm_unmask()`, and `qcom_mpm_set_type()`. Allocation is handled by `qcom_mpm_alloc()`, wake status by `qcom_mpm_handler()`, power-collapse notification by `mpm_pd_power_off()`, and platform setup by `qcom_mpm_probe()`.

## Control Flow
Probe reads `qcom,mpm-pin-count` and `qcom,mpm-pin-map`, maps either RPM message RAM or local MMIO, clears all MPM register banks, initializes a GENPD, acquires a mailbox channel, creates a wakeup irqdomain above the parent GIC domain, and requests the MPM wake IRQ. Allocation translates a two-cell MPM pin, handles `GPIO_NO_WAKE_IRQ` disconnection, installs the MPM chip, maps the pin to its GIC hwirq, normalizes parent trigger type to high/rising, and allocates the parent IRQ. On deep sleep entry, status registers are cleared and RPM is notified by mailbox. On wake, the handler scans enabled pending MPM pins and marks non-level mapped IRQs pending.

## State and Persistence
vMPM register contents are the meaningful state: enable bits, edge selections, polarity bits, and status bits. A raw spinlock serializes register updates. The GENPD power-off path transfers state to RPM; there is no filesystem persistence.

## Dependencies and Integration Points
The driver depends on mailbox/RPM firmware, generic PM domains, OF platform irqchip matching, IRQ wakeup domains, parent GIC hierarchy, and Qualcomm `GPIO_NO_WAKE_IRQ` semantics.

## Risks and Edge Cases
Duplicate GIC hwirq map entries are warned and skipped, which can leave an MPM pin disconnected. `qcom_mpm_handler()` assumes `irq_resolve_mapping()` returns a descriptor for pending pins; malformed maps can expose null descriptor risk. Missing MSI/message RAM mailbox prevents deep-sleep programming.

## Test Signals
Validate suspend/resume wake from each mapped pin, parent GIC type normalization, `GPIO_NO_WAKE_IRQ` paths, duplicate map handling, RPM mailbox notification on GENPD power-off, and status-to-pending replay for edge-triggered interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-qcom-mpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-rda-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-rda-intc.c

## Purpose
`irq-rda-intc.c` is the root interrupt controller driver for RDA8810PL SoCs. It exposes 32 level-triggered interrupt sources to the Linux generic IRQ subsystem.

## Important APIs, Types, and Functions
Global state is `rda_intc_base` and `rda_irq_domain`. Chip callbacks are `rda_intc_mask_irq()`, `rda_intc_unmask_irq()`, and `rda_intc_set_type()`. `rda_handle_irq()` reads `RDA_INTC_FINALSTATUS` and dispatches pending bits. `rda_irq_map()` installs `rda_irq_chip`, and `rda8810_intc_init()` maps registers, masks all sources, creates the domain, and installs the root handler.

## Control Flow
Early OF init maps the controller with `of_io_request_and_map()`, writes `RDA_IRQ_MASK_ALL` to the mask-clear register, creates a 32-entry linear domain, and calls `set_handle_irq()`. During an IRQ exception, `rda_handle_irq()` reads final masked status, repeatedly handles the highest set bit through `generic_handle_domain_irq()`, and clears the bit from the local software copy.

## State and Persistence
The controller has volatile mask and status registers. The driver does not keep per-interrupt software state beyond the irqdomain and mapped base address. No suspend cache is provided.

## Dependencies and Integration Points
It depends on OF irqchip declaration for `rda,8810pl-intc`, Linux irqdomain one-cell translation, ARM exception handler plumbing, and `handle_level_irq`.

## Risks and Edge Cases
`rda_intc_set_type()` accepts high or low level trigger requests only; edge trigger consumers fail. Initialization cleanup only unmaps on domain allocation failure and does not release the requested region explicitly. The root handler assumes final status is already mask-filtered by hardware.

## Test Signals
Boot-time domain creation, mask/unmask register writes, rejection of edge-triggered DT consumers, correct highest-bit dispatch, and no repeated level IRQs after the device deasserts are the key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-rda-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-realtek-rtl.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-realtek-rtl.c

## Purpose
`irq-realtek-rtl.c` implements the cascaded interrupt controller used by Realtek RTL SoCs. It routes up to 32 SoC interrupt inputs onto a parent CPU interrupt and masks/demultiplexes them in software.

## Important APIs, Types, and Functions
Global state includes `realtek_ictl_base` and a raw spinlock. Routing helpers `IRR_OFFSET()`, `IRR_SHIFT()`, and `write_irr()` program the unusual reversed nibble layout in `IRR0` through `IRR3`. IRQ chip callbacks are `realtek_ictl_mask_irq()` and `realtek_ictl_unmask_irq()`. Domain mapping is `intc_map()`, chained dispatch is `realtek_irq_dispatch()`, and init is `realtek_rtl_of_init()`.

## Control Flow
Init maps MMIO, disables all inputs, clears routing for every source, finds the parent IRQ either from DT or by falling back to MIPS CPU IRQ 2, creates a 32-entry domain, and installs a chained handler. Mapping a child IRQ assigns the level handler and programs its routing value to output line 0. Dispatch reads `GIMR & GISR`, reports spurious if no pending bits exist, and dispatches each set input through the domain.

## State and Persistence
State is volatile: global interrupt mask, global status, and routing registers. The raw spinlock protects mask and routing read/modify/write sequences. No suspend/resume persistence is implemented.

## Dependencies and Integration Points
The driver depends on OF address/IRQ parsing, MIPS CPU interrupt fallback, chained IRQ handling, irqdomain one-cell translation, and `handle_level_irq`.

## Risks and Edge Cases
The route value is hard-coded to output 0 for all mapped sources, so platforms with different wiring need DT/driver changes. The fallback parent IRQ path assumes known hardware topology when DT lacks parent interrupts. Routing register indexing is inverted; mistakes there disconnect or misroute sources.

## Test Signals
Validate DT and fallback parent IRQ paths, all 32 input mappings, `GIMR` masking, spurious interrupt logging when status is empty, and correct IRR nibble programming for low and high hwirq numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-realtek-rtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-intc-irqpin.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-intc-irqpin.c

## Purpose
`irq-renesas-intc-irqpin.c` drives Renesas INTC external IRQ pin blocks. It turns one to eight external pins into Linux IRQs, handling sense configuration, priority masking, source clearing, optional shared parent IRQs, wake propagation, and runtime PM.

## Important APIs, Types, and Functions
`struct intc_irqpin_priv` contains register descriptors, per-line IRQ metadata, sense width, platform device, irqchip, domain, wakeup counter, and shared IRQ mask. `struct intc_irqpin_iomem` abstracts 8-bit versus 32-bit access. Core helpers include `intc_irqpin_read_modify_write()`, `intc_irqpin_mask_unmask_prio()`, `intc_irqpin_set_sense()`, enable/disable variants, `intc_irqpin_irq_set_type()`, `intc_irqpin_irq_set_wake()`, per-line and shared handlers, domain map, probe/remove, and suspend.

## Control Flow
Probe enables runtime PM, gathers mandatory register resources and up to eight IRQ resources, maps each register with width-specific accessors, optionally selects individual IRQ mode via IRLM, masks priorities, clears pending source bits, detects whether all lines share one parent IRQ, selects enable/disable strategy, creates a simple domain, and requests either one shared parent IRQ or one parent per line. Runtime demux checks source status, clears the active bit, and invokes the domain IRQ.

## State and Persistence
Software state is per platform instance and devm-managed except the irqdomain. `shared_irq_mask` tracks disabled children when one parent line is shared. `wakeup_path` counts wake-enabled child IRQs and marks the device as a wakeup path during suspend. Register state is not cached across power loss.

## Dependencies and Integration Points
It integrates with platform resources, OF compatibles for several Renesas variants, runtime PM, irqdomain two-cell translation, parent IRQ request APIs, lockdep classing, and `postcore_initcall()` registration.

## Risks and Edge Cases
Mandatory register resources must be in the expected order and size. Shared source registers and priority/sense RMW paths need locking, but source/mask/clear registers assume single-driver ownership. `control-parent` force-masks parent chips directly and assumes 1:1 non-shared parent mapping. Wake counter imbalance would misreport wake paths.

## Test Signals
Test 8-bit and 32-bit register variants, one to eight lines, shared and non-shared parents, `control-parent`, all supported trigger senses, wake enable/disable and suspend marking, IRLM-capable SoCs, and pending-source clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-intc-irqpin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-irqc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-irqc.c

## Purpose
`irq-renesas-irqc.c` implements the Renesas IRQC platform driver, a demultiplexer for up to 32 external interrupts with configurable level/edge detection and wake propagation to parent IRQs.

## Important APIs, Types, and Functions
`struct irqc_priv` stores mapped registers, CPU interrupt base, per-line parent IRQs, generic chip, irqdomain, device, and wakeup counter. `irqc_irq_set_type()` writes `IRQC_CONFIG(n)` sense bits, `irqc_irq_set_wake()` propagates wake to the requested parent IRQ, and `irqc_irq_handler()` checks and clears `DETECT_STATUS` before dispatching a child domain IRQ. Probe/remove/suspend are `irqc_probe()`, `irqc_remove()`, and `irqc_suspend()`.

## Control Flow
Probe enables runtime PM, collects one to 32 parent IRQ resources, maps MMIO, creates a linear generic-chip domain, configures the generic chip to use `IRQC_EN_SET`/`IRQC_EN_STS`, installs set-type and set-wake callbacks, associates the PM device, and requests each parent IRQ with the demux handler. The handler validates the hardware detect bit for its line, clears it by writing the bit back, and dispatches through `generic_handle_domain_irq()`.

## State and Persistence
State is per device instance. The generic chip tracks masks in hardware enable/status registers, while `wakeup_path` records wake-enabled children for suspend. There is no explicit register cache for trigger type or enable state across power loss.

## Dependencies and Integration Points
The driver depends on platform resources, runtime PM, generic IRQ chips with nested-lock init, irqdomain linear mapping, and OF compatible `renesas,irqc`. It registers at `postcore_initcall()`.

## Risks and Edge Cases
`IRQC_EN_STS` is used as the disable register for generic-chip masking, so hardware semantics must match mask-disable helper expectations. Every child line needs a parent IRQ resource; missing optional resources terminate enumeration. Wake count imbalance or parent wake failure is not rolled back.

## Test Signals
Validate all supported trigger types, per-line detect clear, one-line and multi-line instances, runtime PM activation, wake propagation, generic-chip mask/unmask register writes, and clean domain removal on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-irqc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rza1.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rza1.c

## Purpose
`irq-renesas-rza1.c` drives the Renesas RZ/A1 IRQC, a hierarchical controller that configures eight local IRQ inputs and forwards them to a parent GIC according to an `interrupt-map`.

## Important APIs, Types, and Functions
`struct rza1_irqc_priv` stores the device, MMIO base, local irqchip, hierarchical domain, and parsed parent interrupt map. IRQ callbacks are `rza1_irqc_eoi()` and `rza1_irqc_set_type()`. Domain operations are `rza1_irqc_translate()` and `rza1_irqc_alloc()`. `rza1_irqc_parse_map()` reads `interrupt-map`, and probe/remove are `rza1_irqc_probe()`/`rza1_irqc_remove()`.

## Control Flow
Probe maps MMIO, locates the parent GIC domain, parses `interrupt-map` entries in child hwirq order, sets up an irqchip that delegates mask/unmask/retrigger to the parent but locally handles EOI and trigger type, and creates an eight-entry hierarchical domain. Allocation installs the chip for the local hwirq and forwards allocation to the stored parent fwspec. EOI clears `IRQRR` only when the pending bit is set, then EOIs the parent.

## State and Persistence
The parsed parent map is per-device software state. Hardware state is the 16-bit control and request registers. There is no power-management cache or persistent configuration.

## Dependencies and Integration Points
It depends on OF interrupt-map parsing, parent GIC hierarchy, ARM GIC binding cells, irqdomain hierarchy, platform driver registration, and parent irqchip helper callbacks.

## Risks and Edge Cases
`rza1_irqc_parse_map()` requires the `interrupt-map` entries to appear in exact child IRQ order and to target the discovered GIC node. Only low level and edge falling/rising/both are supported; high level is not accepted by local hardware. `rza1_irqc_eoi()` writes all request bits except the current one, so hardware write semantics are critical.

## Test Signals
Test all eight inputs, interrupt-map ordering validation, parent GIC allocation, level-low and edge modes, EOI clearing of `IRQRR`, and removal-domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rza1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzg2l.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzg2l.c

## Purpose
`irq-renesas-rzg2l.c` implements the Renesas RZ/G2L, RZ/G3L, and RZ/Five IRQC. It exposes NMI, direct IRQ, and GPIO TINT sources through a hierarchical domain, with SoC-specific IRQ/TINT counts, shared IRQ selection, TINT lookup tables, and suspend/resume restoration.

## Important APIs, Types, and Functions
`struct rzg2l_irqc_priv` stores MMIO, selected IRQ/TINT chips, parent fwspecs, lock, hardware info, register cache, and shared-line bitmap. `struct rzg2l_hw_info` captures TINT LUT, counts, and shared IRQ layout. Key paths include clear helpers for NMI/IRQ/TINT, RZ/Five mask/unmask helpers, TINT enable/disable, NMI/IRQ/TINT set-type functions, shared IRQ allocation/free, `rzg2l_irqc_alloc()`, `rzg2l_irqc_free()`, interrupt parsing, common probe, and syscore suspend/resume.

## Control Flow
Common probe finds the parent domain, allocates singleton driver state, maps registers, stores SoC info, parses every parent interrupt into fwspecs, deasserts reset, enables runtime PM, initializes the lock, creates a hierarchical domain, and registers syscore callbacks. Allocation translates a two-cell child spec. Hwirq 0 uses the NMI chip; TINT specs may encode GPIOINT in the high 16 bits; direct IRQs use IRQ chips. Shared IRQ-capable variants reserve one of eight shared routes and program `INTTSEL` to select IRQ or TINT mode before allocating the parent.

## State and Persistence
Runtime state includes a global singleton pointer, `used_irqs` bitmap for shared routes, TINT source values stored as chip data, and cached `NITSR`, `IITSR`, `INTTSEL`, and `TITSR` registers for syscore resume. `TSSR` is intentionally restored by pinctrl later to avoid invalid-pin spurious interrupts.

## Dependencies and Integration Points
It integrates with reset control, runtime PM, parent irqdomains, pinctrl GPIO interrupt clients, syscore PM, RZ/Five-specific parent masking, and compat strings `renesas,rzg2l-irqc`, `renesas,r9a08g046-irqc`, and `renesas,r9a07g043f-irqc`.

## Risks and Edge Cases
The singleton design assumes one controller instance. Shared IRQ allocation can return `-EBUSY` if a direct IRQ and TINT compete for the same physical route. TINT source programming temporarily disables the byte lane to avoid spurious delivery. Resume ordering with pinctrl is delicate because `TSSR` is not restored here.

## Test Signals
Validate NMI, direct IRQ, TINT, and shared-route allocation; RZ/G3L LUT mapping; RZ/Five IMSK/TMSK masking; all trigger types supported per source class; suspend/resume register restoration; and failure behavior for invalid encoded TINT hwirqs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzg2l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzt2h.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzt2h.c

## Purpose
`irq-renesas-rzt2h.c` implements the Renesas RZ/T2H ICU hierarchical interrupt controller. It routes non-safety, safety, external IRQ, and SEI inputs to a parent domain and also exports a helper for DMAC request selection.

## Important APIs, Types, and Functions
`struct rzt2h_icu_priv` holds non-safety and safety MMIO bases, parent fwspecs, and a lock. Public API `rzt2h_icu_register_dma_req()` writes DMAC request-selection fields and is exported GPL. IRQ helpers include `rzt2h_icu_irq_to_offset()`, `rzt2h_icu_irq_set_type()`, `rzt2h_icu_set_type()`, `rzt2h_icu_alloc()`, and `rzt2h_icu_parse_interrupts()`.

## Control Flow
Probe finds the parent domain, allocates private state, maps two register banks, parses parent interrupts for all local hwirqs, enables runtime PM, and creates a hierarchical domain. Allocation translates a two-cell child spec, installs `rzt2h_icu_chip`, and forwards allocation to the pre-parsed parent fwspec. Set-type only allows selectable modes for IRQ_NS, IRQ_S, and SEI; internal CPU interrupts are restricted to rising edge and delegated to the parent.

## State and Persistence
Software state is per platform device. The lock serializes trigger mode and DMAC selection register updates. Hardware register state is volatile; there is no syscore or runtime PM register cache in this driver.

## Dependencies and Integration Points
The file depends on the public Renesas RZ/T2H irqchip header, platform driver irqchip macros, reset/runtime PM, parent irqdomains, and DMAC clients that call the exported request-registration helper.

## Risks and Edge Cases
The hwirq layout is encoded by compile-time ranges; DT interrupt ordering must exactly match `RZT2H_ICU_NUM_IRQ`. Safety and SEI sources use the safety register space and a shifted offset; mistakes route writes to the wrong bank. DMAC helper trusts the supplied platform device and channel indexes.

## Test Signals
Exercise all hwirq ranges, type rejection for non-selectable internal CPU interrupts, low/falling/rising/both mode programming for external/SEI lines, parent fwspec forwarding, PM runtime activation, and DMAC request selection writes for multiple channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzt2h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzv2h.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzv2h.c

## Purpose
`irq-renesas-rzv2h.c` drives the Renesas RZ/V2H(P), RZ/V2N, and RZ/G3E ICU. It handles NMI, IRQ, GPIO TINT, CA55 software interrupts, pseudo error interrupts, error-status demuxing, DMAC request selection, SoC-specific TINT layouts, and syscore restore.

## Important APIs, Types, and Functions
`struct rzv2h_icu_priv` stores MMIO, parent fwspecs, lock, SoC hardware info, and register cache. `struct rzv2h_hw_info` describes TINT offset, field width, maximum TSEL, optional LUT, and ECC status ranges. Public `rzv2h_icu_register_dma_req()` programs DMAC request selectors. IRQ operations include EOI handlers, TINT enable/disable, NMI/IRQ/TINT set-type, software interrupt and SWPE pending injection, allocation, error and software IRQ handlers, setup helpers, and common probe.

## Control Flow
Probe maps registers, parses parent interrupts, deasserts reset, enables runtime PM, creates a hierarchical domain, records hardware info, registers syscore PM, and sets up internal CA55 software/error IRQ mappings. Allocation decodes TINT hwirq plus GPIOINT from the high 16 bits, chooses among TINT/IRQ/SWINT/SWPE/NMI chips, and allocates the parent IRQ. Set-type functions program ICU sense registers, clear stale status where appropriate, and force the parent to level-high for ICU-converted sources. Error setup clears/unmasks bus, ECC, and CA55 error registers and requests an ICU error handler.

## State and Persistence
Runtime state is singleton `rzv2h_icu_data`, per-hwirq parent fwspecs, TINT GPIOINT chip data, and a static rotating SWPE bit used for pseudo error injection. Syscore suspend caches NMI/IRQ/TINT type registers and restores them on resume; TSSR is restored by pinctrl instead.

## Dependencies and Integration Points
The driver integrates with parent irqdomains, reset/runtime PM, generic IRQ injection, Renesas public ICU header, DMAC clients, pinctrl TINT clients, syscore PM, and OF platform irqchip matching for three SoC families.

## Risks and Edge Cases
The common probe sets `info` after creating the domain, so no allocation should occur before that assignment and setup. TINT `tint` values are bounds-checked before optional LUT translation, making LUT size and `max_tssel` important. Error handlers clear broad status masks and log warnings only.

## Test Signals
Validate TINT field widths of 8 and 16 bits, RZ/G3E LUT and offset, CA55 software IRQ injection with `CONFIG_GENERIC_IRQ_INJECTION`, SWPE rotation, bus/ECC/IP error clearing, DMAC helper writes, suspend/resume type restore, and invalid encoded TINT rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzv2h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-direct.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-direct.c

## Purpose
`irq-riscv-aplic-direct.c` implements direct-delivery mode for the RISC-V APLIC interrupt controller. In this mode APLIC interrupt delivery controllers claim wired interrupts directly through per-hart IDC registers behind the RISC-V local external interrupt.

## Important APIs, Types, and Functions
`struct aplic_direct` embeds shared `aplic_priv`, a domain pointer, and a CPU mask for usable IDCs. `struct aplic_idc` stores hart index, IDC register base, and backpointer. Main callbacks include `aplic_direct_set_affinity()`, `aplic_direct_irqdomain_translate()`, `aplic_direct_irqdomain_alloc()`, `aplic_direct_handle_irq()`, `aplic_idc_set_delivery()`, CPU hotplug callbacks, parent parsing, and `aplic_direct_setup()`.

## Control Flow
Setup allocates direct state, calls `aplic_setup_priv()` for common APLIC state, enumerates parent external interrupts to map IDC indexes to Linux CPUs and hart indexes, enables IDC delivery for each usable CPU, optionally rewrites target registers if the boot CPU hart index is not zero, installs a chained handler on the RISC-V INTC external interrupt, registers CPU hotplug hooks, enables global APLIC direct mode, and creates a linear domain. Runtime handling claims pending IDs from the local IDC `CLAIMI` register until zero and dispatches mapped Linux IRQs.

## State and Persistence
Per-CPU `aplic_idcs` hold IDC register pointers and direct context. Target registers store hart index and priority. CPU hotplug toggles the parent percpu IRQ. Common APLIC suspend/resume calls `aplic_direct_restore_states()` to re-enable IDC delivery.

## Dependencies and Integration Points
It depends on `irq-riscv-aplic-main.c` common helpers, RISC-V INTC fwnode discovery, OF or ACPI hart mapping, CPU hotplug, percpu IRQs, irqdomain top-level allocation, and direct AIA CSR/register definitions.

## Risks and Edge Cases
Only parent hwirq `RV_IRQ_EXT` is accepted. If no CPU has a valid IDC, setup fails. `aplic_direct_parent_irq` is global, so multiple direct APLIC instances share one chained parent path. Affinity requires the target CPU to be in the controller's `lmask`.

## Test Signals
Validate IDC enumeration on DT and ACPI, CPU hotplug enable/disable of parent external IRQ, claim-loop dispatch, affinity target register writes, boot CPU nonzero hart index handling, and restore after PM domain/syscore resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.c

## Purpose
`irq-riscv-aplic-main.c` provides common RISC-V APLIC setup, register initialization, IRQ type programming, firmware parsing, and power-management state save/restore shared by direct and MSI delivery modes.

## Important APIs, Types, and Functions
Global list `aplics` tracks active controllers. PM helpers are `aplic_save_states()`, `aplic_restore_states()`, syscore callbacks, GENPD notifier, `aplic_pm_add()`, and `aplic_pm_remove()`. Shared IRQ helpers are `aplic_irq_mask()`, `aplic_irq_unmask()`, `aplic_irq_set_type()`, `aplic_irqdomain_translate()`, `aplic_init_hw_global()`, `aplic_setup_priv()`, and platform `aplic_probe()`.

## Control Flow
Probe maps MMIO and selects MSI mode when `msi-parent` exists in DT or IMSIC ACPI fwnode exists; otherwise it selects direct mode. Common setup reads interrupt source count and IDC count from DT or ACPI, resets APLIC source/target/domain registers, allocates saved-register arrays, registers PM hooks, and lets the selected mode build domains. Global init enables domain interrupts and optionally MSI delivery mode. Suspend/GENPD pre-off saves target and enable state; resume restores domain config, MSI address config when applicable, source config before target/enable, and replays pending interrupts for MSI mode.

## State and Persistence
State is MMIO-backed plus `struct aplic_saved_regs`: domain config, optional MSI address config, per-source sourcecfg/target, and per-32-source enable words. It persists only in RAM during PM transitions. The driver supports multiple APLIC instances via the global list.

## Dependencies and Integration Points
It integrates with OF and ACPI RISC-V interrupt descriptions, IMSIC global configuration, platform devices, generic PM domains, runtime PM, syscore PM, and the direct/MSI setup files.

## Risks and Edge Cases
Restore ordering matters because inactive sources make target and enable state read-only zero. The save loop stores enable words in sparse `srcs[i]` entries at 32-source boundaries, including the exact `nr_irqs` boundary when divisible by 32. Mode selection depends on firmware properties and IMSIC availability.

## Test Signals
Validate DT and ACPI source/IDC parsing, direct versus MSI mode selection, PM save/restore with enabled and pending interrupts, source type programming, invalid zero hwirq rejection, and warning paths when `DOMAINCFG` writes do not stick.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.h

## Purpose
`irq-riscv-aplic-main.h` is the internal contract between the RISC-V APLIC common code and its direct/MSI mode implementations.

## Important APIs, Types, and Functions
It defines `APLIC_DEFAULT_PRIORITY`, `struct aplic_msicfg`, `struct aplic_src_ctrl`, `struct aplic_saved_regs`, and `struct aplic_priv`. It declares common mask/unmask/type/translation/global-init/setup helpers, direct restore/setup helpers, and MSI setup. When `CONFIG_RISCV_APLIC_MSI` is disabled, `aplic_msi_setup()` is provided as an inline `-ENODEV` stub.

## Control Flow
The header has no executable flow, but it encodes how `aplic_probe()` hands a mapped register base to either `aplic_direct_setup()` or `aplic_msi_setup()`, while both modes use `aplic_setup_priv()` and shared irqchip callbacks.

## State and Persistence
The central state shape is `struct aplic_priv`, which carries firmware identity, interrupt counts, MMIO base, MSI address layout, saved PM registers, and optional GENPD notifier. `struct aplic_saved_regs` persists volatile hardware state across suspend or PM-domain off.

## Dependencies and Integration Points
It depends on Linux device, I/O, irqdomain, and fwnode types plus RISC-V APLIC register definitions included by implementation files. It is private to the irqchip directory.

## Risks and Edge Cases
The saved register array is indexed by hardware interrupt source IDs and also stores enable words at 32-source boundaries, so implementers must size it for `nr_irqs + 1`. `nr_idcs == 0` is used to distinguish MSI mode from direct mode in restore logic.

## Test Signals
Compile coverage across direct-only, MSI-enabled, DT, and ACPI configurations is the primary signal. Runtime validation comes from APLIC direct/MSI tests that exercise every declared helper contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-msi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-msi.c

## Purpose
`irq-riscv-aplic-msi.c` implements APLIC MSI-delivery mode, where wired interrupt sources are converted by APLIC into MSIs targeted at the RISC-V IMSIC.

## Important APIs, Types, and Functions
IRQ callbacks are `aplic_msi_irq_mask()`, `aplic_msi_irq_unmask()`, `aplic_msi_irq_eoi()`, `aplic_msi_irq_set_type()`, and `aplic_msi_write_msg()`. MSI-domain support comes from `aplic_msi_set_desc()`, `aplic_msi_translate()`, `aplic_msi_template`, and `aplic_msi_setup()`.

## Control Flow
Setup allocates common `aplic_priv`, reads IMSIC global configuration, derives APLIC MSI address field widths and base PPN, enables APLIC global MSI mode, ensures the platform device has an MSI domain, and creates an MSI device IRQ domain. When a parent MSI message is written, `aplic_msi_write_msg()` decodes the IMSIC address into group, hart, and guest indexes and writes the APLIC target register with hart, guest, and EIID data. Mask/unmask orders parent and APLIC operations to prevent unwanted delivery.

## State and Persistence
MSI mode state is in `priv->msicfg`, APLIC target registers, source configuration, and common saved registers. Level-triggered sources require EOI/set-type retrigger through `APLIC_SETIPNUM_LE` if the level is still asserted.

## Dependencies and Integration Points
The file depends on the IMSIC global config exported by `irq-riscv-imsic-state.c`, Linux MSI domain templates, OF MSI configuration, ACPI IMSIC fwnodes, and common APLIC helpers.

## Risks and Edge Cases
IMSIC address layout must fit APLIC field masks; otherwise setup fails. If the device MSI domain is not available yet, setup returns `-EPROBE_DEFER`. Zeroed MSI messages clear target registers by writing zero. Incorrect level retrigger behavior can lose level-sensitive interrupts after EOI.

## Test Signals
Validate MSI domain creation, IMSIC field-width bounds, DT `msi-parent` and ACPI domain discovery, target register composition from MSI messages, level interrupt retriggering, affinity pass-through, and zero-MSI target clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-early.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-early.c

## Purpose
`irq-riscv-imsic-early.c` performs early RISC-V IMSIC setup for interrupt delivery and IPIs before the platform MSI domain is created.

## Important APIs, Types, and Functions
Global state is `imsic_parent_irq` and boot parameter `imsic_noipi`. IPI helpers are `imsic_ipi_send()`, CPU start/stop IPI hooks, and `imsic_ipi_domain_init()`. Runtime delivery uses `imsic_handle_irq()`, `imsic_hw_states_init()`, CPU hotplug callbacks, CPU PM notifier, `imsic_early_probe()`, DT init `imsic_early_dt_init()`, and ACPI init `imsic_early_acpi_init()`.

## Control Flow
Early DT/ACPI init calls `imsic_setup_state()` to parse firmware and allocate global/per-CPU state. It then maps the RISC-V INTC external interrupt, optionally creates an IPI mux using IMSIC ID 1, installs the chained IMSIC handler, registers CPU hotplug callbacks, and registers a CPU PM notifier. The handler syncs pending local vector updates, repeatedly swaps `CSR_TOPEI` to claim IDs, processes IPI IDs via the IPI mux, and dispatches non-IPI vectors through per-CPU vector state.

## State and Persistence
This file controls local IMSIC delivery state and IPI enablement. CPU online and CPU PM exit paths re-enable IPI ID, synchronize all local IDs, and enable IMSIC local delivery. ACPI stores a global IMSIC fwnode for later MSI-domain setup.

## Dependencies and Integration Points
It depends on `irq-riscv-imsic-state.c`, RISC-V INTC root domain, CPU hotplug, CPU PM, IPI mux, PCI MSI fwnode provider registration under ACPI, and AIA CSRs.

## Risks and Edge Cases
Boot parameter `irqchip.riscv_imsic_noipi` disables IMSIC IPI provision. Even if ACPI MSI platform setup fails, IPI delivery continues. The handler assumes vector state exists for claimed IDs; out-of-range IDs are rate-limited warnings.

## Test Signals
Validate early DT and ACPI boot, IPI send/receive, `noipi` boot parameter, CPU hotplug, CPU PM resume, chained external interrupt handling, invalid local ID warnings, and coexistence with later platform MSI-domain probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-early.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-platform.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-platform.c

## Purpose
`irq-riscv-imsic-platform.c` creates the IMSIC MSI parent domain used by platform and PCI MSI consumers after early IMSIC state has been initialized.

## Important APIs, Types, and Functions
Important helpers include `imsic_cpu_page_phys()`, IRQ chip callbacks `imsic_irq_mask()`, `imsic_irq_unmask()`, `imsic_irq_retrigger()`, `imsic_irq_ack()`, MSI composition helpers, SMP affinity move helpers, `imsic_irq_domain_alloc()`, `imsic_irq_domain_free()`, debugfs show, `imsic_init_dev_msi_info()`, `imsic_msi_parent_ops`, `imsic_irqdomain_init()`, and DT/ACPI probe entry points.

## Control Flow
The base IRQ domain allocates one IMSIC vector per Linux IRQ from the global matrix, installs the IMSIC IRQ chip with `handle_edge_irq`, marks it noprobe, and sets affinity to online CPUs. The chip composes MSI messages as a per-CPU IMSIC page address plus vector ID. Affinity changes allocate a new vector, optionally program a temporary vector for non-atomic MSI updates, write the final MSI message, update descriptor chip data and effective affinity, and move pending state between vectors. Platform probe verifies the early fwnode matches and calls `imsic_irqdomain_init()`.

## State and Persistence
The domain stores per-IRQ `struct imsic_vector` chip data. Vector enable/move state is maintained by `irq-riscv-imsic-state.c`. The base domain is singleton `imsic->base_domain` and cannot be created twice.

## Dependencies and Integration Points
It depends on MSI lib parent-domain helpers, IMSIC state exports, PCI/platform MSI bus tokens, irq matrix allocation, SMP affinity infrastructure, generic IRQ debugfs, and ACPI early probe ordering.

## Risks and Edge Cases
Multi-MSI allocation is explicitly unsupported. PCI MSI/MSI-X domains get `IRQCHIP_MOVE_DEFERRED` for non-atomic device message updates. A missing early IMSIC probe or fwnode mismatch fails domain creation. Freeing assumes the chip data vector is valid.

## Test Signals
Test platform and PCI MSI allocation, MSI message address/data composition, retrigger via MMIO write, affinity migration with deferred and immediate moves, debugfs vector display, ACPI early domain creation before PCI scan, and multi-MSI rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.c

## Purpose
`irq-riscv-imsic-state.c` owns the global and per-CPU state for the RISC-V IMSIC, including firmware parsing, MMIO page mapping, vector allocation, local enable/pending synchronization, vector migration, and IRQ matrix management.

## Important APIs, Types, and Functions
It exports global `imsic`, `imsic_get_global_config()`, low-level EIx update, local synchronization/delivery, vector mask/unmask/move/free/allocation, debug helpers, CPU online/offline state hooks, `imsic_setup_state()`, and matrix initialization. Firmware parsing is split among DT/ACPI global population, parent hartid lookup, MMIO resource lookup, and `imsic_parse_fwnode()`.

## Control Flow
Setup rejects multiple IMSIC instances and platforms without AIA, allocates global/per-CPU local config, parses firmware for interrupt IDs and MSI address layout, maps all MMIO register sets, allocates per-CPU local private vectors/dirty bitmaps, associates each parent interrupt with a CPU MSI page, computes minimum guest files, initializes the vector matrix, and frees temporary MMIO arrays. Mask/unmask mark vector IDs dirty and synchronize locally or by pinned timer on target CPU. Move support disables the old vector, enables the new vector, checks pending bits on old and temporary IDs, retriggers on the new CPU by MMIO write, and frees old vectors after synchronization completes.

## State and Persistence
State includes `imsic->global`, per-CPU `imsic_local_priv`, per-vector `enable` and move pointers, dirty bitmaps, timers, and the global IRQ matrix. It is all in RAM plus per-hart IMSIC CSRs/MMIO pages; no filesystem persistence exists. CPU offline deletes synchronization timers and marks matrix CPUs offline.

## Dependencies and Integration Points
The file depends on RISC-V AIA ISA detection, OF/ACPI interrupt and MMIO descriptions, irq matrix allocator, per-CPU storage, timers, SMP, KVM-facing IMSIC global config, and CSR access through `ISELECT`/`IREG`.

## Risks and Edge Cases
The loop that finds MMIO location uses firmware-derived sizing and must handle holes by aligned subtraction. Vector move logic is subtle for non-atomic MSI writes and pending interrupts can be lost if dirty synchronization does not complete. ID 0 and optional IPI ID are reserved in the matrix.

## Test Signals
Validate DT and ACPI parsing, invalid address-layout rejection, multiple MMIO regions, per-CPU MSI page calculation, guest-file minimum calculation, vector allocation exhaustion, mask/unmask synchronization, CPU hotplug, pending interrupt preservation during affinity moves, and debugfs summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.h

## Purpose
`irq-riscv-imsic-state.h` defines the internal IMSIC state model and function contract shared by the early and platform IMSIC drivers.

## Important APIs, Types, and Functions
It defines `IMSIC_IPI_ID`, `IMSIC_NR_IPI`, `struct imsic_vector`, `struct imsic_local_priv`, and `struct imsic_priv`. It declares global `imsic_noipi` and `imsic`, EIx update helpers, local sync/delivery, vector mask/unmask/move/allocation/free/debug APIs, CPU online/offline hooks, `imsic_setup_state()`, and `imsic_irqdomain_init()`.

## Control Flow
The header has no runtime flow, but it separates the early handler/IPI path from MSI-domain allocation. Early code initializes state and local delivery; platform code allocates vectors and composes MSI messages through this interface.

## State and Persistence
`struct imsic_vector` is the unit of MSI identity allocation and migration. `struct imsic_local_priv` keeps local lock, dirty bitmap, optional synchronization timer, and vector table. `struct imsic_priv` holds firmware identity, global hardware config, per-CPU state, matrix allocator, and base domain pointer.

## Dependencies and Integration Points
The contract depends on RISC-V IMSIC public definitions, irqdomain, fwnode, timers, seq_file debug output when enabled, and Linux per-CPU/matrix infrastructure in the implementation.

## Risks and Edge Cases
Callers must obey locking expectations around vector enable and move fields. `imsic_vector_get_move()` returns `move_prev`, so users need to distinguish old and new vector roles. IPI ID reservation depends on `imsic_noipi`.

## Test Signals
Compile coverage with SMP, non-SMP, debugfs, ACPI, and DT configurations is key. Runtime validation comes through IMSIC early/platform tests for vector lifecycle, CPU hotplug, IPI reservation, and affinity migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-intc.c

## Purpose
`irq-riscv-intc.c` implements the per-hart RISC-V local interrupt controller. It is the root domain for local interrupt causes and the parent for PLIC, CLINT/SBI IPI, APLIC direct, IMSIC, and other local-interrupt consumers.

## Important APIs, Types, and Functions
Root handlers are `riscv_intc_irq()` for classic cause-based delivery and `riscv_intc_aia_irq()` for AIA TOPI delivery. Chip callbacks are standard CSR mask/unmask, Andes-specific `SLIE` mask/unmask, and dummy EOI. Domain operations are map, alloc, xlate, and free. Common initialization is `riscv_intc_init_common()`. DT init is `riscv_intc_init()`, with ACPI RINTC parsing helpers under `CONFIG_ACPI`.

## Control Flow
DT contains one INTC node per hart; only the boot CPU's node creates the irqdomain, while other nodes are marked initialized for supplier dependency purposes. Common init creates a tree domain, selects AIA or classic root handler based on ISA extension, registers the global RISC-V INTC fwnode callback, and logs mapped interrupt counts. Allocation maps one-cell hwirqs only if they are within standard or configured custom ranges, marks IRQs percpu-devid, and uses `handle_percpu_devid_irq`.

## State and Persistence
Global state is the root domain, standard IRQ count, custom interrupt base/count, and ACPI RINTC table cache. Mask state lives in local hart CSRs (`IE`, `IEH`, or Andes `SLIE`) and is not persistent across CPU reset.

## Dependencies and Integration Points
It depends on RISC-V CSR access, ISA extension detection, SMP hart ID mapping, OF/ACPI MADT RINTC data, irqdomain tree domains, and child irqchip discovery through `riscv_set_intc_hwnode_fn()`.

## Risks and Edge Cases
CSR mask/unmask can only operate on the local hart. AIA raises the local IRQ count to 64 and uses `TOPI` claim loops. Andes custom local interrupts use hwirq causes starting at 256. ACPI helpers cache per-RINTC data for PLIC/APLIC/IMSIC lookup.

## Test Signals
Validate boot CPU domain creation, non-boot node supplier marking, classic and AIA root handlers, local timer/software/external interrupts, Andes custom SLI interrupts, ACPI RINTC parsing helpers, and rejection of out-of-range hwirqs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-rpmi-sysmsi.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-rpmi-sysmsi.c

## Purpose
`irq-riscv-rpmi-sysmsi.c` implements an RPMI System MSI controller for RISC-V. It exposes firmware-managed system MSI indexes as a wired-to-MSI domain backed by mailbox calls to RPMI firmware and a parent IMSIC MSI domain.

## Important APIs, Types, and Functions
Message payload structs model GET_ATTRIBUTES, SET_MSI_STATE, and SET_MSI_TARGET transactions. `struct rpmi_sysmsi_priv` stores the device, mailbox client/channel, number of MSIs, and ACPI GSI base. Firmware helpers are `rpmi_sysmsi_get_num_msi()`, `rpmi_sysmsi_set_msi_state()`, and `rpmi_sysmsi_set_msi_target()`. IRQ callbacks mask/unmask through firmware and parent chip, write MSI target messages, translate firmware specs, and create an MSI device domain through `rpmi_sysmsi_template`.

## Control Flow
Probe allocates state, configures a mailbox client, requests a channel, queries firmware for MSI count, optionally reads ACPI GSI mapping and updates the GSI range, ensures the device has a platform MSI parent domain through OF or ACPI IMSIC lookup, and creates a device MSI domain. Mask disables the system MSI in firmware then masks the parent; unmask unmasks parent first then enables firmware state. `irq_write_msi_msg` sends target address/data to firmware.

## State and Persistence
State lives in RPMI firmware and the mailbox-backed system MSI table. The Linux driver keeps only the count and GSI base. Zeroed MSI messages are ignored rather than clearing firmware target state.

## Dependencies and Integration Points
It depends on RPMI mailbox message APIs, IMSIC MSI domains, OF `riscv,rpmi-system-msi`, ACPI ID `RSCV0006`, RISC-V ACPI GSI helpers, and Linux MSI domain templates.

## Risks and Edge Cases
Mailbox failures during mask/unmask/write only warn after probe, so firmware desynchronization can persist. No remove path frees the mailbox channel after successful builtin probe. The translation subtracts `gsi_base`; invalid firmware specs below that base can underflow into large hwirqs.

## Test Signals
Validate firmware attribute count, no-MSI rejection, mailbox error conversion, OF and ACPI MSI parent discovery, ACPI GSI range update, mask/unmask ordering, MSI target programming, and behavior when parent MSI domain probes late.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-rpmi-sysmsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sa11x0.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sa11x0.c

## Purpose
`irq-sa11x0.c` implements generic IRQ handling for SA11x0 systems without device tree. It maps the 32 internal interrupt controller sources, handles root dispatch, wake control, and syscore save/restore.

## Important APIs, Types, and Functions
Global state is `iobase`, `sa1100_normal_irqdomain`, and `sa1100irq_state`. Chip callbacks are `sa1100_mask_irq()`, `sa1100_unmask_irq()`, and `sa1100_set_wake()`. Domain mapping is `sa1100_normal_irqdomain_map()`. PM callbacks are `sa1100irq_suspend()` and `sa1100irq_resume()`. Root dispatch is `sa1100_handle_irq()`, and legacy init is `sa11x0_init_irq_nodt()`.

## Control Flow
`sa11x0_init_irq_nodt()` maps the interrupt controller, disables all IRQs, configures all sources as IRQ rather than FIQ, sets `ICCR` for wait-on-irq behavior, creates a simple 32-entry domain using the supplied legacy IRQ base, and installs the root handler. The handler repeatedly reads pending and mask registers, dispatches the first set enabled interrupt, and stops when no enabled pending bits remain.

## State and Persistence
Suspend caches `ICMR`, `ICLR`, and `ICCR`, marks state saved, and disables GPIO-based interrupts by preserving only upper internal-mask bits. Resume restores cached control, level, and mask registers. Wake configuration is delegated to `sa11x0_sc_set_wake()`.

## Dependencies and Integration Points
The file depends on legacy SA1100 platform init, `soc/sa1100/pwer.h`, syscore ops, irqdomain one/two-cell translation, architecture root IRQ handler setup, and the public `irq-sa11x0.h` init declaration.

## Risks and Edge Cases
It is nodt-only and assumes a single controller. `irq_ack` masks the source because internal IRQs generally need no explicit ACK; GPIO IRQs are handled elsewhere. Suspend masking of GPIO-based interrupts uses a fixed `0xfffff000` boundary, so source numbering must match SA1100 hardware.

## Test Signals
Validate legacy boot with correct IRQ base, root dispatch ordering, mask/unmask register updates, wake enable propagation, suspend/resume register restore, and no FIQ routing after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-sa11x0.c -->
