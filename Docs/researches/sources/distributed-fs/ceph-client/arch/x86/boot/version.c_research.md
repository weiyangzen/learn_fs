# sources/distributed-fs/ceph-client/arch/x86/boot/version.c

Purpose: embeds the kernel version string into the setup image.

Important APIs and state: defines `const char kernel_version[]` from generated `UTS_RELEASE`, `LINUX_COMPILE_BY`, `LINUX_COMPILE_HOST`, and `UTS_VERSION`.

Control flow: no runtime logic.

Dependencies and integration: `header.S` references `kernel_version` in the boot protocol header. Generated version headers are produced by the kernel build.

Risks and test signals: stale generated headers or layout changes can expose wrong version metadata to bootloaders/tools. Test by inspecting bzImage setup header version string after a build.
