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
