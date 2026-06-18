# sources/distributed-fs/ceph-client/drivers/mfd/iqs62x.c

Purpose: I2C MFD core for Azoteq IQS620A/621/622/624/625 sensors. It identifies calibrated device variants, optionally parses vendor firmware records, initializes event masks and ATI, broadcasts sensor events through a notifier chain, and registers keys/ALS/PWM/temp/position children.

Important APIs/types/functions: `iqs62x_probe()`, `iqs62x_firmware_parse()`, `iqs62x_dev_init()`, `iqs62x_irq()`, `iqs62x_firmware_load()`, exported `iqs62x_events`, `iqs62x_devs`, and `struct iqs62x_core`.

Control flow: probe initializes regmap and completions, reads product/software/hardware IDs, selects a descriptor after calibration checks, then requests firmware asynchronously. Firmware load parses records into write blocks, initializes registers, requests threaded IRQ, waits for ATI completion, and adds descriptor-specific children. IRQ reads the whole event window, maps bytes to event flags/data, handles reset/ATI, and notifies subscribers.

State and persistence: keeps firmware block list, device descriptor, UI selection, event cache, completions for firmware and ATI, notifier head, and hardware revision numbers. Power management waits for firmware completion and switches halt/normal modes.

Dependencies and integration: depends on firmware loader, regmap I2C, OF compatibles, notifier chain, MFD children, and `linux/mfd/iqs62x.h` event definitions used by child drivers.

Risks: async firmware means remove/suspend must wait for completion. Firmware parser bounds and product checks protect against bad blobs. ATI timing and communication-window delays are hardware-sensitive. Reset during IRQ reinitializes registers and may drop concurrent events.

Test signals: product/calibration detection, missing/invalid firmware paths, ATI completion timeout, notifier events to key/ALS/position children, reset recovery, suspend/resume power mode changes, and OF child compatibility.
