# sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Makefile

## Purpose
This Makefile connects the Atmel wireless Kconfig symbol to the kernel build system. Its only build rule compiles and links the Atmel `at76c50x` USB wireless driver object when `CONFIG_AT76C50X_USB` is enabled.

## Important APIs, Types, and Targets
- SPDX license line: `GPL-2.0-only`.
- `obj-$(CONFIG_AT76C50X_USB) += at76c50x-usb.o`
  - If `CONFIG_AT76C50X_USB=y`, `at76c50x-usb.o` is built into the kernel image.
  - If `CONFIG_AT76C50X_USB=m`, it is built as a loadable module.
  - If the symbol is unset, no object is built from this directory entry.

## Control Flow
The kernel kbuild system expands `obj-y` and `obj-m` from the `obj-$(CONFIG_...)` assignment. There is no imperative flow in this file. Build behavior is entirely determined by the value selected through `drivers/net/wireless/atmel/Kconfig`.

## State and Persistence
The Makefile has no runtime state. Build state is represented by generated object files, modules, and dependency files in the kernel build output directory. Source state is a single declarative object mapping.

## Dependencies and Integration Points
- Consumes `CONFIG_AT76C50X_USB` defined in the adjacent Kconfig file.
- Integrates with the parent wireless Makefile through normal recursive kbuild directory traversal.
- The object name implies a companion source file `at76c50x-usb.c` in the same directory, built under mac80211/USB dependencies from Kconfig.

## Risks and Edge Cases
- If the object filename drifts from the actual source/module name, enabling `CONFIG_AT76C50X_USB` fails at build time.
- Dependency correctness lives in Kconfig, not this Makefile; adding objects here without updating Kconfig can expose build failures under incomplete configurations.
- Since there is only one object, any future split into multiple compilation units must preserve the module composition expected by kbuild.

## Test Signals
- `CONFIG_AT76C50X_USB=y` should include `at76c50x-usb.o` in built-in wireless objects.
- `CONFIG_AT76C50X_USB=m` should produce an `at76c50x-usb.ko` module.
- `CONFIG_AT76C50X_USB=n` should not build the object.
