# sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor_arch.h

Purpose: defines s390 XOR selection policy.

Important APIs and flow: declares `xor_block_xc`; `arch_xor_init()` calls `xor_force(&xor_block_xc)`, making the core use the s390 `xc` implementation without measuring alternatives.

State and persistence: sets the XOR core forced-template pointer during initialization.

Dependencies and integration: included by `xor-core.c` when architecture XOR blocks are configured.

Risks and test signals: forced selection assumes `xc` is universally preferable and correct. Signals include boot template message, KUnit, and s390 RAID parity tests.
