# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.h

Purpose: declarations for Samsung legacy static platform devices and platform-data setters.

Important APIs/types/functions: declares exported `platform_device` objects for S3C devices and setter functions for framebuffer, SDHCI, I2C, and other board-configurable peripherals.

Control flow: no local flow; board files include this to register devices and attach platform data.

State and persistence: declarations refer to static device state defined in `devs.c` and related device files.

Dependencies and integration points: ties board files to legacy platform devices and Kconfig-selected definitions.

Risks: declaration must stay conditional-compatible with Kconfig, or board files hit link failures.

Test signals: compile coverage for boards using every declared device and successful platform registration.
