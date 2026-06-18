<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead.c

Purpose: Defines T-Head vendor ISA extension metadata and disables T-Head vector support when requested.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_thead[]`, `riscv_isa_vendor_ext_list_thead`, and `disable_xtheadvector()`.

Control flow: The metadata table feeds discovery. `disable_xtheadvector()` clears the global T-Head vector enable state so generic vector support will not use it.

State and persistence: Static metadata and mutable T-Head vector enable state.

Dependencies and integration points: Used by vector setup, vendor extension aggregate, and T-Head hwprobe.

Risks: Disabling vector too late can leave inconsistent vector sizing/context state.

Test signals: T-Head vector-capable boot, command/config paths that disable xtheadvector, and vendor hwprobe checks.

Source read size: 29 lines, 901 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead.c -->
