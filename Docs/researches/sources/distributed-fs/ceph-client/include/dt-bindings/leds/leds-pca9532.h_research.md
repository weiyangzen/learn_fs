<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca9532.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca9532.h

## Purpose
This header defines child output type constants for PCA9532 LED/GPIO bindings.

## Important APIs, types, and functions
It exports `PCA9532_TYPE_NONE`, `PCA9532_TYPE_LED`, `PCA9532_TYPE_N2100_BEEP`, `PCA9532_TYPE_GPIO`, and `PCA9532_LED_TIMER2`.

## Control flow
DTS child nodes use these constants to classify each PCA9532 output. The driver uses the value to decide whether to register an LED, expose a GPIO, ignore a pin, or apply board-specific beep/timer behavior.

## State and persistence
No state lives in the header. Values persist in DTB configuration and affect runtime device registration.

## Dependencies and integration points
It integrates with PCA9532 LED controller support, GPIO registration, LED timer hardware, and legacy N2100 board beep behavior.

## Risks and test signals
Risks include classifying an output incorrectly, which can expose the wrong kernel interface or drive the wrong pin. Test signals include DTS validation, LED registration, GPIO line tests, beep output tests where applicable, and timer2 blink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca9532.h -->
