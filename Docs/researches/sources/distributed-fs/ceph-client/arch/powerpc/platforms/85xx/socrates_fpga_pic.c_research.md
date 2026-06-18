# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c

### Purpose
IRQ-domain and irq_chip implementation for the Socrates board FPGA interrupt controller. It maps FPGA interrupt lines, handles masking/ack/eoi/type configuration, and cascades from a parent interrupt.

### Important APIs, Types, And Functions
Important items include `struct socrates_fpga_irq_info`, `fpga_irqs[]`, `socrates_fpga_pic_cascade()`, `socrates_fpga_pic_ack()`, `mask()`, `mask_ack()`, `unmask()`, `eoi()`, `set_type()`, `socrates_fpga_pic_chip`, `socrates_fpga_pic_host_map()`, `socrates_fpga_pic_host_xlate()`, and public `socrates_fpga_pic_init()`.

### Control Flow
Initialization maps FPGA registers from the DT node, creates a linear IRQ domain, maps the parent cascade IRQ, and installs a chained handler. When the parent IRQ fires, the cascade handler reads pending/enabled bits and dispatches child mappings. Per-IRQ operations update FPGA mask/status/type registers.

### State, Persistence, And Dependencies
State includes static IRQ metadata, mapped FPGA MMIO, IRQ domain, cached polarity/trigger configuration, and chained handler linkage. No durable persistence exists. Dependencies include OF address/IRQ parsing, irq_domain APIs, Linux irq_chip callbacks, and Socrates board register layout.

### Integration Points
Used by `socrates.c` to expose FPGA interrupt sources as normal Linux IRQs to device drivers.

### Risks
Bit numbering, type programming, and ack/mask order can create lost interrupts or interrupt storms. The xlate path must validate specifier bounds.

### Test Signals
Trigger each FPGA interrupt line, test edge/level type configuration, mask/unmask behavior, cascade parent accounting, and invalid DT interrupt specifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/socrates_fpga_pic.c -->
