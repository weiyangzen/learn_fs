# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c

### Purpose
Embedded Planet EP88xC board support for MPC8xx. It configures CPM1 pins, board-control registers, and OF platform-device publication.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `ep88xc_pins[]`, `init_ioports()`, `ep88xc_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(ep88xc)` with compatible `fsl,ep88xc`. It maps `fsl,ep88xc-bcsr`, applies CPM1 pin/clock helpers, and publishes `soc`/`simple-bus` style devices.

### Control Flow
Setup applies CPM I/O pin muxing, maps board-control registers if present, and performs board-specific initialization. A machine device initcall publishes platform devices.

### State, Persistence, And Dependencies
State includes CPM pin/clock registers, BCSR MMIO settings, PIC/timebase machine callbacks, and platform devices. No durable persistence. Dependencies include OF, CPM1, 8xx common setup, and platform probing.

### Integration Points
Connects EP88xC board pins and control registers to serial/Ethernet/platform drivers.

### Risks
Pin table and BCSR values are board-specific. Incorrect muxing can disable console or network.

### Test Signals
Boot EP88xC DTB, verify serial console, Ethernet, BCSR-controlled peripherals, interrupts, and platform-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/ep88xc.c -->
