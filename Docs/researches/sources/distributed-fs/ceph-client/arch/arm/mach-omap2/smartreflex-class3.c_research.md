# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/smartreflex-class3.c

## Purpose
Registers SmartReflex Class 3 behavior for OMAP voltage adaptation using error generation and the voltage processor.

## APIs, Flow, And State
Static callbacks implement `enable`, `disable`, and `configure` for `struct omap_sr_class_data`. Enable reads the current voltage from the voltage domain, refuses with `-ENODATA` if unknown, enables the voltage processor, then calls `sr_enable(sr, volt)`. Disable turns off SR error generation, disables the VP, disables SR, and optionally resets the voltage domain. Configure delegates to `sr_configure_errgen()`. `sr_class3_init()` registers the class at OMAP late init.

## Dependencies And Integration
Depends on Linux SmartReflex APIs, OMAP SoC initcall gating, and OMAP voltage-domain/VP helpers. It integrates with SmartReflex core registration through `sr_register_class()`.

## Risks And Test Signals
Enabling without a known voltage is blocked, but VP/SR sequencing still affects live voltage control. Test signals are late init registration, SmartReflex enable/disable cycles, voltage reset behavior, and no warnings about unknown current voltage during normal operation.
