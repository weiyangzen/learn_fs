# sources/distributed-fs/ceph-client/include/crypto/sha3.h

Purpose: declares direct SHA-3 and SHAKE sponge contexts, initialization, update, finalize/squeeze, and one-shot helpers.

Important APIs, types, and flow: constants define SHA3 digest and block sizes, SHAKE defaults, and 200-byte Keccak state size. `sha3_state` stores the sponge state; `__sha3_ctx` tracks byte index and block size; `sha3_ctx` adds digest size and finalization; `shake_ctx` supports extendable-output squeezing. Inline initializers set domain suffixes and sizes for SHA3-224/256/384/512 and SHAKE128/256. APIs update, finalize SHA-3, squeeze SHAKE output, and run one-shot variants.

State and persistence: caller-owned contexts hold sponge state and are explicitly zeroized by provided inline helpers. No persistence exists.

Dependencies and integration: integrates with hash users needing direct SHA-3/SHAKE primitives and with ML-DSA or other modern crypto implementations.

Risks and test signals: risks include domain-separation suffix mistakes, squeeze-after-update misuse, state zeroization, and block-size calculations. Signals include FIPS SHA-3/SHAKE vectors, variable-length SHAKE output tests, split-update tests, zeroization review, and generic/optimized parity.
