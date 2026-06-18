# File Research: sources/block-storage/kvdo/vdo/thread-config.c

This file constructs and names VDO thread layouts. `allocate_thread_config()` allocates the config and arrays for logical, physical, hash, and bio threads, storing zone/thread counts.

`vdo_make_thread_config()` supports two modes:
- Single shared base-thread mode when logical/physical/hash zone counts are all zero: logical, physical, hash, journal, packer, and admin effectively share the same request thread identity.
- Multi-thread mode: assigns admin/journal, packer, logical zone, physical zone, and hash zone thread ids separately.

It always assigns dedupe, optional bio-ack, CPU, and bio thread ids. `vdo_free_thread_config()` releases all arrays.

`vdo_get_thread_name()` maps thread ids to stable queue names: `reqQ`, `journalQ`, `adminQ`, `packerQ`, `dedupeQ`, `ackQ`, `cpuQ`, `logQ<N>`, `physQ<N>`, `hashQ<N>`, `bioQ<N>`, or fallback `reqQ<ID>`.
