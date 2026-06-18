# sources/distributed-fs/ceph-client/arch/sparc/lib/Makefile

Purpose: Builds SPARC architecture library objects for 32-bit and 64-bit kernel configurations.

Important APIs/functions: Uses `lib-$(CONFIG_SPARC32)`, `lib-$(CONFIG_SPARC64)`, `lib-y`, and `obj-*` lists. Adds `asflags-y := -DST_DIV0=0x02`.

Control flow: Kbuild conditionally includes arithmetic helpers, checksums, memory/string routines, copy routines, CPU-specific SPARC64 copy/page variants, atomics, tracing support, and I/O helpers based on `CONFIG_SPARC32`, `CONFIG_SPARC64`, and `$(BITS)`.

State and persistence: No runtime state. It controls build artifacts and link composition.

Dependencies/integration: Integrates every file in this subset into kernel build output. It selects generated variants (`GEN*`), UltraSPARC (`U1`, `U3`), Niagara (`NG`, `NG2`, `NG4`), and M7 routines so runtime patchers can redirect public symbols.

Risks/test signals: Missing or incorrectly conditioned objects cause unresolved symbols or wrong CPU patch availability. Test both SPARC32 and SPARC64 builds, verify object lists for selected configs, and run `nm`/link checks for exported symbols.
