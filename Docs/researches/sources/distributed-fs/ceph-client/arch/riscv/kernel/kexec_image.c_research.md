# sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_image.c

Purpose: Loads raw RISC-V `Image` kernels for `kexec_file_load`.

Important APIs/types/functions: Defines `image_probe()`, `image_load()`, and `image_kexec_ops`.

Control flow: The probe validates the RISC-V image header and magic. Load checks image size and endianness flags, places the kernel image with alignment from `text_offset`, sets `image->start`, then adds extra DTB/initrd/cmdline segments.

State and persistence: Populates `struct kimage` buffers and start address; no file-local persistent state.

Dependencies and integration points: Depends on RISC-V boot image header definitions, kexec buffer placement, endian config, and machine kexec extra segment setup.

Risks and test signals: Header parsing is boot ABI critical; wrong alignment or endian acceptance can boot garbage. Test raw Image kexec, BE/LE mismatch rejection, malformed image sizes, and initrd/cmdline propagation.
