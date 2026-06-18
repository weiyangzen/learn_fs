# sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/Makefile

Purpose: builds the PCI endpoint kselftest binary.

Important settings: `CFLAGS` enables optimization, `-Wall`, kernel header includes, and `-Wl,-no-as-needed`. `LDFLAGS` links realtime, pthread, and math libraries. `TEST_GEN_PROGS` contains `pci_endpoint_test`.

Control flow/integration: inclusion of `../lib.mk` connects the binary to the kselftest build and install rules.

State/dependencies: no runtime state in the Makefile. The built test depends on the PCI endpoint test character device and kernel UAPI header `pcitest.h`.

Risks: link flags may be broader than currently needed but keep compatibility with harness/library usage. Missing kernel headers or endpoint config will fail build or runtime.

Test signals: build success produces the test executable; runtime signals come from `pci_endpoint_test.c`.
