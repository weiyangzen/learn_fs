# sources/distributed-fs/ceph-client/drivers/firmware/meson/Kconfig

Purpose: Defines the Amlogic Meson secure monitor driver configuration.

Important APIs/types/functions: `MESON_SM` is a tristate depending on `ARCH_MESON || COMPILE_TEST`, defaulting on Meson, and requiring `ARM64_4K_PAGES`.

Control flow: No runtime flow. It controls whether `meson_sm.o` is compiled.

State and persistence behavior: No state. The setting determines availability of secure monitor calls and exported helpers for efuse/chip-id/power control consumers.

Dependencies and integration points: Coordinates with ARM64 page-size constraints and the Meson firmware subsystem.

Risks and test signals: The 4K page dependency matters because secure monitor shared memory mapping assumptions may not hold for other page sizes. Test Meson defconfig, allmodconfig, and compile-test coverage.
