# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpufeature.c

Purpose: Central RISC-V ISA discovery, validation, feature bitmap construction, ELF HWCAP exposure, user ISA enablement, vendor extension aggregation, and alternative patch application.

Important APIs/types/functions: Exports `riscv_isa_extension_base()`, `__riscv_isa_extension_available()`, `riscv_fill_hwcap()`, `riscv_get_elf_hwcap()`, `riscv_user_isa_enable()`, `riscv_cpufeature_patch_func()`, global `elf_hwcap`, `riscv_isa`, `hart_isa[]`, and `riscv_isa_ext[]` with validation callbacks for F/D, vector, crypto, CFI, cache-block, compressed, and supervisor extensions.

Control flow: Boot parses either DT `riscv,isa-extensions`, deprecated `riscv,isa`, or ACPI RHCT ISA strings. It resolves dependencies iteratively, disables unsupported extensions by kernel config or missing properties, intersects per-hart bitmaps into host-wide capabilities, applies vendor extension aggregation, runs T-Head vector/ghostwrite handling, initializes vector size, then prints base ISA and ELF HWCAPs. Later alternative patching scans `alt_entry` records and patches text when a standard or vendor extension is available.

State and persistence: Maintains global and per-hart ISA bitmaps, `elf_hwcap`, cache-block availability flags, `thead_vlenb_of`, and command-line fallback state. `riscv_user_isa_enable()` writes current thread `envcfg` bits for cache-block user access.

Dependencies and integration points: Integrates with DT, ACPI RHCT, SBI/CSR identity, vector setup, vendor extension lists, alternative patching, text patching, user CFI command-line policy, hwprobe, `/proc/cpuinfo`, and ELF aux vector HWCAP.

Risks and test signals: This file is boot- and ABI-critical. Dependency resolution, heterogeneous harts, deprecated ISA fallback, duplicate or malformed extension entries, and alternative patching can expose unsupported instructions or hide real features. Test DT and ACPI boots, extension dependency matrices, F-without-D, vector/no-vector configs, CFI disable flags, cache block size validation, vendor extension alternatives, and ELF HWCAP regression tests.
