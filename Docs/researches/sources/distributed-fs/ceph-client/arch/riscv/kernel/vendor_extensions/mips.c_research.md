<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips.c

Purpose: Defines MIPS vendor ISA extension metadata for RISC-V.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_mips[]` and `riscv_isa_vendor_ext_list_mips`.

Control flow: Table-only build-time contribution.

State and persistence: Static vendor extension descriptors persist in the kernel image.

Dependencies and integration points: Used by `vendor_extensions.c` and MIPS hwprobe support.

Risks: Vendor extension bit/table mismatches yield wrong hwprobe reporting.

Test signals: MIPS vendor extension parsing and hwprobe key results.

Source read size: 22 lines, 635 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips.c -->
