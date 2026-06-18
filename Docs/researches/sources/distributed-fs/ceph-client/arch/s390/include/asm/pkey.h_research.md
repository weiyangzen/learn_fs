# sources/distributed-fs/ceph-client/arch/s390/include/asm/pkey.h

Purpose: This header exposes the in-kernel API for converting s390 key blobs into protected keys through the pkey device driver.

Important APIs/types/functions: `pkey_key2protkey()` is declared along with execution flags `PKEY_XFLAG_NOMEMALLOC` and `PKEY_XFLAG_NOCLEARKEY`.

Control flow: Kernel crypto users pass a key blob and output buffers; the pkey implementation derives a protected key, optionally avoiding allocations or rejecting clear-key tokens according to flags.

State and persistence: Persistent state is in protected-key material produced for callers and any pkey driver/preallocated buffers; the header owns no state.

Dependencies and integration points: It depends on UAPI pkey definitions and integrates with s390 crypto hardware, protected-key ciphers, and callers constrained by crypto allocation rules.

Risks and test signals: Key length/type outputs and no-allocation constraints must be respected to avoid sleeping in crypto paths or accepting insecure clear keys. Tests should cover all supported key blob types, flag combinations, insufficient output buffers, no-memory paths, and crypto driver integration.
