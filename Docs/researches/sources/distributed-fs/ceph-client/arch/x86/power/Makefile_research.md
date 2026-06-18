<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/power/Makefile

## Purpose
Builds x86 suspend CPU-state support and architecture-specific hibernation restore code with compiler flags suited for low-level restore paths.

## Important APIs, Types, And Functions
`cpu.o` is built for `CONFIG_PM_SLEEP`; hibernation includes `hibernate_$(BITS).o`, `hibernate_asm_$(BITS).o`, and `hibernate.o`. `CFLAGS_cpu.o` disables stack protector, and LTO flags are removed from `cpu.o`.

## Control Flow
Kbuild selects bitness-specific hibernation C and assembly files and removes compiler features that can break `__restore_processor_state()`.

## State And Persistence
No runtime state exists in this file.

## Dependencies And Integration Points
Integrates with PM sleep, hibernation core, compiler hardening options, and x86 32/64-bit build variants.

## Risks And Edge Cases
Instrumentation or stack protector in restore code can corrupt `%gs`/stack assumptions during resume. The explicit flag removal is part of correctness.

## Test Signals
Builds under GCC/Clang, LTO, stack protector, PM sleep, and hibernation configs, plus successful suspend/hibernate resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/Makefile -->
