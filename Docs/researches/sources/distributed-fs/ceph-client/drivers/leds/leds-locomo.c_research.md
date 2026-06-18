# sources/distributed-fs/ceph-client/drivers/leds/leds-locomo.c

Purpose: Locomo companion-chip LED driver for older Sharp/Zaurus-style platforms, exposing fixed amber charge and green mail LEDs.

Important APIs/types/functions: `locomoled_brightness_set()` writes `LOCOMO_LPT_TOFH` or `LOCOMO_LPT_TOFL` to one Locomo LED pulse/toggle register offset under local IRQ masking. Wrapper callbacks bind offsets `LOCOMO_LPT0` and `LOCOMO_LPT1`. A `locomo_driver` registers against `LOCOMO_DEVID_LED`.

Control flow: module init registers the Locomo driver. Probe registers two static LED classdevs with devm. Brightness nonzero writes the high command; zero writes the low command.

State and persistence: no private allocation; classdevs are static. Hardware Locomo registers hold output state. Local IRQ masking protects the small MMIO sequence from interruption on the local CPU.

Dependencies/integration: Locomo bus/device model, architecture Locomo accessors, LED triggers `"main-battery-charging"` and `"nand-disk"`.

Risks: static classdevs imply a single Locomo LED device. There is no module exit/unregister in this file, consistent with older bus code but relevant for unloadability. No locking beyond local IRQ masking.

Test signals: Locomo device binding, amber/green classdev registration, MMIO offsets and values for ON/OFF, default trigger attachment, and module init behavior.
