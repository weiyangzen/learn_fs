<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.c

### Purpose
Provides common non-DT S3C64xx initialization: early I/O maps, CPU table, UART setup, PWM timer setup, core device registration, VIC initialization, and external interrupt demuxing.

### Important APIs, Types, And Functions
Public functions include `s3c64xx_set_xtal_freq()`, `s3c64xx_set_xusbxti_freq()`, `s3c64xx_set_timer_source()`, `s3c64xx_timer_init()`, `s3c64xx_init_io()`, and `s3c64xx_init_irq()`. Internal IRQ functions include `s3c_irq_eint_mask()`, `s3c_irq_eint_unmask()`, `s3c_irq_eint_ack()`, `s3c_irq_eint_set_type()`, demux handlers for EINT groups, and `s3c64xx_init_irq_eint()`.

### Control Flow
Board map code calls `s3c64xx_init_io()` to install static maps, detect CPU ID, initialize CPU-specific hooks, and register PWM platform data. Timer init calls Samsung PWM clocksource setup. IRQ init initializes the two ARM VICs after clock init. An arch initcall registers EINT0-27 as child IRQs and attaches chained handlers to grouped VIC lines on non-DT S3C64xx boots.

### State, Persistence, And Dependencies
State includes early crystal frequency globals, CPU table, static `map_desc` entries, the PWM variant, subsystem device, and IRQ chip registrations. Dependencies include ARM VIC irqchip, Samsung clock/PWM/GPIO code, OF detection, and S3C64xx map/register headers.

### Integration Points
Legacy board files call this during machine setup. DT machines use only selected common mapping/timer helpers while pinctrl handles EINT.

### Risks
Static MMIO mapping must match hardware. EINT type setup uses bank-specific pin mux rules for GPN/GPL/GPM; mistakes break GPIO interrupts. The platform is marked deprecated and scheduled for removal without maintainer feedback.

### Test Signals
Boot logs, clocksource operation, VIC IRQ delivery, EINT trigger-type tests, GPIO interrupt demuxing, and S3C6410 board boot validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/s3c64xx.c -->
