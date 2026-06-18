# sources/distributed-fs/ceph-client/include/crypto/twofish.h

Purpose: declares Twofish block cipher constants, context, and key setup entry points.

Important APIs, types, and flow: constants define 16- to 32-byte key sizes and 16-byte block size. `struct twofish_ctx` stores key-dependent S-box words and subkeys. `__twofish_setkey()` prepares a direct context; `twofish_setkey()` adapts setkey to a crypto transform.

State and persistence: expanded key state is transform/context-local and sensitive. No persistence exists.

Dependencies and integration: used by Twofish cipher implementations and block-mode templates.

Risks and test signals: risks include key-size validation, key schedule generation, and optimized/generic divergence. Signals include Twofish known-answer vectors for 128/192/256-bit keys, mode self-tests, invalid key lengths, and key zeroization review.
