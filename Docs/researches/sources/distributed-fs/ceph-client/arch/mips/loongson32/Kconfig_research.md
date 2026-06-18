<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson32/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/loongson32/Kconfig

Purpose: Defines the Loongson32 built-in DTB source-name configuration.

Important APIs/types/functions: `BUILTIN_DTB_NAME` is a string option depending on `BUILTIN_DTB`.

Control flow: Kconfig prompts for a DTS basename relative to `arch/mips/boot/dts/loongson` when built-in DTB support is enabled.

State and persistence: Build configuration only.

Dependencies and integration: Used by MIPS DTB build rules.

Risks: Incorrect basename prevents the desired DTB from being linked.

Test signals: Enabling built-in DTB should build the selected Loongson DTS into the kernel image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson32/Kconfig -->
