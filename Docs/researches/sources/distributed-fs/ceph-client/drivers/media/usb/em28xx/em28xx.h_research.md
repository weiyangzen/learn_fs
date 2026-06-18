# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx.h

Purpose: defines the shared em28xx driver contract: board IDs, buffer types, board metadata, video/audio/I2C/device state structures, extension operations, and cross-module prototypes.

Important APIs/types/functions: `struct em28xx` is the central device object with kref, submodule pointers, board identity, flags, I2C adapters/clients, V4L2 routing state, locks, resources, EEPROM data, DMA queues, USB endpoint/altsetting state, low-level register callbacks, button state, media entities, and dual-TS linkage. `struct em28xx_v4l2`, `struct em28xx_audio`, `struct em28xx_usb_ctl`, `struct em28xx_buffer`, `struct em28xx_board`, `struct em28xx_input`, `struct em28xx_led`, and `struct em28xx_button` define submodule contracts. `struct em28xx_ops` provides extension init/fini/suspend/resume registration.

Control flow: this header does not execute code except `ac97_return_record_select()`, but it shapes all module interactions. Core/cards allocate and identify `struct em28xx`, then extension modules register `struct em28xx_ops`; the core invokes extension lifecycle callbacks. Video, DVB, audio, and input modules share queues, locks, bridge mode, I2C adapters, and board GPIO/input metadata through this header.

State and persistence: most driver state is declared here. Long-lived state includes krefs, `devlist`, EEPROM buffers/hashes, current mode, selected input/audio/frequency, USB transfer buffers, active vb2 buffers, I2C bus selection, device disconnect flag, and per-extension pointers. Hardware state is represented by register callback operations and board GPIO sequences.

Dependencies and integration points: includes Linux workqueue/I2C/mutex/kref/V4L2/vb2/rc-core headers plus tuner helper headers and `em28xx-reg.h`. It declares functions from `em28xx-core.c`, `em28xx-cards.c`, `em28xx-camera.c`, and `em28xx-i2c.c`, making it the primary compile-time integration point for the driver family.

Risks: because many fields are shared across interrupt, workqueue, file operation, and disconnect contexts, locking discipline is critical. Bitfield capability flags and board tables must stay consistent with actual hardware. `INPUT(nr)` depends on a local variable named `dev`, which is convenient but fragile in new call sites. Tests are mostly build and integration signals: compile all module combinations, probe representative boards, validate extension load/unload order, check kref release on disconnect with open fds, and run V4L2/DVB/input/audio smoke tests.
