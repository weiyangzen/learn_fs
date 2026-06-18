# sources/distributed-fs/ceph-client/arch/x86/kernel/ebda.c

## Purpose
Conservatively reserves low conventional BIOS/EBDA firmware memory so the kernel does not allocate RAM used by BIOS or legacy DMA devices.

## Important APIs, Types, And Functions
`reserve_bios_regions()` reads the BIOS RAM size word at `0x413`, consults `get_bios_ebda()`, clamps to sane bounds, and reserves from the detected BIOS start to 1 MiB with `memblock_reserve()`.

## Control Flow
The function exits for platforms that disable legacy BIOS reservation. Otherwise it converts the BIOS kilobyte count to bytes, distrusts values outside 128 KiB to 640 KiB, lowers the start if EBDA begins earlier in a sane range, and reserves everything up to the 1 MiB mark.

## State, Persistence, And Dependencies
State is a memblock reservation in the low megabyte. It depends on legacy platform policy, BIOS data area mapping, EBDA probing, and memblock.

## Integration Points
Runs during early memory setup and protects the real-mode trampoline area from overlapping with firmware-reserved conventional memory.

## Risks
The code intentionally over-reserves when firmware data is suspicious. Reserving too little risks corrupting BIOS/EBDA or DMA state; reserving too much can starve low-memory trampoline allocations on tiny systems.

## Test Signals
Boot logs/memblock dumps should show low-memory reservations; systems with bogus BIOS RAM size should still reserve from 640 KiB; paravirtual platforms should skip this path.
