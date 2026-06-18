<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/soc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/soc.h

Purpose: Declares RISC-V SoC identification hooks used to attach vendor/platform-specific behavior.

Important APIs/types/functions: Defines `struct riscv_soc_id` matching data and `riscv_soc_init()`-style declarations.

Control flow: Platform code matches discovered SoC IDs against tables during boot and runs selected init hooks.

State and persistence: State is discovered SoC identity and any platform init side effects outside this header.

Dependencies and integration points: Integrates with DT/ACPI platform discovery, errata, cache, and vendor extension code.

Risks: Incorrect matching can apply errata or platform quirks to the wrong hardware.

Test signals: Boot on supported SoCs, DT/ACPI matching tests, and vendor errata enablement checks.

Source read size: 24 lines, 627 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/soc.h -->
