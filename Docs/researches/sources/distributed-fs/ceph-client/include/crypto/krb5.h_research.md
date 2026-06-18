# sources/distributed-fs/ceph-client/include/crypto/krb5.h

Purpose: declares Kerberos 5 crypto type constants, enctype descriptors, and helper APIs for encryption, checksum, MIC verification, and PRF+ generation.

Important APIs, types, and flow: constants enumerate Kerberos enctypes, checksum types, key-usage seeds, and Kerberos error values. `enum krb5_crypto_mode` distinguishes checksum, encryption, integrity, and key derivation use. `struct krb5_buffer` describes external buffers; `struct krb5_enctype` describes enctype identifiers, names, crypto algorithm names, hash/HMAC names, key/confounder/checksum/block sizes, usage seed offsets, and key-derivation hooks. APIs locate encrypted/checksum data ranges, prepare AEAD or shash transforms, decrypt scatterlists, verify MICs, and compute PRF+ output.

State and persistence: state is transform-local and caller-buffer based. Keys are passed to helpers and may be stored in crypto transforms; no persistence exists.

Dependencies and integration: integrates `crypto_aead`, `crypto_shash`, scatterlists, network/security subsystems using Kerberos, and RFC enctype definitions.

Risks and test signals: risks include enctype constant mismatches, key-usage derivation errors, scatterlist data-range mistakes, checksum truncation differences, and weak legacy enctypes. Signals include Kerberos protocol test vectors, AES CTS/HMAC vectors, MIC failure tests, SG-layout coverage, and enctype negotiation tests.
