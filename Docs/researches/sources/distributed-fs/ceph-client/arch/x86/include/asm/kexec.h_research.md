<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec.h

## Purpose
x86 kexec/crash-kernel architecture contract for relocation code, crash register capture, kimage architecture data, purgatory relocation, and crash hotplug support. The header is 237 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/bits.h>`; `#include <linux/string.h>`; `#include <linux/kernel.h>`; `#include <asm/asm.h>`; `#include <asm/page.h>`; `#include <asm/ptrace.h>`

Notable constants/macros: `#define _ASM_X86_KEXEC_H`; `#define RELOC_KERNEL_PRESERVE_CONTEXT BIT(0)`; `#define RELOC_KERNEL_CACHE_INCOHERENT BIT(1)`; `#define ARCH_HAS_KIMAGE_ARCH`; `#define arch_kexec_post_alloc_pages arch_kexec_post_alloc_pages`; `#define arch_kexec_pre_free_pages arch_kexec_pre_free_pages`; `#define arch_kexec_protect_crashkres arch_kexec_protect_crashkres`; `#define arch_kexec_unprotect_crashkres arch_kexec_unprotect_crashkres`; `#define arch_kexec_apply_relocations_add arch_kexec_apply_relocations_add`; `#define arch_kimage_file_post_load_cleanup arch_kimage_file_post_load_cleanup`; `#define arch_crash_handle_hotplug_event arch_crash_handle_hotplug_event`; `#define arch_crash_hotplug_support arch_crash_hotplug_support`; `#define crash_get_elfcorehdr_size arch_crash_get_elfcorehdr_size`

Notable declarations and inline helpers: `#define _ASM_X86_KEXEC_H`; `# define PA_CONTROL_PAGE 0`; `# define VA_CONTROL_PAGE 1`; `# define PA_PGD 2`; `# define PA_SWAP_PAGE 3`; `# define PAGES_NR 4`; `# define KEXEC_DEBUG_EXC_HANDLER_SIZE 6 /* PUSHI, PUSHI, 2-byte JMP */`; `#define RELOC_KERNEL_PRESERVE_CONTEXT BIT(0)`; `#define RELOC_KERNEL_CACHE_INCOHERENT BIT(1)`; `# define KEXEC_CONTROL_PAGE_SIZE 4096`; `# define KEXEC_CONTROL_CODE_MAX_SIZE 2048`; `struct kimage;`; `# define KEXEC_SOURCE_MEMORY_LIMIT (-1UL)`; `# define KEXEC_DESTINATION_MEMORY_LIMIT (-1UL)`; `# define KEXEC_CONTROL_MEMORY_LIMIT TASK_SIZE`; `# define KEXEC_ARCH KEXEC_ARCH_386`; `# define vmcore_elf_check_arch_cross(x) ((x)->e_machine == EM_X86_64)`; `# define KEXEC_SOURCE_MEMORY_LIMIT (MAXMEM-1)`; `# define KEXEC_DESTINATION_MEMORY_LIMIT (MAXMEM-1)`; `# define KEXEC_CONTROL_MEMORY_LIMIT (MAXMEM-1)`; `# define KEXEC_ARCH KEXEC_ARCH_X86_64`; `extern unsigned long kexec_va_control_page;`; `extern unsigned long kexec_pa_table_page;`; `extern unsigned long kexec_pa_swap_page;`

## Control Flow
Normal kexec prepares control pages and jumps through relocate_kernel; crash paths capture pt_regs, protect crash memory, build ELF core headers, and optionally shoot down CPUs via NMI.

## State and Persistence
State is kimage_arch metadata, control/swap/table pages, crashk resource protection, preserved context flags, and debug IDT/serial settings.

## Dependencies and Integration Points
Depends on page layout, ptrace regs, ELF/purgatory, memory encryption/cache coherency, CPU hotplug, NMI shootdown, and kexec_file loader ops.

## Risks
Risks include relocation page corruption, bad crash register capture, wrong 32/64-bit entry register setup, cache incoherency, and crash hotplug races.

## Test Signals
Tests should run kexec and kdump, file_load bzImage, crash hotplug, encrypted memory guests, serial debug, CPU offline/online, and relocation/purgatory validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec.h -->
