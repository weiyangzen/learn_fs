# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7734.c

Purpose: registers SH7734 PFC and GPIO register windows with the PFC core.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7734`. `sh7734_pfc_resources` contains a PFC range `0xfffc0000-0xfffc011c` and GPIO range `0xffc40000-0xffc4502b`.

Control flow: the arch initcall publishes both resource ranges, allowing the PFC driver to manage function selection and GPIO controller registers.

State and persistence: local state is immutable resource metadata. Persistent state is hardware pin configuration and GPIO register contents.

Dependencies and integration points: integrates with `<cpu/pfc.h>` and SH7734 platform setup for SCIF, TMU, RTC, I2C, and external interrupt pin routing.

Risks: two distinct MMIO windows must remain in the expected order. The PFC driver likely assumes index 0 is PFC and index 1 is GPIO.

Test signals: probe should claim both ranges; GPIO and PFC debug output should expose SH7734 pins; external IRQ pin modes selected in `setup-sh7734.c` should work.
