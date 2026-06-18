<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem_proc.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem_proc.c

Purpose: creates ALSA proc binary entries for dumping GUS RAM banks and InterWave ROM banks.

Important APIs/types/functions: `struct gus_proc_private` stores ROM flag, address, size, and card pointer. `snd_gf1_mem_proc_dump()` services reads using `snd_gus_dram_read()`. `snd_gf1_mem_proc_init()` creates `gus-ram-N` and `gus-rom-N` entries.

Control flow: init iterates RAM bank descriptors and ROM presence bits. For each non-empty bank it allocates private data, creates a card proc entry, marks it as data content, installs the read ops, sets entry size, and arranges `private_free` cleanup. Read calls into DRAM/ROM access with the supplied file position and count.

State and persistence: private proc state mirrors detected bank addresses and sizes. It does not update allocator state or hardware except through reads. Entries live with the ALSA card.

Dependencies and integration: called from `snd_gf1_start()` after memory initialization. Depends on `gus_dram.c`, ALSA info/proc infrastructure, and bank metadata from memory detection.

Risks: the dump function ignores `priv->address` and passes `pos` directly to `snd_gus_dram_read()`, so bank-relative proc offsets depend on how callers interpret addresses; this is legacy behavior worth verifying. Test signals are proc entry creation for each detected bank, correct entry sizes, successful reads, ROM-vs-RAM selection, and cleanup without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem_proc.c -->
