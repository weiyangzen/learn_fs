<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwprobe.h

Purpose: Defines the `riscv_hwprobe` userspace ABI for detailed RISC-V hardware capability and performance queries.

Important APIs/types/functions: Defines `struct riscv_hwprobe`, keys for vendor/arch IDs, base behavior, ISA extension bitmaps, misaligned access performance, block sizes, virtual address range, time CSR frequency, vendor extension keys, and `RISCV_HWPROBE_WHICH_CPUS`.

Control flow: Userspace passes key/value entries to the hwprobe syscall; kernel fills values for the selected CPU set.

State and persistence: Returned values reflect probed CPU capability state and may vary by CPU selection.

Dependencies and integration points: Integrated with `sys_hwprobe.c`, cpufeature, vendor extensions, libc/runtime dispatch, and documentation.

Risks: This is a stable UAPI; bit reuse or incorrect per-CPU aggregation can make userspace dispatch unsafe.

Test signals: hwprobe selftests, heterogeneous CPU masks, vendor extension keys, extension matrix, and headers ABI checks.

Source read size: 125 lines, 4979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwprobe.h -->
