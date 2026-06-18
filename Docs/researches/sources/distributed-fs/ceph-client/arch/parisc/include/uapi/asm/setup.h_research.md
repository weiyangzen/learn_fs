<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/setup.h

Source read size: 7 lines, 173 bytes.

Purpose: exposes PA-RISC boot command-line size. Important API: `COMMAND_LINE_SIZE` set to 1024. Control flow: boot/setup code uses this bound when copying or parsing kernel command lines. State and persistence: boot command line persists in early boot/init state and procfs. Dependencies and integration points: setup and boot loader handoff. Risks: truncation beyond 1024 bytes can drop boot parameters; changing the value affects boot ABI expectations. Test signals: boot with long command lines and inspect `/proc/cmdline`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/setup.h -->
