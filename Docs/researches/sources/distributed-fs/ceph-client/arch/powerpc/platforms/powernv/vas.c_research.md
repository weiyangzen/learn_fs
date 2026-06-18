## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.c

### Purpose
`vas.c` discovers VAS hardware instances from device tree, allocates per-instance state, configures global fault IRQs/windows, maps CPU-to-VAS affinity, and registers the platform driver.

### Important APIs, Types, And Functions
Important symbols are global `vas_mutex`, `init_vas_instance()`, `vas_irq_fault_window_setup()`, `find_vas_instance()`, exported `chip_to_vas_id()`, `vas_probe()`, and `vas_init()`.

### Control Flow
`vas_init()` registers the platform driver and manually creates platform devices for `ibm,vas` nodes. Probe reads `ibm,vas-id`, `ibm,chip-id`, and four resources, initializes `struct vas_instance`, derives paste window shift, allocates a XIVE IRQ on the chip, maps it to a Linux virq, captures the XIVE trigger page as IRQ port, assigns CPUs on the same chip to this VAS id, links the instance globally, optionally sets up threaded fault handling and a fault window, initializes debugfs, and stores driver data.

### State, Persistence, And Dependencies
State includes the global instance list, `cpu_vas_id` per-CPU mapping, per-instance IDA/window tables/mutex/fault fields, IRQ mapping, and BAR addresses. Dependencies include OF platform resources, XIVE native IRQ allocation, IRQ domains, `vas-fault.c`, and debugfs helpers.

### Integration Points
Window open paths call `find_vas_instance()`. External users can map a chip to a VAS id with `chip_to_vas_id()`.

### Risks
Several error paths after IRQ allocation return without freeing earlier allocations. VAS expects exactly four DT resources and a sane paste shift. If fault setup fails, user send windows are disabled by clearing `virq`.

### Test Signals
DT probing with multiple chips, CPU affinity mapping, XIVE IRQ allocation failures, fault-window setup failure, and `vasid == -1` local lookup are useful tests.
