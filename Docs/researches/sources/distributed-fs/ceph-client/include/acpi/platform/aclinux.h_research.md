# sources/distributed-fs/ceph-client/include/acpi/platform/aclinux.h

Purpose: Configures ACPICA for Linux kernel and Linux userspace builds, mapping ACPICA types, allocators, exports, debug defaults, include policy, and disabled-ACPI stubs to Linux conventions.

Important APIs, types, and functions: Defines Linux ACPICA feature macros, enforces `<linux/acpi.h>` inclusion for external kernel code, sets `ACPI_MACHINE_WIDTH`, `ACPI_USE_SYSTEM_INTTYPES`, `ACPI_USE_GPE_POLLING`, `ACPI_INIT_FUNCTION`, `ACPI_EXPORT_SYMBOL`, `acpi_cache_t`, lock types, `acpi_uintptr_t`, `ACPI_OFFSET`, log prefixes, alternate OSL prototype macros, and no-`CONFIG_ACPI` external-return stubs.

Control flow: Preprocessor splits kernel versus userspace. Kernel builds include Linux headers and optional asm ACPI environment, set configuration from Kconfig, and define stub bodies when ACPI is disabled. Userspace builds select standard headers and infer 32/64-bit width from architecture macros.

State and persistence: No runtime state; it controls compile-time ABI and feature availability.

Dependencies and integration points: Integrates ACPICA with Linux kernel memory allocation, spinlocks, exports, printk, PCI config, ACPI reduced hardware, debugger options, and userspace ACPICA utilities.

Risks and test signals: Risks include direct ACPICA inclusion by kernel code, wrong machine width in userspace, disabled-ACPI stubs masking calls, and mismatched alternate OSL prototypes. Test `CONFIG_ACPI=y/n`, debug and debugger configs, 32-bit/64-bit userspace tools, and include-policy compile failures.
