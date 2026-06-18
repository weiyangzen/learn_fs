# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/headsmp.S

Purpose: contains low-level ARM assembly support for `mach-berlin` in `headsmp.S`.

Important APIs/types/functions: exports assembly entry points or data symbols referenced by C platform code, typically for secondary CPU startup, secure monitor calls, or suspend routines.

Control flow: execution enters through exported labels from C or CPU reset firmware, performs register-level setup, and returns or branches into common ARM startup/resume code.

State and persistence: assembly mutates CPU registers and sometimes SoC reset/power registers; persistent software state is limited to exported symbols and code copied or referenced by C.

Dependencies and integration: tied to ARM calling conventions, linker symbols, machine-specific C files, and Kconfig symbols that include the object.

Risks: no type checking across the C/assembly boundary; wrong register usage, symbol naming, or section placement can fail only at boot/resume time.

Test signals: successful assembly/link, boot or suspend path that reaches the entry point, and CPU online/resume tests on matching hardware.
