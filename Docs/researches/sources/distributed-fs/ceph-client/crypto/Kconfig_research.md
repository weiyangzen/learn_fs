# sources/distributed-fs/ceph-client/crypto/Kconfig

Purpose: defines the kernel cryptographic API configuration surface: core crypto framework options, self-test/FIPS controls, public-key algorithms, block ciphers, modes, AEADs, hashes, CRCs, compression, RNGs, userspace AF_ALG interfaces, and architecture/driver crypto submenus.

Important APIs, types, and functions: this is Kconfig data rather than C code. Key symbols include `CRYPTO`, `CRYPTO_ALGAPI`, `CRYPTO_MANAGER`, `CRYPTO_SELFTESTS`, `CRYPTO_FIPS`, front-end families such as `CRYPTO_AEAD`, `CRYPTO_SKCIPHER`, `CRYPTO_HASH`, `CRYPTO_RNG`, `CRYPTO_AKCIPHER`, `CRYPTO_ACOMP`, algorithms such as `CRYPTO_AES`, `CRYPTO_ADIANTUM`, `CRYPTO_AEGIS128`, hash/MAC selections, compression selections, and `CRYPTO_USER_API_*` switches.

Control flow and behavior: selecting `CRYPTO` opens the whole menu and sources `crypto/async_tx/Kconfig`, architecture Kconfigs, driver crypto Kconfig, asymmetric keys, certs, and Kerberos crypto. Many public options select hidden second-level implementation symbols, which then drive object inclusion in the Makefile. `CRYPTO_MANAGER2` is forced when the algorithm API is built in with manager not disabled, ensuring templates and self-test infrastructure are available when needed.

State and persistence: the file persists kernel build configuration, not runtime state. Its selected tristate/bool/string values become `.config` inputs and determine compiled-in or modular crypto code, FIPS metadata strings, jitter entropy tunables, and exposed userspace interfaces.

Dependencies and integration points: it integrates with `crypto/Makefile`, architecture crypto directories, `drivers/crypto`, `certs`, `crypto/asymmetric_keys`, and consumers such as IPsec, fscrypt, dm-crypt, NFS/RxRPC Kerberos, and AF_ALG userspace clients. `select` chains pull in crypto libraries, ASN.1 parsers, MPILIB, compression libraries, and RNG prerequisites.

Risks and correctness concerns: dependency mistakes can expose algorithms without their core API, omit self-tests in FIPS-related builds, or allow obsolete algorithms when not intended. `select` is forceful in Kconfig, so new dependencies must avoid impossible combinations and recursive selections. FIPS options require especially careful alignment with self-tests, module signatures, and DRBG availability.

Test signals: use `olddefconfig`, `allmodconfig`, `allyesconfig`, minimal crypto builds, and FIPS/self-test build matrices. Validate module/object inclusion against `crypto/Makefile`, boot-time algorithm self-tests, AF_ALG socket availability for selected userspace APIs, and architecture submenu coverage with `KMSAN` excluded assembly paths.
