<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/version.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/version.c

Purpose: Builds the boot-visible kernel version string used in early diagnostics.

Important APIs/types/functions: Defines `const char kernel_version[]` from generated `UTS_RELEASE`, `LINUX_COMPILE_BY`, `LINUX_COMPILE_HOST`, and `UTS_VERSION`.

Control flow: No runtime logic; the string is compiled into the boot image.

State and persistence: `kernel_version` is read by boot fault and OOM diagnostics.

Dependencies and integration points: Used by `pgm_check.c` and `physmem_info.c` for early crash/OOM reporting. Depends on generated version headers.

Risks: If generated headers are unavailable or inconsistent, boot diagnostics lose version fidelity or the build fails.

Test signals: Build-time generation of UTS headers and early fault/OOM logs containing the expected version string.

Source read size: 8 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/version.c -->
