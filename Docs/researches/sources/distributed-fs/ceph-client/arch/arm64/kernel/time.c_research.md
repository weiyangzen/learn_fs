## sources/distributed-fs/ceph-client/arch/arm64/kernel/time.c

### Purpose
`time.c` initializes ARM64 timer infrastructure and implements `profile_pc` support for timer-based profiling.

### Important APIs, Types, And Functions
It exports `profile_pc` and defines `time_init`. The helper `profile_pc_cb` skips lock functions while walking the stack.

### Control Flow
`profile_pc` walks the current stack from the supplied regs until it finds a non-lock-function PC and returns it for profiling. `time_init` initializes clocks from firmware, probes timers, sets up hrtimer tick broadcast, verifies the architected timer rate, calibrates `lpj_fine`, and initializes paravirtual time.

### State, Persistence, And Dependencies
State includes global clocksource/clockevent registration, tick broadcast setup, `lpj_fine`, and paravirtual time state. The file itself does not persist data.

### Integration Points
It depends on OF clock setup, ACPI/DT timer probing, generic clocksource/clockevents, stack unwinding, profiling, and ARM64 paravirtual time.

### Risks
A missing architected timer rate panics the kernel. Bad stack unwinding can skew profiling. Timer initialization order affects scheduler ticks, delay calibration, and vDSO timekeeping.

### Test Signals
Boot DT and ACPI platforms, verify timer frequency and delay calibration, run high-resolution timer/tick broadcast tests, paravirtual time tests, and profiling samples inside lock-heavy paths.
