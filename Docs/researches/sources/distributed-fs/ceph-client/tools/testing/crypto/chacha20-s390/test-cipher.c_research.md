# sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/test-cipher.c

Purpose: kernel module self-test that compares `chacha20-generic`, `chacha20-s390`, and `chacha_crypt_arch()` outputs and decryptability for a configurable data size.

Important APIs, types, and functions: defines module parameters `size` and `debug`, `struct skcipher_def`, `test_lib_chacha()`, `test_skcipher_encdec()`, `test_skcipher()`, module init `chacha_s390_test_init()`, and exit `chacha_s390_test_exit()`. It uses crypto skcipher APIs, `chacha_init()`, `chacha_crypt_arch()`, scatterlists, `crypto_wait_req()`, `ktime_get_ns()`, vmalloc/vfree, and optional `print_hex_dump()`.

Control flow: init allocates plaintext, generic cipher, s390 cipher, and revert buffers; fills plaintext with mostly random first bytes; encrypts/decrypts through `chacha20-generic` and verifies plaintext recovery; repeats with `chacha20-s390`; compares generic and s390 ciphertext; then runs the low-level library implementation and compares recovery and ciphertext against generic. It prints timing for each encryption/decryption. The init function returns `-1` intentionally after freeing buffers so `insmod` unloads while still executing the test.

State and persistence: all buffers are transient. Module parameters determine data size and debug dumping. Kernel logs preserve test results.

Dependencies and integration points: depends on the kernel crypto API, s390 ChaCha implementation availability, and module loading. `run-tests.sh` drives multiple sizes.

Risks: returning `-1` is intentional but looks like load failure to automation. Large sizes allocate multiple vmalloc buffers and can stress memory. Fixed key/IV are test-only. Include list is broad, increasing compile sensitivity. The library path uses architecture implementation through `chacha_crypt_arch()`, so availability and behavior are architecture-dependent.

Test signals: dmesg should report generic, s390, and library en/decryption checks OK plus s390-vs-generic and lib-vs-generic OK. Any memcmp failure or crypto allocation error is a clear regression.
