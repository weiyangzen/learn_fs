# Research: subset-b-000914

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/init.c

## Purpose
`init.c` allocates, relocates, protects, and publishes the x86 real-mode trampoline blob used for secondary CPU startup, real-mode restart, and ACPI wakeup paths.

## Important APIs, types, and functions
Key symbols are `real_mode_header`, `trampoline_cr4_features`, `trampoline_pgd_entry`, `load_trampoline_pgtable()`, `reserve_real_mode()`, `init_real_mode()`, and the early initcall `do_init_real_mode()`. `sme_sev_setup_real_mode()` adjusts the trampoline for SME/SEV-ES.

## Control flow
Early boot reserves low memory below 1 MiB, copies `real_mode_blob`, applies 16-bit segment and 32-bit linear relocations from `real_mode_relocs`, then fills `struct trampoline_header`. On 64-bit it prepares EFER, CR4, the trampoline lock, and a trampoline PGD that identity maps the low stub and imports kernel mappings. Later `set_real_mode_permissions()` marks the blob NX/RO except executable text.

## State and persistence behavior
Persistent state is the allocated low-memory real-mode area referenced by `real_mode_header`, the trampoline PGD entry, trampoline lock/header fields, and CR4 feature pointer used by CPU bring-up. SME hosts decrypt the trampoline pages.

## Dependencies and integration points
It depends on memblock allocation, page attribute APIs, CR3/CR4/TLB helpers, `asm/realmode.h`, SEV-ES AP jump-table setup, embedded data from `rmpiggy.S`, and the platform `x86_platform.realmode_init()` hook.

## Risks and edge cases
Low-memory allocation failure prevents SMP trampoline use. Relocation ordering is critical because the trampoline header is dereferenced only after relocation. PCID must be cleared before switching to the trampoline page table, and stale global TLB entries are explicitly flushed. SME/SEV setup is sensitive to encrypted/decrypted memory state.

## Test signals
Boot tests with SMP CPU bring-up, kexec/reboot paths, ACPI S3 resume, SME/SEV-ES guests/hosts, and page-permission debugging are the main signals. A missing low-memory reservation or bad signature/relocation should fail early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/Makefile

## Purpose
`rm/Makefile` builds the 32-bit ELF real-mode image, relocation table, and final `realmode.bin` consumed by the kernel.

## Important APIs, types, and functions
Targets include `realmode.elf`, `realmode.bin`, `realmode.relocs`, generated `pasyms.h`, and `realmode.lds`. Object groups include `header.o`, `trampoline_$(BITS).o`, `stack.o`, `reboot.o`, and ACPI wakeup/video objects under `CONFIG_ACPI_SLEEP`.

## Control flow
Kbuild first extracts physical-address symbols with `nm | sed`, preprocesses the linker script, links an `elf32-i386` image with relocations, runs `arch/x86/tools/relocs --realmode`, and objcopies the binary blob.

## State and persistence behavior
It persists generated build artifacts only. The order of video objects is encoded as build state because VGA must be probed before VESA and BIOS fallback.

## Dependencies and integration points
It depends on real-mode compiler flags from the parent makefile, `arch/x86/tools/relocs`, `nm`, `ld`, `objcopy`, and boot include paths for shared 16-bit code.

## Risks and edge cases
Object order and relocation generation are high-risk: missing `pasyms.h`, wrong `BITS`, or omitted `--emit-relocs` breaks `init.c` relocation. Real-mode C flags must avoid unsupported unwind metadata.

## Test signals
Signals are successful generation of `realmode.bin`/`realmode.relocs`, no unsupported relocations from `relocs`, and resume/reboot paths using the generated blob.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/bioscall.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/bioscall.S

## Purpose
`bioscall.S` is a real-mode wrapper that includes the shared boot implementation for `bioscall` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/bioscall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/copy.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/copy.S

## Purpose
`copy.S` is a real-mode wrapper that includes the shared boot implementation for `copy` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/copy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/header.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/header.S

## Purpose
`header.S` defines the read-only real-mode blob header that the protected-mode kernel uses to find trampoline, wakeup, restart, and page-table entry points after relocation.

## Important APIs, types, and functions
It emits `real_mode_header` in `.header` with offsets such as `pa_text_start`, `pa_ro_end`, `pa_trampoline_start`, `pa_trampoline_header`, optional SEV-ES and 64-bit trampoline pointers, ACPI wakeup pointers, `pa_machine_real_restart_asm`, and the 32-bit kernel CS value. It also emits `end_signature`.

## Control flow
The linker resolves `pa_*` symbols from `pasyms.h`; `init.c` copies the blob and patches this header before consumers dereference it. The `.signature` value lets wakeup code verify the complete real-mode region.

## State and persistence behavior
State is intentionally read-only header metadata. Mutable state must live in `.data`/`.bss` through pointers so page permissions can protect the header.

## Dependencies and integration points
It depends on `realmode.h`, linker-script symbols, `CONFIG_AMD_MEM_ENCRYPT`, `CONFIG_X86_64`, and `CONFIG_ACPI_SLEEP` layout choices.

## Risks and edge cases
The C `struct real_mode_header` must match field order exactly. Missing or reordered fields will redirect CPU startup or restart code to the wrong physical offset.

## Test signals
Test signals are compile-time structure layout agreement, valid `REALMODE_END_SIGNATURE`, successful relocation, and boot/resume paths that consume every configured header pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/header.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.h -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.h

## Purpose
`realmode.h` provides small shared definitions for real-mode assembly, primarily the handcrafted 16-bit far jump macro and end-of-blob signature.

## Important APIs, types, and functions
The important API is `LJMPW_RM(to)`, used where gas cannot encode a relocatable segment operand, and `REALMODE_END_SIGNATURE` for integrity checking.

## Control flow
Assembly code uses `LJMPW_RM()` when switching CS to the relocated real-mode segment. Wakeup code compares the signature after entering the blob.

## State and persistence behavior
No runtime state is stored; the constants influence encoded instruction bytes and signature data.

## Dependencies and integration points
It depends on `real_mode_seg` being supplied by the realmode linker script and included only in the blob assembly context for the macro.

## Risks and edge cases
Incorrect far-jump encoding breaks all real-mode transitions. Signature drift must match `header.S` and `wakeup_asm.S` checks.

## Test signals
Signals include objdump inspection of far jumps, real-mode relocation validation, and S3/reboot/SMP startup smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.lds.S

## Purpose
`realmode.lds.S` lays out the relocatable `elf32-i386` real-mode image and defines the physical-address symbols used by the blob header and relocation tool.

## Important APIs, types, and functions
It defines sections `.header`, `.rodata`, `.text`, `.text32`, `.text64`, `.data`, `.bss`, `.signature`, `video_cards`, `video_cards_end`, `pa_text_start`, `pa_ro_end`, and includes generated `pasyms.h`.

## Control flow
The linker starts at zero so emitted addresses are offsets within the blob. Text is page aligned for later page-permission changes; data and bss are separated; note/debug sections are discarded.

## State and persistence behavior
State is the binary layout contract. The header and permission code depend on `pa_text_start`/`pa_ro_end`; the video code depends on `video_cards` bounds.

## Dependencies and integration points
It depends on `PAGE_SIZE`, kbuild-generated `pasyms.h`, and all realmode object sections using the expected names.

## Risks and edge cases
Misalignment or misplaced sections can make executable permissions too broad/narrow, hide video-card descriptors, or produce bad relocation offsets.

## Test signals
Signals are link success, inspection of section offsets, real-mode relocation output, and runtime permission checks in `init.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/reboot.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/reboot.S

## Purpose
`reboot.S` implements `machine_real_restart_asm`, a protected-mode to real-mode transition that performs BIOS or APM reset from the real-mode blob.

## Important APIs, types, and functions
Important labels are `machine_real_restart_asm`, `machine_real_restart_paging_off` on 64-bit, the 16-bit `machine_real_restart_asm16` body, `machine_real_restart_idt`, and `machine_real_restart_gdt`.

## Control flow
On 64-bit it loads a low trampoline GDT, disables paging to leave long mode, clears EFER, then continues as 32-bit/16-bit transition code. It loads real-mode-compatible IDT/GDT descriptors, loads segment registers, disables paging/cache bits, invalidates cache when needed, clears PE through CR0, far-jumps to real mode, and then either calls APM int 15h or jumps to BIOS reset vector `f000:fff0`.

## State and persistence behavior
The only persistent state is descriptor data in `.rodata`. Machine state is deliberately destroyed: CR0, CR3, EFER, segment registers, IDT/GDT, cache state, and control flow are rewritten for reset.

## Dependencies and integration points
It depends on x86 descriptor constants, MSR/CR0 definitions, `LJMPW_RM`, the real-mode base symbols, and callers passing restart type in the ABI-specific primary argument register.

## Risks and edge cases
This code is intentionally fragile: descriptor bases must be below 4 GiB on 64-bit, instructions around CR0 mode switches must be adjacent to far jumps, and cache/paging state changes can fault if the blob is misrelocated.

## Test signals
Signals are reboot tests for BIOS and APM modes, kdump/restart coverage on 32-bit and 64-bit kernels, and objdump checks around the CR0/far-jump sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/reboot.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/regs.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/regs.c

## Purpose
`regs.c` is a real-mode wrapper that includes the shared boot implementation for `regs` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/stack.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/stack.S

## Purpose
`stack.S` reserves a small heap and stack for 16-bit real-mode C and assembly routines in the realmode blob.

## Important APIs, types, and functions
It exports `HEAP`, `heap_end`, `rm_heap`, `rm_stack`, and global `rm_stack_end`.

## Control flow
The linker places this data in `.data`/`.bss`; trampoline and wakeup code load `rm_stack_end` into ESP before calling C or verification routines.

## State and persistence behavior
Persistent state is 2 KiB heap plus 2 KiB stack storage inside the low-memory real-mode blob. It is reused by AP startup and wakeup paths, with 64-bit trampoline serialization via a lock.

## Dependencies and integration points
It depends on the realmode linker script and consumers such as `trampoline_64.S` and `wakeup_asm.S` using the exported labels.

## Risks and edge cases
Stack size is fixed and small; adding deeper C calls or interrupts in real mode can overflow it. Shared stack use needs locking where multiple APs can enter concurrently.

## Test signals
Signals are successful AP startup/resume under stress and stack-label presence in `pasyms.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/stack.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_32.S

## Purpose
`trampoline_32.S` is the 32-bit SMP secondary CPU real-mode trampoline that switches an AP from real mode to protected mode and jumps to `startup_32_smp`.

## Important APIs, types, and functions
Exports include `trampoline_start`, `startup_32`, and `trampoline_header` fields `tr_start`, `tr_gdt_pad`, and `tr_gdt`.

## Control flow
An AP enters in real mode, flushes cache, far-jumps to the relocated segment, initializes DS, disables interrupts, loads the destination from `tr_start`, loads a null IDT and supplied GDT, sets CR0.PE with `lmsw`, and far-jumps to `pa_startup_32`. The 32-bit stub then jumps through EAX.

## State and persistence behavior
State is the trampoline header filled by `init.c` with start address and GDT descriptor. The code otherwise relies on CPU control registers and segment state.

## Dependencies and integration points
It depends on real-mode relocation symbols, `__BOOT_CS`, `startup_32_smp`, and `trampoline_common.S` for IDT storage.

## Risks and edge cases
Bad GDT descriptor placement or a wrong `tr_start` will hang AP bring-up. The code assumes no usable incoming stack and must remain relocation-safe.

## Test signals
Signals are 32-bit SMP boot, CPU hotplug, objdump relocation checks, and AP startup timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_64.S

## Purpose
`trampoline_64.S` implements the 64-bit AP trampoline for real-mode, SEV-ES, compatibility-mode, and direct 64-bit BIOS entry paths.

## Important APIs, types, and functions
Important symbols are `trampoline_start`, optional `sev_es_trampoline_start`, `startup_32`, `pa_trampoline_compat`, `startup_64`, `trampoline_start64`, descriptor tables `tr_gdt`/`tr_gdt64`/`tr_compat`, `trampoline_pgd`, and `trampoline_header` fields for start, EFER, CR4, flags, and lock.

## Control flow
The real-mode path serializes stack use, optionally verifies long-mode support, loads IDT/GDT, enters protected mode, handles SME MSR setup, installs CR4/CR3/EFER, enables paging/long mode, and jumps to 64-bit kernel entry. The direct 64-bit path checks LA57 paging compatibility and either jumps directly with trampoline PGD or drops through compatibility mode to switch paging width.

## State and persistence behavior
Persistent blob state includes the trampoline page table, duplicated GDTs, lock word, CR4/EFER/start fields, and SME flag. CPU state transitions cover CR0, CR3, CR4, EFER, segment registers, and stack.

## Dependencies and integration points
It depends on `verify_cpu.S`, AMD memory-encryption flags, `struct trampoline_header`, `init.c` header initialization, and page-table constants for 4-level/5-level switching.

## Risks and edge cases
Relocation avoidance is critical; the comment explicitly requires objdump relocation checks. Races on the shared real-mode stack are controlled by `tr_lock`. EFER writes are skipped when already correct to avoid TDX #VE behavior.

## Test signals
Signals include 64-bit SMP and CPU hotplug, SEV-ES AP startup, SME-enabled boot, LA57 paging transitions, direct 64-bit firmware handoff testing, and relocation-free objdump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_common.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_common.S

## Purpose
`trampoline_common.S` provides the shared zero-IDT descriptor used by real-mode trampolines before entering protected or long mode.

## Important APIs, types, and functions
It exports local `tr_idt`, sized with a 2-byte limit and 8-byte base field to satisfy both 32-bit and 64-bit descriptor-load forms.

## Control flow
Trampoline code includes this file and loads the descriptor before switching modes so unexpected faults shut down rather than vectoring through firmware state.

## State and persistence behavior
No mutable state exists; the descriptor is constant `.rodata`.

## Dependencies and integration points
It depends on `linux/linkage.h`-style symbol macros from the including file context and consumers using `lidt/lidtl` appropriately.

## Risks and edge cases
Wrong descriptor size can corrupt adjacent realmode data or leave a stale IDT active during AP startup.

## Test signals
Signals are AP startup stability and disassembly confirming the IDT descriptor has expected limit/base bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/trampoline_common.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-bios.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-bios.c

## Purpose
`video-bios.c` is a real-mode wrapper that includes the shared boot implementation for `video-bios` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-bios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-mode.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-mode.c

## Purpose
`video-mode.c` is a real-mode wrapper that includes the shared boot implementation for `video-mode` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vesa.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vesa.c

## Purpose
`video-vesa.c` is a real-mode wrapper that includes the shared boot implementation for `video-vesa` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vesa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vga.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vga.c

## Purpose
`video-vga.c` is a real-mode wrapper that includes the shared boot implementation for `video-vga` so the ACPI wakeup/realmode blob can reuse boot-time BIOS, copy, register, or video-mode code without maintaining a fork.

## Important APIs, types, and functions
The file exports whatever symbols are emitted by the included `arch/x86/boot` source; locally it only contains a preprocessor include directive.

## Control flow
Build flow is textual inclusion: kbuild compiles this file under real-mode flags, the included boot source emits 16-bit routines, and the realmode linker script places the resulting text/data into `realmode.bin`.

## State and persistence behavior
There is no file-local state. Any mutable state belongs to the included boot code, such as BIOS register structures, port-I/O helpers, video-card tables, or copy buffers.

## Dependencies and integration points
It depends on `arch/x86/boot` sources and on `rm/Makefile` supplying `_SETUP`, `_WAKEUP`, and boot include paths so the shared source sees the expected environment.

## Risks and edge cases
The risk is indirect: changes in boot code can affect suspend wakeup real-mode behavior, and link order matters for the video wrappers because VGA/VESA/BIOS probing order is intentional.

## Test signals
Useful signals are successful `realmode.bin` linking, S3 resume video restoration tests, BIOS-call path testing on legacy systems, and objdump checks that the wrapper emits relocation-safe 16-bit code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/video-vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakemain.c -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakemain.c

## Purpose
`wakemain.c` is the C portion of the ACPI S3 real-mode wakeup helper, handling optional beep/debug, video BIOS callout, and video-mode restoration before returning to protected mode.

## Important APIs, types, and functions
Important functions are `udelay()`, `beep()`, `send_morse()`, global `pio_ops`, and `main()`. It uses boot video APIs `probe_cards()` and `set_mode()` from included boot code.

## Control flow
`main()` initializes default I/O operations, validates `wakeup_header.real_magic`, optionally sends a Morse pattern, optionally calls the VGA BIOS at `c000:0003`, and optionally probes/restores the requested video mode.

## State and persistence behavior
State comes from `wakeup_header` fields populated before suspend and from port I/O side effects on PIT/speaker and video BIOS hardware. No persistent kernel data is updated here.

## Dependencies and integration points
It depends on `wakeup.h`, boot `boot.h`, legacy port I/O, video wrappers, and BIOS interrupt/call support in real mode.

## Risks and edge cases
The code runs in a constrained real-mode environment with limited stack and no kernel services. BIOS calls can hang or corrupt state on firmware with broken video restore.

## Test signals
Signals include S3 resume with video restore flags, speaker debug flag testing, and header magic mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakemain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup.h -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup.h

## Purpose
`wakeup.h` defines the packed ACPI wakeup header shared by 16-bit assembly and C wakeup code.

## Important APIs, types, and functions
The central type is `struct wakeup_header` with video mode, protected-mode resume CS/CR0/CR3/CR4/EFER/GDT/MISC_ENABLE, behavior flags, real-mode flags, magic, and signature. It defines `WAKEUP_HEADER_OFFSET`, `WAKEUP_HEADER_SIGNATURE`, and behavior bits for restoring MSRs/control registers.

## Control flow
Suspend code fills the header before S3. `wakeup_asm.S` validates the signature and restores selected control state; `wakemain.c` reads `realmode_flags` and `video_mode`.

## State and persistence behavior
The structure is persistent across suspend/resume inside the real-mode blob and must be packed to match the assembly layout exactly.

## Dependencies and integration points
It depends on Linux integer types for C and exact label layout in `wakeup_asm.S` for assembly.

## Risks and edge cases
Field order or packing changes can resume to the wrong protected-mode address or restore wrong control-register/MSR values.

## Test signals
Signals are compile/build checks, S3 resume, and runtime signature/magic validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup_asm.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup_asm.S

## Purpose
`wakeup_asm.S` is the ACPI S3 wakeup assembly stub that repairs real-mode segment state, calls wakeup C code, and transfers back to protected/long-mode kernel resume.

## Important APIs, types, and functions
It emits the `wakeup_header` data object, `wakeup_start`, `wakeup_gdt`, and a local real-mode IDT. The header labels must match `struct wakeup_header`.

## Control flow
The stub enters with unknown firmware segment state, temporarily enables protected mode to load known descriptors, returns to real mode, sets stack/segments, validates header and blob signatures, calls `main()`, restores MISC_ENABLE and optionally CR3/CR4/EFER on 32-bit, then jumps through `startup_32` or the 64-bit trampoline.

## State and persistence behavior
Persistent state is the wakeup header and descriptor tables. Runtime state includes restored CR/MSR/GDT/IDT values and stack selection from `rm_stack_end`.

## Dependencies and integration points
It depends on `realmode.h`, `wakeup.h`, `stack.S`, `trampoline_32.S`/`trampoline_64.S`, MSR constants, and ACPI suspend code populating the header.

## Risks and edge cases
Firmware can resume with invalid segment descriptors, which this code explicitly repairs. Any mismatch between C header and assembly data layout breaks resume. Bad signature handling intentionally halts.

## Test signals
Signals include ACPI S3 resume on 32-bit and 64-bit, video-restore combinations, MISC_ENABLE/EFER restore coverage, and disassembly of mode-switch sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/wakeup_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rmpiggy.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rmpiggy.S

## Purpose
`rmpiggy.S` embeds the generated real-mode binary and relocation stream into kernel init data so `init.c` can copy them to low memory.

## Important APIs, types, and functions
It exports `real_mode_blob`, `real_mode_blob_end`, and `real_mode_relocs` using `.incbin` of `realmode.bin` and `realmode.relocs`.

## Control flow
During vmlinux link the generated files become aligned `.init.data`. Early init copies the blob and walks the relocation data.

## State and persistence behavior
State is build-time binary data only; it is freed with init data after boot once copied and initialized.

## Dependencies and integration points
It depends on `rm/Makefile` producing the two included files before assembly and on `PAGE_SIZE` alignment.

## Risks and edge cases
Missing or stale included binaries produce broken trampoline setup. Alignment matters for later page permission management.

## Test signals
Signals are successful vmlinux link, correct blob size in `init.c`, and real-mode relocation processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rmpiggy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/tools/Makefile

## Purpose
`tools/Makefile` builds x86 host utilities used for instruction-decoder tests, relocation extraction, and vDSO conversion.

## Important APIs, types, and functions
It defines `posttest`, `insn_decoder_test`, `insn_sanity`, `relocs`, and `vdso2c`, including host include paths for generated instruction tables and UAPI headers.

## Control flow
`posttest` disassembles `.text` from `vmlinux`, reformats objdump output, runs decoder length comparison, then runs random decoder sanity testing. The host programs are built as kbuild host tools.

## State and persistence behavior
No runtime kernel state exists. Build artifacts and test outputs are the only persistence.

## Dependencies and integration points
It depends on objdump, awk, generated `inat-tables.c`, x86 tools library sources, and configuration-derived 32/64-bit mode flags.

## Risks and edge cases
Host include path skew can test against stale generated decoder tables. The tests can be expensive at the one-million-iteration sanity setting.

## Test signals
Signals are successful host-tool builds, `make arch/x86/tools/posttest`, and decoder success output for both 32-bit and 64-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/cpufeaturemasks.awk -->
# sources/distributed-fs/ceph-client/arch/x86/tools/cpufeaturemasks.awk

## Purpose
`cpufeaturemasks.awk` converts `cpufeatures.h` plus `.config` into C preprocessor masks for compile-time required and disabled x86 CPU features.

## Important APIs, types, and functions
It emits `REQUIRED_MASKn`, `DISABLED_MASKn`, and `*_MASK_BIT_SET(x)` macros. Internally it builds `feats[]` from `X86_FEATURE_*`, reads `NCAPINTS`, and maps `CONFIG_X86_REQUIRED_FEATURE_*`/`CONFIG_X86_DISABLED_FEATURE_*` settings.

## Control flow
The script processes two inputs with different field separators, accumulates feature status, prints comments naming selected features, and emits one 32-bit mask per capability word.

## State and persistence behavior
State is transient AWK arrays. The generated header persists in the build tree and is consumed by CPU feature policy code.

## Dependencies and integration points
It depends on the exact macro shape in `arch/x86/include/asm/cpufeatures.h` and config option naming conventions.

## Risks and edge cases
Feature-word parsing assumes every word has at least one feature and uses AWK exponentiation for bit masks; unusual AWK behavior or macro format changes can generate wrong masks.

## Test signals
Signals are generated header diffs after CPU feature changes, build coverage with required/disabled feature configs, and runtime boot checks that required feature enforcement matches config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/cpufeaturemasks.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/gen-insn-attr-x86.awk -->
# sources/distributed-fs/ceph-client/arch/x86/tools/gen-insn-attr-x86.awk

## Purpose
`gen-insn-attr-x86.awk` generates x86 instruction attribute tables from `x86-opcode-map.txt` for the in-kernel/tools instruction decoder.

## Important APIs, types, and functions
Important routines include `check_awk_implement()`, `clear_vars()`, `semantic_error()`, `print_table()`, `convert_operands()`, and table emission logic for primary, escape, group, AVX, EVEX, XOP, and prefix tables.

## Control flow
It parses table directives, tracks opcode variants, operand/immediate/modrm attributes, prefix-specific tables, group references, escape maps, and final table pointer arrays. Semantic errors abort generation when opcode maps redefine entries or use unknown operands.

## State and persistence behavior
All state is AWK arrays such as `table`, `lptable*`, `etable`, `gtable`, `atable`, and `xoptable`. The persistent artifact is generated `inat-tables.c`.

## Dependencies and integration points
It depends on opcode-map syntax, `asm/inat.h` flag names, AWK formatting correctness, and generated C being included by `insn.c` users.

## Risks and edge cases
Decoder correctness relies on this parser preserving prefix and operand semantics. New ISA encodings can be misdecoded if regex classifications are incomplete.

## Test signals
Signals are successful generation, `insn_decoder_test` against objdump, `insn_sanity` fuzzing, and review of table diffs when opcode maps change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/gen-insn-attr-x86.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/insn_decoder_test.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/insn_decoder_test.c

## Purpose
`insn_decoder_test.c` is a host test that compares the x86 instruction decoder's computed length with objdump's instruction byte length.

## Important APIs, types, and functions
Key functions are `parse_args()`, `malformed_line()`, `dump_field()`, `dump_insn()`, and `main()`. It directly includes `inat.c` and `insn.c` from tools.

## Control flow
The program reads reformatted objdump lines, tracks symbol context, parses hex bytes into a 16-byte buffer, calls `insn_decode()` in 32-bit or 64-bit mode, and reports mismatches or decode errors.

## State and persistence behavior
State is process-local counters, symbol name, verbosity, and architecture mode. It does not write persistent files.

## Dependencies and integration points
It depends on `objdump_reformat.awk`, generated inat tables, `tools/arch/x86/lib` decoder sources, and `linux/kallsyms.h` for symbol buffer sizing.

## Risks and edge cases
Input format is strict tab-delimited output from the AWK reformatter. Decoder false positives may come from objdump syntax quirks or unsupported instruction encodings.

## Test signals
Signals are zero-warning posttest runs on `vmlinux` and verbose dumps for any decoder-length mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/insn_decoder_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/insn_sanity.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/insn_sanity.c

## Purpose
`insn_sanity.c` fuzzes the x86 instruction decoder with random or supplied byte streams to ensure decoding stays within the instruction buffer.

## Important APIs, types, and functions
Important functions include `parse_args()`, `init_random_seed()`, `read_next_insn()`, `generate_insn()`, `dump_stream()`, and `main()`. Options select 32/64-bit mode, verbosity, seed/iteration, max count, or input file.

## Control flow
The test fills a buffer with generated bytes and NOP guard bytes, decodes it via `insn_decode()`, then verifies `insn.next_byte` is within the legal instruction window. It prints reproduction commands for violations.

## State and persistence behavior
State is local seed, iteration range, input file handle, counters, and generated buffers. No kernel state is mutated.

## Dependencies and integration points
It depends on `/dev/urandom`, libc I/O, generated inat tables, and tools decoder sources.

## Risks and edge cases
Coverage is probabilistic unless a seed or input file is supplied. The guard checks pointer bounds, not semantic decode correctness.

## Test signals
Signals are successful million-iteration sanity runs, reproducible seed output on failures, and CI coverage for both instruction modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/insn_sanity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/objdump_reformat.awk -->
# sources/distributed-fs/ceph-client/arch/x86/tools/objdump_reformat.awk

## Purpose
`objdump_reformat.awk` normalizes objdump disassembly into the tab-separated instruction format consumed by `insn_decoder_test`.

## Important APIs, types, and functions
It tracks `prev_addr`, `prev_hex`, and `prev_mnemonic`, filters bad/prefix-only mnemonics with `bad_expr`, and splits `fwait` when objdump folds it into another x87 instruction.

## Control flow
For symbol lines it emits a compact symbol marker. For instruction lines it joins continuation byte lines, filters the previous instruction if needed, emits address/hex/mnemonic triples, and flushes the final instruction in `END`.

## State and persistence behavior
State is only the previous instruction accumulator in AWK variables.

## Dependencies and integration points
It depends on objdump text format and the decoder test's parser expecting tabs and contiguous hex byte text.

## Risks and edge cases
Objdump format changes can break parsing or cause malformed-line errors. Filtering bad instructions reduces false failures but can also hide decoder gaps.

## Test signals
Signals are successful `posttest` pipeline runs and spot checks around long instructions and x87 `fwait` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/objdump_reformat.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs.c

## Purpose
`relocs.c` is the shared ELF parser and relocation classifier for x86 kernel and real-mode relocation streams.

## Important APIs, types, and functions
Major pieces include ELF type macros, global ELF/section state, symbol regex policies, `regex_init()`, `read_ehdr()`, `read_shdrs()`, `read_strtabs()`, `read_symtabs()`, `read_relocs()`, `walk_relocs()`, `do_reloc32()`, `do_reloc64()`, `do_reloc_real()`, `emit_relocs()`, and `process()`.

## Control flow
The processor validates ELF metadata, loads sections/string/symbol/relocation tables, optionally reports absolute symbols/relocs or relocation info, otherwise walks allocated relocation sections and emits sorted relocation offsets. Kernel mode ignores PC-relative relocations and rejects unsafe absolute relocations. Realmode mode separates 16-bit segment relocations from 32-bit linear relocations.

## State and persistence behavior
State is process-static ELF header/section arrays and relocation vectors `relocs16`, `relocs32`, and `relocs64`. Output persistence is the binary or textual relocation stream consumed at boot/build time.

## Dependencies and integration points
It depends on ELF32/ELF64 specializations, regex whitelists for linker-script symbols, endian conversion helpers, and Linux build-time conventions for `pa_` realmode symbols.

## Risks and edge cases
Whitelists are security- and boot-correctness sensitive: accepting a bad absolute relocation can make a relocated kernel fail, while rejecting valid linker-script symbols can break builds. Realmode validation must distinguish segment and linear references.

## Test signals
Signals are build failures on unsupported relocation types, `--abs-relocs` audits, `--reloc-info` diagnostics across linkers, and successful boot of relocated kernels/realmode trampolines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.h -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs.h

## Purpose
`relocs.h` is the shared interface for the x86 relocation extraction host tool.

## Important APIs, types, and functions
It defines `enum symtype`, `ARRAY_SIZE`, the `die()` printf/noreturn declaration, and `process_32()`/`process_64()` prototypes with flags for realmode, text output, absolute-symbol reporting, and relocation info.

## Control flow
`relocs_common.c` parses CLI/options and dispatches to `process_32` or `process_64`; `relocs_32.c` and `relocs_64.c` include the common implementation with ELF-width macros.

## State and persistence behavior
No runtime kernel state exists; the header standardizes process-local parsing state across translation units.

## Dependencies and integration points
It depends on libc, ELF headers, endian helpers, regex, and `tools/le_byteshift.h`.

## Risks and edge cases
ABI mismatches between this header and `relocs.c` wrappers can produce wrong ELF class handling. Host endianness support is intentionally explicit.

## Test signals
Signals are clean host-tool compilation and relocation output for both 32-bit, 64-bit, and `--realmode` ELF files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs_32.c

## Purpose
`relocs_32.c` specializes the shared relocation extraction implementation for 32-bit i386 ELF files.

## Important APIs, types, and functions
It defines `ELF_BITS=32`, `ELF_MACHINE=EM_386`, `SHT_REL_TYPE=SHT_REL`, `Elf_Rel=ElfW(Rel)`, and ELF32 access macros before including `relocs.c`.

## Control flow
Compilation produces the 32-bit `process_32()` function. The common code then validates ELF headers, walks REL relocation sections, and emits kernel or realmode relocation offsets.

## State and persistence behavior
State is the static parser state instantiated from `relocs.c` for this translation unit.

## Dependencies and integration points
It depends on `relocs.h` and the common implementation honoring the macros defined here.

## Risks and edge cases
Wrong macro specialization would decode REL entries as RELA or accept the wrong machine type, corrupting relocation streams.

## Test signals
Signals are `relocs` processing of 32-bit vmlinux/realmode ELF and failure on unsupported relocation types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs_64.c

## Purpose
`relocs_64.c` specializes the shared relocation extraction implementation for x86-64 ELF files.

## Important APIs, types, and functions
It defines `ELF_BITS=64`, `ELF_MACHINE=EM_X86_64`, `SHT_REL_TYPE=SHT_RELA`, `Elf_Rel=Elf64_Rela`, and ELF64 access macros before including `relocs.c`.

## Control flow
The generated `process_64()` validates 64-bit ELF input, walks RELA relocation sections, rejects realmode mode, and emits 64-bit/32-bit relocation streams for compressed kernel relocation.

## State and persistence behavior
State is per-translation-unit static state from `relocs.c`, including 64-bit relocation collection.

## Dependencies and integration points
It depends on ELF64 relocation constants and a binutils environment that emits expected x86-64 relocation types.

## Risks and edge cases
Offsets must fit in 32 bits for output; unsupported or absolute relocations intentionally fail the build.

## Test signals
Signals are successful relocation extraction from 64-bit `vmlinux` and warnings/errors for newly introduced absolute relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_common.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/relocs_common.c

## Purpose
`relocs_common.c` contains the CLI front end for the `relocs` host tool and dispatches to 32-bit or 64-bit ELF processors.

## Important APIs, types, and functions
Important functions are `die()`, `usage()`, and `main()`. Options include `--abs-syms`, `--abs-relocs`, `--reloc-info`, `--text`, and `--realmode`.

## Control flow
`main()` parses options, opens the ELF file, reads `e_ident`, rewinds, chooses `process_64()` for `ELFCLASS64` or `process_32()` otherwise, and closes the file.

## State and persistence behavior
State is option flags, filename, file pointer, and the ELF identification buffer. It writes relocation data or diagnostics to standard output/error.

## Dependencies and integration points
It depends on `relocs.h`, libc file I/O, and the specialized processors compiled from `relocs_32.c`/`relocs_64.c`.

## Risks and edge cases
An unreadable or malformed file aborts the build. Dispatch is based only on `EI_CLASS`; detailed machine/type validation happens later.

## Test signals
Signals are CLI usage checks, realmode relocation generation, absolute-relocation audits, and kbuild invocations from realmode/compressed kernel rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/relocs_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.c -->
# sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.c

## Purpose
`vdso2c.c` is the host front end that converts raw and stripped vDSO shared objects into either raw output or a generated C `struct vdso_image` definition.

## Important APIs, types, and functions
Important data/functions include `required_syms[]`, `fail()`, endian access macros `GET_LE`/`PUT_LE`, dual inclusion of `vdso2c.h` for 64/32-bit `go*()`, `map_input()`, `go()`, and `main()`.

## Control flow
`main()` derives an image name from the output filename unless output ends in `.so`, mmaps raw and stripped inputs, opens output, and dispatches by ELF class. The generated code retains metadata needed for runtime vDSO mapping and exported symbol offsets.

## State and persistence behavior
State is process-local mapped input files and `outfilename` for cleanup on failure. Persistent output is generated C or raw `.so` data.

## Dependencies and integration points
It depends on Linux ELF/types headers, little-endian unaligned helpers, `vdso2c.h`, objcopy-produced stripped inputs, and required vDSO symbols.

## Risks and edge cases
The tool rejects dynamic relocations and malformed PT_LOAD/PT_DYNAMIC layout. Required symbol or section handling must preserve old userspace/debugger expectations around section tables and build-id notes.

## Test signals
Signals are successful vDSO build, generated image initialization, absence of dynamic relocations, and runtime vDSO symbol availability in user processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.h -->
# sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.h

## Purpose
`vdso2c.h` is a macro-parametric implementation included twice by `vdso2c.c` to generate 32-bit and 64-bit vDSO conversion routines.

## Important APIs, types, and functions
It defines `BITSFUNC(copy)`, `BITSFUNC(extract)`, and `BITSFUNC(go)`. The generated `go32()`/`go64()` parse ELF headers, program headers, dynamic tags, section headers, symbol tables, altinstructions, and exception tables.

## Control flow
The converter verifies a single load segment at offset/vaddr zero, rejects dynamic relocations, locates required symbols, optionally writes raw stripped output, otherwise emits a page-aligned `raw_data` array and `struct vdso_image` with symbol offsets and optional alt/extable metadata.

## State and persistence behavior
State is local parsing variables and collected signed-width symbol offsets. Persistent state is generated C arrays and image metadata.

## Dependencies and integration points
It depends on `ELF_BITS` macros, little-endian access helpers, `required_syms[]`, and vDSO linker scripts producing the expected ET_DYN shape.

## Risks and edge cases
Malformed section offsets can overrun input; the code explicitly checks extracted sections. Missing symbols or dynamic relocations fail hard because runtime vDSO mapping cannot fix them.

## Test signals
Signals are generated C compilation, vDSO initcall success, symbol-offset validation, and userland `clock_gettime`/signal trampoline behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/um/Kconfig

## Purpose
`um/Kconfig` selects x86 UML architecture capabilities and 32-bit versus 64-bit UML configuration.

## Important APIs, types, and functions
Important symbols are `UML_X86`, `64BIT`, `X86_32`, `X86_64`, `ARCH_HAS_SC_SIGNALS`, and `GENERIC_HWEIGHT`; it also sources `arch/x86/Kconfig.cpu`.

## Control flow
Kconfig derives bitness from `SUBARCH`, selects module ELF relocation style, old syscall ABI flags for 32-bit, queued locks, efficient unaligned access, and SMP support when `X86_CX8` exists.

## State and persistence behavior
State is compile-time configuration only.

## Dependencies and integration points
It depends on Kconfig CPU feature definitions and UML generic architecture configuration.

## Risks and edge cases
Wrong defaults can build a UML binary for the wrong host ABI or select incompatible syscall/module semantics.

## Test signals
Signals are `allnoconfig`/`defconfig` UML builds for i386 and x86_64 and inspection of selected module relocation formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/um/Makefile

## Purpose
`um/Makefile` selects x86 UML objects, subarchitecture library objects, and generated user-offset headers.

## Important APIs, types, and functions
It defines `BITS`, core `obj-y`, 32-bit `syscalls_32.o` and checksum/atomic helpers, 64-bit `mem_64.o`, `syscalls_64.o`, `vdso/`, `USER_OBJS`, `user-offsets.s`, and hardening exclusions for `stub_segv.o`.

## Control flow
Kbuild chooses 32/64-bit object names, compiles user-facing objects with `USER_CFLAGS`, generates `include/generated/user_constants.h` from `user-offsets.s`, and includes UML make rules.

## State and persistence behavior
State is build artifacts and generated constants used by ptrace/sysdep headers.

## Dependencies and integration points
It depends on `arch/um/scripts/Makefile.rules`, x86 library objects, and generated headers.

## Risks and edge cases
Missing generated offsets break register indexing shared with host ptrace/ucontext code. Hardening/profiling flags must not instrument syscall stubs.

## Test signals
Signals are complete UML builds for both bitnesses and correct regenerated `user_constants.h` after host ABI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/apic.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/apic.h

## Purpose
`apic.h` is an intentionally empty UML APIC shim so generic x86 includes resolve without exposing hardware APIC operations.

## Important APIs, types, and functions
It exports only include guards and no runtime functions or types.

## Control flow
Compilation includes the shim to satisfy generic header dependencies; no control flow is generated.

## State and persistence behavior
No runtime or persistent state exists.

## Dependencies and integration points
It depends on include ordering in the UML/x86 header stack.

## Risks and edge cases
Adding native hardware assumptions here would be incorrect for UML and could pull in unavailable definitions.

## Test signals
Signals are successful UML builds that include generic x86 headers without unresolved APIC/vector/feature dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/apic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/arch_hweight.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/arch_hweight.h

## Purpose
`arch_hweight.h` routes UML hweight operations to the generic bitops implementation.

## Important APIs, types, and functions
It includes `<asm-generic/bitops/arch_hweight.h>` and exports no local code.

## Control flow
All calls compile to generic helpers selected by the included header.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
It depends on generic bitops and `GENERIC_HWEIGHT` Kconfig selection.

## Risks and edge cases
The risk is performance rather than correctness if UML could use a better host intrinsic but does not.

## Test signals
Signals are bitops selftests/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/barrier.h

## Purpose
`barrier.h` defines UML/x86 memory barrier primitives using x86 instructions suitable for device and shared-memory ordering.

## Important APIs, types, and functions
APIs are `mb()`, `rmb()`, and `wmb()`. On 32-bit they use alternatives between locked stack ops and SSE fences; on 64-bit they directly emit `mfence`, `lfence`, and `sfence`.

## Control flow
Callers expand the macros inline, then generic barrier definitions fill in the rest of the Linux barrier API.

## State and persistence behavior
No state exists except alternative patching metadata on 32-bit builds.

## Dependencies and integration points
It depends on `cpufeatures.h`, `alternative.h`, and generic barrier fallbacks.

## Risks and edge cases
Instruction selection must be valid for the configured CPU feature set; barriers are required even on UP because UML can interact with devices/shared host state.

## Test signals
Signals are build coverage, lock/barrier tests, and runtime stability under SMP/time-travel/device I/O workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum.h

## Purpose
`checksum.h` provides UML/x86 checksum inline helpers for IP/TCP/UDP using x86 carry-chain assembly.

## Important APIs, types, and functions
Important APIs are `csum_partial()`, `csum_partial_copy_generic()`, `csum_fold()`, `csum_tcpudp_nofold()`, `csum_tcpudp_magic()`, `ip_fast_csum()`, and inclusion of bitness-specific checksum headers.

## Control flow
Networking code calls these helpers to fold partial sums, compute IPv4 header checksums, and build pseudo-header sums. Inline assembly accumulates carries through `addl/adcl` sequences.

## State and persistence behavior
No persistent state exists; all state is in registers and packet buffers passed by callers.

## Dependencies and integration points
It depends on Linux checksum types, IPv6/uaccess headers, and x86 lib checksum implementations linked through `um/Makefile`.

## Risks and edge cases
Inline assembly constraints must preserve modified input registers; checksum length/alignment assumptions match generic networking expectations.

## Test signals
Signals are networking checksum selftests, packet send/receive under UML, and build coverage for 32/64-bit includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_32.h

## Purpose
`checksum_32.h` adds 32-bit UML checksum helpers, including IPv6 pseudo-header checksum assembly.

## Important APIs, types, and functions
APIs are `ip_compute_csum()` and `_HAVE_ARCH_IPV6_CSUM` `csum_ipv6_magic()`.

## Control flow
`ip_compute_csum()` folds `csum_partial()`. `csum_ipv6_magic()` adds source/destination IPv6 words, length, protocol, and incoming sum with carry propagation before folding.

## State and persistence behavior
No persistent state exists.

## Dependencies and integration points
It depends on `csum_partial()`, `csum_fold()`, and network byte-order helpers.

## Risks and edge cases
Carry handling and htonl inputs must match Linux checksum ABI; 32-bit register constraints are architecture-specific.

## Test signals
Signals are IPv4/IPv6 networking tests and checksum validation against generic implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_64.h

## Purpose
`checksum_64.h` adds 64-bit UML checksum glue.

## Important APIs, types, and functions
It defines `add32_with_carry()` and declares `ip_compute_csum()`.

## Control flow
The inline helper performs a 32-bit add and folds carry with `adcl`; full checksum work is provided by linked 64-bit library code.

## State and persistence behavior
No persistent state exists.

## Dependencies and integration points
It depends on x86-64 checksum library objects selected by `um/Makefile`.

## Risks and edge cases
Assembly constraints must maintain 32-bit semantics on 64-bit registers.

## Test signals
Signals are 64-bit UML networking checksum tests and successful linking of `ip_compute_csum`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/desc.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/desc.h

## Purpose
`desc.h` provides the one descriptor predicate UML needs: checking whether an i386 TLS/LDT `user_desc` is empty.

## Important APIs, types, and functions
The API is `LDT_empty(info)`, comparing base, limit, contents, read/exec, 32-bit, page-limit, present, and usable fields.

## Control flow
TLS code uses the macro to identify cleared descriptors and decide whether to reject or synthesize an empty entry.

## State and persistence behavior
No state exists.

## Dependencies and integration points
It depends on Linux `struct user_desc` layout from x86 LDT headers.

## Risks and edge cases
Field-layout drift would misclassify TLS entries, breaking `set_thread_area` emulation.

## Test signals
Signals are 32-bit UML TLS/syscall tests and ptrace thread-area operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/elf.h

## Purpose
`elf.h` defines x86 UML ELF ABI details for executable loading, core dumps, relocation constants, and vDSO auxiliary vector exposure.

## Important APIs, types, and functions
Important macros include `elf_check_arch`, `ELF_CLASS`, `ELF_DATA`, `ELF_ARCH`, `ELF_PLAT_INIT`, `ELF_CORE_COPY_REGS`, `ELF_PLATFORM`, `ELF_HWCAP`, `ELF_ET_DYN_BASE`, and 64-bit `ARCH_DLINFO`/`AT_SYSINFO_EHDR`.

## Control flow
The ELF loader uses these macros to accept the correct machine type, initialize registers, set personality/platform/HWCAP aux values, and copy general registers into core-dump notes. On 64-bit it also maps the UML vDSO.

## State and persistence behavior
State is external `elf_aux_hwcap`, `elf_aux_platform`, and `um_vdso_addr`; otherwise definitions are compile-time ABI contracts.

## Dependencies and integration points
It depends on ptrace register macros, user structures, SKAS support, and `vdso/vma.c` on 64-bit.

## Risks and edge cases
Register order in core dumps must match userspace ABI. Wrong `ELF_ET_DYN_BASE` or vDSO aux data affects dynamic linker behavior.

## Test signals
Signals are running 32/64-bit UML userspace, core-dump register checks, and vDSO presence in auxv/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/irq_vectors.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/irq_vectors.h

## Purpose
`irq_vectors.h` is an intentionally empty UML IRQ-vector shim because UML does not program native x86 interrupt vector tables.

## Important APIs, types, and functions
It exports only include guards and no runtime functions or types.

## Control flow
Compilation includes the shim to satisfy generic header dependencies; no control flow is generated.

## State and persistence behavior
No runtime or persistent state exists.

## Dependencies and integration points
It depends on include ordering in the UML/x86 header stack.

## Risks and edge cases
Adding native hardware assumptions here would be incorrect for UML and could pull in unavailable definitions.

## Test signals
Signals are successful UML builds that include generic x86 headers without unresolved APIC/vector/feature dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/irq_vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/processor.h

## Purpose
`processor.h` defines UML/x86 processor-facing helpers and thread register access conventions.

## Important APIs, types, and functions
Important macros/functions are `KSTK_EIP`, `KSTK_ESP`, `KSTK_EBP`, `ARCH_IS_STACKGROW`, `native_pause()`, `cpu_relax()`, `task_pt_regs()`, and inclusion of bitness-specific `arch_thread` definitions.

## Control flow
Scheduler and memory-management code use these helpers to inspect saved host register arrays and decide stack growth. Busy-wait loops call `cpu_relax()`, which advances time-travel modes instead of only executing `pause`.

## State and persistence behavior
State lives in each task's `thread.regs` and `thread.arch`; this header only defines accessors.

## Dependencies and integration points
It depends on `sysdep/faultinfo.h`, `processor_32.h`/`processor_64.h`, time-travel internals, and generic processor definitions.

## Risks and edge cases
Stack-growth decisions depend on a correct saved SP. Time-travel modes require `cpu_relax()` to avoid infinite simulated CPU loops.

## Test signals
Signals are UML scheduler tests, stack-growth fault handling, and time-travel mode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_32.h

## Purpose
`processor_32.h` defines 32-bit UML thread architecture state, including TLS descriptors and debug registers.

## Important APIs, types, and functions
Types/macros include `struct uml_tls_struct`, `struct arch_thread`, `INIT_ARCH_THREAD`, `STACKSLOTS_PER_LINE`, `arch_flush_thread()`, `arch_copy_thread()`, `current_sp()`, and `current_bp()`.

## Control flow
Fork/exec/thread cleanup copies or clears TLS arrays; ptrace/sysrq code uses debug register and saved fault info fields.

## State and persistence behavior
Persistent per-task state includes three TLS descriptors with present/flushed bits, eight debug registers, a sequence number, and last fault info.

## Dependencies and integration points
It depends on `asm/segment.h`, `asm/ldt.h`, and 32-bit TLS management in `tls_32.c`.

## Risks and edge cases
TLS flush bookkeeping must stay synchronized with host thread-area state; stale descriptors can leak into another UML task.

## Test signals
Signals are 32-bit clone/set_thread_area, context-switch TLS tests, and ptrace debug-register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_64.h

## Purpose
`processor_64.h` defines the smaller 64-bit UML architecture thread state.

## Important APIs, types, and functions
It provides `struct arch_thread`, `INIT_ARCH_THREAD`, `STACKSLOTS_PER_LINE`, empty `arch_flush_thread()`/`arch_copy_thread()`, and inline `current_sp()`/`current_bp()`.

## Control flow
64-bit FS/GS base state lives in the saved ptrace register array, so flush/copy hooks do not need TLS descriptor management.

## State and persistence behavior
Persistent per-task state is debug registers, sequence number, and last fault info.

## Dependencies and integration points
It depends on `struct faultinfo` and register-offset definitions used elsewhere.

## Risks and edge cases
The main risk is assuming no extra per-thread x86 state needs copy/flush as host ABI evolves.

## Test signals
Signals are 64-bit context-switch, arch_prctl, and ptrace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/ptrace.h

## Purpose
`ptrace.h` maps UML `pt_regs` accessors onto the architecture-neutral `uml_pt_regs` saved-register structure.

## Important APIs, types, and functions
It defines regset enum values, `PT_REGS_*` macros, `user_mode()`, syscall-return helpers, thread-area prototypes/stubs, 64-bit high-register accessors, `arch_prctl()`, `user_stack_pointer()`, and `arch_switch_to()`.

## Control flow
Kernel code uses these macros to read/write saved user registers independent of host bitness. 32-bit builds route TLS ptrace operations to `tls_32.c`; 64-bit builds return `-ENOSYS` for thread-area and expose `arch_prctl`.

## State and persistence behavior
State is not stored here; macros access `task->thread.regs.regs` and embedded `uml_pt_regs` fields.

## Dependencies and integration points
It depends on `ptrace-generic.h`, generated frame offsets, bitness-specific sysdep ptrace headers, and task structures.

## Risks and edge cases
Accessor offsets must match `user-offsets.c`; otherwise signal, syscall, and ptrace code modify wrong registers.

## Test signals
Signals are ptrace selftests, signal delivery/return, syscall restart behavior, and core dump register checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/required-features.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/required-features.h

## Purpose
`required-features.h` is a placeholder needed by shared x86 headers when building UML, where native boot CPU feature enforcement is not used.

## Important APIs, types, and functions
It exports only include guards and no runtime functions or types.

## Control flow
Compilation includes the shim to satisfy generic header dependencies; no control flow is generated.

## State and persistence behavior
No runtime or persistent state exists.

## Dependencies and integration points
It depends on include ordering in the UML/x86 header stack.

## Risks and edge cases
Adding native hardware assumptions here would be incorrect for UML and could pull in unavailable definitions.

## Test signals
Signals are successful UML builds that include generic x86 headers without unresolved APIC/vector/feature dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/required-features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/segment.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/segment.h

## Purpose
`segment.h` defines UML TLS GDT entry range macros for 32-bit thread-area emulation.

## Important APIs, types, and functions
It declares `host_gdt_entry_tls_min` and defines `GDT_ENTRY_TLS_ENTRIES`, `GDT_ENTRY_TLS_MIN`, and `GDT_ENTRY_TLS_MAX`.

## Control flow
TLS code initializes `host_gdt_entry_tls_min` after probing the host, then uses these macros to validate requested TLS slots.

## State and persistence behavior
Global state is `host_gdt_entry_tls_min`, initialized by `tls_32.c`.

## Dependencies and integration points
It depends on host TLS probing in `os-Linux/tls.c` and Linux `user_desc` semantics.

## Risks and edge cases
Wrong host minimum index can make UML write the wrong GDT TLS slots on i386 or x86_64 hosts running 32-bit UML.

## Test signals
Signals are boot log host TLS detection and `set_thread_area`/`get_thread_area` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/spinlock.h

## Purpose
`spinlock.h` selects queued spinlock and queued rwlock implementations for UML/x86.

## Important APIs, types, and functions
It includes `asm/qspinlock.h` and `asm/qrwlock.h`.

## Control flow
Lock users receive the generic queued lock APIs through these includes.

## State and persistence behavior
No state is local; lock state lives in lock objects.

## Dependencies and integration points
It depends on Kconfig selections in `um/Kconfig`.

## Risks and edge cases
Incorrect lock implementation selection affects SMP UML synchronization.

## Test signals
Signals are lockdep, SMP boot, and concurrency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/syscall.h

## Purpose
`syscall.h` defines the UML syscall table function type and audit architecture selection.

## Important APIs, types, and functions
Important interfaces are `sys_call_ptr_t`, external `sys_call_table[]`, and `syscall_get_arch()` returning `AUDIT_ARCH_I386` or `AUDIT_ARCH_X86_64`.

## Control flow
Generic syscall code indexes `sys_call_table` and audit code calls `syscall_get_arch()` for records.

## State and persistence behavior
State is the external syscall table generated in `sys_call_table_*.c`.

## Dependencies and integration points
It depends on generic syscall helpers and UAPI audit constants.

## Risks and edge cases
The function pointer signature must match syscall table wrappers; wrong audit arch breaks audit/seccomp classification.

## Test signals
Signals are syscall execution, audit/seccomp tests, and table-size sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/vm-flags.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/vm-flags.h

## Purpose
`vm-flags.h` sets UML/x86 default VMA flags for data and stack mappings.

## Important APIs, types, and functions
It defines `VMA_DATA_DEFAULT_FLAGS` on 32-bit and `VMA_STACK_DEFAULT_FLAGS` on 64-bit.

## Control flow
MM code includes these defaults while creating VMAs, selecting executable data on 32-bit and executable grow-down stacks on 64-bit.

## State and persistence behavior
No state exists.

## Dependencies and integration points
It depends on generic VMA flag macros.

## Risks and edge cases
Defaults affect executable memory policy and compatibility; tightening flags can break old UML userspace expectations.

## Test signals
Signals are ELF loading, stack execution compatibility tests, and memory permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/vm-flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/bugs_32.c

## Purpose
`bugs_32.c` probes host CMOV support for 32-bit UML and diagnoses SIGILL in init caused by CMOV instructions.

## Important APIs, types, and functions
`arch_check_bugs()`, `arch_examine_signal()`, `cmov_sigill_test_handler()`, `host_has_cmov`, and `cmov_test_return`.

## Control flow
Boot installs a SIGILL handler, executes a CMOV test under setjmp/longjmp, records support, and later examines SIGILL instruction bytes in PID 1 to print a targeted diagnostic.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/bugs_64.c

## Purpose
`bugs_64.c` is the 64-bit UML placeholder for architecture bug checks.

## Important APIs, types, and functions
`arch_check_bugs()` and `arch_examine_signal()` are empty implementations.

## Control flow
Boot and signal paths call these hooks, but 64-bit UML has no CMOV-style compatibility check here.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/delay.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/delay.c

## Purpose
`delay.c` implements UML/x86 busy-wait delay primitives.

## Important APIs, types, and functions
`__delay()`, `__const_udelay()`, `__udelay()`, and `__ndelay()` are exported.

## Control flow
Callers scale microsecond/nanosecond requests through `loops_per_jiffy`, then spin in an assembly decrement loop.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/fault.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/fault.c

## Purpose
`fault.c` implements exception-table fixup for UML faults.

## Important APIs, types, and functions
`arch_fixup()` and external `search_exception_tables()` plus local `exception_table_entry` layout.

## Control flow
On a fault address, it searches exception tables and rewrites `UPT_IP(regs)` to the fixup target when found.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/mem_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/mem_64.c

## Purpose
`mem_64.c` names the 64-bit UML vDSO VMA.

## Important APIs, types, and functions
`arch_vma_name()` checks `um_vdso_addr`.

## Control flow
VM reporting code calls it and receives `[vdso]` when the VMA start equals the UML vDSO address.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/mem_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/Makefile

## Purpose
`os-Linux/Makefile` builds host-OS-facing x86 UML support.

## Important APIs, types, and functions
Objects are `registers.o`, `mcontext.o`, and 32-bit `tls.o`; `USER_OBJS` marks them for user-mode compilation rules.

## Control flow
Kbuild compiles these with UML user object rules so host libc/ucontext/ptrace APIs can be used.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/mcontext.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/mcontext.c

## Purpose
`mcontext.c` translates between host signal `mcontext_t` frames and UML `uml_pt_regs`, including floating-point/XSTATE and stub state.

## Important APIs, types, and functions
Important APIs are `get_regs_from_mc()`, `mc_set_rip()`, `get_mc_from_regs()`, `get_stub_state()`, and `set_stub_state()`.

## Control flow
Signal/stub paths copy GPRs between host ucontext and UML register arrays, locate FP state on the stub signal stack, copy XSTATE with size checks, convert i387/fxsave on 32-bit, and mark FS/GS base sync on 64-bit.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/mcontext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/registers.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/registers.c

## Purpose
`registers.c` handles host ptrace register-set discovery and floating-point register get/set for UML traced processes.

## Important APIs, types, and functions
`get_fp_registers()`, `put_fp_registers()`, `arch_init_registers()`, `get_thread_reg()`, globals `ptrace_regset` and `host_fp_size`.

## Control flow
Initialization probes `NT_X86_XSTATE`, falls back to legacy FP regsets, records host FP size, and later uses `PTRACE_GETREGSET`/`SETREGSET`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/registers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/tls.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/tls.c

## Purpose
`os-Linux/tls.c` is the host ptrace/syscall layer for i386 TLS descriptors.

## Important APIs, types, and functions
`check_host_supports_tls()`, `os_set_thread_area()`, and `os_get_thread_area()`.

## Control flow
Boot probes possible TLS GDT minima using `get_thread_area`; runtime ptrace helpers set/get child thread areas by entry number.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/tls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/ptrace.c

## Purpose
`ptrace.c` implements UML regset views and FP state conversions shared by ptrace, core dumps, and signal code.

## Important APIs, types, and functions
Key functions include i387/fxsr conversion helpers, `genregs_get()`, `genregs_set()`, `generic_fpregs_get/set()`, `task_user_regset_view()`, and `init_regset_xstate_info()`.

## Control flow
Regset operations iterate saved UML register slots, copy FP/XSTATE buffers, and expose i386/x86_64 note types through `user_uml_view`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/ptrace_32.c

## Purpose
`ptrace_32.c` implements 32-bit UML register get/set, USER-area peek/poke, TLS switch hook, and legacy FP ptrace requests.

## Important APIs, types, and functions
`arch_switch_to()`, `putreg()`, `poke_user()`, `getreg()`, `peek_user()`, and `subarch_ptrace()`.

## Control flow
Ptrace requests validate register offsets/selectors, update saved syscall number or debug registers, and delegate FP/FXSR copies to regsets.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/ptrace_64.c

## Purpose
`ptrace_64.c` implements 64-bit UML register get/set, USER-area access, and `PTRACE_ARCH_PRCTL`.

## Important APIs, types, and functions
`putreg()`, `poke_user()`, `getreg()`, `peek_user()`, and `subarch_ptrace()`.

## Control flow
The code validates canonical FS/GS bases and ring-3 segment selectors, maps user offsets to host register indices, handles debug registers, and routes FP/arch_prctl requests.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_user.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/ptrace_user.c

## Purpose
`ptrace_user.c` wraps host `PTRACE_GETREGS` and `PTRACE_SETREGS` for UML user-mode helpers.

## Important APIs, types, and functions
`ptrace_getregs()` and `ptrace_setregs()`.

## Control flow
Each wrapper calls host ptrace and returns `-errno` on failure.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/setjmp_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/setjmp_32.S

## Purpose
`setjmp_32.S` implements 32-bit kernel setjmp/longjmp used by UML host-side control transfers.

## Important APIs, types, and functions
Exports `kernel_setjmp` and `kernel_longjmp` with jmp_buf layout matching `archsetjmp_32.h`.

## Control flow
`kernel_setjmp` saves callee-saved registers, post-return ESP, and return address; `kernel_longjmp` restores them and jumps to saved EIP.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/setjmp_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/setjmp_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/setjmp_64.S

## Purpose
`setjmp_64.S` implements 64-bit kernel setjmp/longjmp for UML.

## Important APIs, types, and functions
Exports `kernel_setjmp` and `kernel_longjmp` with jmp_buf layout matching `archsetjmp_64.h`.

## Control flow
It saves/restores RBX, RSP, RBP, R12-R15, return RIP, and returns the longjmp value in EAX.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/setjmp_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp.h

## Purpose
`archsetjmp.h` defines or selects the host-side jump-buffer layout used by UML setjmp/longjmp code.

## Important APIs, types, and functions
It exposes `jmp_buf` layout fields and `JB_IP`/`JB_SP` aliases, or selects the 32/64-bit header and declares `get_thread_reg()`.

## Control flow
Assembly setjmp code writes the layout, and host-side helpers read saved IP/SP/BP values through these definitions.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp_32.h

## Purpose
`archsetjmp_32.h` defines or selects the host-side jump-buffer layout used by UML setjmp/longjmp code.

## Important APIs, types, and functions
It exposes `jmp_buf` layout fields and `JB_IP`/`JB_SP` aliases, or selects the 32/64-bit header and declares `get_thread_reg()`.

## Control flow
Assembly setjmp code writes the layout, and host-side helpers read saved IP/SP/BP values through these definitions.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp_64.h

## Purpose
`archsetjmp_64.h` defines or selects the host-side jump-buffer layout used by UML setjmp/longjmp code.

## Important APIs, types, and functions
It exposes `jmp_buf` layout fields and `JB_IP`/`JB_SP` aliases, or selects the 32/64-bit header and declares `get_thread_reg()`.

## Control flow
Assembly setjmp code writes the layout, and host-side helpers read saved IP/SP/BP values through these definitions.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/archsetjmp_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo.h

## Purpose
`faultinfo.h` defines or selects x86 UML fault metadata extracted from host traps.

## Important APIs, types, and functions
It provides `struct faultinfo`, `FAULT_WRITE`, `FAULT_ADDRESS`, `SEGV_IS_FIXABLE`, `PTRACE_FULL_FAULTINFO`, and the nofault backtrack macro where bitness-specific.

## Control flow
Signal/ptrace code fills the structure from host trap context; fault handlers inspect it to decide page fault handling and fixups.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_32.h

## Purpose
`faultinfo_32.h` defines or selects x86 UML fault metadata extracted from host traps.

## Important APIs, types, and functions
It provides `struct faultinfo`, `FAULT_WRITE`, `FAULT_ADDRESS`, `SEGV_IS_FIXABLE`, `PTRACE_FULL_FAULTINFO`, and the nofault backtrack macro where bitness-specific.

## Control flow
Signal/ptrace code fills the structure from host trap context; fault handlers inspect it to decide page fault handling and fixups.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_64.h

## Purpose
`faultinfo_64.h` defines or selects x86 UML fault metadata extracted from host traps.

## Important APIs, types, and functions
It provides `struct faultinfo`, `FAULT_WRITE`, `FAULT_ADDRESS`, `SEGV_IS_FIXABLE`, `PTRACE_FULL_FAULTINFO`, and the nofault backtrack macro where bitness-specific.

## Control flow
Signal/ptrace code fills the structure from host trap context; fault handlers inspect it to decide page fault handling and fixups.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/mcontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/mcontext.h

## Purpose
`mcontext.h` declares host mcontext to UML register conversion APIs and fault-info extraction macros.

## Important APIs, types, and functions
It declares `get_regs_from_mc()`, `get_mc_from_regs()`, `get_stub_state()`, `set_stub_state()`, and `GET_FAULTINFO_FROM_MC()`.

## Control flow
Host signal handlers pass `ucontext_t` mcontext into these helpers so UML can save/restore interrupted guest register state.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/mcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace.h

## Purpose
`ptrace.h` maps host ptrace register arrays to UML register accessor macros.

## Important APIs, types, and functions
It defines `REGS_*`, `UPT_*`, syscall-argument macros, host register indices, USER-area offsets, and `struct uml_pt_regs` where applicable.

## Control flow
All UML signal/syscall/ptrace paths access saved registers through these macros, with bitness-specific argument order for i386 versus x86-64.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_32.h

## Purpose
`ptrace_32.h` maps host ptrace register arrays to UML register accessor macros.

## Important APIs, types, and functions
It defines `REGS_*`, `UPT_*`, syscall-argument macros, host register indices, USER-area offsets, and `struct uml_pt_regs` where applicable.

## Control flow
All UML signal/syscall/ptrace paths access saved registers through these macros, with bitness-specific argument order for i386 versus x86-64.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_64.h

## Purpose
`ptrace_64.h` maps host ptrace register arrays to UML register accessor macros.

## Important APIs, types, and functions
It defines `REGS_*`, `UPT_*`, syscall-argument macros, host register indices, USER-area offsets, and `struct uml_pt_regs` where applicable.

## Control flow
All UML signal/syscall/ptrace paths access saved registers through these macros, with bitness-specific argument order for i386 versus x86-64.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_user.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_user.h

## Purpose
`ptrace_user.h` maps host ptrace register arrays to UML register accessor macros.

## Important APIs, types, and functions
It defines `REGS_*`, `UPT_*`, syscall-argument macros, host register indices, USER-area offsets, and `struct uml_pt_regs` where applicable.

## Control flow
All UML signal/syscall/ptrace paths access saved registers through these macros, with bitness-specific argument order for i386 versus x86-64.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub-data.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub-data.h

## Purpose
`stub-data.h` defines syscall-stub support used by UML code executing in a traced host process.

## Important APIs, types, and functions
It provides `stub_syscall0..6`, `trap_myself()`, `get_stub_data()`, `stub_start()`, arch stub data, and seccomp restore helpers depending on bitness.

## Control flow
Stub code issues raw host syscalls, stores per-arch sync state, obtains its adjacent stub-data page, and traps back to the UML monitor when needed.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub.h

## Purpose
`stub.h` defines syscall-stub support used by UML code executing in a traced host process.

## Important APIs, types, and functions
It provides `stub_syscall0..6`, `trap_myself()`, `get_stub_data()`, `stub_start()`, arch stub data, and seccomp restore helpers depending on bitness.

## Control flow
Stub code issues raw host syscalls, stores per-arch sync state, obtains its adjacent stub-data page, and traps back to the UML monitor when needed.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_32.h

## Purpose
`stub_32.h` defines syscall-stub support used by UML code executing in a traced host process.

## Important APIs, types, and functions
It provides `stub_syscall0..6`, `trap_myself()`, `get_stub_data()`, `stub_start()`, arch stub data, and seccomp restore helpers depending on bitness.

## Control flow
Stub code issues raw host syscalls, stores per-arch sync state, obtains its adjacent stub-data page, and traps back to the UML monitor when needed.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_64.h

## Purpose
`stub_64.h` defines syscall-stub support used by UML code executing in a traced host process.

## Important APIs, types, and functions
It provides `stub_syscall0..6`, `trap_myself()`, `get_stub_data()`, `stub_start()`, arch stub data, and seccomp restore helpers depending on bitness.

## Control flow
Stub code issues raw host syscalls, stores per-arch sync state, obtains its adjacent stub-data page, and traps back to the UML monitor when needed.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/tls.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/tls.h

## Purpose
`tls.h` provides UML x86 sysdep definitions.

## Important APIs, types, and functions
It defines bitness-sensitive typedefs, constants, or externs used by host-facing UML code.

## Control flow
The definitions are selected at compile time and consumed by adjacent sysdep implementation files.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/signal.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/signal.c

## Purpose
`signal.c` builds and restores x86 UML user signal frames for old i386, RT i386, and x86-64 signal ABIs.

## Important APIs, types, and functions
Important functions are `copy_sc_from_user()`, `copy_sc_to_user()`, `setup_signal_stack_sc()`, `setup_signal_stack_si()`, `sigreturn`, and `rt_sigreturn`.

## Control flow
Delivery copies GPR/fault/FP state to user sigcontext/ucontext frames, writes restorer signatures, aligns stacks per ABI, sets handler arguments/registers, and return syscalls restore signal masks and register state.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/stub_segv.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/stub_segv.c

## Purpose
`stub_segv.c` provides the signal handler used inside UML syscall stubs to capture fault information.

## Important APIs, types, and functions
`stub_segv_handler()` is placed in `.__syscall_stub`.

## Control flow
On SIGSEGV it extracts fault info from host ucontext into stub data and traps back to the UML monitor with `int3`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/stub_segv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_32.c

## Purpose
`sys_call_table_32.c` builds the i386 UML syscall dispatch table.

## Important APIs, types, and functions
It maps unsupported hardware syscalls `iopl`, `ioperm`, `vm86old`, and `vm86` to `sys_ni_syscall`, includes `asm/syscalls_32.h`, and exports `sys_call_table` plus `syscall_table_size`.

## Control flow
Preprocessor expansion first declares syscall prototypes, then emits the function pointer table.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_64.c

## Purpose
`sys_call_table_64.c` builds the x86-64 UML syscall dispatch table.

## Important APIs, types, and functions
It maps unsupported `iopl`/`ioperm` to `sys_ni_syscall`, includes `asm/syscalls_64.h`, and exports `sys_call_table` plus `syscall_table_size`.

## Control flow
Preprocessor expansion declares syscall prototypes and then fills the cacheline-aligned table.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/syscalls_32.c

## Purpose
`syscalls_32.c` supplies the 32-bit UML `arch_prctl` syscall stub.

## Important APIs, types, and functions
`SYSCALL_DEFINE2(arch_prctl)` always returns `-EINVAL`.

## Control flow
The syscall table can expose the symbol, but i386 UML does not implement x86-64 FS/GS base arch_prctl semantics.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/syscalls_64.c

## Purpose
`syscalls_64.c` implements 64-bit UML `arch_prctl`, context-switch no-op, and mmap offset validation.

## Important APIs, types, and functions
`arch_prctl()`, `SYSCALL_DEFINE2(arch_prctl)`, `arch_switch_to()`, and `SYSCALL_DEFINE6(mmap)`.

## Control flow
FS/GS base options read/write saved register slots; mmap rejects unaligned byte offsets and calls `ksys_mmap_pgoff`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sysrq_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/sysrq_32.c

## Purpose
`sysrq_32.c` prints 32-bit UML register state for diagnostics.

## Important APIs, types, and functions
`show_regs()` prints EIP/ESP/EFLAGS and i386 GPR/segment fields.

## Control flow
Sysrq/oops paths pass saved pt_regs and the function formats register values with taint/CPU context.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sysrq_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sysrq_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/sysrq_64.c

## Purpose
`sysrq_64.c` prints 64-bit UML register state for diagnostics.

## Important APIs, types, and functions
`show_regs()` prints task/module/release context and RIP/RSP/EFLAGS plus RAX-R15.

## Control flow
Sysrq/oops paths format saved pt_regs using `PT_REGS_*` accessors.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sysrq_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/tls_32.c

## Purpose
`tls_32.c` implements 32-bit UML TLS descriptor management and `set_thread_area`/`get_thread_area` emulation.

## Important APIs, types, and functions
Important functions are `do_set_thread_area()`, `get_free_idx()`, `load_TLS()`, `needs_TLS_update()`, `clear_flushed_tls()`, `arch_switch_tls()`, `arch_set_tls()`, syscall handlers, ptrace thread-area helpers, and `__setup_host_supports_tls()`.

## Control flow
Boot probes host TLS support. Runtime stores guest TLS descriptors in task state, flushes them to host via ptrace or seccomp stub sync on context switch, and services syscalls/ptrace by reading/writing the task TLS array.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/tls_64.c

## Purpose
`tls_64.c` implements the minimal 64-bit UML TLS hooks.

## Important APIs, types, and functions
`clear_flushed_tls()` is empty and `arch_set_tls()` stores CLONE_SETTLS value into the saved FS_BASE register slot.

## Control flow
Context switches need no explicit TLS descriptor load because FS/GS base travels in the ptrace register set.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/user-offsets.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/user-offsets.c

## Purpose
`user-offsets.c` generates host register and syscall constants for UML user-space helper code.

## Important APIs, types, and functions
`foo()` emits `HOST_*`, `UM_FRAME_SIZE`, poll constants, and mmap protection constants through kbuild `DEFINE`/`COMMENT`.

## Control flow
Kbuild compiles to assembly and converts the definitions into `include/generated/user_constants.h`, shared by sysdep ptrace/stub code.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/user-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/Makefile

## Purpose
`um/vdso/Makefile` builds the 64-bit UML vDSO shared object and embeds it into the kernel.

## Important APIs, types, and functions
It defines vDSO objects `vdso-note.o` and `um_vdso.o`, kernel objects `vdso.o` and `vma.o`, generated targets `vdso.so`, `vdso.so.dbg`, `vdso.lds`, and special PIC/shared linker flags.

## Control flow
Kbuild compiles vDSO objects with user-style PIC flags and no profiling, links `vdso.so.dbg` with the linker script, strips it to `vdso.so`, and rebuilds `vdso.o` from the embedded binary.

## State and persistence behavior
State is build artifacts and the embedded vDSO image.

## Dependencies and integration points
It depends on 64-bit compiler/linker support, `vdso.lds.S`, objcopy, and UML build rules.

## Risks and edge cases
Wrong flags can introduce undefined symbols, stack protectors, profiling calls, or non-vDSO-safe relocations.

## Test signals
Signals are successful vDSO link, readelf checks on the shared object, and runtime `[vdso]` mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/um_vdso.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/um_vdso.c

## Purpose
`um_vdso.c` implements UML vDSO time entry points as simple syscall trampolines so UML can trap them normally.

## Important APIs, types, and functions
Exports `__vdso_clock_gettime`, `clock_gettime` alias, `__vdso_gettimeofday`, `gettimeofday` alias, `__vdso_time`, and `time` alias.

## Control flow
Each function loads the corresponding syscall number and arguments into x86-64 syscall registers and executes `syscall`, returning the host/UML syscall result.

## State and persistence behavior
No persistent state exists; calls operate on user-provided time buffers.

## Dependencies and integration points
It depends on x86-64 syscall ABI, `asm/unistd.h`, and vDSO linker version exports.

## Risks and edge cases
Because these run in userspace, profiling/stack protector dependencies must be absent. Register clobbers must match syscall ABI.

## Test signals
Signals are userland calls to `clock_gettime`, `gettimeofday`, and `time` through the vDSO and fallback syscall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/um_vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-layout.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-layout.lds.S

## Purpose
`vdso-layout.lds.S` defines the shared layout for the UML x86-64 vDSO ELF image.

## Important APIs, types, and functions
It lays out hash/dynamic/string/symbol/version/note/eh_frame/rodata/data/alt/text sections and declares PHDRs for one read-execute load segment plus dynamic, note, and GNU EH frame headers.

## Control flow
The linker places the DSO at `VDSO_PRELINK + SIZEOF_HEADERS`, keeps code aligned away from data, and marks explicit program headers so the vDSO has the expected read-only executable shape.

## State and persistence behavior
State is linker-script layout only.

## Dependencies and integration points
It depends on `VDSO_PRELINK` from `vdso.lds.S` and linker support for the specified PHDR types.

## Risks and edge cases
Layout mistakes can break dynamic symbol lookup, unwinding, build-id/note discovery, or runtime mapping permissions.

## Test signals
Signals are readelf layout checks and successful userland vDSO symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-layout.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-note.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-note.S

## Purpose
`vdso-note.S` emits the Linux version note inside the UML vDSO.

## Important APIs, types, and functions
It uses `ELFNOTE_START/END` to write a `Linux` note containing `LINUX_VERSION_CODE`.

## Control flow
The note is linked into the vDSO PT_NOTE segment for userspace tooling.

## State and persistence behavior
No mutable state exists.

## Dependencies and integration points
It depends on Linux elfnote, uts, and version headers.

## Risks and edge cases
Incorrect note formatting can confuse debuggers or ELF parsers.

## Test signals
Signals are readelf note inspection on `vdso.so`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso-note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.S

## Purpose
`vdso.S` embeds the built UML vDSO shared object into kernel init data.

## Important APIs, types, and functions
It exports `vdso_start` and `vdso_end` around an `.incbin` of `arch/x86/um/vdso/vdso.so`.

## Control flow
The kernel link includes the stripped vDSO bytes; `vma.c` copies them into a page during init.

## State and persistence behavior
State is embedded init data only until copied to `um_vdso`.

## Dependencies and integration points
It depends on `vdso.so` being built first and linkage macros for init data.

## Risks and edge cases
Stale or oversized embedded bytes break vDSO mapping.

## Test signals
Signals are successful link and `vma.c` size check under one page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.lds.S

## Purpose
`vdso.lds.S` chooses the UML x86-64 vDSO prelink address and exported symbol version set.

## Important APIs, types, and functions
It defines `VDSO_PRELINK`, includes `vdso-layout.lds.S`, exports `clock_gettime`, `__vdso_clock_gettime`, `gettimeofday`, `__vdso_gettimeofday`, `time`, and `__vdso_time` under `LINUX_2.6`, and defines `VDSO64_PRELINK`.

## Control flow
The linker uses this as both layout and version script when building `vdso.so.dbg`.

## State and persistence behavior
State is build-time symbol visibility/versioning.

## Dependencies and integration points
It depends on the symbols implemented by `um_vdso.c`.

## Risks and edge cases
Version-script omissions make dynamic linker lookups fail; wrong prelink constants can desynchronize kernel macros and DSO layout.

## Test signals
Signals are `readelf --dyn-syms --version-info` checks and runtime auxv/vDSO calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vma.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/vma.c

## Purpose
`vma.c` allocates and maps the UML vDSO page into new 64-bit user address spaces.

## Important APIs, types, and functions
Important symbols are `um_vdso_addr`, static `um_vdso`, `init_vdso()`, and `arch_setup_additional_pages()`.

## Control flow
At subsys init it checks the embedded DSO fits in one page, chooses `task_size - PAGE_SIZE`, allocates a page, and copies the image. During exec it installs a special read/exec mapping at `um_vdso_addr`.

## State and persistence behavior
Persistent state is the allocated `um_vdso` page and exported `um_vdso_addr` used by ELF auxv and VMA naming.

## Dependencies and integration points
It depends on embedded `vdso_start`/`vdso_end`, mm special mappings, and ELF `ARCH_DLINFO`.

## Risks and edge cases
Failure to allocate panics. Mapping must hold `mmap_write_lock` and preserve special mapping semantics.

## Test signals
Signals are `/proc/pid/maps` showing `[vdso]`, auxv `AT_SYSINFO_EHDR`, and successful vDSO time calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/video/Makefile

## Purpose
`video/Makefile` builds the common x86 video helper object.

## Important APIs, types, and functions
It adds `video-common.o` to `obj-y`.

## Control flow
Kbuild links the helper whenever the x86 video directory is included.

## State and persistence behavior
No runtime state exists in the Makefile.

## Dependencies and integration points
It depends on parent x86 architecture kbuild selection.

## Risks and edge cases
The risk is only omitted helper linkage for framebuffer/primary-device users.

## Test signals
Signals are successful x86 build and exported symbols from `video-common.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/video-common.c -->
# sources/distributed-fs/ceph-client/arch/x86/video/video-common.c

## Purpose
`video-common.c` provides common x86 framebuffer page-protection and primary-display detection helpers.

## Important APIs, types, and functions
Exports `pgprot_framebuffer()` and `video_is_primary_device()`.

## Control flow
Framebuffer mappings clear cache mode bits and use UC-minus on CPUs newer than 386. Primary-device detection checks PCI display class, VGA default device, and optionally whether PCI BARs overlap resources derived from `screen_info`.

## State and persistence behavior
No long-lived state is local; it reads `boot_cpu_data`, `sysfb_primary_display`, VGA arbiter state, and PCI resources.

## Dependencies and integration points
It depends on PCI, sysfb/screen_info, VGA arbitration, cache-mode helpers, and `asm/video.h`.

## Risks and edge cases
Cache attributes affect framebuffer correctness/performance. Primary detection can be wrong if firmware screen_info resources do not match PCI BARs.

## Test signals
Signals are framebuffer mmap behavior, boot console handoff, DRM/fbdev primary-device selection, and PCI resource matching tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/video-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/Makefile

## Purpose
`virt/Makefile` selects x86 virtualization support directories and common hardware enablement glue.

## Important APIs, types, and functions
It always descends into `svm/` and `vmx/`; it builds `hw.o` when `CONFIG_KVM_X86` is built-in or modular.

## Control flow
Kbuild composes vendor-specific virtualization support and common VMX/SVM enablement code for KVM consumers.

## State and persistence behavior
No runtime state is held in the Makefile.

## Dependencies and integration points
It depends on KVM and vendor virtualization configuration symbols.

## Risks and edge cases
Wrong conditional substitution would omit `hw.o` for modular KVM, breaking exported virtualization reference APIs.

## Test signals
Signals are built-in and modular KVM builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/hw.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/hw.c

## Purpose
`hw.c` centralizes host CPU VMX/SVM enablement references, emergency virtualization shutdown, and KVM emergency callback registration.

## Important APIs, types, and functions
Important APIs are `x86_virt_register_emergency_callback()`, `x86_virt_unregister_emergency_callback()`, `x86_virt_get_ref()`, `x86_virt_put_ref()`, `x86_virt_emergency_disable_virtualization_cpu()`, and `x86_virt_init()`. VMX helpers allocate per-CPU root VMCS pages; SVM helpers set/clear EFER.SVME.

## Control flow
Init probes VMX and SVM, installs exactly one `virt_ops` provider, and clears VMX capability on failure. At runtime per-CPU reference counts enable virtualization on first user and disable on last put. Emergency paths set `virt_rebooting`, invoke KVM callbacks, and turn off VMX/SVM with IRQs disabled so INIT/reboot can proceed.

## State and persistence behavior
Persistent state includes `virt_ops`, exported `virt_rebooting`, per-CPU `virtualization_nr_users`, optional per-CPU `root_vmcs`, and an RCU-protected KVM callback.

## Dependencies and integration points
It depends on CPU feature probing, VMX MSRs/VMCS layout, SVM EFER bits, Intel PT VMX handling, RCU, preemption guards, and KVM exports.

## Risks and edge cases
Reference-count imbalance can leave virtualization enabled or disabled incorrectly. Emergency paths run in constrained contexts and intentionally swallow VMXOFF/STGI faults. VMX and SVM both appearing is treated as invalid.

## Test signals
Signals are KVM load/unload, CPU hotplug, reboot/crash paths, Intel PT interaction, and warnings for VMXON/VMXOFF faults or refcount misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/svm/Makefile

## Purpose
`virt/svm/Makefile` selects AMD SVM virtualization support outside KVM proper.

## Important APIs, types, and functions
It builds `sev.o` for `CONFIG_KVM_AMD_SEV` and `cmdline.o` for `CONFIG_CPU_SUP_AMD`.

## Control flow
Kbuild includes SEV-SNP RMP host support and SEV command-line parsing according to configuration.

## State and persistence behavior
No runtime state is held here.

## Dependencies and integration points
It depends on AMD CPU and KVM AMD SEV config symbols.

## Risks and edge cases
A wrong dependency can omit SEV command-line parsing or RMP support from capable hosts.

## Test signals
Signals are AMD SEV/SNP configured builds and symbol availability for CCP/KVM modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/cmdline.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/svm/cmdline.c

## Purpose
`cmdline.c` parses the `sev=` kernel command-line options for AMD SEV/SNP host support.

## Important APIs, types, and functions
It defines global `sev_cfg`, `init_sev_config()`, and the `__setup("sev=", ...)` hook. Recognized options are `debug` and `nosnp` outside hypervisor guests.

## Control flow
Boot parsing splits the option string by comma, sets debug mode, or clears SNP CPU/platform capabilities for `nosnp` on bare metal. Unknown or disallowed options log an informational warning.

## State and persistence behavior
Persistent state is `sev_cfg.debug` and CPU/platform capability bits modified during boot.

## Dependencies and integration points
It depends on `asm/sev-common.h`, CPU feature helpers, confidential-computing platform attributes, and command-line setup infrastructure.

## Risks and edge cases
`nosnp` is deliberately ignored under a hypervisor, so deployment assumptions must account for guest context. Unknown tokens are nonfatal.

## Test signals
Signals are boot logs for `sev=debug`, `sev=nosnp`, and unknown options, plus SNP capability visibility after parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/sev.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/svm/sev.c

## Purpose
`sev.c` implements AMD SEV-SNP host RMP table discovery, setup, lookup, update, direct-map adjustment, page leak tracking, and SNP enable/shutdown preparation.

## Important APIs, types, and functions
Key types are `struct rmpentry`, `struct rmpentry_raw`, and `struct rmp_segment_desc`. Major APIs include `snp_probe_rmptable_info()`, `snp_fixup_e820_tables()`, `snp_rmptable_init()`, `snp_prepare()`, `snp_shutdown()`, `snp_lookup_rmpentry()`, `snp_dump_hva_rmpentry()`, `psmash()`, `rmp_make_private()`, `rmp_make_shared()`, `__snp_leak_pages()`, and `kdump_sev_callback()`.

## Control flow
Boot probes contiguous or segmented RMP MSRs/CPUID, reserves unaligned RMP edges in e820/memblock, maps RMP bookkeeping and segment tables, validates RAM coverage, and enables SNP through MSR programming on all CPUs after clearing RMP and HSAVE state. Runtime lookups use RMPREAD when available or raw mapped RMP entries otherwise, with nospec bounds. RMPUPDATE transitions pages between shared/private, splitting large direct-map mappings when 4K private pages could conflict with host writes.

## State and persistence behavior
Persistent global state includes RMP configuration/base/size, segment table descriptors, bookkeeping mapping, leaked-page list and count, and `crash_kexec_post_notifiers`. RMP hardware state persists in firmware-owned RMP memory and CPU MSRs.

## Dependencies and integration points
It depends on AMD SNP/SME MSRs and instructions (`RMPREAD`, `RMPUPDATE`, `PSMASH`), IOMMU SNP enablement, e820/memblock, direct-map page attribute APIs, CPUID leaf `0x80000025`, CCP firmware sequencing, KVM users of exported RMP functions, and crash/kdump callbacks.

## Risks and edge cases
Coverage and alignment checks are safety-critical: an RMP table that misses RAM or overlaps 2 MiB boundaries can cause fatal RMP faults. RMP updates can fail on overlap and are retried, but other failures dump RMP state and stack. Raw RMP format is model-specific when RMPREAD is absent. Leaked pages are intentionally withheld from the allocator.

## Test signals
Signals include SNP-capable AMD boot, RMP table probe logs, SNP_INIT/SHUTDOWN via CCP, KVM SNP guest private/shared page transitions, RMP fault diagnostics, kdump with SNP enabled, and direct-map split warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/sev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/Makefile

## Purpose
`virt/vmx/Makefile` selects Intel VMX-side virtualization support directories.

## Important APIs, types, and functions
It descends into `tdx/` when `CONFIG_INTEL_TDX_HOST` is enabled.

## Control flow
Kbuild includes host TDX support only for TDX host configurations.

## State and persistence behavior
No runtime state is stored here.

## Dependencies and integration points
It depends on Intel TDX host configuration.

## Risks and edge cases
Incorrect selection can omit SEAMCALL/TDX module support on TDX-capable hosts.

## Test signals
Signals are TDX host configured builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/Makefile

## Purpose
`virt/vmx/tdx/Makefile` builds the Intel TDX host support objects in the TDX subdirectory.

## Important APIs, types, and functions
It adds `seamcall.o` and `tdx.o` to `obj-y`.

## Control flow
Kbuild links the SEAMCALL assembly wrappers with the higher-level TDX host implementation.

## State and persistence behavior
No runtime state is held in the Makefile.

## Dependencies and integration points
It depends on parent `CONFIG_INTEL_TDX_HOST` selection and the sibling `tdx.o` source.

## Risks and edge cases
Object omission would leave TDX module call sites unresolved.

## Test signals
Signals are TDX host build/link success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/seamcall.S -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/seamcall.S

## Purpose
`seamcall.S` provides host-side assembly wrappers for Intel SEAMCALL into P-SEAMLDR or the TDX module.

## Important APIs, types, and functions
Exports `__seamcall`, `__seamcall_ret`, and noinstr `__seamcall_saved_ret`, all implemented through `TDX_MODULE_CALL` from `tdxcall.S`.

## Control flow
Callers pass the leaf in RDI and a `struct tdx_module_args` pointer in RSI. The macro moves inputs into SEAMCALL registers, executes the module call, optionally saves outputs, and returns either `TDX_SEAMCALL_VMFAILINVALID` or the leaf completion status. The saved variant preserves/saves all argument registers for KVM TDH.VP.ENTER use.

## State and persistence behavior
No file-local data state exists; architectural state is the SEAMCALL register ABI and output fields written to the args structure.

## Dependencies and integration points
It depends on `tdxcall.S`, linkage/frame macros, TDX module ABI, and noinstr constraints for KVM entry paths.

## Risks and edge cases
Register clobber/save semantics are critical. Instrumentation is forbidden for the saved wrapper because KVM uses it in a non-instrumentable path.

## Test signals
Signals are TDX module initialization, KVM TDX entry/exit tests, objtool/noinstr validation, and SEAMCALL failure status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/seamcall.S -->
