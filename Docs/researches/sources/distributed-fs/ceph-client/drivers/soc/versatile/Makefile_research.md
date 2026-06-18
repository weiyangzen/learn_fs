# sources/distributed-fs/ceph-client/drivers/soc/versatile/Makefile

## Purpose
This Makefile maps Versatile-family SoC bus Kconfig symbols to their object files.

## Important APIs, Types, And Functions
It builds `soc-integrator.o` for `CONFIG_SOC_INTEGRATOR_CM` and `soc-realview.o` for `CONFIG_SOC_REALVIEW`.

## Control Flow
Kbuild includes each object according to its config symbol.

## State And Persistence
There is no runtime state. The only persistent effect is build object selection.

## Dependencies And Integration Points
It depends on the local Kconfig file and source filenames.

## Risks And Test Signals
Risks are symbol/file drift. Test signals are expected object inclusion under each config in build logs.
