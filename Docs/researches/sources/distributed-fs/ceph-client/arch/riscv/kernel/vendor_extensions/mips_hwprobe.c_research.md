<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips_hwprobe.c

Purpose: Reports MIPS vendor ISA extension bits through the RISC-V hwprobe vendor key.

Important APIs/types/functions: Implements `hwprobe_isa_vendor_ext_mips_0()`.

Control flow: Initializes the hwprobe pair value, checks configured MIPS vendor extension availability over the requested CPU mask, and sets public hwprobe bits for common extensions.

State and persistence: Reads per-CPU/vendor extension state only.

Dependencies and integration points: Called by `sys_hwprobe.c` for `RISCV_HWPROBE_KEY_VENDOR_EXT_MIPS_0`.

Risks: Must expose only extensions common to all CPUs in the mask and only ABI-approved bits.

Test signals: hwprobe vendor MIPS key on systems with and without the advertised extensions.

Source read size: 23 lines, 612 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/mips_hwprobe.c -->
