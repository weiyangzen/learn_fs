# sources/distributed-fs/ceph-client/arch/s390/kernel/jump_label.c

Purpose: implements s390 jump-label static branch patching by replacing six-byte `brcl` encodings between no-op and unconditional branch forms.

Important APIs and types: `struct insn` is the packed opcode/offset form. `arch_jump_label_transform()`, `arch_jump_label_transform_queue()`, and `arch_jump_label_transform_apply()` are the architecture hooks used by the generic jump-label core.

Control flow: helpers build expected old and desired new instruction bytes from `jump_entry_code()` and `jump_entry_target()`. `jump_label_transform()` validates that the live text matches the expected form, panics on mismatch via `jump_label_bug()`, writes the replacement with `s390_kernel_write()`, and callers synchronize text poking through `text_poke_sync()`.

Dependencies and integration: depends on generic jump labels, module jump entries, s390 text patching, and IPL panic behavior. Queued transforms write immediately but defer the sync to `arch_jump_label_transform_apply()`.

Risks and test signals: wrong offsets or patching corrupted text is fatal by design. Test static keys in built-in and module code, queued batch patching, module load/unload with jump labels, and mismatch detection in fault-injection or debug builds.
