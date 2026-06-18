# sources/distributed-fs/openafs/src/util/vice.h

Purpose: Defines pioctl data structures and ioctl-construction macros for AFS user/kernel communication.

Important types and macros: Defines kernel `struct ViceIoctl32` with fixed-width pointer fields and user-space `struct ViceIoctl` on non-Windows. Defines `_VICEIOCTL(id)`, `_VICEIOCTL2(dev, id)`, `_CVICEIOCTL(id)`, and `_OVICEIOCTL(id)` using `_IOW()` with the appropriate structure type.

Control flow and state: Header-only ABI definitions. It encodes structure size into ioctl numbers so kernel code can identify argument layout.

Dependencies and integration: Includes system ioctl headers on non-Windows depending on platform/kernel configuration. Used by cache-manager pioctl interfaces and command tools.

Risks and test signals: ABI sensitivity is high: pointer-size differences and Alpha/Digital Unix exceptions are explicitly handled. Windows uses a different structure in `sys/pioctl_nt.h`. Tests are pioctl command behavior across 32/64-bit user/kernel combinations.
