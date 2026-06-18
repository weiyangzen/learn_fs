<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive_hwprobe.c

Purpose: Reports SiFive vendor ISA extension bits through hwprobe.

Important APIs/types/functions: Implements `hwprobe_isa_vendor_ext_sifive_0()`.

Control flow: Checks SiFive vendor extension availability across the CPU mask and sets the public hwprobe value for supported common bits.

State and persistence: Reads CPU feature/vendor extension state.

Dependencies and integration points: Dispatched by `sys_hwprobe.c` for `RISCV_HWPROBE_KEY_VENDOR_EXT_SIFIVE_0`.

Risks: Heterogeneous CPU masks must not report extensions missing on one CPU.

Test signals: hwprobe vendor SiFive key with matching and empty extension sets.

Source read size: 22 lines, 642 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive_hwprobe.c -->
