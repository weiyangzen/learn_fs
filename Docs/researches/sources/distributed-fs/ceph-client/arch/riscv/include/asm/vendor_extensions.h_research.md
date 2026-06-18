<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions.h

Purpose: Defines the framework for RISC-V vendor-specific ISA extension discovery and lookup.

Important APIs/types/functions: Includes `struct riscv_isa_vendor_ext_data_list`, vendor bitmap helpers, vendor extension availability checks, and extern lists for Andes, MIPS, SiFive, and T-Head.

Control flow: Boot/vendor code populates per-vendor extension bitmaps; feature checks query by vendor ID and extension number.

State and persistence: Persistent state is per-vendor/per-CPU extension bitmaps and vendor extension data lists.

Dependencies and integration points: Used by cpufeature, hwprobe, vector/errata code, and vendor extension implementation files.

Risks: Vendor ID or bit assignment errors expose unsupported instructions or hide required errata.

Test signals: Vendor extension parsing, hwprobe vendor keys, boot on vendor CPUs, and fallback builds without vendor configs.

Source read size: 104 lines, 3247 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions.h -->
