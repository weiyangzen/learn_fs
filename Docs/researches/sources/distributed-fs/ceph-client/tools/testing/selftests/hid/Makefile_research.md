<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/Makefile

## Purpose
This Makefile builds HID selftest user binaries, HID-BPF programs, libbpf/bpftool support, and registers hid-tools wrapper scripts.

## Important APIs, Types, And Functions
It defines many `TEST_PROGS` wrappers, `TEST_FILES := run-hid-tools-tests.sh tests`, `TEST_GEN_PROGS = hid_bpf hidraw`, `TEST_GEN_PROGS_EXTENDED += $(DEFAULT_BPFTOOL)`, BPF object/skeleton generation rules, libbpf/bpftool/resolve_btfids build rules, `VMLINUX_BTF` discovery, clang/GCC BPF build macros, and C compile/link rules.

## Control Flow
The build locates vmlinux BTF, builds libbpf for target and host as needed, builds bpftool, dumps `vmlinux.h`, compiles BPF programs from `progs/*.c`, generates skeleton headers, then compiles `hid_bpf` and `hidraw`. Shell wrappers run hid-tools Python targets via `run-hid-tools-tests.sh`.

## State And Persistence
It creates scratch build directories under `$(OUTPUT)/tools` and host tools under `$(OUTPUT)/host-tools`, BPF objects, skeleton headers, helper binaries, and bpftool.

## Dependencies And Integration Points
It depends on kernel tools sources, libelf, zlib, pthread, clang or BPF GCC, bpftool, vmlinux BTF, HID, HIDRAW, UHID, HID-BPF, USB HID, and hid-tools test files.

## Risks
Builds fail hard if no vmlinux BTF is found. Cross-compilation requires separate host libbpf/bpftool paths. BPF compiler include paths and endianness handling are architecture-sensitive.

## Test Signals
Successful generation of `vmlinux.h`, BPF skeletons, `hid_bpf`, `hidraw`, and PASS from each hid-tools wrapper indicate healthy integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/Makefile -->
