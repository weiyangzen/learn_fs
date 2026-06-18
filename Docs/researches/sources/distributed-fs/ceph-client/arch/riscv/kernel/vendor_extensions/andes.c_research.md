<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/andes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/andes.c

Purpose: Defines Andes vendor ISA extension metadata.

Important APIs/types/functions: Provides `riscv_isa_vendor_ext_andes[]` and `riscv_isa_vendor_ext_list_andes`.

Control flow: No dynamic flow; the table maps Andes extension names/bits for CPU feature discovery.

State and persistence: Static extension data list is consumed by the aggregate vendor extension layer.

Dependencies and integration points: Included when `CONFIG_RISCV_ISA_VENDOR_EXT_ANDES` is enabled.

Risks: Incorrect bit numbers or vendor IDs break extension reporting.

Test signals: Andes extension parsing and availability checks on compatible firmware descriptions.

Source read size: 18 lines, 575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/andes.c -->
