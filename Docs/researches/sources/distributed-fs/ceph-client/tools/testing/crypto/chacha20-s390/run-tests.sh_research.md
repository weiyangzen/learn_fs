# sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/run-tests.sh

Purpose: root-side script that loads ChaCha20 implementations and repeatedly inserts the test module with varied plaintext sizes to exercise s390 ChaCha20 paths.

Important APIs, types, and functions: uses `lsmod`, `rmmod`, `modprobe chacha_generic`, `modprobe chacha_s390`, repeated `insmod test_cipher.ko size=<N>`, and `dmesg | tail -170`.

Control flow: removes currently loaded modules whose names match `chacha`, loads generic and s390 modules, inserts the test module for block-boundary sizes and large sizes, then prints recent kernel logs. The comments note that `insmod` failure is expected because the module init returns failure after running tests.

State and persistence: modifies loaded kernel modules and kernel log state. It does not keep local files except module build products produced elsewhere.

Dependencies and integration points: depends on root privileges, s390 ChaCha module availability, and `test_cipher.ko` in the working directory. It is paired with `test-cipher.c`.

Risks: `lsmod | grep chacha | xargs rmmod` can pass no arguments or remove broader modules than intended. There is no `set -e`, so failures may be obscured. It assumes dmesg access and sufficient permissions.

Test signals: dmesg should contain OK/FAILED comparison lines and timing for generic, s390, and library encryption/decryption across the tested sizes.
