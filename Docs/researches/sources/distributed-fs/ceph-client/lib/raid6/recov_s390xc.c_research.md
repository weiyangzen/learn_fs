# sources/distributed-fs/ceph-client/lib/raid6/recov_s390xc.c

Purpose: implements s390 RAID6 recovery using the `xc` instruction for block XOR acceleration.

Important APIs and flow: `xor_block()` applies `xc` over 256 bytes. `raid6_2data_recov_s390xc()` performs standard syndrome-delta setup, XORs deltas with P/Q in 256-byte blocks, applies scalar GF table multipliers per byte, and XORs reconstructed data back. `raid6_datap_recov_s390xc()` handles data+P similarly. Published `raid6_recov_s390xc` has priority 1 and no validity callback.

State and persistence: temporarily rewrites `ptrs`, restores it, and mutates failed/P buffers.

Dependencies and integration: depends on `raid6_call.gen_syndrome`, GF scalar tables, and the recovery selector.

Risks and test signals: risks include assuming byte counts are multiples of 256 and correctness of inline `xc` memory constraints. Signals include s390 recovery tests, boot logs selecting `s390xc`, and RAID6 rebuild validation.
