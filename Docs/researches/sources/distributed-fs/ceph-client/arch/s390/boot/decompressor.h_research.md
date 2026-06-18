<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/decompressor.h -->
# sources/distributed-fs/ceph-client/arch/s390/boot/decompressor.h

Purpose: declares decompressor entry points for s390 boot code when the kernel is compressed. Important declarations are `mem_safe_offset` and `deploy_kernel` under `!CONFIG_KERNEL_UNCOMPRESSED`. Control flow is preprocessor-only, avoiding declarations when decompression is not built. State and persistence are none. Dependencies include the boot Makefile's compression object selection and `decompressor.c`. Risks are mismatched guards causing missing prototypes or unused code, and call sites not handling uncompressed configs. Test signals: compressed and uncompressed kernel builds, warning-free prototypes, and early boot call paths that compute safe memory placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/decompressor.h -->
