<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead_hwprobe.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead_hwprobe.c

Purpose: Reports T-Head vendor ISA extension bits through hwprobe.

Important APIs/types/functions: Implements `hwprobe_isa_vendor_ext_thead_0()`.

Control flow: Checks T-Head vendor extension availability across requested CPUs and writes public hwprobe bits for extensions common to the mask.

State and persistence: Reads vendor extension bitmaps and T-Head feature state.

Dependencies and integration points: Called by `sys_hwprobe.c` for `RISCV_HWPROBE_KEY_VENDOR_EXT_THEAD_0`.

Risks: Must align with the T-Head extension table and avoid exposing disabled vector behavior.

Test signals: T-Head hardware/firmware hwprobe results, heterogeneous masks, and disabled xtheadvector scenarios.

Source read size: 19 lines, 537 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vendor_extensions/thead_hwprobe.c -->
