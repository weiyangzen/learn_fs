# subset-b-004005 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htpic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htpic.c

### Purpose
`irq-loongson-htpic.c` initializes the Loongson HyperTransport PIC bridge used to feed legacy i8259-style interrupts into the Linux IRQ subsystem. It owns one global HTPIC instance, maps the controller registers, builds the i8259 IRQ domain, and cascades up to four parent interrupt lines into that domain.

### Important APIs, Types, And Functions
The key state is `struct loongson_htpic`, carrying the MMIO base and i8259-backed `irq_domain`. `htpic_of_init()` is the OF entry declared by `IRQCHIP_DECLARE()`. `htpic_irq_dispatch()` is the chained parent handler, and `htpic_reg_init()` resets cause/enable registers. `htpic_syscore_ops` restores register state on resume by re-running initialization.

### Control Flow
During boot, the OF initializer rejects duplicate controllers, maps MMIO, calls `__init_i8259_irqs(node)`, parses parent IRQs with `irq_of_parse_and_map()`, initializes all eight HT vector enable/cause slots, enables the low 16 vectors, and installs `htpic_irq_dispatch()` on each parent. Dispatch reads the first cause register, writes the same value back to acknowledge all currently pending bits, reports spurious entries when no valid bit exists, and calls `generic_handle_domain_irq()` for bits 0-15.

### State, Persistence, And Dependencies
Persistent state is the singleton `htpic`, the i8259 domain, parent chained handlers, and syscore registration. It depends on OF address/IRQ parsing, i8259 initialization, chained IRQ helpers, raw MMIO access, and syscore resume ordering.

### Integration Points
This driver is the legacy PIC endpoint in Loongson HT systems. It bridges firmware-described HT parent interrupts to the i8259 IRQ domain consumed by legacy ISA-style devices.

### Risks
Only one HTPIC is supported. Dispatch intentionally acknowledges all pending bits before walking them, which avoids flood behavior but relies on hardware latch semantics. Bits above 15 are treated as spurious even though the register is 32-bit. Failure paths remove the IRQ domain and unmap MMIO, but successful init has no remove path.

### Test Signals
Boot with valid and missing parent IRQs, verify legacy IRQ0-15 delivery, trigger simultaneous pending bits, suspend/resume with enabled devices, and check spurious accounting when parent IRQ fires with an empty cause register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htpic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htvec.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htvec.c

### Purpose
`irq-loongson-htvec.c` implements the Loongson HyperTransport vector interrupt controller. It exposes a linear domain over 32 vectors per parent line and cascades parent interrupts from firmware into edge-style Linux IRQs. It also acts as the ACPI cascade point for Loongson PCH PIC and MSI controllers.

### Important APIs, Types, And Functions
`struct htvec` stores parent count, MMIO base, IRQ domain, lock, and saved enable registers. `htvec_init()` is the shared OF/ACPI initializer. `htvec_domain_alloc()` maps one-cell firmware specs to `htvec_irq_chip`. `htvec_irq_dispatch()` fans out pending vector bits. `htvec_acpi_init()` allocates an ACPI fwnode and then parses BIO PIC and MSI PIC MADT subtables.

### Control Flow
OF setup reads the MMIO resource and up to eight parent IRQs, then calls `htvec_init()`. ACPI setup maps cascade entries through the parent domain. Initialization creates a linear domain sized at `32 * num_parents`, resets all cause/enable registers, chains each parent IRQ, stores the global private pointer, and registers syscore suspend/resume hooks. Dispatch scans every parent cause register and handles `bit + 32 * parent_index`; ack writes the bit to the cause register and mask/unmask update the corresponding enable register under `htvec_lock`.

### State, Persistence, And Dependencies
State includes `htvec_priv`, enable-register save slots, chained handlers, and the domain fwnode. Dependencies include irqdomain hierarchy/translation helpers, OF and ACPI MADT parsing, MMIO, syscore PM, and the Loongson PCH helper declarations in `irq-loongson.h`.

### Integration Points
The domain is the parent for PCH PIC and PCH MSI vector allocations on Loongson platforms. ACPI cascade parsing creates those downstream domains after HTVEC exists.

### Risks
The global singleton is assumed by ACPI parsers. OF setup does not explicitly reject zero parents before `htvec_init()`, so malformed firmware can create an empty domain. Type handling is fixed to `handle_edge_irq`; downstream code must configure devices accordingly. Multi-parent dispatch scans all cause registers for every chained entry.

### Test Signals
Validate OF and ACPI boot, parent IRQ fan-out across all eight vector groups, mask/unmask and ack register writes, suspend/resume preservation of enables, and ACPI creation of PCH PIC/MSI child domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htvec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-liointc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-liointc.c

### Purpose
`irq-loongson-liointc.c` implements the Loongson local I/O interrupt controller with 32 child interrupts, four parent lines, and per-core status registers. It supports OF revisions 1.0/1.0a/2.0 and ACPI MADT initialization, then cascades to HT vector controllers when present.

### Important APIs, Types, And Functions
`struct liointc_priv` holds the generic chip, parent handler data, core ISR addresses, route-map cache, saved polarity/edge registers, and errata flag. `liointc_init()` is shared initialization. `liointc_chained_handle_irq()` handles parent IRQs. `liointc_set_type()` programs edge/polarity bits. `liointc_suspend()` and `liointc_resume()` preserve programmable state. `liointc_acpi_init()` is the ACPI entry.

### Control Flow
Firmware supplies parent IRQs and `loongson,parent_int_map` masks. Initialization maps registers, optionally remaps per-core ISR regions for revision 2, creates a linear domain using generic-chip ops or ACPI xlate ops, allocates one generic chip, disables all interrupts, defaults to level mode, builds route bytes from parent maps plus boot CPU routing, writes the route table, configures generic-chip enable/disable/type callbacks, and chains each parent IRQ. Dispatch reads the current core's status register and handles each pending child bit.

### State, Persistence, And Dependencies
Persistent state is the linear domain, generic-chip mask cache, route table cache, saved edge/polarity values, parent maps, and global `liointc_handle`. It depends on Loongson CPU/core ID helpers, boot CPU ID configuration, generic IRQ chips, OF or ACPI firmware data, and HTVEC ACPI cascade creation.

### Integration Points
The domain sits below CPU/parent interrupt controllers and above HTVEC/PCH domains on ACPI systems. Child IRQ consumers use normal firmware IRQ specifiers, while ACPI specs are translated from GSI space using `GSI_MIN_CPU_IRQ`.

### Risks
Parent maps are global static arrays and must be fully populated before init. Revision-2 per-core ISR remapping can leave mixed base-derived and separately mapped ISR pointers. The LPC errata path fabricates IRQ10 pending when hardware reports none, so false positives are possible but intentional. Resume restores route and mask state under the generic-chip lock.

### Test Signals
Exercise all supported compatibles, parent map parsing, IRQ type changes, per-core delivery, LPC errata behavior, ACPI HT_PIC cascade parsing, suspend/resume register restoration, and invalid firmware maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-liointc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-lpc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-lpc.c

### Purpose
`irq-loongson-pch-lpc.c` implements the Loongson LS7A LPC interrupt controller. It provides a legacy 1:1 domain for 16 LPC/ISA-style IRQs and cascades a single parent IRQ from the PCH PIC.

### Important APIs, Types, And Functions
`struct pch_lpc` carries MMIO base, domain, lock, and saved control/enable/polarity registers. `pch_lpc_init()` is the shared OF/ACPI initializer. `lpc_irq_dispatch()` demultiplexes enabled status bits. `lpc_irq_ack()`, `lpc_irq_mask()`, `lpc_irq_unmask()`, and `lpc_irq_set_type()` implement `pch_lpc_irq_chip`. `pch_lpc_acpi_init()` maps the parent cascade using the parent domain.

### Control Flow
Initialization maps MMIO, rejects a controller that appears disabled by returning all ones in enable/status, creates a legacy domain for IRQs 0-15, resets control/enables/status, chains the parent IRQ, publishes `pch_lpc_handle`, and registers syscore PM. Dispatch intersects `LPC_INT_ENA` and `LPC_INT_STS`, handles each set bit in the LPC domain, and reports spurious parent interrupts when no enabled status exists.

### State, Persistence, And Dependencies
State is the singleton `pch_lpc_priv`, the fwnode handle, saved registers for resume, and the chained parent mapping. It depends on Loongson PCH PIC as parent, irqdomain legacy mapping, OF/ACPI firmware, and syscore PM.

### Integration Points
This is the legacy LPC leaf beneath PCH PIC. ACPI creation is triggered by `irq-loongson-pch-pic.c` after the first PCH PIC domain is created.

### Risks
The domain is fixed to 16 entries while reset clears 18 status bits, reflecting hardware behavior but worth regression testing. `lpc_irq_set_type()` ignores non-level requests by returning success without changing the handler. Singleton state prevents multiple LPC controllers.

### Test Signals
Check IRQ0-15 legacy mappings, ACPI and OF parent cascade mapping, level-high/level-low polarity, disabled-controller detection, spurious parent IRQs, and suspend/resume preservation of control, enable, and polarity registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-msi.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-msi.c

### Purpose
`irq-loongson-pch-msi.c` provides the Loongson PCH MSI parent domain used by PCI MSI/MSI-X devices. It allocates MSI vector numbers from a bitmap, composes doorbell messages, and forwards masking/ack/affinity operations to the parent interrupt domain.

### Important APIs, Types, And Functions
`struct pch_msi_data` stores the MSI doorbell address, first vector, vector count, bitmap, and lock. `pch_msi_init()` and `pch_msi_init_domains()` create the MSI parent domain. `pch_msi_middle_domain_alloc()` allocates hardware vectors and parent IRQs. `pch_msi_compose_msi_msg()` writes MSI address/data. `get_pch_msi_handle()`, `pch_msi_acpi_init()`, and `pch_msi_acpi_init_avec()` support ACPI lookup and AVEC integration.

### Control Flow
OF setup finds the parent domain, reads the doorbell resource and `loongson,msi-*` vector properties, then creates a parent MSI irqdomain. Allocation reserves a power-of-two bitmap region for the requested MSI count, allocates corresponding parent interrupts, and installs `middle_irq_chip` for each virq. Freeing tears down parent IRQs and releases the bitmap region. ACPI either creates a new fwnode-backed MSI domain or upgrades an AVEC parent domain into an MSI parent.

### State, Persistence, And Dependencies
Persistent state includes per-controller bitmap allocation, doorbell address, global `pch_msi_handle[]`, and the MSI parent ops. It depends on generic MSI infrastructure, `irq-msi-lib.c`, PCI MSI flags, OF PCI metadata, Loongson ACPI tables, and parent vector domains such as HTVEC or AVEC.

### Integration Points
PCI host bridge code can retrieve an MSI fwnode by PCI segment. Downstream PCI MSI device domains select this parent via `msi_lib_irq_domain_select()`.

### Risks
Bitmap allocation uses `get_count_order(num_req)`, so multi-MSI allocations consume aligned power-of-two regions. `nr_pics` and handle arrays assume firmware does not exceed `MAX_IO_PICS`. ACPI fwnode allocation failure is checked in normal init but not explicitly before calling `pch_msi_init()` in every path.

### Test Signals
Exercise single and multi MSI allocation/free, MSI-X, vector exhaustion, ACPI segment lookup, AVEC parent upgrade, MSI message contents, and parent affinity propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-pic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-pic.c

### Purpose
`irq-loongson-pch-pic.c` implements the Loongson PCH PIC, a hierarchical interrupt controller that maps PCH GSIs through HT vector IDs. It supports multiple I/O PICs and provides ACPI helpers to locate a PIC by GSI range.

### Important APIs, Types, And Functions
`struct pch_pic` stores MMIO base, child domain, vector base/count, GSI base, lock, saved mask/polarity/edge registers, and a software hwirq-to-hardware-bit table. `pch_pic_init()` creates the hierarchy. `pch_pic_domain_translate()` assigns table slots. `pch_pic_alloc()` programs `PCH_INT_HTVEC()` and allocates parent vectors. `find_pch_pic()` and `pch_pic_acpi_init()` are ACPI integration points.

### Control Flow
Initialization maps registers, clears the software table to undefined, derives vector count, creates a hierarchical domain under the parent, resets route/vector/mask/clear/HTMSI state, records the domain handle, and registers syscore hooks for the first PIC. Translation converts OF hwirqs or ACPI GSIs into table indices, assigning a new table slot when needed. Allocation writes the HT vector number for the hardware bit, allocates the parent hwirq, and installs `pch_pic_irq_chip`. Mask, unmask, ack, and type operations update mask/clear/edge/polarity registers and propagate parent operations.

### State, Persistence, And Dependencies
State persists in global `pch_pic_priv[]`, `pch_pic_handle[]`, `nr_pics`, per-PIC route tables, and saved PM registers. It depends on parent HTVEC/AVEC domains, Loongson ACPI MADT BIO/LPC PIC structures, irqdomain hierarchy, and syscore PM.

### Integration Points
This is the parent for Loongson LPC PIC on ACPI systems and for normal PCH device interrupts. MSI is separate but shares parent vector infrastructure.

### Risks
The software table decouples firmware hwirq/GSI from hardware bit and must remain stable after allocation. `pch_pic_reset()` writes routes for all 64 table indices, including undefined entries at early boot. `nr_pics` lacks explicit bound checks before storing. Suspend/resume iterates all registered PICs and assumes their pointers are valid.

### Test Signals
Validate GSI-to-PIC lookup, repeated translation of the same GSI, table exhaustion, type changes and handler switching, parent allocation failure cleanup, ACPI LPC cascade creation, and resume restoration of mask/edge/polarity registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-pch-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson.h -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson.h

### Purpose
`irq-loongson.h` is the local coordination header for Loongson irqchip drivers. It declares cross-driver ACPI initialization hooks and lookup helpers used to build the Loongson interrupt hierarchy from MADT subtables.

### Important APIs, Types, And Functions
The header declares `find_pch_pic()`, `liointc_acpi_init()`, `eiointc_acpi_init()`, `avecintc_acpi_init()`, `htvec_acpi_init()`, `pch_lpc_acpi_init()`, `pch_pic_acpi_init()`, `pch_msi_acpi_init()`, and `pch_msi_acpi_init_avec()`. These functions pass `struct irq_domain *` parent domains and Loongson ACPI MADT structure pointers between independent driver files.

### Control Flow
There is no executable control flow in the header. It enables staged initialization: CPU/local controllers create parent domains, parse ACPI subtables, and call the next-level controller's init function with the new parent domain and firmware data.

### State, Persistence, And Dependencies
The header owns no state. It depends on Linux IRQ domain declarations and architecture ACPI MADT type definitions being visible to including C files.

### Integration Points
It is included by Loongson LIOINTC, HTVEC, PCH PIC, PCH LPC, PCH MSI, and related controllers so they can form a firmware-described cascade without exposing symbols through a broader public header.

### Risks
Because it is a private header, signature drift across driver files would be caught at compile time. The real risk is initialization-order coupling: callers assume global domains such as LIOINTC or HTVEC have already been created.

### Test Signals
Build coverage with `CONFIG_ACPI`, `CONFIG_OF`, AVEC/EIOINTC combinations, and Loongson platforms using PCH PIC, PCH LPC, and PCH MSI ensures all declarations match their definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lpc32xx.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-lpc32xx.c

### Purpose
`irq-lpc32xx.c` supports the NXP LPC32xx main interrupt controller and secondary interrupt controllers. The MIC installs the CPU-level IRQ handler; SIC instances cascade from parent IRQs into separate linear domains.

### Important APIs, Types, And Functions
`struct lpc32xx_irq_chip` stores MMIO base, physical address, and domain. `lpc32xx_of_ic_init()` initializes MIC or SIC nodes. `lpc32xx_handle_irq()` is the top-level exception handler. `lpc32xx_sic_handler()` is the chained handler for SICs. `lpc32xx_irq_set_type()` programs polarity and edge/level registers and switches the Linux handler.

### Control Flow
The OF initializer maps registers, creates a 32-entry linear domain, and either records the MIC and calls `set_handle_irq()` or chains every parsed parent IRQ for a SIC. It then masks all interrupts and defaults polarity/type registers to low-level behavior. Runtime dispatch reads `STAT`, loops set bits, and routes them through the correct domain. Mask/unmask update the `MASK` register, and ack writes the hwirq bit to `RAW`.

### State, Persistence, And Dependencies
Persistent state is per-controller MMIO/domain state plus the global MIC pointer. It depends on OF resources, chained IRQ helpers, ARM exception handling, irqdomains, and seq-file chip printing.

### Integration Points
The driver is the interrupt root for LPC32xx when handling MIC interrupts and a cascaded controller for SIC nodes. Device-tree child interrupt specifiers use two-cell irqdomain translation.

### Risks
Register read-modify-write operations are not explicitly locked; callers rely on IRQ core serialization for descriptor operations. SIC handlers do not report empty status as spurious. The MIC global must be initialized before top-level dispatch can be used.

### Test Signals
Boot with MIC and multiple SIC nodes, verify edge and level polarity changes, IRQ ack/mask/unmask behavior, nested SIC delivery, `/proc/interrupts` chip names, and malformed DT resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lpc32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-extirq.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-extirq.c

### Purpose
`irq-ls-extirq.c` implements the NXP Layerscape external IRQ polarity adapter. It creates a small hierarchical domain that maps board external IRQ lines onto a parent interrupt controller while programming SCFG INTPCR polarity bits.

### Important APIs, Types, And Functions
`struct ls_extirq_data` stores the INTPCR MMIO pointer, endian mode, SoC quirk flag, number of IRQs, and pre-parsed parent `irq_fwspec` map. `ls_extirq_parse_map()` reads `interrupt-map`. `ls_extirq_set_type()` converts low/falling semantics into parent high/rising types while programming inversion bits. `ls_extirq_domain_alloc()` installs `ls_extirq_chip` and allocates the parent IRQ.

### Control Flow
Probe locates the parent domain, maps the SCFG register, parses each external hwirq mapping from `interrupt-map`, determines endian and SoC bit-order quirks, and creates a hierarchical domain. Allocation validates a two-cell child spec, installs chip data, and allocates the corresponding parent fwspec. Type changes compute the polarity bit position, update INTPCR under a raw spinlock, and call the parent with the converted high/rising type.

### State, Persistence, And Dependencies
State persists as devm-managed `ls_extirq_data`, the hierarchy domain, and cached parent fwspecs. Dependencies include OF interrupt-map parsing, endian-aware MMIO access, GIC binding cells, and parent irqchip type support.

### Integration Points
It sits between board external pins and the ARM GIC or another parent controller. Device-tree external IRQ users address this domain, while the domain forwards to the parent mapping captured from `interrupt-map`.

### Risks
The parser assumes compact map entries and has a hard maximum of 12 lines. Low/falling child interrupts are implemented by hardware inversion plus parent high/rising settings; mismatched firmware polarity causes inverted behavior. `of_find_node_by_phandle()` references are stored by fwnode pointer.

### Test Signals
Validate all compatible strings, big-endian and little-endian register access, LS1021A/LS1043A reversed bit numbering, each supported trigger type, invalid map entries, and parent-domain probe deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-extirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-scfg-msi.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-scfg-msi.c

### Purpose
`irq-ls-scfg-msi.c` provides Freescale/NXP Layerscape SCFG MSI/MSI-X support. It creates an MSI parent domain backed by SCFG MSI interrupt registers and chains each MSIR parent interrupt to decode pending MSI bits.

### Important APIs, Types, And Functions
`struct ls_scfg_msi` stores registers, MSIIR address, SoC-specific config, MSIR descriptors, hwirq bitmap, and the MSI parent domain. `struct ls_scfg_msir` records each shared MSI register's parent GIC IRQ and bit range. `ls_scfg_msi_domain_irq_alloc()` allocates MSI hwirqs. `ls_scfg_msi_irq_handler()` decodes MSIR status. `ls_scfg_msi_compose_msg()` writes MSI address/data with optional CPU-affinity encoding.

### Control Flow
Probe selects SoC config, maps registers, reserves all possible hwirqs, counts parent IRQs, optionally limits MSIRs to CPU count for affinity mode, sets up chained handlers for each MSIR, releases bitmap bits covered by available MSIRs, creates an MSI parent domain, and stores drvdata. Allocation finds a free hwirq, prepares IOMMU MSI translation, and installs the parent chip. The chained handler reads an MSIR register big-endian, iterates set bits in its configured range, reconstructs hwirqs from bit position and SRS, and handles them in the MSI domain.

### State, Persistence, And Dependencies
Persistent state includes the used bitmap, chained parent handlers, SoC config table, global `msi_affinity_flag` from the `lsmsi=` early parameter, and the MSI domain. It depends on platform resources, OF IRQ counts, IOMMU MSI preparation, generic MSI parent ops, and `irq-msi-lib.c`.

### Integration Points
PCI MSI/MSI-X domains select this parent through the MSI bus token. It forwards device interrupts to the Linux MSI layer and parent GIC IRQs through chained handlers.

### Risks
`ls_scfg_msi_domain_irq_alloc()` leaks the allocated bitmap bit if `iommu_dma_prepare_msi()` fails. Affinity mode assumes MSIR index-to-CPU binding and disables itself if too few MSIRs exist. Status decoding uses big-endian reads regardless of CPU endianness as required by hardware.

### Test Signals
Exercise all compatibles including LS1043 v1.1 bit layout, `lsmsi=no-affinity`, MSI-X allocation/free, IOMMU MSI preparation failure, CPU affinity selection, chained MSIR dispatch, remove teardown, and vector exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls-scfg-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls1x.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls1x.c

### Purpose
`irq-ls1x.c` implements the Loongson-1 interrupt controller. It provides a 32-interrupt linear generic-chip domain and cascades one parent IRQ into that domain.

### Important APIs, Types, And Functions
`struct ls1x_intc_priv` stores the domain and MMIO base. `ls1x_intc_of_init()` sets up the controller. `ls1x_chained_handle_irq()` demultiplexes status and enable bits. `ls_intc_set_type()` programs edge and polarity registers, then asks the generic IRQ core to switch to the alternate edge or level chip type.

### Control Flow
Initialization maps the controller, parses a parent IRQ, creates a 32-entry linear domain using generic-chip ops, allocates two generic chip types, masks all IRQs, acknowledges pending bits, defaults polarity high, configures level and edge chip variants, and chains the parent IRQ. Dispatch reads `STATUS & EN`, handles each pending bit through the domain, and reports spurious interrupts when empty.

### State, Persistence, And Dependencies
State is the allocated private structure, generic-chip domain, MMIO registers, and chained parent handler. It depends on OF resources, generic IRQ chip helpers, chained IRQ handling, and Loongson-1 register semantics.

### Integration Points
Child devices use the LS1X interrupt domain. The controller sits below a CPU interrupt line or SoC parent described by the first interrupt in device tree.

### Risks
`ls_intc_set_bit()` performs unlocked read-modify-write sequences. Initial generic-chip allocation marks IRQs no-request, no-probe, and no-auto-enable, which is expected for an interrupt controller but can confuse tests that expect automatic enables. Unsupported types return `-EINVAL`.

### Test Signals
Validate parent cascade, all four trigger types, alternate chip selection, mask/ack/unmask register effects, spurious parent interrupts, and malformed DT with missing parent IRQ or MMIO resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ls1x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-madera.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-madera.c

### Purpose
`irq-madera.c` exposes Cirrus Logic Madera codec interrupt status bits as Linux IRQs through the regmap IRQ framework. It is an MFD child driver for Madera codecs rather than a memory-mapped SoC interrupt controller.

### Important APIs, Types, And Functions
`madera_irqs[]` maps `MADERA_IRQ_*` IDs to status register offsets and masks. `madera_irq_chip` describes the regmap IRQ chip with status, mask, ack bases, runtime PM, and 32 status registers. `madera_irq_probe()` determines host IRQ polarity, programs codec polarity when needed, and calls `regmap_add_irq_chip()`. PM callbacks temporarily disable/re-enable the host IRQ across suspend phases.

### Control Flow
Probe gets the parent `struct madera`, determines IRQ flags from platform data or the existing host IRQ descriptor, rejects edge-triggered host IRQs, optionally switches codec IRQ polarity for active-high hosts, registers the regmap IRQ chip with `IRQF_ONESHOT`, and stores the IRQ device pointer for sibling MFD users. Remove clears the pointer and unregisters the regmap IRQ chip. Sleep PM disables the host IRQ before runtime PM becomes unavailable, re-enables it during noirq for wake events, disables it again on resume_noirq, and finally re-enables normal handling.

### State, Persistence, And Dependencies
Persistent state lives in the parent MFD `struct madera`: regmap, host IRQ, IRQ data, platform IRQ flags, and `irq_dev`. The driver depends on regmap IRQ support, runtime PM, Madera register definitions, and parent MFD probe ordering.

### Integration Points
Sibling codec components consume IRQs from the regmap domain created here. The parent MFD supplies the physical IRQ and register map.

### Risks
Host IRQs must be level-triggered because the codec status/mask model is serviced through regmap. Suspend ordering is delicate: interrupts are enabled in noirq only for wake-capable handling. Polarity defaults to active-low if firmware/platform data is silent.

### Test Signals
Probe with active-low and active-high host IRQs, reject edge-triggered hosts, validate regmap child IRQ delivery for representative status bits, runtime PM access during IRQ handling, suspend wake behavior, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-madera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mbigen.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mbigen.c

### Purpose
`irq-mbigen.c` implements HiSilicon MBIGEN, a wired-interrupt-to-MSI generator. It creates device MSI domains for OF child interrupt-controller nodes or an ACPI device, programs MBIGEN vector/type/clear registers, and routes events to an ITS/MSI parent.

### Important APIs, Types, And Functions
`struct mbigen_device` stores the platform device and MMIO base. Address helpers compute node, vector, type, and clear register offsets. `mbigen_msi_template` supplies the MSI chip, translate, and descriptor setup callbacks. `mbigen_domain_translate()` validates pin numbers and trigger type. `mbigen_write_msi_msg()` writes the event ID into the vector register.

### Control Flow
Probe maps the MBIGEN resource, then either creates device domains for child OF interrupt-controller nodes using their `num-pins` or creates one ACPI device domain from the `num-pins` property. Allocation is handled by the MSI core using `mbigen_msi_template`: translation validates pins 64-1407 and level-high or edge-rising type; descriptor setup copies the firmware hwirq; EOI writes the clear register then EOIs the parent; type programming updates MBIGEN type registers.

### State, Persistence, And Dependencies
State is devm-managed private data and per-device MSI domains attached to child devices. It depends on MSI/ITS infrastructure, OF platform population, ACPI device properties, MBIGEN register layout, and `msi_create_device_irq_domain()`.

### Integration Points
MBIGEN child devices expose interrupt-controller domains that convert wired pins into MSI messages consumed by an ITS or other MSI parent domain.

### Risks
Pins 0-63 are reserved and rejected. Offset calculations skip the clear register window for high node IDs; regressions here can corrupt the clear register. `mbigen_write_msi_msg()` only programs event ID and assumes doorbell address is encoded in hardware. Failed OF child domain creation can leave previously created child devices.

### Test Signals
Validate OF and ACPI domain creation, invalid pin/type rejection, vector register event ID writes, type register updates for level/edge, EOI clear writes, high pin offsets around the clear-register skip, and MSI parent availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mbigen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mchp-eic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mchp-eic.c

### Purpose
`irq-mchp-eic.c` supports the Microchip SAMA7G5 external interrupt controller. It adapts two external lines to parent GIC SPIs, including polarity/level conversion, wake control, clock handling, and syscore suspend/resume.

### Important APIs, Types, And Functions
`struct mchp_eic` stores MMIO base, peripheral clock, hierarchy domain, parent SPI numbers, saved SCFG registers, and wake mask. `mchp_eic_probe()` creates the domain. `mchp_eic_domain_alloc()` translates two-cell child specs and allocates parent GIC SPIs. `mchp_eic_irq_set_type()` programs `SCFG` polarity/level bits and converts low/falling types to parent high/rising types.

### Control Flow
Probe allocates the singleton, maps registers, finds the parent domain, gets/enables `pclk`, disables both EIC lines, parses the two parent IRQ specs to capture SPI numbers, creates a two-entry hierarchy domain, and registers syscore PM. Mask/unmask update the EIC enable bit and parent state. Wake toggles parent wake and tracks `wakeup_source`. Suspend saves SCFG registers and disables the clock when no wake source is armed; resume re-enables the clock and restores SCFG.

### State, Persistence, And Dependencies
State is the global `eic`, saved per-line SCFG values, wake mask, clock state, and hierarchy domain. Dependencies include OF IRQ parsing, GIC three-cell bindings, common clock framework, irqchip hierarchy helpers, and syscore PM.

### Integration Points
The EIC is a small child irqdomain under the GIC. Board devices reference the EIC for external wake-capable interrupt lines while the driver forwards actual delivery through parent SPIs.

### Risks
Only two IRQs are supported. The global singleton prevents multiple EICs. `mchp_eic_irq_set_wake()` calls `irq_set_irq_wake()` but ignores its return value. Clock state during suspend depends on correct wake mask tracking.

### Test Signals
Check all four trigger types, parent type conversion, wake enable/disable and clock behavior across suspend, missing clock or parent domain errors, and correct parsing of both parent SPI entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mchp-eic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-meson-gpio.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-meson-gpio.c

### Purpose
`irq-meson-gpio.c` implements the Amlogic Meson GPIO interrupt multiplexer. It maps many GPIO input hwirqs onto a small number of hardware interrupt channels connected to a parent GIC, with SoC-specific mux and trigger programming.

### Important APIs, Types, And Functions
`struct meson_gpio_irq_params` captures per-SoC hwirq count, channel count, register bit layout, both-edge support, and operation callbacks. `struct meson_gpio_irq_controller` stores params, MMIO base, channel IRQ numbers, channel bitmap, and lock. `meson_gpio_irq_domain_alloc()` assigns a channel and allocates the parent GIC IRQ. `meson_gpio_irq_set_type()` programs local trigger bits and converts output type for the parent.

### Control Flow
Probe finds the parent domain, allocates controller state, maps registers, matches SoC params, reads `amlogic,channel-interrupts`, runs optional hardware init, and creates a hierarchical domain sized by available GPIO hwirqs. Allocation translates the two-cell child spec, reserves the first free channel, programs that channel's pin mux to the requested GPIO, allocates the parent SPI listed for that channel, and stores a pointer to the channel entry as chip data. Freeing releases the parent IRQ and clears the channel bit. Type changes use Meson8/A1/S4-specific register layouts and always tell the GIC to expect active-high level or rising edge.

### State, Persistence, And Dependencies
Persistent state is the channel allocation bitmap, channel-to-parent IRQ table, SoC parameter table, and MMIO trigger/mux registers. It depends on OF matching, parent GIC domains, raw spinlocks for register RMW, and Amlogic binding properties.

### Integration Points
GPIO controller drivers or board devices request interrupts from this domain. The driver hides the limited channel hardware by dynamically multiplexing GPIO hwirqs onto parent GIC SPIs.

### Risks
Channels are scarce; allocation fails with `-ENOSPC` when all are in use. Trigger-bit layouts vary widely by SoC, including special both-edge behavior. Freeing uses pointer arithmetic on `channel_irqs`, so chip data must remain a valid pointer into the controller. S4-style type programming touches two registers with different bit meanings.

### Test Signals
Exercise all compatible parameter sets, channel exhaustion/reuse, both-edge support and rejection on older SoCs, mux register programming for low/high channel numbers, parent SPI type conversion, allocation failure cleanup, and concurrent type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-meson-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-cpu.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-cpu.c

### Purpose
`irq-mips-cpu.c` implements the base MIPS CPU interrupt controller for the eight CP0 interrupt lines. It also optionally exposes software interrupt lines as an IPI domain on MIPS MT systems.

### Important APIs, Types, And Functions
`mips_cpu_irq_controller` masks/unmasks CP0 status interrupt bits. `mips_mt_cpu_irq_controller` adds MIPS MT software interrupt ack/startup and IPI send support. `plat_irq_dispatch()` is the weak default top-level dispatcher. `mips_cpu_intc_map()` maps hwirqs to percpu handlers. `mips_cpu_register_ipi_domain()` creates a two-entry IPI hierarchy domain when `CONFIG_GENERIC_IRQ_IPI` is enabled.

### Control Flow
Initialization clears all CP0 interrupt mask and cause bits, creates a legacy 8-entry IRQ domain, and optionally registers the IPI domain. The default dispatcher computes `cause & status & ST0_IM`, reports spurious interrupts if none are pending, then processes highest-priority pending bits, routing software interrupts through the IPI domain and others through the CPU domain. Mask/unmask operations set or clear CP0 status bits with hazard barriers.

### State, Persistence, And Dependencies
Persistent state is the CPU IRQ domain, optional IPI domain, and per-domain bitmap state for allocated software IPIs. It depends on MIPS CP0 register helpers, MIPS MT VPE manipulation, generic IPI support, and architecture setup constants.

### Integration Points
This is the fallback/root CPU interrupt controller for MIPS systems and can be the parent for higher-level interrupt controllers such as MIPS GIC.

### Risks
Software interrupt IPIs are only valid for sibling VPEs on the local core. `plat_irq_dispatch()` is weak and may be replaced by platform code, so behavior varies. Vector interrupt mode installs the same dispatch handler per hardware line. The IPI allocator has only two hardware slots.

### Test Signals
Boot with and without MIPS MT, software interrupt IPI send/receive, CP0 mask/unmask behavior, spurious dispatch accounting, vector interrupt handler setup, and exhaustion of the two IPI slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-gic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-gic.c

### Purpose
`irq-mips-gic.c` implements the MIPS Global Interrupt Controller. It handles shared external interrupts, local per-VPE interrupts, EIC routing, per-cluster register access, SMP affinity, optional IPI domains, and CPU hotplug startup.

### Important APIs, Types, And Functions
Global state includes `mips_gic_base`, `gic_irq_domain`, shared interrupt count, CPU pin, per-CPU pending masks, and IPI reservation bitmaps. `gic_of_init()` initializes hardware and domains. `gic_handle_shared_int()` and `gic_handle_local_int()` dispatch pending interrupts. `gic_set_type()` and `gic_set_affinity()` program polarity, trigger, dual-edge, VP routing, and per-CPU masks. `gic_register_ipi_domain()` allocates per-CPU shared vectors for IPIs.

### Control Flow
Init selects an available CPU vector, maps or inherits the GIC base, enables the GIC through the CM when present, reads shared interrupt capacity, installs either an EIC vector handler or a chained CPU IRQ handler, creates a domain covering local plus shared hwirqs, registers IPIs, records the EIC bind callback, resets shared interrupt polarity/trigger/masks in every cluster, and registers CPU hotplug startup. Dispatch first handles local pending/masked bits, then reads shared pending bitmaps, intersects with the current CPU's software mask, and handles each mapped hwirq. Allocation maps local interrupts to percpu handlers or shared interrupts to routed level chips.

### State, Persistence, And Dependencies
State includes hardware routing registers, per-CPU shared masks, all-VPE local interrupt metadata, IPI reserved/available bitmaps, and CPU hotplug callbacks. Dependencies include MIPS CM/CPS support, GIC register accessors, OF bindings, cpuhotplug, SMP affinity, and generic IRQ/IPI infrastructure.

### Integration Points
The GIC can replace direct CPU interrupt handling, supplies timer/perf/FDC local IRQ mappings, exports `gic_get_c0_*_int()` helpers, and provides a DOMAIN_BUS_IPI domain for SMP cross-calls.

### Risks
Cluster redirection locking is subtle; wrong effective affinity can program the wrong cluster. IPI allocation reserves shared vectors that must not collide with normal shared IRQs. Local interrupts that are not routable fall back to CPU IRQs or fail mapping. `gic_ipi_domain_alloc()` checks availability using a loop that is sensitive to the requested count and base index.

### Test Signals
Test VEIC and non-VEIC boot, inherited and DT-specified base addresses, shared IRQ type/affinity changes across clusters, CPU hotplug restoring local masks, IPI allocation/free/send, reserved vector conflicts, timer/perf/FDC helper mappings, and spurious or masked shared interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mips-gic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mmp.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mmp.c

### Purpose
`irq-mmp.c` implements Marvell MMP/PXA-style ICU interrupt handling, including primary ICU dispatch and optional cascaded MMP2 mux interrupt controllers.

### Important APIs, Types, And Functions
`struct icu_chip_data` stores IRQ counts, virtual base, cascade IRQ, mask/status registers, configuration masks, and domain. `mmp_init_bases()` creates the primary domain and static mappings. `mmp_handle_irq()` and `mmp2_handle_irq()` read selected pending hwirqs from CPU-specific selector registers. `icu_mux_irq_demux()` demultiplexes cascaded mux controllers. `icu_irq_chip` provides mask, mask_ack, and unmask.

### Control Flow
Primary initialization maps ICU registers, reads `mrvl,intc-nr-irqs`, creates a linear domain, eagerly maps every hwirq to stable Linux IRQs, configures SoC-specific enable/disable masks, and installs the exception handler. MMP3 may map a second ICU base. Mux initialization interprets the legacy offset-style `reg` property, creates a child domain, maps all mux hwirqs, records optional PMIC clear behavior, and chains the mux parent IRQ. Top-level dispatch reads `PJ1_INT_SEL` or `PJ4_INT_SEL`; mux dispatch loops until no unmasked status bits remain.

### State, Persistence, And Dependencies
Persistent state is held in global ICU bases, `icu_data[]`, virtual IRQ bases, domains, and `max_icu_nr`. It depends on OF resources, ARM exception handling, irqdomain mapping, chained IRQ helpers, and MMP SoC-specific PMIC clear code.

### Integration Points
It is the root interrupt controller for MMP variants and a cascade point for muxed secondary interrupt blocks. Device-tree users may depend on stable legacy-style virq bases due to eager mapping.

### Risks
The driver relies on global arrays and fixed `MAX_ICU_NR`. Mux handling uses virtual IRQ base arithmetic instead of domain lookup. Primary mask operations differ for ICU0 versus mux controllers. Historical `reg` offsets in mux nodes are not normal bus addresses.

### Test Signals
Boot MMP, MMP2, and MMP3 variants; verify primary selector dispatch, mux cascade loops, mask/unmask for ICU0 and mux controllers, PMIC interrupt clear path, malformed `mrvl,intc-nr-irqs` or `reg`, and stable IRQ numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mscc-ocelot.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mscc-ocelot.c

### Purpose
`irq-mscc-ocelot.c` implements Microsemi/Microchip VCore-III internal CPU interrupt controllers for Ocelot, Serval, Luton, and Jaguar2 SoCs. It uses generic IRQ chips with SoC-specific register offsets.

### Important APIs, Types, And Functions
`struct chip_props` describes register offsets, flags, and IRQ count per SoC. `vcoreiii_irq_init()` is the shared initializer. `ocelot_irq_handler()` demultiplexes the `INTR_IDENT` register. `ocelot_irq_unmask()` handles edge sticky clearing for controllers with trigger registers.

### Control Flow
Initialization parses the parent IRQ, creates a linear domain, allocates one generic chip, maps MMIO, configures ack/mask/unmask register callbacks according to SoC flags, masks and acks all interrupts, optionally enables the IRQ0 output path, stores properties in domain host data, and chains the parent. Dispatch reads the destination interrupt identification register and handles each set hwirq from highest bit downward. Unmask clears sticky state for edge-mode interrupts before setting enable bits.

### State, Persistence, And Dependencies
State is the generic chip, mapped MMIO, domain host data pointing to static SoC properties, and parent chain. Dependencies include OF matching, generic-chip APIs, chained IRQ helpers, and SoC register semantics.

### Integration Points
This is the internal interrupt controller feeding a parent CPU interrupt line on VCore-III SoCs. Child devices use normal domain mappings created from device tree.

### Risks
SoC register offsets differ and incorrect matching causes wrong MMIO writes. The unmask path reads two trigger register replicas to infer edge mode; this is hardware-specific. Luton needs an explicit output enable bit. There is no runtime remove path for early irqchip declarations.

### Test Signals
Validate all four compatibles, trigger/sticky clearing behavior, parent cascade delivery, generic-chip mask/ack registers, Luton output enable, and empty/invalid parent IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mscc-ocelot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-msi-lib.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-msi-lib.c

### Purpose
`irq-msi-lib.c` is a shared helper library for irqchip drivers that expose MSI parent domains. It normalizes child MSI domain flags/chip callbacks and provides a common domain selection function for NEXUS or generic MSI parent domains.

### Important APIs, Types, And Functions
`msi_lib_init_dev_msi_info()` validates `msi_parent_ops`, reconciles child `msi_domain_info` flags with parent required/supported flags, installs default EOI/ACK/mask/affinity callbacks when requested, and prepares device MSI or wired-to-MSI domains. `msi_lib_irq_domain_select()` matches an IRQ domain by fwnode and bus token against the parent ops bus selection mask. Both are exported GPL symbols.

### Control Flow
Initialization first verifies the real parent has MSI parent ops and that the selected domain bus token matches the parent token. It switches on the requested child bus token, rejects unsupported PCI MSI configurations, adjusts required flags for device and wired-to-MSI domains, masks unsupported flags, enforces required flags, and fills missing chip operations. Selection obtains the relevant fwnode, rejects nonzero firmware parameters or fwnode mismatch, then returns true for direct parent token matches or supported child bus tokens.

### State, Persistence, And Dependencies
The file owns no persistent state. It mutates caller-provided `msi_domain_info` and IRQ chip structures during domain creation. It depends on generic MSI core types, irqdomain flags/tokens, and parent-driver `msi_parent_ops`.

### Integration Points
Used by Loongson PCH MSI, Layerscape SCFG MSI, Marvell GICP/ODMI/SEI, and similar irqchip MSI parent drivers to avoid duplicating MSI domain policy.

### Risks
The helpers intentionally warn and fail for unexpected bus-token combinations. Because they mutate chip callbacks, callers must pass a chip structure that can be safely modified for the child domain. Incorrect parent flags can silently mask child features before required flags are re-added.

### Test Signals
Create PCI MSI, PCI MSI-X, platform MSI, device MSI, and wired-to-MSI domains against several parent ops configurations; verify flag filtering, default affinity/mask/eoi/ack injection, fwnode-parent matching, and rejection of nonzero fwspec parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-msi-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mst-intc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mst-intc.c

### Purpose
`irq-mst-intc.c` implements the MStar/MediaTek MST interrupt controller, a hierarchical SPI adapter that masks, polarity-inverts, and optionally EOIs interrupts before forwarding them to a parent GIC-like controller.

### Important APIs, Types, And Functions
`struct mst_intc_chip_data` stores MMIO base, hwirq range mapping, lock, `no_eoi`, and PM list state. `mst_intc_domain_translate()` validates GIC-style OF specs. `mst_intc_domain_alloc()` installs `mst_intc_chip` and allocates the shifted parent SPI range. `mst_irq_chip_set_type()` programs reverse polarity and forces parent level-high. PM helpers save and restore polarity registers.

### Control Flow
OF init finds the parent domain, reads `mstar,irqs-map-range`, maps registers, records `irq_start` and `nr_irqs`, creates a hierarchy domain, and adds the controller to a global PM list. Allocation rejects PPIs, maps local hwirqs to parent `irq_start + hwirq`, and always passes `IRQ_TYPE_LEVEL_HIGH` to the parent because the MST block latches/normalizes signals. Mask/unmask set or clear bits in `INTC_MASK`, EOI sets `INTC_EOI` unless disabled, and type programming controls `INTC_REV_POLARITY`.

### State, Persistence, And Dependencies
State includes per-controller chip data, hardware polarity/mask/eoi registers, and a global suspend list guarded by syscore callbacks. Dependencies include OF hierarchy domains, GIC-style interrupt cells, syscore PM, and raw spinlocks.

### Integration Points
This driver is inserted between device SPIs and the parent interrupt controller. It maps a local range onto a contiguous parent SPI range specified by firmware.

### Risks
The parent always sees level-high, so local edge semantics rely on MST latching and EOI. `mstar,intc-no-eoi` changes completion semantics and must match hardware. PM only saves polarity, not mask state. Range math must match firmware's parent SPI numbering.

### Test Signals
Validate `mstar,irqs-map-range`, reject PPI specs, trigger all supported polarity/type modes, verify EOI/no-EOI behavior, parent allocation parameters, suspend/resume polarity restore, and multiple controller instances on the PM list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mst-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-cirq.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-cirq.c

### Purpose
`irq-mtk-cirq.c` implements the MediaTek CIRQ low-power interrupt recorder. It mirrors a configured external IRQ range from a parent controller and records edge interrupts during suspend so they can be flushed back on resume.

### Important APIs, Types, And Functions
`struct mtk_cirq_chip_data` stores MMIO base, external IRQ start/end, register-offset table, and domain. `mtk_cirq_domain_translate()` maps GIC SPI numbers in the configured range to local CIRQ hwirqs. `mtk_cirq_set_type()` programs polarity/sensitivity and delegates to the parent. `mtk_cirq_suspend()` acks safe recorded state and enables edge recording; `mtk_cirq_resume()` flushes then disables CIRQ.

### Control Flow
OF init finds the parent domain, maps registers, reads `mediatek,ext-irq-range`, selects v1/v2 register offsets, creates a hierarchy domain, and registers syscore PM. Allocation validates a single SPI in range, installs `mtk_cirq_chip`, and allocates the unchanged parent fwspec. Suspend walks every supported CIRQ line, checks parent pending/masked state to avoid losing interrupts that arrived after global IRQ disable, acks safe lines, then enables edge-only CIRQ recording. Resume sets `CIRQ_FLUSH`, then clears `CIRQ_EDGE` and `CIRQ_EN`.

### State, Persistence, And Dependencies
Persistent state is the singleton `cirq_data`, external range, offset table, hierarchy domain, and CIRQ control registers. It depends on parent irqchip state queries, OF bindings, syscore suspend ordering, and MediaTek CIRQ register layouts.

### Integration Points
The CIRQ domain is a transparent child of the GIC for supported external SPIs. It mainly matters in system suspend/resume paths.

### Risks
Only one global CIRQ instance is supported. `mtk_cirq_set_type()` defaults through unsupported types rather than returning `-EINVAL` before delegating, so parent rejection is important. Suspend correctness depends on parent pending/masked state support. Range translation rejects PPIs and out-of-range SPIs.

### Test Signals
Test both offset-table versions, valid and out-of-range SPIs, each trigger type, parent state query failures, interrupts arriving between `arch_suspend_disable_irqs()` and CIRQ suspend, resume flush delivery, and malformed DT range properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-cirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-sysirq.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-sysirq.c

### Purpose
`irq-mtk-sysirq.c` implements the MediaTek SYSIRQ polarity controller. It creates a hierarchy domain above the GIC and uses one or more INTPOL register banks to invert low/falling interrupts before forwarding high/rising types to the parent.

### Important APIs, Types, And Functions
`struct mtk_sysirq_chip_data` stores INTPOL base pointers, per-base word counts, and precomputed hwirq-to-base/word lookup tables. `mtk_sysirq_set_type()` updates the INTPOL bit and delegates converted type to the parent. `mtk_sysirq_domain_alloc()` installs `mtk_sysirq_chip` and allocates parent interrupts.

### Control Flow
Initialization counts MMIO address ranges, maps each range, computes total interrupt capacity from resource sizes, allocates lookup arrays mapping every hwirq to an INTPOL bank and word, creates a hierarchy domain, and initializes the spinlock. Allocation rejects PPIs, sets hwirq/chip for each requested virq, rewrites the fwspec fwnode to the parent, and allocates parent IRQs. Type setting locks the chip, sets the polarity bit for low/falling child types while converting them to high/rising parent types, clears it otherwise, writes the register, and calls the parent `irq_set_type`.

### State, Persistence, And Dependencies
Persistent state is the mapped INTPOL banks, lookup arrays, domain, and hardware polarity bits. It depends on OF resources, parent GIC-style domains, raw spinlocks, and hierarchy IRQ operations.

### Integration Points
SYSIRQ is the polarity adaptation layer for MediaTek external SPIs. Devices reference SYSIRQ while actual interrupt delivery remains through the parent GIC.

### Risks
The lookup construction assumes hwirq numbers densely cover all INTPOL bits. Parent `irq_set_type` is invoked while holding the SYSIRQ raw spinlock, so parent implementations must be IRQ-safe. Only SPI-style specs are accepted.

### Test Signals
Validate multiple register banks, all polarity conversions, parent type propagation, PPI rejection, hwirq values near bank boundaries, cleanup on mapping/allocation errors, and DTs with zero or malformed resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-sysirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-gicp.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-gicp.c

### Purpose
`irq-mvebu-gicp.c` implements the Marvell AP806 GICP platform-MSI parent. It allocates GIC SPIs from firmware-provided ranges and composes two-message set/clear MSI payloads for level-capable platform MSI users.

### Important APIs, Types, And Functions
`struct mvebu_gicp` stores SPI ranges, total SPI count, bitmap, resource, lock, and device. `gicp_idx_to_spi()` maps bitmap indices to real SPI numbers. `gicp_irq_domain_alloc()` reserves an SPI, allocates the parent GIC IRQ, and installs `gicp_irq_chip`. `gicp_compose_msi_msg()` emits SETSPI and CLRSPI messages. `gicp_msi_parent_ops` advertises platform MSI support.

### Control Flow
Probe reads `marvell,spi-ranges`, builds the range table and bitmap, finds the parent domain, clears pending interrupts by writing the CLRSPI register for entries 0-63, and creates an MSI parent domain. Allocation reserves the first free bitmap index, maps it to a GIC SPI, allocates a parent SPI as edge-rising initially, and installs the chip. Freeing tears down the parent IRQ and releases the bitmap bit.

### State, Persistence, And Dependencies
State is devm-managed GICP data, SPI bitmap, parent MSI domain, and MMIO resource used for MSI message addresses. Dependencies include OF properties, parent GIC domain, MSI parent helpers, and `irq-msi-lib.c`.

### Integration Points
Platform MSI devices select the GICP domain and receive MSI messages targeting the GICP set/clear registers, which in turn assert or clear parent GIC SPIs.

### Risks
Firmware range errors directly affect parent SPI allocation. Probe clears only 64 possible pending values even if ranges describe more. Allocation handles one IRQ at a time despite receiving `nr_irqs`. The parent type is initially edge-rising until the child sets type.

### Test Signals
Validate multi-range SPI mapping, bitmap exhaustion/free, MSI message set/clear addresses, level-capable MSI flags, pending clear on probe, parent-domain absence, and invalid `marvell,spi-ranges` lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-gicp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-icu.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-icu.c

### Purpose
`irq-mvebu-icu.c` implements the Marvell CP110 ICU wired-to-MSI bridge. It supports NSR and SEI ICU subsets, legacy and child-node bindings, and configures ICU interrupt entries to emit MSI messages toward a platform MSI parent.

### Important APIs, Types, And Functions
`struct mvebu_icu` stores base and device. `struct mvebu_icu_msi_data` binds an ICU instance to subset data and one-time MSI address initialization. `mvebu_icu_translate()` validates firmware specs and trigger type. `mvebu_icu_write_msi_msg()` initializes set/clear message addresses and writes `ICU_INT_CFG()`. Separate MSI templates cover NSR and SEI behavior.

### Control Flow
The parent ICU probe maps registers, detects legacy single-node bindings, clears existing NSR/SEI configurations, stores drvdata, and either probes a synthetic subset or populates child subset devices. Subset probe gets the platform MSI parent domain, selects NSR or SEI template, and creates a device IRQ domain with `ICU_MAX_IRQS`. MSI message writes program the ICU set/clear target addresses once per subset, then enable the hwirq, encode type and group, and mirror SATA0/SATA1 entries when required.

### State, Persistence, And Dependencies
State includes mapped ICU registers, static key for legacy bindings, per-subset initialized atomics, MSI domain data, and ICU configuration registers. Dependencies include platform MSI domains, OF child population, MSI device domains, `irq-msi-lib.c`, and `mvebu-icu.h` group constants.

### Integration Points
Devices with wired ICU interrupts get a per-device MSI domain; the ICU converts their lines into MSIs routed through GICP/SEI-like platform MSI parents.

### Risks
Legacy binding mode globally affects parameter count and group interpretation. SEI subset translation forces edge-rising and comments that handling is unreliable because ICU input semantics differ. SATA entries are intentionally programmed in pairs. One-time address initialization relies on the first nonzero MSI message.

### Test Signals
Validate legacy and child-node bindings, NSR and SEI subsets, invalid hwirqs and parameter counts, MSI write and clear paths, SATA paired programming, probe deferral without MSI parent, and clearing firmware-provided ICU state on boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-icu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-odmi.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-odmi.c

### Purpose
`irq-mvebu-odmi.c` implements the Marvell ODMI platform-MSI parent. Each ODMI frame provides eight interrupt slots mapped to parent GIC SPIs and exposed through a generic MSI parent domain.

### Important APIs, Types, And Functions
`struct odmi_data` stores each frame's resource, base, and SPI base. Global `odmis`, `odmis_bm`, and `odmis_count` manage slot allocation. `odmi_irq_domain_alloc()` reserves a slot and allocates a parent SPI. `odmi_compose_msi_msg()` builds the ODMI doorbell address/data. `odmi_msi_parent_ops` declares platform MSI support.

### Control Flow
OF init reads `marvell,odmi-frames`, allocates frame state and a bitmap, maps each frame resource, reads its `marvell,spi-base`, and creates an MSI parent domain sized at `frames * 8`. Allocation reserves the first free hwirq, computes frame and slot, allocates the parent GIC SPI as edge-rising, explicitly sets parent type to edge-rising, and installs `odmi_irq_chip`. Freeing releases the parent IRQ and bitmap slot.

### State, Persistence, And Dependencies
State is global frame arrays, bitmap, mapped MMIO frames, and the MSI parent domain. Dependencies include OF resources/properties, GIC three-cell specs, MSI parent helpers, and `irq-msi-lib.c`.

### Integration Points
Platform MSI clients use ODMI as a generic MSI parent; ODMI turns MSI writes into GIC SPI assertions.

### Risks
On parent allocation failure the error path clears `odmin` rather than full `hwirq`, which can release the wrong bitmap bit for frames beyond zero. Global state allows one ODMI controller set. Group events are not supported; only eight interrupts per frame are exposed.

### Test Signals
Validate multiple frames, per-frame SPI base mapping, bitmap allocation/free beyond frame zero, MSI message data/address, parent edge type setup, malformed properties, and ENOSPC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-odmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-pic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-pic.c

### Purpose
`irq-mvebu-pic.c` implements the Marvell Armada 7K/8K PIC, a per-CPU cascaded interrupt controller with 32 local interrupts and one parent per-CPU IRQ.

### Important APIs, Types, And Functions
`struct mvebu_pic` stores MMIO base, parent IRQ, domain, and platform device. `mvebu_pic_probe()` maps resources, creates the domain, chains the parent, and enables the per-CPU IRQ on all CPUs. `mvebu_pic_handle_cascade_irq()` dispatches cause bits. `mvebu_pic_chip` masks, unmasks, EOIs, and prints the device name.

### Control Flow
Probe maps MMIO, parses the parent IRQ, creates a 32-entry linear domain, installs the chained parent handler and handler data, calls `on_each_cpu()` to reset the PIC and enable the per-CPU parent IRQ, and stores drvdata. Domain mapping marks each virq as percpu devid and uses `handle_percpu_devid_irq`. Cascade handling reads `PIC_CAUSE` and handles every set bit in the domain. Remove disables the per-CPU parent on each CPU and removes the domain.

### State, Persistence, And Dependencies
State is devm-managed controller data, MMIO mask/cause registers, per-CPU parent enable state, and the IRQ domain. Dependencies include platform driver binding, OF IRQ parsing, per-CPU IRQ APIs, chained IRQ handling, and seq-file printing.

### Integration Points
The PIC feeds per-CPU interrupt sources into Linux on Armada 7K/8K. Child interrupts are represented as per-CPU device IRQs.

### Risks
Mask register semantics are inverted from many controllers: reset writes zero to mask and the mask callback sets bits. Cascade dispatch does not mask cause with enable/mask state, so hardware cause behavior must be reliable. Parent IRQ setup uses separate `irq_set_chained_handler()` and `irq_set_handler_data()` calls.

### Test Signals
Validate per-CPU enable/disable on all CPUs, cause-bit dispatch, EOI writes, mask/unmask semantics, remove cleanup, parent IRQ parse failures, and `/proc/interrupts` chip printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-sei.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-sei.c

### Purpose
`irq-mvebu-sei.c` implements the Marvell AP806 SEI controller. It creates a root SEI domain, a wired AP child domain, and a platform-MSI CP child domain over separate interrupt ranges.

### Important APIs, Types, And Functions
`struct mvebu_sei` stores MMIO, resource, domains, range capabilities, CP MSI bitmap/lock, and mask lock. `mvebu_sei_handle_cascade_irq()` reads SEI cause registers and dispatches root hwirqs. `mvebu_sei_ap_alloc()` maps wired AP interrupts. `mvebu_sei_cp_domain_alloc()` allocates CP MSI slots. `mvebu_sei_cp_compose_msi_msg()` builds SET_SEI MSI messages.

### Control Flow
Probe maps registers, loads AP/CP range capabilities, maps the top-level SPI parent, creates the root SEI nexus domain, creates a wired AP hierarchy domain, creates a CP MSI parent domain, resets cause/mask registers, and chains the parent IRQ. Root allocation only installs the low-level SEI chip. AP allocation offsets hwirqs by the AP range and uses level handling. CP allocation reserves one bitmap slot, offsets by the CP range, allocates the root parent, and uses edge handling. Cascade dispatch walks both 32-bit cause registers and reports unmapped hwirqs as spurious warnings.

### State, Persistence, And Dependencies
Persistent state includes root/AP/CP domains, CP allocation bitmap, MMIO cause/mask registers, and capability ranges. Dependencies include OF match data, platform MSI helpers, chained IRQ handling, irqdomain hierarchy, and `irq-msi-lib.c`.

### Integration Points
AP wired interrupts and CP platform MSI users share the same SEI hardware and root cascade. The CP MSI domain is selected by platform MSI clients.

### Risks
CP MSI allocation supports only single IRQ requests. AP type is restricted to level-high and CP type to edge-rising. The root domain has no translate callback and depends on child domains passing expected fwspecs. Affinity on the root chip returns `-EINVAL`.

### Test Signals
Validate AP and CP range mapping, CP bitmap exhaustion/free, MSI message data/address, cascade dispatch of mapped and unmapped bits, mask/unmask/ack register operations, parent SPI parse failure, and invalid type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-sei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mxs.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mxs.c

### Purpose
`irq-mxs.c` implements the Freescale MXS ICOLL interrupt collector and the related Alphascale ASM9260 variant. It installs the architecture top-level IRQ handler and maps collector hwirqs into a linear domain.

### Important APIs, Types, And Functions
`struct icoll_priv` stores register pointers and controller type. `icoll_of_init()` handles MXS ICOLL, while `asm9260_of_init()` handles ASM9260. `icoll_handle_irq()` reads the active vector/status, acknowledges the vector register, and handles the domain IRQ. `mxs_icoll_chip` and `asm9260_icoll_chip` provide variant-specific mask/unmask operations.

### Control Flow
MXS init maps registers, assigns register pointers, resets the block with `stmp_reset_block()`, creates a 128-entry domain, and installs `icoll_handle_irq()`. ASM9260 init maps alternate register offsets, enables controller IRQs, manually initializes priority/level registers because no reset bit exists, creates its domain, and installs the same handler. The top-level handler reads the current hwirq, writes it to the vector register, and calls `generic_handle_domain_irq()`.

### State, Persistence, And Dependencies
State is global `icoll_priv` and `icoll_domain`. Dependencies include OF mapping, STMP reset support, ARM exception handling, variant register definitions, and irqdomain APIs.

### Integration Points
The driver is the root interrupt controller for MXS/ASM9260 systems. Child devices use one-cell interrupt specifiers into the linear domain.

### Risks
Global state allows one controller. The handler assumes the status register always returns a valid active hwirq. ASM9260 packs four interrupts per register, so bit-shift helper correctness is critical. There is no explicit spurious handling.

### Test Signals
Boot both compatibles, validate controller reset/manual initialization, mask/unmask bit positions for representative hwirqs, top-level vector dispatch, domain map size differences, and invalid MMIO mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mxs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-nvic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-nvic.c

### Purpose
`irq-nvic.c` supports the ARMv7-M Nested Vectored Interrupt Controller. It creates a generic-chip domain over implemented NVIC external interrupts and installs the Cortex-M exception IRQ handler.

### Important APIs, Types, And Functions
`nvic_irq_domain` is the global domain. `nvic_of_init()` reads the number of interrupt banks, maps NVIC registers, allocates generic chips, disables all interrupts, sets priorities, and calls `set_handle_irq()`. `nvic_handle_irq()` reads SCB `ICSR.VECTACTIVE` and subtracts 16 to obtain the external hwirq. `nvic_irq_domain_alloc()` maps one-cell specs to generic chips.

### Control Flow
Initialization reads `V7M_SCS_ICTR` to compute implemented banks, caps the total at `NVIC_MAX_IRQ`, maps the NVIC resource, creates a linear domain, allocates one generic chip per 32 interrupts using `handle_fasteoi_irq`, programs each bank's enable/disable registers, disables all lines, zeroes priority registers, and installs the handler. Runtime dispatch handles the active exception's corresponding hwirq through the domain.

### State, Persistence, And Dependencies
Persistent state is the global NVIC domain, mapped NVIC base stored in generic chips, mask cache, and priority/enable hardware registers. It depends on ARMv7-M SCB definitions, OF resources, generic IRQ chips, and exception return providing EOI semantics.

### Integration Points
This is the root irqchip for ARMv7-M platforms. Device tree interrupt specifiers are one-cell NVIC external interrupt numbers.

### Risks
`nvic_handle_irq()` assumes `VECTACTIVE >= 16` for external interrupts. The last bank may expose only 16 interrupts, but generic chips are allocated in 32-line units while total IRQ count is capped. EOI is a no-op because exception return completes the interrupt.

### Test Signals
Validate bank count detection, max IRQ capping, priority initialization, enable/disable registers, active-vector dispatch, one-cell mappings, and Cortex-M systems with partial final banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-nvic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-omap-intc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-omap-intc.c

### Purpose
`irq-omap-intc.c` implements the OMAP2/OMAP3/AM33xx INTC controller. It handles root IRQ dispatch, generic-chip allocation, legacy and linear irqdomain modes, context save/restore, and OMAP idle workarounds.

### Important APIs, Types, And Functions
Global state includes `domain`, `omap_irq_base`, `omap_nr_pending`, `omap_nr_irqs`, and saved `intc_context`. `intc_of_init()` selects 96 or 128 IRQ mode. `omap_intc_handle_irq()` reads `INTC_SIR` and dispatches active IRQs. `omap_alloc_gc_of()` and `omap_alloc_gc_legacy()` configure generic chips. Exported helpers include `omap_intc_save_context()`, `omap_intc_restore_context()`, `omap_irq_pending()`, and OMAP3 idle/suspend helpers.

### Control Flow
OF init sets controller size based on compatible, initializes either legacy domains for OMAP2/3 DMA compatibility or linear domains for newer SoCs, soft-resets the hardware, enables protection, and installs the exception handler. Generic chips use MIR clear/set registers for unmask/mask and `omap_mask_ack_irq()` for ack. Dispatch reads the sorted active IRQ register, detects spurious values, acknowledges spurious interrupts, otherwise handles the active IRQ through the domain.

### State, Persistence, And Dependencies
State includes saved sysconfig/protection/idle/threshold/ILR/MIR registers, mapped INTC base, domain mappings, and generic-chip mask caches. Dependencies include ARM exception handling, OF matching, legacy IRQ descriptor allocation, generic-chip helpers, and OMAP PM/idle callers.

### Integration Points
This is the root interrupt controller on supported OMAP families. PM code calls context and idle helpers, while older DMA code drives the legacy-domain decision.

### Risks
OMAP2/3 legacy mode is retained for DMA compatibility, so changing domain mode can break old platform code. Spurious IRQs are expected under posted-write timing and are only logged once. Context restore comments note MIRs are also saved/restored elsewhere, so PM ordering matters.

### Test Signals
Boot OMAP2/3 and AM33xx/DM81xx, validate 96 vs 128 IRQ sizing, legacy and OF linear domains, spurious SIR handling, mask/ack/unmask registers, context save/restore, idle workaround calls, and pending IRQ detection during suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-omap-intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ompic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ompic.c

### Purpose
`irq-ompic.c` implements the OpenRISC Open Multi-Processor Interrupt Controller, used for inter-processor interrupts on multi-core OpenRISC systems.

### Important APIs, Types, And Functions
Global `ompic_base` maps the controller. Per-CPU `ops` stores pending IPI message bits and `ipi_dummy_dev` backs the percpu IRQ request. `ompic_raise_softirq()` is registered as the SMP cross-call function. `ompic_ipi_handler()` acknowledges the hardware interrupt and dispatches pending IPI messages via `handle_IPI()`. `ompic_of_init()` validates DT and installs the percpu IRQ.

### Control Flow
Initialization rejects duplicate controllers, validates the MMIO resource size against `num_possible_cpus()`, maps registers, parses the shared per-CPU IPI IRQ, marks it percpu devid, requests it with `request_percpu_irq()`, and registers `set_smp_cross_call()`. Raising an IPI sets the message bit in the destination CPU's per-CPU `ops` word, then writes the source CPU control register with generate, destination, and data bits. The handler acknowledges the CPU's control register, atomically drains pending ops with `xchg()`, and calls `handle_IPI()` for each bit.

### State, Persistence, And Dependencies
Persistent state is the MMIO base, per-CPU pending operation bitmaps, requested percpu IRQ, and architecture cross-call hook. Dependencies include OpenRISC SMP support, OF resource/IRQ parsing, big-endian MMIO accessors, and percpu interrupt APIs.

### Integration Points
The driver provides the low-level IPI transport used by OpenRISC SMP. It does not expose child IRQ domains because OMPIC has no device interrupt inputs.

### Risks
Resource size must cover every possible CPU. Atomic `set_bit()` and `xchg()` are relied on for ordering on OpenRISC; other architectures would need explicit barriers. Hardware IRQ data field is unused except for a constant payload. There is no shutdown path after successful early init.

### Test Signals
Validate duplicate-controller rejection, resource-size checks, percpu IRQ request and enablement, cross-CPU IPI delivery to all online CPUs, multiple pending IPI bits, big-endian register writes, and failure cleanup for IRQ parse/request errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ompic.c -->
