<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/text-patching.h

Purpose: Declares low-level RISC-V text patching APIs.

Important APIs/types/functions: Includes `patch_text_nosync()`, `patch_text_set_nosync()`, `patch_text()`, and related patch helpers.

Control flow: Callers write replacement instructions and then synchronize instruction execution when using the syncing API.

State and persistence: Persistent effect is modified kernel/module/vDSO text.

Dependencies and integration points: Used by alternatives, jump labels, ftrace, kprobes, BPF, and errata patching.

Risks: Incorrect patch size/alignment or missing sync can corrupt executable text.

Test signals: Alternatives boot, ftrace/jump-label/kprobe tests, module patching, and W^X permission tests.

Source read size: 16 lines, 449 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/text-patching.h -->
