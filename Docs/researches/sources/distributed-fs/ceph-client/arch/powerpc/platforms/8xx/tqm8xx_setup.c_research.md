# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c

### Purpose
TQM8xx board support. It configures CPM1 pin muxing, optional FEC pins based on device-tree properties, platform-device publication, and standard 8xx machine callbacks.

### Important APIs, Types, And Functions
Defines `struct cpm_pin`, `tqm8xx_pins[]`, `tqm8xx_fec_pins[]`, `init_pins()`, `init_ioports()`, `tqm8xx_setup_arch()`, `declare_of_platform_devices()`, and `define_machine(tqm8xx)` with compatible `tqc,tqm8xx`.

### Control Flow
Setup applies baseline CPM pins, conditionally applies FEC pins when a matching DT property/device indicates Ethernet use, then common machine callbacks handle PIC, timebase, RTC, and restart. Device publication occurs from a machine initcall.

### State, Persistence, And Dependencies
State includes CPM pin/clock registers, platform devices, and common 8xx runtime state. No durable persistence. Dependencies include OF properties, CPM1, 8xx PIC/setup, and platform probing.

### Integration Points
Connects TQM8xx board muxing to CPM serial/Ethernet drivers and OF platform devices.

### Risks
Conditional FEC pin logic can break Ethernet if DT properties change. Console pins must remain configured early enough.

### Test Signals
Boot TQM8xx with and without FEC nodes/properties, validate serial, Ethernet, interrupts, RTC/timebase, restart, and platform-device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/tqm8xx_setup.c -->
