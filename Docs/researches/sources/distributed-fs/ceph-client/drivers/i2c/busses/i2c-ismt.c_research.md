# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ismt.c

Purpose: implements the Intel SMBus Message Transport PCI driver for Atom S12xx and related Intel devices. It supports hardware PEC, block buffer, process call, block process call, I2C block transactions, descriptor-ring execution, MSI or INTx completion, and ACPI resource conflict checks.

Important APIs, types, and functions: `struct ismt_desc` is the packed hardware descriptor with target address, command/write length, read length, control/status, retry, byte counts, and DMA pointer. `struct ismt_priv` stores the adapter, PCI BAR, coherent descriptor ring, head pointer, completion, aligned data buffer, and interrupt log. `ismt_access()` is the SMBus algorithm hook. `ismt_process_desc()` translates descriptor status and copies read results. `ismt_hw_init()`, `ismt_dev_init()`, and `ismt_int_init()` configure hardware, coherent memory, and interrupts.

Control flow: probe enables the PCI device, sets bus mastering, checks BAR and ACPI conflicts, maps BAR0, enables 64-bit coherent DMA, allocates descriptors and interrupt log, initializes hardware registers, requests MSI or shared INTx, and registers the adapter. Each SMBus operation clears the current descriptor and log, fills descriptor fields and an aligned DMA buffer based on the SMBus protocol, maps the data buffer if needed, submits the descriptor by advancing firmware head pointer and setting start, waits up to one second for interrupt completion, unmaps DMA, processes descriptor status, then advances the ring head.

State and persistence: persistent state includes coherent descriptor memory, interrupt log memory, `head` ring index, `cmp` completion, bus speed module parameter-derived hardware speed, and adapter retry count. Hardware persists descriptor base, interrupt cause location, descriptor size, retry policy, and speed timing until reinitialized.

Dependencies and integration points: integrates with PCI ids for multiple Intel SMT devices, ACPI companion/resource checks, DMA mapping/coherent APIs, MSI/INTx IRQ APIs, `i2c_add_adapter`, and SMBus core functionality flags including PEC.

Risks: descriptor and DMA buffer layout is hardware-sensitive, including 16-byte alignment of `priv->buffer`. I2C block read forces the address R/W bit to write per hardware spec, which is easy to regress. MSI and INTx have different interrupt acknowledgement semantics. Timeout kills the transaction but descriptor/ring state still advances after cleanup. Large-packet, CRC, collision, and timeout statuses map to distinct errno values.

Test signals: PCI probe on MSI-capable and INTx-only systems, every advertised SMBus protocol including PEC and block process call, I2C block read/write, DMA mapping failure, descriptor timeout and kill path, NAK/CRC/collision/large-packet/clock-low status translation, bus speed module parameter values 0/80/100/400/1000, and remove while adapter is registered.
