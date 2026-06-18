# sources/distributed-fs/ceph-client/include/linux/leds-pca9532.h

Purpose: defines LED class and platform data structures for the PCA9532 16-channel LED/GPIO controller.

Important APIs and types: `enum pca9532_state` covers off/on/PWM0/PWM1/keep. `struct pca9532_led` includes channel id, I2C client, name/default trigger, embedded `led_classdev`, work item, type, and state. `struct pca9532_platform_data` carries sixteen LED descriptors, two PWM duty values, two prescalers, and GPIO base.

Control flow: driver probe consumes platform/DT data, registers LED class devices, and uses work items for asynchronous state updates to the I2C controller.

State and persistence: current state is cached per LED and reflected in hardware registers. Platform PWM/prescaler defaults are static.

Dependencies and integration points: depends on LED core, workqueues, I2C client declarations, and DT binding constants. Integrates LED and optional GPIO-style use of the PCA9532.

Risks and test signals: risks include channel count/order mistakes, asynchronous work after remove, PWM state sharing, and `PCA9532_KEEP` handling. Test all 16 channels, PWM0/PWM1 groups, trigger interaction, remove/cancel work, and GPIO base behavior.
