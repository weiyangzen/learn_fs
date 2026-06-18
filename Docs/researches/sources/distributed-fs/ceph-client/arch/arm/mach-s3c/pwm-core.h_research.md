<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pwm-core.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pwm-core.h

### Purpose
Declares S3C64xx timer/PWM selection support for the Samsung PWM clocksource.

### Important APIs, Types, And Functions
`enum s3c64xx_timer_mode` names PWM timer channels. `s3c64xx_set_timer_source()` selects which timers are reserved for event/source clock roles.

### Control Flow
Board or DT map code calls the setter before `s3c64xx_timer_init()` initializes the PWM clocksource.

### State, Persistence, And Dependencies
The selected timer mask is stored in the S3C64xx PWM variant in `s3c64xx.c`. Dependencies include Samsung PWM clocksource support.

### Integration Points
Cragganmore and S3C64xx DT setup select PWM3/PWM4 before timer initialization.

### Risks
Choosing a timer used by board PWM consumers can conflict with backlight or other PWM users.

### Test Signals
Clocksource registration, timer interrupts, and PWM consumer availability validate the selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/pwm-core.h -->
