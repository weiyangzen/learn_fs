# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_6xx.S

## Purpose
Implements 6xx/7xxx 32-bit PowerPC idle power-save routines, including DOZE/NAP entry, CPU-specific pre/post handling, and early per-CPU idle initialization.

## Important APIs, Types, And Functions
Exports `init_idle_6xx`, `ppc6xx_idle`, `power_save_ppc32_restore`, `nap_save_msscr0`, `nap_save_hid1`, and `powersave_lowspeed`. It manipulates HID0/HID1/MSSCR0, MSR POW/EE, Altivec DSSALL, and thread flag `_TLF_NAPPING`.

## Control Flow
`init_idle_6xx` clears leftover NAP mode and records per-CPU default MSSCR0/HID1 values for CPUs that need restore after nap. `ppc6xx_idle` selects DOZE or NAP based on CPU features and `powersave_nap`, performs errata workarounds such as disabling L2 prefetch and 750FX low-speed mode, writes HID0 to enter low power, marks `_TLF_NAPPING`, enables EE and POW in MSR, then spins until an exception redirects return. `power_save_ppc32_restore` changes the interrupted NIP to LR so the idle function returns and restores saved MSSCR0/HID1.

## State And Persistence
Per-CPU saved SPR snapshots are stored in `nap_save_msscr0` and `nap_save_hid1`; `powersave_lowspeed` and `powersave_nap` influence runtime behavior. CPU SPR changes persist until restored on wakeup. No durable storage exists.

## Dependencies And Integration Points
Depends on CPU feature fixups, `powersave_nap` from `idle.c`, exception wakeup code that recognizes `_TLF_NAPPING`, PowerPC 6xx SPR definitions, Altivec support, and `head_book3s_32.S` calling `init_idle_6xx` during boot and secondary startup.

## Risks And Edge Cases
Risks include entering NAP on CPUs or boards that do not tolerate it, incomplete restoration of HID1/MSSCR0, L2 prefetch errata timing, low-speed PLL assumptions on 750FX, and interrupt return paths not rewriting NIP to LR. The code assumes per-CPU save arrays are indexed consistently before normal per-CPU infrastructure is fully active.

## Test Signals
Signals include 6xx/7xxx boot, idle wakeup by timer and external interrupts, `powersave_nap` toggling, CPU feature matrix builds, Altivec-enabled nap, SMP secondary idle initialization, and hardware tests on 745x and 750FX-like systems.
