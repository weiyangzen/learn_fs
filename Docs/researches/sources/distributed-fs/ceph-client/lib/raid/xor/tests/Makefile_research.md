# sources/distributed-fs/ceph-client/lib/raid/xor/tests/Makefile

Purpose: builds the XOR KUnit test module.

Important APIs and flow: adds `xor_kunit.o` to the build when `CONFIG_XOR_KUNIT_TEST` is enabled.

State and persistence: no runtime state here; it controls build inclusion.

Dependencies and integration: integrated into Kbuild under the XOR library test directory.

Risks and test signals: local risk is only config wiring. The test signal is the `xor` KUnit suite appearing and running when enabled.
