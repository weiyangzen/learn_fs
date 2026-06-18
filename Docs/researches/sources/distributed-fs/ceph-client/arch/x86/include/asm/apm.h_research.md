
# sources/distributed-fs/ceph-client/arch/x86/include/asm/apm.h

Purpose: 32-bit APM BIOS call glue for legacy power-management paths. It wraps far calls through `apm_bios_entry` while preserving registers expected by BIOS interfaces.

Important APIs and control flow: `apm_bios_call_asm()` takes function and input registers, optionally zeros data segments under `APM_ZERO_SEGS`, pushes `edi`/`ebp`, performs `lcall *%cs:apm_bios_entry`, captures carry in `%al`, restores saved registers/segments, and returns EAX/EBX/ECX/EDX/ESI. `apm_bios_call_simple_asm()` is the reduced form that returns only EAX and a carry-derived error flag.

State, dependencies, and risks: state lives outside the header in the APM BIOS descriptor/entry point and CPU segment registers. Dependencies include 32-bit protected-mode BIOS calling convention and caller-side synchronization. Risks include segment-state corruption, BIOS clobbers, fragile inline-assembly constraints, and legacy-only behavior that is hard to exercise on modern machines. Test signal is mostly boot or suspend/resume on APM-era hardware or emulator coverage.
