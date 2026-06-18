<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/hardware.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/hardware.h

Purpose: declares X3PROTO baseboard GPIO capacity and gpio chip type.

Important APIs/types/functions: `NR_BASEBOARD_GPIOS` and forward declaration of `struct gpio_chip`.

Control flow: board GPIO code sizes its GPIO range from this constant.

State and persistence: GPIO state is owned by gpiolib and board registers elsewhere.

Dependencies/integration: integrates X3PROTO baseboard support with Linux gpiolib.

Risks: wrong GPIO count breaks descriptor allocation and IRQ mapping.

Test signals: probe all baseboard GPIOs and validate line numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-x3proto/mach/hardware.h -->
