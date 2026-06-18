## sources/distributed-fs/ceph-client/drivers/acpi/apei/Makefile

Purpose: this `Makefile` maps APEI kernel configuration symbols to object files and composes multi-object built-ins/modules for ACPI Platform Error Interface support.

Important build rules: `obj-$(CONFIG_ACPI_APEI) += apei.o` builds the base aggregate. `obj-$(CONFIG_ACPI_APEI_GHES) += ghes.o` builds GHES. A conditional disables KASAN instrumentation for `ghes.o` when compile-testing with older Clang versions below 18. `obj-$(CONFIG_ACPI_APEI_PCIEAER) += ghes_helpers.o`, `obj-$(CONFIG_ACPI_APEI_EINJ) += einj.o`, `obj-$(CONFIG_ACPI_APEI_ERST_DEBUG) += erst-dbg.o`, and `obj-$(CONFIG_ACPI_APEI_GHES_NVIDIA) += ghes-nvidia.o` add optional pieces. `einj-y` is `einj-core.o` plus optional `einj-cxl.o`; `apei-y` is `apei-base.o hest.o erst.o bert.o`.

Control flow: there is no runtime control flow, but the build composition controls which translation units are linked into each feature object.

State and dependencies: build-time state comes from Kconfig symbols and the `clang-min-version` helper. Runtime state is defined in compiled C files, not here.

Integration points: Kconfig selects symbols; this file turns them into the actual APEI base, GHES, EINJ, ERST debug, and vendor handler objects linked into the kernel.

Risks: object composition affects symbol availability. The Clang/KASAN workaround indicates `ghes.o` stack use or instrumentation sensitivity under older compilers. Missing optional object inclusion would silently drop feature support despite config prompts.

Test signals: build `CONFIG_ACPI_APEI` base, GHES with old/new Clang compile-test KASAN conditions, EINJ with and without CXL, ERST debug as module, NVIDIA handler as module, and all features disabled.
