<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/Kbuild

Source read size: 3 lines, 89 bytes.

Purpose: tells Kbuild to generate PA-RISC UAPI syscall number headers. Important outputs: `unistd_32.h` and `unistd_64.h`. Control flow: during headers generation, Kbuild emits the generated headers from syscall tables. State and persistence: generated files become exported UAPI artifacts for userspace builds. Dependencies and integration points: integrates with syscall table generation and `include/uapi/asm/unistd.h`. Risks: omitting a generated header breaks 32-bit or 64-bit userspace header installation. Test signals: `make headers_install`, cross-compile UAPI header checks, and syscall-number consistency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/Kbuild -->
