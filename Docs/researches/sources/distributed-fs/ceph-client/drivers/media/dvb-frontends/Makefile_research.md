# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Makefile

## Purpose
This Makefile maps DVB frontend Kconfig symbols to kernel objects and subdirectories. It is the compilation index for the `drivers/media/dvb-frontends` directory.

## Important APIs, Types, And Build Contracts
The relevant object mappings are `CONFIG_DVB_A8293 -> a8293.o`, `CONFIG_DVB_AF9013 -> af9013.o`, `CONFIG_DVB_AF9033 -> af9033.o`, `CONFIG_DVB_AS102_FE -> as102_fe.o`, `CONFIG_DVB_ASCOT2E -> ascot2e.o`, `CONFIG_DVB_ATBM8830 -> atbm8830.o`, `CONFIG_DVB_AU8522 -> au8522_common.o`, `CONFIG_DVB_AU8522_DTV -> au8522_dig.o`, and `CONFIG_DVB_AU8522_V4L -> au8522_decoder.o`. The file adds `drivers/media/tuners/` to the include path for all objects and conditionally adds the DVB USB v2 include path for `CONFIG_DVB_RTL2832_SDR`.

## Control Flow And Integration
The build is flat for most drivers, with a few multi-object composites such as `cxd2820r`, `drxd`, `drxk`, `stb0899`, and `stv0900`. Entries are intended to remain sorted by Kconfig name. AU8522 demonstrates shared-object integration: common state helpers are compiled under `DVB_AU8522`, while the digital and analog entry points compile under separate Kconfig symbols.

## State, Persistence, And Dependencies
The Makefile has no runtime state. Its persistent effect is the generated object/module set selected by `.config`. The include-path choices affect all source files in the directory, so headers from tuner drivers are intentionally available.

## Risks
Missing object mappings make valid Kconfig symbols ineffective. Unsorted additions violate the local maintenance rule and can cause review churn. AU8522 object separation can break at link/load time if exported helpers in `au8522_common.o` are not built before either DTV or V4L consumers.

## Test Signals
Run targeted `make M=drivers/media/dvb-frontends` or full kernel module builds for the selected configs. Link errors around `au8522_*`, `af9013_*`, or `af9033_*` symbols are strong integration signals.
