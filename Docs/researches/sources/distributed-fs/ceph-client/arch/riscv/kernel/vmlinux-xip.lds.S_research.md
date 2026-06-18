<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux-xip.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux-xip.lds.S

Purpose: Linker script for execute-in-place RISC-V kernel images.

Important APIs/types/functions: Defines XIP-specific section layout, load/virtual addresses, init sections, data/rodata/bss boundaries, exception tables, and discarded sections.

Control flow: Build-time only; the linker lays out the kernel image according to XIP constraints.

State and persistence: Determines persistent symbol addresses and section boundaries used at boot/runtime.

Dependencies and integration points: Used by the architecture build when XIP kernel support is enabled; must match head code, memory mapping, alternatives, init freeing, and module/kallsyms expectations.

Risks: Address or alignment mistakes can make XIP kernels unbootable. Section placement must preserve read-only/data permissions and init discard boundaries.

Test signals: XIP kernel link, boot on XIP-capable platforms, section map inspection, initmem freeing, and relocation checks.

Source read size: 143 lines, 2843 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vmlinux-xip.lds.S -->
