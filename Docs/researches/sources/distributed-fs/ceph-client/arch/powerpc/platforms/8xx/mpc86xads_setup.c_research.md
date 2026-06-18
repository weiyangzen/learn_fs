# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c

### Purpose
MPC86xADS board setup. It configures CPM1 pins, maps board-control registers, publishes OF platform devices, and registers the 8xx machine descriptor.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `mpc866ads_pins[]`, `init_ioports()`, `mpc86xads_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(mpc86x_ads)` with compatible `fsl,mpc866ads`. It uses constants from `mpc86xads.h`.

### Control Flow
Setup applies CPM pin muxing, finds `fsl,mpc866ads-bcsr`, maps and writes board-control registers, and uses common 8xx callbacks for PIC, IRQ, time, RTC, and restart. Device publication occurs from a machine initcall.

### State, Persistence, And Dependencies
State includes CPM registers, BCSR MMIO settings, platform devices, and common 8xx machine state. No durable persistence. Dependencies include OF, CPM1, 8xx PIC/setup, and board constants.

### Integration Points
Connects MPC86xADS board-control and CPM pins to Linux serial/Ethernet/platform drivers.

### Risks
BCSR writes and pin muxes are board-critical. Missing BCSR node must be handled without crashing but may leave peripherals disabled.

### Test Signals
Boot MPC86xADS, verify console, Ethernet, BCSR-controlled devices, interrupts, timebase/RTC, restart, and platform-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/mpc86xads_setup.c -->
