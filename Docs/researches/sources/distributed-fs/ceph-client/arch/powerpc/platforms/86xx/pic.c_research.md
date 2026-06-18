# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c

### Purpose
Common MPIC initialization for 86xx boards.

### Important APIs, Types, And Functions
Public `mpc86xx_init_irq()` locates the OpenPIC interrupt controller node, allocates an MPIC with appropriate flags, initializes it, and prepares the machine for `mpic_get_irq`.

### Control Flow
Board `init_IRQ` callbacks call this helper during early boot. It maps and initializes the interrupt controller before normal device interrupts are enabled.

### State, Persistence, And Dependencies
State is MPIC allocation, mapping, and interrupt-domain state. No durable persistence. Dependencies include OF interrupt-controller lookup, MPIC APIs, and PowerPC IRQ core.

### Integration Points
Shared by all 86xx machine descriptors that use MPIC as the root interrupt controller.

### Risks
OpenPIC node matching and MPIC flags must match hardware endianness and routing. A failed allocation blocks interrupt delivery.

### Test Signals
Boot each 86xx board and verify MPIC initialization logs, timer/device interrupts, and `mpic_get_irq` operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/pic.c -->
