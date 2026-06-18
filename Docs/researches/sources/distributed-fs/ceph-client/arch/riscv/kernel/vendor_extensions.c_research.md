<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions.c

Purpose: Aggregates configured RISC-V vendor ISA extension lists and answers vendor-extension availability queries.

Important APIs/types/functions: Defines `riscv_isa_vendor_ext_list[]` and exported `__riscv_isa_vendor_extension_available()`.

Control flow: The query validates vendor ID and bit, resolves the vendor list, and checks either a specific CPU's vendor extension bitmap or all CPUs when `cpu < 0`.

State and persistence: Uses configured vendor extension list pointers and per-CPU ISA extension bitmaps populated during CPU feature discovery.

Dependencies and integration points: Used by hwprobe vendor extension handlers and any code gating vendor-specific features.

Risks: Vendor ID/list mismatches can report unsupported instructions. All-CPU semantics must clear features absent on any CPU.

Test signals: Vendor extension hwprobe results on Andes, MIPS, SiFive, and T-Head configs; heterogeneous CPU masks; and disabled config builds.

Source read size: 86 lines, 2490 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions.c -->
