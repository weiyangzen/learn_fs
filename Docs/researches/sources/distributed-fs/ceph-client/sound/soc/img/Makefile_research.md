# sources/distributed-fs/ceph-client/sound/soc/img/Makefile

Purpose: kbuild mapping for Imagination ASoC drivers.

Important APIs/types/functions: maps six Kconfig symbols to `img-i2s-in.o`, `img-i2s-out.o`, `img-parallel-out.o`, `img-spdif-in.o`, `img-spdif-out.o`, and `pistachio-internal-dac.o`.

Control flow: each driver object is compiled independently when its config is enabled.

State and persistence: no runtime state.

Dependencies/integration: paired with `img/Kconfig` and the driver source files in the same directory.

Risks: no aggregate object; object names must track source file names exactly.

Test signals: kbuild object inclusion for each config symbol.
