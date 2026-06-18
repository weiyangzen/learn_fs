# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-memory.c

Purpose: IP32 memory discovery from CRIME memory-bank registers.

Important APIs and control flow: `prom_meminit()` calls `crime_init()`, iterates CRIME banks, derives base from `CRIME_MEM_BANK_CONTROL_ADDR`, skips zero-base nonzero banks, derives size as 32 or 128 MiB, adjusts banks crossing the 256 MiB split by adding `CRIME_HI_MEM_BASE`, logs each bank, and adds it to memblock.

State, persistence, and integration: state includes CRIME/MACE mappings and memblock RAM ranges. Dependencies include CRIME registers and O2 memory layout. Risks include bank zero special handling, fixed size encoding, and high-memory base adjustment assumptions. Test signals are CRIME MC bank logs, correct total RAM, and no overlapping memblock ranges.
