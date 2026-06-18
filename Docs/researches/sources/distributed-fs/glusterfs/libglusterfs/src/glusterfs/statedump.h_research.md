# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/statedump.h

Purpose: `statedump.h` declares the process/translator diagnostic dump interface used to emit memory, iobuf, callpool, inode, fd, history, latency, and private translator state.

Important APIs and types: `gf_dump_xl_options_t` controls per-translator private/inode/fd/context/history dumps. `gf_dump_options_t` controls global dump classes and output path. `gf_proc_dump_build_key` builds hierarchical keys into a fixed 4096-byte buffer. APIs initialize/fini/cleanup dumping, trigger dump on signal/context, add sections, write key/value entries, dump inode/fd tables, dump memory and mempool info to dicts, and dump xlator profile/history/meminfo/private state.

Control flow and state: `dump_options` is global. Dump functions write either to the dump output or dictionaries. The key-building helper prefixes keys and guards negative snprintf/vsnprintf results.

Dependencies and integration: depends on inode, fd, dict, strfd, xlator, and latency types. Graph cleanup and memory-pool diagnostics rely on statedump visibility.

Risks: dump routines often run during failure or signal-triggered diagnostics, so lock ordering and allocation behavior are sensitive. Fixed key buffer truncation can merge/lose detail. Dumping private translator data can expose inconsistent state if translators mutate concurrently.

Test signals: statedump smoke tests should verify section/key formatting, disabled/enabled option filtering, dictionary dump paths, long key handling, and no deadlock while active fops are present.
