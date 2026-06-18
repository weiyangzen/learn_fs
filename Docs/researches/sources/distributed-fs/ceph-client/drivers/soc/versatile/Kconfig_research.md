# sources/distributed-fs/ceph-client/drivers/soc/versatile/Kconfig

## Purpose
This Kconfig file defines build symbols for ARM Integrator core module and ARM RealView SoC bus identity drivers.

## Important APIs, Types, And Functions
It defines `SOC_INTEGRATOR_CM` and `SOC_REALVIEW`, both bool options depending on their respective architectures or `COMPILE_TEST`, and both selecting `SOC_BUS`.

## Control Flow
Selection of each symbol controls whether the corresponding Makefile object is built. There is no runtime control flow here.

## State And Persistence
Configuration state persists in `.config` and determines built-in driver availability.

## Dependencies And Integration Points
The symbols integrate with `soc-integrator.c`, `soc-realview.c`, and Linux SoC bus support.

## Risks And Test Signals
Risks are limited to build dependency drift. Test signals are successful COMPILE_TEST builds and correct object inclusion when each symbol is enabled.
