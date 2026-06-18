## sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate.c

### Purpose
`relocate.c` performs early kernel relocation and KASLR fixups for LoongArch. It copies the kernel to a randomized aligned address when enabled, applies relative and absolute relocations, handles RELR entries, updates the runtime relocation offset, and registers a panic notifier that prints relocation information.

### Important APIs, Types, And Functions
The main entry is `relocate_kernel`. Helpers include `relocate_relative`, `relocate_absolute`, `rotate_xor`, `get_random_boot`, `kaslr_disabled`, `determine_relocation_address`, `relocation_addr_valid`, `update_reloc_offset`, and the panic notifier callback. It uses linker symbols `__rela_dyn_*`, `__relr_dyn_*`, `__la_abs_*`, `_text`, `_end`, `_sdata`, and `__bss_start`.

### Control Flow
The entry maps the firmware command line from `fw_arg1`, copies it into `boot_command_line`, chooses a KASLR destination unless `nokaslr`, hibernation resume parameters, or `kexec_file` disable randomization, validates alignment/non-overlap, computes base relocation offset, and unmaps the command line. If randomized, it copies the kernel image, flushes instruction/data ordering, adjusts `__current_thread_info`, and writes the new relocation offset into the relocated image. It then applies relative relocations and patches absolute address materialization instruction sequences.

### State, Persistence, And Dependencies
`reloc_offset` persists as the runtime offset and is printed on panic. The relocated kernel image and patched relocation entries are permanent for the booted kernel. Dependencies include early ioremap, random entropy, LoongArch instruction formats, linker-provided relocation sections, command-line policy, and panic notifier infrastructure.

### Integration Points
Early boot assembly calls `relocate_kernel`. `setup.c` later uses the copied `boot_command_line`. Panic reporting uses the notifier registered at `arch_initcall`. Kexec-file disables KASLR through the command-line marker added by `machine_kexec_file.c`.

### Risks
KASLR entropy is intentionally simple and early; it should not be treated as cryptographic. Absolute relocation patching assumes exact instruction sequences described by `struct rela_la_abs`. Destination validation only checks alignment and original-kernel overlap, so platform memory-map assumptions matter. Hibernation command-line detection disables KASLR to preserve resume behavior.

### Test Signals
Boot with and without `CONFIG_RANDOMIZE_BASE`, `nokaslr`, `resume=`, `noresume`, `nohibernate`, and kexec-file. Inspect dmesg/panic relocation output, verify symbol addresses move by a consistent offset, and test RELR-enabled builds.
