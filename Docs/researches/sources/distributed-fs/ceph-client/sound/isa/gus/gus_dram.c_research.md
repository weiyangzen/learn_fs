<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dram.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_dram.c

Purpose: user-facing DRAM/ROM byte access helpers for GUS and InterWave memory windows.

Important APIs/types/functions: exported functions are `snd_gus_dram_write()` and `snd_gus_dram_read()`. Internal helpers `snd_gus_dram_poke()` and `snd_gus_dram_peek()` copy in 256-byte chunks and switch between InterWave block I/O and plain GF1 byte pokes.

Control flow: write copies data from userspace into a stack buffer and writes to card memory. Read fills a stack buffer from RAM or ROM and copies to userspace. InterWave paths select memory control mode, set the DRAM address once per chunk, then use `outsb()`/`insb()`; non-InterWave paths iterate through `snd_gf1_poke()`/`snd_gf1_peek()`.

State and persistence: hardware DRAM/ROM contents are persistent while the card is powered and driver-managed; no allocator metadata is changed here. InterWave memory-control register is temporarily changed and restored to RAM mode after ROM reads.

Dependencies and integration: used by proc memory dump entries in `gus_mem_proc.c`; depends on `copy_from_user()`, `copy_to_user()`, GF1 register locking, and low-level DRAM helpers.

Risks: caller must validate address/size against bank limits; these helpers do not enforce bounds. User copy failures return `-EFAULT`. Test signals are `/proc` RAM/ROM reads, write/readback to allocated RAM, InterWave ROM read selection, and copy fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dram.c -->
