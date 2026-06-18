# sources/distributed-fs/ceph-client/include/acpi/platform/acenv.h

Purpose: Selects ACPICA host/compiler configuration, defines environment feature defaults, and includes the correct compiler and OS platform headers before common ACPICA types are used.

Important APIs, types, and functions: Defines configuration constants such as `ACPI_BINARY_SEMAPHORE`, `ACPI_OSL_MUTEX`, debugger threading modes, application/tool feature macros, default compiler-dependent integer types, mutex/global-lock defaults, calling-convention macros, C-library/file abstractions, and `ACPI_INIT_FUNCTION`.

Control flow: Preprocessor logic detects ACPICA tools, libraries, GCC/MSVC, Linux, BSD, EFI, Zephyr, Windows, and other environments. Unknown targets trigger `#error`. Defaults fill in symbols not defined by the selected platform.

State and persistence: No runtime state; it controls compile-time feature state such as local cache use, debug output, hardware reduction, disassembler/debugger inclusion, and C-library usage.

Dependencies and integration points: Includes `acgcc.h`, `aclinux.h`, `aczephyr.h`, or other platform files. It is the first-stage configuration dependency for `actypes.h`, ACPICA OSL, tools, and Linux ACPI integration.

Risks and test signals: Risks include wrong target detection, conflicting tool/kernel macros, missing `ACPI_MACHINE_WIDTH`, and unintended debug/allocation behavior. Test kernel and userspace ACPICA builds, tool builds (`iasl`, `acpi_exec`, dump tools), Zephyr/EFI paths when relevant, and unknown-target failure behavior.
