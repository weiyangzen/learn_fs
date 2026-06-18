# sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs-prefetch.c

Purpose: generic scalar XOR implementation that uses register temporaries and software prefetch.

Important APIs and flow: `xor_32regs_p_{2,3,4,5}` prefetch destination and source lines, load eight `long` values into locals, XOR requested sources, write back, and use a `once_more` tail pattern because the loop prefetches one line ahead. `DO_XOR_BLOCKS()` emits `xor_gen_32regs_p()`, exposed as `xor_block_32regs_p`.

State and persistence: no persistence; mutates destination in place.

Dependencies and integration: depends on `<linux/prefetch.h>` and `xor_impl.h`; registered by generic and several architecture init paths.

Risks and test signals: risks include off-by-one loop handling and prefetching near guard pages. The KUnit test's end-of-buffer placement is a key overread signal.
