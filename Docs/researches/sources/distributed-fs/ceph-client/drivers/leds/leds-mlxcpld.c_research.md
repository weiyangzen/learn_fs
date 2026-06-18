# sources/distributed-fs/ceph-client/drivers/leds/leds-mlxcpld.c

Purpose: legacy Mellanox CPLD LED driver using LPC I/O port access and DMI-selected board profiles.

Important APIs/types/functions: profile arrays describe CPLD offsets, masks, base colors, defaults, and LED names. `mlxcpld_led_platform_check_sys_type()` selects default or MSN2100 profile by DMI product name. `mlxcpld_led_store_hw()` performs spinlocked nibble updates through `inb/outb`. Brightness and blink callbacks map LED class state to CPLD color codes.

Control flow: module init checks chassis vendor, creates a platform device, probes the driver once, allocates global private state, selects profile, registers each LED, and applies default-on LEDs. Blink accepts only off/on pairs for 3 Hz or 6 Hz, or defaults to 3 Hz when both delays are zero.

State and persistence: driver state is global `mlxcpld_led` plus LED profile data. Hardware state is CPLD register nibbles; no readback cache is maintained beyond register read-modify-write.

Dependencies and integration: depends on DMI, direct I/O port access, platform-device self-registration, LED class, and spinlock serialization.

Risks: global singleton design and manual platform-device lifecycle are fragile. Hard-coded LPC base and DMI profiles limit portability. `mlxcpld_led_exit()` assumes init/probe created global state. Blink only supports exact delay constants.

Test signals: DMI match and profile selection, I/O nibble polarity for high/low masks, default LED state writes, blink delay validation, and module load/unload on unsupported systems.
