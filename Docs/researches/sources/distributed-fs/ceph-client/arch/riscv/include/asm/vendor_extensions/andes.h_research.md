<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/andes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/andes.h

Purpose: Declares `andes` vendor-specific RISC-V extension IDs and extension list metadata.

Important APIs/types/functions: Provides enum/define values for vendor extension bit numbers and extern data-list declarations.

Control flow: No runtime flow; boot cpufeature code consumes the list when parsing ISA/vendor strings or probing hardware.

State and persistence: Persistent state is vendor extension bitmap entries allocated according to these IDs.

Dependencies and integration points: Used by `vendor_extensions.h`, cpufeature parsing, hwprobe vendor reporting, and any vendor errata/feature users.

Risks: Renumbering extension IDs breaks bitmap interpretation and userspace hwprobe mapping.

Test signals: Vendor ISA parsing, hwprobe vendor tests, and builds with each vendor extension config enabled/disabled.

Source read size: 19 lines, 473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/andes.h -->
