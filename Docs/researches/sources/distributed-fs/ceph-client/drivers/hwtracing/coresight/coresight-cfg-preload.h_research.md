# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.h

## Purpose
`coresight-cfg-preload.h` declares the built-in CoreSight configuration and feature descriptors that can be preloaded by the syscfg subsystem.

## Important APIs, Types, And Functions
Under `CONFIG_CORESIGHT_SOURCE_ETM4X`, it declares the ETMv4 feature descriptors `strobe_etm4x` and `gen_etrig_etm4x`, plus configuration descriptors `afdo_etm4x` and `pstop_etm4x`. There are no functions or types defined in this header.

## Control Flow
The header affects compile-time visibility only. `coresight-cfg-preload.c` includes it to populate preload arrays with descriptors from `coresight-cfg-afdo.c` and `coresight-cfg-pstop.c`.

## State And Persistence
There is no direct state. The declared symbols refer to static descriptor objects in their defining C files.

## Dependencies And Integration Points
The header relies on the ETMv4 source Kconfig guard to keep declarations aligned with descriptor definitions. It is part of the preload integration contract between built-in descriptor providers and the syscfg loader.

## Risks
The header has no include guard in this source copy; repeated inclusion is currently harmless because it only contains extern declarations under a Kconfig guard, but an include guard would reduce future fragility. Any mismatch between declarations and definitions would break builds.

## Test Signals
Build testing with ETMv4 enabled and disabled is the primary signal. Preload tests indirectly exercise these declarations by verifying all declared descriptors are loadable.
