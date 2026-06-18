# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/Makefile

## Purpose
This Makefile builds the Cirrus DSP firmware support library and descends into the KUnit test directory.

## Important Targets
`obj-$(CONFIG_FW_CS_DSP) += cs_dsp.o` builds the production library. `obj-y += test/` always includes the test subdirectory in kbuild traversal, while the test subdirectory's own Makefile gates actual object inclusion on Kconfig test symbols.

## Control Flow, State, And Persistence
There is no runtime state. Build state flows from `CONFIG_FW_CS_DSP` into object inclusion and from parent traversal to the test Makefile.

## Dependencies And Integration Points
This file integrates with `drivers/firmware/cirrus/Kconfig` and with test module construction under `cirrus/test`. The unconditional test directory traversal keeps test object rules visible without forcing test compilation.

## Risks And Test Signals
Risk is limited to build-graph drift. Test with `FW_CS_DSP=n`, `FW_CS_DSP=y`, and KUnit-enabled configurations to confirm `cs_dsp.o` and test objects appear only under the intended symbols.
