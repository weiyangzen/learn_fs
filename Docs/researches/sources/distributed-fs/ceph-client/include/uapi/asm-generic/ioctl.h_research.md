# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ioctl.h

Purpose: Defines the generic ioctl command-number bit layout and helper macros.

Important APIs/types/functions: Exports `_IOC_*BITS`, masks, shifts, direction constants `_IOC_NONE/_IOC_WRITE/_IOC_READ`, `_IOC()`, `_IO`, `_IOR`, `_IOW`, `_IOWR`, bad-size variants, extractors `_IOC_DIR/_IOC_TYPE/_IOC_NR/_IOC_SIZE`, and legacy `IOC_*` aliases.

Control flow: Preprocessor guards allow architectures to override size/direction bits or direction constants. In userspace, `_IOC_TYPECHECK(t)` uses `sizeof(t)`.

State/persistence: No runtime state; establishes ABI encoding for ioctl numbers.

Dependencies/integration: Used by almost every UAPI ioctl definition through `<linux/ioctl.h>` or asm headers.

Risks: Bit allocation and size checking are ABI-critical. Incorrect `_IOC_SIZEBITS` can truncate command sizes or conflict with architecture numbering.

Test signals: Compile representative ioctl headers and compare generated command numbers against known ABI values.
