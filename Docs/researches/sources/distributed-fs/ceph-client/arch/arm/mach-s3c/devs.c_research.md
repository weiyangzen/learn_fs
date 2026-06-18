# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.c

Purpose: legacy Samsung static platform device definitions for framebuffer, MMC/SDHCI, I2C, USB, keypad, PWM, SPI, and related controllers.

Important APIs/types/functions: exports devices such as `s3c_device_fb`, `s3c_device_hsmmc*`, `s3c_device_i2c*`, and platform-data setters including `s3c_fb_set_platdata()`, `s3c_sdhci*_set_platdata()`, and `s3c_i2c*_set_platdata()`.

Control flow: board code selects devices and calls setters to clone board platform data into static `platform_device` structures before registration. Default I2C data is used when callers pass NULL, and GPIO config callbacks are filled if missing.

State and persistence: static resources encode MMIO/IRQ/DMA masks; setter functions allocate/copy platform data into devices. No disk persistence.

Dependencies and integration points: integrates many Samsung legacy drivers with map/IRQ constants, GPIO mux helpers, and platform data headers.

Risks: platform-data copying and defaulting can hide missing board setup. Static resource definitions must match SoC variant and Kconfig-selected device availability.

Test signals: legacy board boot with each selected device probing, resource conflicts, I2C bus numbering, SDHCI card detection, framebuffer IRQs, and USB/keypad/PWM/SPI operation.
