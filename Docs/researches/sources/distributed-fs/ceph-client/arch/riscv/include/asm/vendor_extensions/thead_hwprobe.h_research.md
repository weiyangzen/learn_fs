<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead_hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead_hwprobe.h

Purpose: Declares hwprobe glue for RISC-V vendor extension reporting in `thead_hwprobe.h`.

Important APIs/types/functions: Defines vendor hwprobe key/bit mapping declarations and helper prototypes used by `sys_hwprobe.c`.

Control flow: The hwprobe syscall asks vendor-specific code to translate kernel extension bitmaps into UAPI bit masks.

State and persistence: State is read from vendor extension bitmaps and exposed as syscall output.

Dependencies and integration points: Integrates with `uapi/asm/hwprobe.h`, `vendor_extensions.h`, and vendor extension lists.

Risks: Incorrect mapping exposes unstable or wrong userspace capability bits.

Test signals: hwprobe selftests for vendor keys, unsupported vendor fallback, and vendor hardware/QEMU coverage.

Source read size: 19 lines, 496 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead_hwprobe.h -->
