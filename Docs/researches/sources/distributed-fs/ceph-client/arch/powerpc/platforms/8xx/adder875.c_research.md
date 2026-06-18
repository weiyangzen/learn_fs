# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c

### Purpose
Adder875 MPC8xx board support. It initializes board-specific CPM1 pins, platform devices, and machine callbacks for a PQ1/8xx system.

### Important APIs, Types, And Functions
The file defines a CPM pin table, an `init_ioports()` helper, board setup, platform-device publication, and a `define_machine()` descriptor. It relies on `cpm1_set_pin()`, `cpm1_clk_setup()` where needed, `mpc8xx_pic_init()`, `mpc8xx_get_irq()`, `mpc8xx_calibrate_decr()`, RTC helpers, and restart support from shared 8xx code.

### Control Flow
Machine setup applies pin muxing, initializes CPM and board peripherals, then platform devices are published from the board initcall. The machine descriptor routes interrupts through the 8xx SIU PIC.

### State, Persistence, And Dependencies
State is CPM pin/register programming, PIC state, platform devices, and board setup side effects. No durable data is written. Dependencies include OF, CPM1, 8xx PIC, and common `m8xx_setup.c` helpers.

### Integration Points
Connects board pin muxing and device-tree buses to CPM/serial/Ethernet/platform drivers.

### Risks
Pin tables are hardware-specific and easy to regress. Wrong interrupt callbacks or timebase setup prevent stable boot.

### Test Signals
Boot Adder875 DTB, verify serial/Ethernet pins, interrupts, RTC/timebase, restart path, and platform-device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/adder875.c -->
