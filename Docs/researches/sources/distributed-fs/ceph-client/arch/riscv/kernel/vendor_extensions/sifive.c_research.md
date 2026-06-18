<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive.c

Purpose: Defines SiFive vendor ISA extension metadata.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_sifive[]` and `riscv_isa_vendor_ext_list_sifive`.

Control flow: Table-only metadata used by CPU feature discovery.

State and persistence: Static extension descriptors remain in kernel image.

Dependencies and integration points: Used by vendor extension aggregate and SiFive hwprobe file.

Risks: Table drift from hardware/firmware extension naming breaks discovery.

Test signals: SiFive extension parsing and hwprobe results under `CONFIG_RISCV_ISA_VENDOR_EXT_SIFIVE`.

Source read size: 21 lines, 811 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/sifive.c -->
