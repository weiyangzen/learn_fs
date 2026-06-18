<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/io.h

## Purpose
`io.h` is the top-level m68k I/O access selector. It chooses MMU or non-MMU I/O definitions and then layers generic Linux I/O helpers on top.

## Important APIs, Types, and Functions
For `__uClinux__` or `CONFIG_COLDFIRE`, it includes `io_no.h`; otherwise it includes `io_mm.h`. It aliases `gf_ioread32` and `gf_iowrite32` to big-endian `ioread32be`/`iowrite32be`.

## Control Flow, State, and Persistence
There is no runtime state. Configuration controls which accessor implementation is compiled.

## Dependencies and Integration Points
It integrates all m68k drivers using standard `readb`, `writeb`, `inb`, `outb`, `ioremap`, and generic I/O APIs. The `gf_*` aliases support drivers that expect Open Firmware-style big-endian cell access.

## Risks
Wrong configuration selection changes endian behavior and address translation. Since generic `asm-generic/io.h` is included after arch-specific definitions, arch macros must be defined before the generic fallback is parsed.

## Test Signals
Build both MMU and non-MMU/ColdFire configs. Runtime tests should verify endian-correct MMIO on internal peripherals, PCI, ISA bridges, and big-endian firmware-style register accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io.h -->
