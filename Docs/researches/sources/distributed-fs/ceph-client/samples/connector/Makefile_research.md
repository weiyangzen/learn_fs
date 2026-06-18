# sources/distributed-fs/ceph-client/samples/connector/Makefile

Purpose: kbuild glue for the connector sample.

Important APIs/functions: builds `cn_test.o` when `CONFIG_SAMPLE_CONNECTOR` is enabled and builds the user program `ucon` when `CONFIG_CC_CAN_LINK` permits host/user linking. Adds `-I usr/include` to user C flags so exported kernel UAPI headers are found.

Control flow: no runtime code; kbuild selects one kernel module and one optional user-space utility.

State and persistence: none.

Dependencies and integration: integrates with Linux sample build infrastructure and connector UAPI headers.

Risks: user program availability depends on a usable linker and installed/exported UAPI headers.

Test signals: `make samples/connector/` or a full kernel samples build should produce `cn_test.ko` and, on link-capable builds, `ucon`.
