# sources/distributed-fs/ceph-client/tools/testing/crypto/chacha20-s390/Makefile

Purpose: Kbuild wrapper for compiling the `test_cipher` kernel module used to compare generic, s390, and library ChaCha20 implementations.

Important APIs, types, and functions: sets `obj-m += test_cipher.o` and maps `test_cipher-y := test-cipher.o`. Targets `all` and `clean` invoke the running kernel build directory with `M=$(PWD)`.

Control flow: `make` builds an external module against `/lib/modules/$(uname -r)/build`; `make clean` asks that same kernel build tree to clean module artifacts.

State and persistence: generated module artifacts remain in the current directory until cleaned.

Dependencies and integration points: depends on an installed kernel build tree and headers matching the running kernel. It integrates with `run-tests.sh`, which expects `test_cipher.ko`.

Risks: hard-wires the running kernel rather than an explicit target kernel, so cross-builds or alternate test kernels require overriding the invocation manually. The object/module name differs in hyphen/underscore form, which is normal for Kbuild but worth preserving.

Test signals: successful build produces `test_cipher.ko`; clean removes module outputs.
