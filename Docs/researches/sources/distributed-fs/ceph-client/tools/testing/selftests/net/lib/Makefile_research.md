# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/Makefile

## Purpose
This Makefile builds and packages the reusable networking selftest helper programs, BPF objects, Python scripts, shell helpers, and YNL/spec files needed by tests outside this directory.

## Important Targets and Variables
`CFLAGS` enables warnings, debug info, optimization, kernel UAPI include paths, and kselftest include paths. `TEST_FILES` installs the kernel YNL tree, netlink specs, and `ksft_setup_loopback.sh`. `TEST_GEN_FILES` builds object files for all `*.bpf.c` files plus the `csum`, `gro`, and `xdp_helper` executables. `TEST_INCLUDES` collects Python and shell helper files. The file includes the common `../../lib.mk` and networking BPF rules from `../bpf.mk`.

## Control Flow and State
The Makefile is declarative; build state is the generated binaries/objects and installed selftest file set. Wildcards automatically add new BPF C files and helper includes without target edits.

## Dependencies and Integration
It depends on the kernel selftests Makefile framework, a C compiler, libbpf/BPF build support from `bpf.mk`, and kernel headers. It feeds the helper artifacts consumed by shell and Python networking tests, including XDP, GRO, checksum, and YNL-based tests.

## Risks and Test Signals
The broad wildcard for `*.bpf.c` can expose build breaks when new BPF programs are added. Header paths must match the kernel source tree layout. A successful signal is creation of all `TEST_GEN_FILES`; failures will usually appear as compiler, linker, or BPF skeleton/toolchain errors.
