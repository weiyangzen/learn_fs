# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_entry_64.S

Purpose: this 64-bit assembly entry helper calls Open Firmware/PROM code that runs in 32-bit big-endian mode, while preserving the 64-bit kernel register and MSR state needed to return safely.

Important API: `_GLOBAL(enter_prom)` is the exported entry point. It saves LR, creates a switch frame, saves registers PROM may clobber, saves CR and MSR, loads the PROM entry address from `r4` into SRR0, sets a local return trampoline in LR, constructs a 32-bit big-endian MSR in SRR1, and transfers control using the proper return-from-interrupt sequence for Book3E or Book3S. On return, it fixes endian state, repairs the high half of `r1`, restores MSR, registers, CR, LR, stack pointer, and returns.

Control flow: caller enters with a PROM function address. The helper builds a protected frame, switches processor mode through SRR0/SRR1, PROM executes and returns to the trampoline label, and the helper restores 64-bit kernel execution context. `FIXUP_ENDIAN`, `MTMSRD`, and `RFI_TO_KERNEL` abstract CPU-family details.

State and persistence: it does not own global state. It temporarily persists saved GPRs, CR, MSR, and LR on the kernel stack. Processor state changes include clearing 64-bit and little-endian bits before PROM entry, then restoring the original MSR after return.

Dependencies and integration points: depends on PowerPC exception return mechanics, stack-frame offsets from `asm-offsets.h`, Book3S/Book3E exception macros, PROM calling conventions, and `ppc_asm.h` save/restore helpers. It is part of the low-level Open Firmware call path used during early boot or firmware interactions on 64-bit systems.

Risks: any mismatch in saved frame layout or MSR bit manipulation can prevent returning to the kernel. PROM clobbers upper halves of registers it saves, which is why the helper saves nonvolatile state; missing a clobbered register would corrupt callers. Endianness and 32/64-bit mode transitions are fragile and CPU-family-specific.

Test signals: firmware calls through this path should return with preserved nonvolatile registers, CR, MSR, stack pointer, and LR. Boot-time OF interactions on 64-bit Book3S and Book3E configurations are the main validation. Failures usually appear as early boot hangs, bad return addresses, or corrupted stack/register state.
