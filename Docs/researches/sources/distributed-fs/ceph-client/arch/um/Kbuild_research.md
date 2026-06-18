# sources/distributed-fs/ceph-client/arch/um/Kbuild

Purpose: top-level Kbuild fragment for User-Mode Linux architecture subdirectories.

Important APIs/targets: adds `kernel/`, `drivers/`, and `os-Linux/` to `obj-y`.

Control flow: kbuild descends into those UML subdirectories when building the architecture.

State and persistence: no runtime state.

Dependencies and integration points: integrates UML architecture core, drivers, and Linux-host OS support into the build.

Risks: removing or renaming a subdirectory entry drops large parts of UML from the build or causes unresolved symbols.

Test signals: UML `ARCH=um` build, link of kernel/driver/os-Linux objects, and booting a UML kernel.
