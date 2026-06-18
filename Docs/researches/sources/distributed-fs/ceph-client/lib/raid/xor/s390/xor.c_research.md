# sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor.c

Purpose: implements the s390 optimized XOR template using the `xc` instruction.

Important APIs and flow: `xor_xc_{2,3,4,5}` use inline assembly to process 256-byte blocks with `xc`, then handle a remaining byte count through `exrl`. `DO_XOR_BLOCKS(xc, ...)` emits `xor_gen_xc()`, and `xor_block_xc` exposes the template.

State and persistence: no persistence; destination bytes are XORed in place.

Dependencies and integration: `s390/xor_arch.h` forces this template, bypassing generic calibration.

Risks and test signals: risks include inline assembly length handling and forced selection on all s390 builds. Signals include KUnit XOR tests, RAID parity verification, and boot logs showing the forced `xc` template.
