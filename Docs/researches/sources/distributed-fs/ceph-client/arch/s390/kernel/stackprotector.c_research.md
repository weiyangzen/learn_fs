## sources/distributed-fs/ceph-client/arch/s390/kernel/stackprotector.c

Purpose: Patches compiler-generated stack canary loads so s390 code reads the task or lowcore stack canary instead of a single global `__stack_chk_guard`. It supports both decompressor-time physical patching and normal kernel virtual-address patching.

Important APIs and functions: Exports `__stack_chk_guard` and provides `__stack_protector_apply()` plus decompressor-only `__stack_protector_apply_early()`. Local helpers translate virtual/physical instruction addresses, stringify RIL instructions, verify expected `larl`/`lgrl` opcodes, dump patches when `stack_protector_debug` is enabled, and write replacement instructions with `s390_kernel_write()`.

Control flow: The linker provides a stack-protector relocation table. For each location, the code resolves the real instruction address, verifies that the instruction is an expected RIL form, rewrites it to an `llilf`-style load of `__LC_STACK_CANARY` plus lowcore relocation adjustment, optionally logs the before/after bytes, and writes the patched instruction.

State and persistence: State consists of `__stack_chk_guard`, boot-preserved `stack_protector_debug`, and the patched text image. Once applied, the change is persistent for the running kernel image.

Dependencies and integration: Depends on linker-provided stack protector tables in `vmlinux.lds.S`, lowcore constants, relocated-lowcore detection, decompressor address translation, and safe kernel text patching.

Risks and test signals: A wrong opcode pattern panics in the decompressor and reports an emergency error later, making linker/compiler instruction drift the key risk. Test signals are boot with `CONFIG_STACKPROTECTOR`, decompressor and post-relocation patch success, `stack_protector_debug` patch logs, and deliberate build checks that stack protector references land in the expected section.
