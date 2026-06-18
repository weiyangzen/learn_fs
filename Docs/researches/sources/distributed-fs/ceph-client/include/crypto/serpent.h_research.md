# sources/distributed-fs/ceph-client/include/crypto/serpent.h

Purpose: declares Serpent block cipher constants, context, key setup, and block encrypt/decrypt primitives.

Important APIs, types, and flow: constants define key size range, expanded-key words, and 16-byte block size. `struct serpent_ctx` stores the expanded key. `__serpent_setkey()` initializes a context directly; `serpent_setkey()` adapts setkey to a crypto transform; `__serpent_encrypt()` and `__serpent_decrypt()` process one block.

State and persistence: expanded key state is transform/context-local and sensitive. No persistence exists.

Dependencies and integration: used by Serpent cipher drivers and templates that invoke block primitives.

Risks and test signals: risks include accepting zero-length keys if caller-side validation is absent, key schedule mistakes, and endian differences in optimized versions. Signals include Serpent known-answer vectors for all key lengths, transform setkey tests, generic vs optimized parity, and weak alignment tests.
