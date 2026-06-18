# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.h

Purpose: declaration and configuration wrapper for USB Gecko udbg initialization.

Important APIs and control flow: when `CONFIG_USBGECKO_UDBG` is enabled, declares `ug_udbg_init`; otherwise provides an empty inline. Always declares `udbg_init_usbgecko` for early debug builds.

State, dependencies, and risks: state is owned by `usbgecko_udbg.c`; the header controls whether board code calls a real initializer. Dependencies are Kconfig selection and early-debug build paths. Risks are unresolved early-debug symbols if platform constraints are wrong and silent no-op final debug when the option is off. Test signals are compile coverage for enabled/disabled USB Gecko udbg and early debug configurations.
