# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Kconfig

## Purpose
This Kconfig fragment declares the `DVB_DRX39XYJ` frontend option for Micronas DRX-J demodulators, specifically the DRX39xx family such as `drx3933j`.

## Important APIs, Types, and Functions
The single symbol is `config DVB_DRX39XYJ`, a tristate named "Micronas DRX-J demodulator". It depends on `DVB_CORE` and `I2C`, defaults to module when `MEDIA_SUBDRV_AUTOSELECT` is disabled, and documents support for ATSC 8VSB plus QAM64/256 tuner modules.

## Control Flow
Kernel configuration selects this symbol directly or through media subdriver autoselection. The symbol controls compilation of the `drx39xyj` object from the local Makefile and enables the reachable attach declaration in `drx39xxj.h`.

## State and Persistence
Kconfig contributes build-time state only. There is no runtime state or persistence.

## Dependencies and Integration Points
The option integrates with the media DVB frontend menu, DVB core, I2C subsystem, the local Makefile, and callers that use `IS_REACHABLE(CONFIG_DVB_DRX39XYJ)`.

## Risks and Edge Cases
If the symbol is disabled, attach callers receive a `NULL` inline stub. The help text mentions a tuner module even though this directory builds a demodulator frontend, which may confuse configuration review. Missing `I2C` or `DVB_CORE` correctly prevents selection.

## Test Signals
Build test `y`, `m`, and disabled configurations; verify `drx39xyj.o` is produced when enabled and callers handle the disabled attach stub.
