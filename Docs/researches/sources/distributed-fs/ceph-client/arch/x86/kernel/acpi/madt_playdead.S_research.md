# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_playdead.S

## Purpose
`madt_playdead.S` contains the 64-bit assembly handoff used by ACPI MADT Multiprocessor Wakeup support when a CPU is stopped or offlined and control must be returned to firmware through a reset vector. It is the low-level endpoint called from `madt_wakeup.c`.

## Important APIs, Types, and Functions
- `asm_acpi_mp_play_dead(reset_vector, pgd)` is the sole exported symbol in this file.
- Arguments follow the x86-64 C ABI: `%rdi` carries the physical/identity-mapped reset-vector target and `%rsi` carries the page-global-directory address for an identity mapping.
- The code uses `ANNOTATE_NOENDBR` and `ANNOTATE_RETPOLINE_SAFE` because it intentionally enters from low-level CPU-stop paths and jumps indirectly to firmware.

## Control Flow
The routine clears `X86_CR4_PGE` from CR4 to disable global TLB entries, writes CR3 with the supplied identity-mapping PGD, then performs an indirect jump to the reset vector. There is no return path: firmware takes control of the CPU.

## State and Persistence Behavior
The routine mutates CPU-local CR4 and CR3 state and leaves kernel virtual mappings behind. The CPU is expected not to resume kernel execution through this path. Persistent state needed by the routine, such as the reset vector and identity PGD physical address, is prepared and stored by `madt_wakeup.c`.

## Dependencies and Integration Points
This file depends on x86 processor flag definitions, page alignment, linkage macros, and branch-mitigation annotations. `madt_wakeup.c` maps this exact code page into an identity mapping and sets SMP callbacks to call it from `play_dead`, `stop_this_cpu`, and reset handoff paths.

## Risks
- The code must be identity-mapped at the same virtual location before and after CR3 switch; otherwise the CPU can fault after switching page tables.
- Clearing PGE and replacing CR3 in a CPU teardown path is irreversible for this flow.
- The reset vector target comes from ACPI firmware; invalid firmware data can strand the CPU.

## Test Signals
- Exercise ACPI MADT MP wakeup v1 CPU offlining on capable systems.
- Confirm `madt_wakeup.c` identity mapping includes the page containing `asm_acpi_mp_play_dead`.
- Validate kexec/offline paths do not attempt to return from this function.
