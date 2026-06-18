# sources/distributed-fs/ceph-client/arch/parisc/math-emu/Makefile

Purpose: defines the PA-RISC floating-point emulation object list and compiler flags. It builds the dispatcher, exception decoder, denormal support, double/single arithmetic, fused operations, conversions, and comparison helpers.

Important APIs/types/functions: `ccflags-y` suppresses warnings expected from old PA-RISC math-emulation code, including implicit declarations, old-style definitions, and missing prototypes. `obj-y` always includes `frnd.o`, `driver.o`, `decode_exc.o`, `fpudispatch.o`, `denormal.o`, arithmetic objects, conversion objects, and compare objects. `obj-$(CONFIG_MATH_EMULATION)` adds `unimplemented-math-emulation.o`.

Control flow: Kbuild consumes the object variables. `CFLAGS_REMOVE_fpudispatch.o = -Wimplicit-fallthrough` relaxes one warning setting for the large dispatcher.

State and dependencies: no runtime state. Depends on PA-RISC arch Kbuild and `CONFIG_MATH_EMULATION`.

Risks: the warning suppressions can hide real type/prototype regressions. The comment says full math emulation is needed only for very old or stripped-down CPUs and not currently supported, so build-time inclusion may not imply a fully supported runtime configuration.

Test signals: PA-RISC allmodconfig/defconfig builds with and without `CONFIG_MATH_EMULATION`, warning-budget checks after changing prototypes, and boot tests on hardware or emulators that enter the FPU exception path.
