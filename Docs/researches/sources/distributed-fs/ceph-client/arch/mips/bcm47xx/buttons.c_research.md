## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/buttons.c

Purpose: maps detected BCM47XX board models to GPIO-backed input buttons and registers a `gpio-keys` platform device. It covers many Asus, Belkin, Buffalo, Dell, D-Link, Huawei, Linksys, Luxul, Microsoft, Motorola, Netgear, and SimpleTech boards.

Important APIs and functions: `bcm47xx_buttons_register()` is the board-specific registration entry. `bcm47xx_buttons_copy()` duplicates `__initconst` button arrays into normal memory with `kmemdup()`. Macros `BCM47XX_GPIO_KEY()` and `BCM47XX_GPIO_KEY_H()` define active-low and active-high `gpio_keys_button` entries. Static arrays encode GPIO numbers and Linux input key codes such as `KEY_RESTART`, `KEY_WPS_BUTTON`, `KEY_RFKILL`, `BTN_0`, and `KEY_POWER`.

Control flow: registration reads `bcm47xx_board_get()`, switches on the enum, copies the matching static button array into `bcm47xx_button_pdata`, and registers `bcm47xx_buttons_gpio_keys`. Unsupported boards log debug and return `-ENOTSUPP`; allocation failure returns `-ENOMEM`; platform device registration errors are logged and returned.

State and persistence: copied button data is retained for the lifetime of the platform device. GPIO input events are runtime-only. No persistent storage is written.

Dependencies and integration: depends on board detection from `board.c`, Linux `gpio-keys`, input key codes, platform device core, and BCM47XX GPIO providers from SSB/BCMA support.

Risks: the switch table must stay synchronized with board detection enums. Wrong active polarity or GPIO numbers can cause stuck keys or missing reset/WPS behavior. Some arrays lack `__initconst` annotations while most have them, which is not functional but inconsistent. No cleanup path frees copied data if platform registration fails after allocation.

Test signals: `/proc/bus/input/devices` or evdev should show gpio-keys on supported boards. Pressing reset/WPS/RF kill/mode buttons should emit expected key codes and polarity. Unsupported boards should fail gracefully without a bogus gpio-keys device.
