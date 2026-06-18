<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/led.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/led.c

## Purpose
Creates a `leds-gpio` platform device for known Bay Trail/Cherry Trail tablets whose AtomISP2 camera LED GPIO is not described by ACPI. The immediate goal is to force LEDs off at boot and expose them via the LED class.

## Important APIs, Types, And Functions
Uses `struct gpio_led`, `gpio_led_platform_data`, DMI matching, and `gpiod_lookup_table`. Lookup tables map ASUS T100TA/T200TA and T100CHI systems to specific `INT33FC` GPIO pins. `atomisp2_led_init()` performs DMI selection, adds the lookup table, and registers the `leds-gpio` device.

## Control Flow
Module init exits with `-ENODEV` unless the DMI table matches. On match it installs the GPIO lookup table, then registers `leds-gpio` with one LED named `atomisp2::camera` and default state off. Exit unregisters the platform device and lookup table.

## State And Persistence
Global pointers track the active lookup table and platform device. Hardware GPIO/LED state persists through the GPIO and LED framework after registration.

## Dependencies And Integration Points
Depends on DMI, GPIO consumer machine lookups, platform devices, and `leds-gpio`. Soft-depends on `asus_nb_wmi` so this driver can turn off LEDs after ASUS WMI firmware methods turn them on.

## Risks And Test Signals
Risks are wrong DMI matches, wrong GPIO controller/pin indexes, and load order. Test on listed ASUS devices by checking that the LED is off after boot, appears under LED sysfs, and toggles only the camera LED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/led.c -->
