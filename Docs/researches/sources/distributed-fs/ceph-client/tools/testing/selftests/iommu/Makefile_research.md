# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/Makefile

Purpose: this kselftest Makefile builds IOMMUFD selftest binaries.

Important APIs and variables: it sets `CFLAGS += -Wall -O2 -Wno-unused-function`, adds `$(KHDR_INCLUDES)` for kernel UAPI headers, links with `-lcap`, and registers `TEST_GEN_PROGS += iommufd iommufd_fail_nth`. `include ../lib.mk` supplies kselftest rules.

Control flow: make builds the generated programs from corresponding C sources in the directory, using kernel headers and libcap. The generated binaries are installed/run by kselftest infrastructure.

State and persistence: produces `iommufd` and `iommufd_fail_nth` binaries. No runtime state is defined here.

Dependencies and integration points: integrates with kselftest, kernel headers, libcap, and the IOMMUFD test sources. It pairs with the adjacent `config` file for required kernel options.

Risks: libcap is a mandatory link dependency; suppressing unused-function warnings may hide dead helper drift; empty initial `TEST_GEN_PROGS :=` is harmless but redundant.

Test signals: build success yields both binaries; runtime signals come from those binaries.
