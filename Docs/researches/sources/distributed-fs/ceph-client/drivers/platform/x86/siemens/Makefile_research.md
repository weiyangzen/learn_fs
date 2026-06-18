# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Makefile

Purpose: This Makefile maps Siemens SIMATIC IPC Kconfig symbols to object files for the central platform driver and CMOS battery monitor variants.

Important APIs, types, and functions: It builds `simatic-ipc.o`, `simatic-ipc-batt.o`, `simatic-ipc-batt-apollolake.o`, `simatic-ipc-batt-elkhartlake.o`, and `simatic-ipc-batt-f7188x.o` according to their `CONFIG_` symbols.

Control flow: Kbuild includes each object when the corresponding symbol is `y` or `m`. There are no composite objects in this file.

State and persistence: Build configuration is the only state; runtime state belongs to the compiled drivers.

Dependencies and integration points: The file integrates with Kbuild and the Kconfig symbols in the same directory.

Risks and edge cases: Object names must stay aligned with platform aliases and `request_module()`/softdep strings used by the source files. A rename here without matching module aliases would break automatic child-driver binding.

Test signals: Run targeted builds for each config symbol and confirm module filenames match Kconfig help and `MODULE_ALIAS("platform:" KBUILD_MODNAME)` expectations.
