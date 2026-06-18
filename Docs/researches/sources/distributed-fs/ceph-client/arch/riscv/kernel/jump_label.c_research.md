# sources/distributed-fs/ceph-client/arch/riscv/kernel/jump_label.c

Purpose: Implements RISC-V static key/jump label patching.

Important APIs/types/functions: Provides `arch_jump_label_transform()` and architecture helpers to patch branch/NOP instruction sequences for static keys.

Control flow: Static key core requests enable/disable transformations. The RISC-V implementation encodes either a jump to the target or a NOP at the patch site and writes it using text patching, with early boot or runtime synchronization as required.

State and persistence: Persistent state is patched kernel text and static key metadata owned by generic jump label code.

Dependencies and integration points: Depends on RISC-V instruction encoding, `patch_text`, alternatives/text mutex, and Linux jump label core.

Risks and test signals: Offset range, instruction length, and synchronization mistakes can produce bad text. Test static key toggling, tracepoints, scheduler/static branch sites, modules, and concurrent CPU execution during patching.
