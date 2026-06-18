# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand-timer.c

This file provides a stub timer-based RAND method so Heimdal's Fortuna code can link in kernel space. All method callbacks either do nothing, return success without filling data, or report not-ready status.

Important symbols are static callbacks `timer_seed`, `timer_bytes`, `timer_cleanup`, `timer_add`, `timer_pseudorand`, `timer_status`, the `hc_rand_timer_method` descriptor, and `RAND_timer_method`. There is no useful entropy state and no persistence.

Dependencies are hcrypto `RAND_METHOD` and `AFS_STRUCT_INIT`. Integration is link compatibility for `rand-fortuna.c`; actual randomness should come from `rand.c` and `osi_readRandom` or Fortuna seeded elsewhere. Risks are severe if this method is ever used as a real random source because `bytes` returns success without populating output. Test signals are audits that no production path selects `RAND_timer_method` for output and kernel RNG tests that exercise `RAND_bytes` instead.
