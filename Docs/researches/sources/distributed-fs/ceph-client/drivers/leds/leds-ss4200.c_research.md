# sources/distributed-fs/ceph-client/drivers/leds/leds-ss4200.c

Purpose: Intel SS4200-E and related NAS/Home Server LED driver using ICH7 LPC GPIO I/O registers. It exposes drive and power LEDs plus a custom `blink` sysfs attribute.

Important APIs, types, and functions: `struct nasgpio_led` maps LED names to GPIO bits and class devices. `ich7_lpc_probe()` discovers PM/GPIO bases through PCI config space and requests the GPIO I/O region. `ich7_gpio_init()` configures GPIO use/direction non-destructively. `nasgpio_led_set_brightness()` and `nasgpio_led_set_blink()` control `GP_LVL` and `GPO_BLINK`. `register_nasgpio_led()` registers each LED with `nasgpio_led_groups`.

Control flow: module init checks a DMI whitelist unless `nodetect` is set, registers the PCI driver, then registers every LED against the discovered PCI device. Brightness writes clear blink on off and set binary output based on `LED_HALF`. Blink supports only 500/500 ms hardware blink. Load also changes the power indicator to solid amber.

State and persistence: global I/O base, PCI device pointer, resource pointer, and static LED array hold module state. Hardware registers are the persistent state. A spinlock protects port read-modify-write sequences.

Dependencies and integration points: DMI, PCI, x86 I/O port access, LED class, device attributes, and ICH7-specific register layout. It is not a conventional platform driver and assumes one supported NAS device.

Risks and test signals: risks include false-positive DMI/nodetect binding, global singleton state, direct I/O port programming, and partial LED registration cleanup. Tests should cover DMI gating, PCI resource failure paths, blink sysfs read/write, off clearing blink, module unload cleanup, and real GPIO polarity.
