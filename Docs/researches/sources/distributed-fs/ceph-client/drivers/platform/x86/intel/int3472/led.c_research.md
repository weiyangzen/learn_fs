<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/led.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/led.c

## Purpose
Registers GPIO-backed LED class devices for INT3472 privacy/strobe GPIOs and links them to camera sensor consumers.

## Important APIs, Types, And Functions
`int3472_led_set()` writes the brightness value to the GPIO. `skl_int3472_register_led()` creates a stable LED name from the sensor ACPI name and connection ID, registers an `led_classdev`, and adds an LED lookup for the sensor device. `skl_int3472_unregister_leds()` removes lookups, unregisters class devices, and releases GPIOs.

## Control Flow
`discrete.c` calls register for GPIO types privacy LED and strobe. The LED class callback controls the GPIO directly.

## State And Persistence
LED state is held in `int3472->leds[]` and the GPIO output state. Registered lookup entries persist until cleanup.

## Dependencies And Integration Points
Depends on LED class, GPIO descriptors, ACPI device names, and sensor driver LED lookup use.

## Risks And Test Signals
Risks are LED naming collisions, GPIO polarity mistakes, and missing lookup removal. Test LED sysfs brightness, sensor privacy LED lookup, and cleanup on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/led.c -->
