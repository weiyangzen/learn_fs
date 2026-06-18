<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/setup.h

Purpose: exports Xtensa setup constant `COMMAND_LINE_SIZE`, set to 256.

Control flow is none; it bounds boot command-line buffers and UAPI expectations. Persistent state affected is boot command-line storage and parsing length in setup code. Dependencies are consumers that include UAPI setup headers. Integration points include bootloader parameter parsing, `setup_arch`, proc/cmdline exposure, and userspace headers. Risks are truncation of long command lines and ABI-visible change if size is altered. Test signals include boot with long command line, setup parser behavior, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/setup.h -->
