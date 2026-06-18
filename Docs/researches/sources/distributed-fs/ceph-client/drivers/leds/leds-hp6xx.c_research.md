# sources/distributed-fs/ceph-client/drivers/leds/leds-hp6xx.c

Purpose: board-specific LED driver for HP Jornada 6xx handhelds, exposing fixed red and green LEDs through direct SuperH/HD64461 I/O register operations.

Important APIs/types/functions: `hp6xxled_green_set()` reads/writes `PKDR` and toggles `PKDR_LED_GREEN`; `hp6xxled_red_set()` reads/writes `HD64461_GPBDR` and toggles `HD64461_GPBDR_LED_RED`. Two static `led_classdev`s define names, default triggers, brightness callbacks, and suspend/resume behavior.

Control flow: platform probe registers red then green classdevs with devm. Brightness callbacks perform read-modify-write on board registers; a nonzero value clears the active-low LED bit, and zero sets it.

State and persistence: no allocated driver state. Hardware register bits persist until another board component changes them or the system resets. LED core suspend/resume flag requests core handling around power transitions.

Dependencies/integration: architecture headers `<asm/hd64461.h>` and `<mach/hp6xx.h>`, platform device `"hp6xx-led"`, LED triggers `"hp6xx-charge"` and `"disk-activity"`.

Risks: direct I/O has no local locking, so concurrent register users could race read-modify-write operations. Static classdev instances mean this is intended for one board instance. Active-low semantics are embedded in callbacks.

Test signals: verify red/green registration, active-low bit behavior on real or emulated HP6xx hardware, default trigger binding, and suspend/resume LED core behavior.
