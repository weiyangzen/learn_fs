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
