# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64-glue.c

Purpose: publishes SPARC64 VIS and Niagara assembly XOR functions as core XOR templates.

Important APIs and flow: declares `xor_vis_{2,3,4,5}` and `xor_niagara_{2,3,4,5}` implemented in assembly. `DO_XOR_BLOCKS()` creates `xor_gen_vis()` and `xor_gen_niagara()`, exposed as `xor_block_VIS` and `xor_block_niagara`.

State and persistence: no persistence; selection is handled by `sparc/xor_arch.h`.

Dependencies and integration: depends on `xor-sparc64.S` for implementation and on SPARC architecture detection to force the proper template.

Risks and test signals: mismatch between glue prototypes and assembly ABI would be severe. Signals include sparc64 build/link coverage, boot forced-template logs, and RAID/KUnit parity checks.
