# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/Makefile

## Purpose
Maps Intel pinctrl Kconfig symbols to the object files that implement each driver. It is the build glue for the Intel pinctrl directory.

## Important APIs, Types, and Functions
The file uses standard kbuild `obj-$(CONFIG_...) += ...` assignments. It builds custom legacy drivers such as `pinctrl-baytrail.o` and `pinctrl-cherryview.o`, the shared core `pinctrl-intel.o`, the generic platform driver `pinctrl-intel-platform.o`, and descriptor drivers such as Alder Lake, Broxton, Cannon Lake, Cedar Fork, Denverton, Elkhart Lake, Emmitsburg, Gemini Lake, Ice Lake, Jasper Lake, Lakefield, Lewisburg, Meteor Lake, Meteor Point, Sunrise Point, and Tiger Lake.

## Control Flow
Kbuild evaluates the selected symbols from `.config`. Built-in selections compile into `drivers/pinctrl/intel/built-in.a`; modular selections produce loadable modules. Platform files that import the `PINCTRL_INTEL` namespace rely on `pinctrl-intel.o` being selected through Kconfig.

## State and Persistence Behavior
There is no runtime state. The Makefile controls persistent build artifacts and determines which driver init functions are linked or emitted as modules.

## Dependencies and Integration Points
Integrates with `drivers/pinctrl/Makefile`, the Intel Kconfig file, module namespace imports, and the C driver filenames. It must stay synchronized with Kconfig symbols and actual source files.

## Risks
A stale object mapping causes a selected driver not to build, or a removed file to break the build. Adding a descriptor driver without selecting `PINCTRL_INTEL` in Kconfig can compile the platform file without its shared core. Ordering is generally low risk, but missing the common core object affects all shared-core users.

## Test Signals
Builds with each Intel `CONFIG_PINCTRL_*` symbol as built-in and module, `make drivers/pinctrl/intel/`, module installation output, and absence of unknown-object or unresolved-symbol errors validate this file.
