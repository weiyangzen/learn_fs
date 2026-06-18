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
