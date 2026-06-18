# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c

### Purpose
MPC885ADS board setup. It programs CPM1 pin muxing, board-control registers, optional FEC/PHY-related bits, platform-device publication, and machine callbacks.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `mpc885ads_pins[]`, `init_ioports()`, `mpc885ads_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(mpc885_ads)` with compatible `fsl,mpc885ads`. It uses `mpc885ads.h`, CPM1 helpers, OF node mapping, and shared 8xx callbacks.

### Control Flow
Setup initializes CPM pins/clocks, maps `fsl,mpc885ads-bcsr`, applies board-control values, and registers standard 8xx machine callbacks. A machine device initcall probes OF devices.

### State, Persistence, And Dependencies
State includes CPM register programming, BCSR MMIO bits, platform devices, PIC/timebase/RTC runtime state. No durable persistence. Dependencies include OF, CPM1, BCSR constants, and 8xx shared setup.

### Integration Points
Connects MPC885ADS hardware mux/control to Linux CPM, Ethernet, serial, and platform drivers.

### Risks
Pin tables and BCSR bits are board-specific. Incorrect ordering can break console or network before diagnostics are available.

### Test Signals
Boot MPC885ADS, validate serial, Ethernet/FEC, BCSR-controlled features, interrupts, RTC/timebase, restart, and platform-device probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc885ads_setup.c -->
