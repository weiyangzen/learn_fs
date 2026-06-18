# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/hid_bpf.c

## Purpose
`hid_bpf.c` is a kselftest binary for the kernel HID-BPF integration path. It creates a synthetic UHID device, loads the generated `hid.skel.h` libbpf skeleton, attaches selected HID `struct_ops` programs from `progs/hid.c`, then validates that raw HID input, report descriptor fixups, hw request hooks, output report hooks, and injected input reports behave as expected through the kernel-visible `hidraw` node.

## Important APIs, types, and functions
The `FIXTURE(hid_bpf)` state owns a `struct uhid_device`, an open `hidraw_fd`, the BPF skeleton pointer, and up to three attached `bpf_link` objects. `load_programs()` is the central helper: it opens the skeleton, finds BPF programs by name, enables autoload, finds each corresponding struct_ops map by removing the `hid_` prefix from the program name, writes the fixture HID id into the first struct_ops field, disables autoattach for maps, loads the object, attaches struct_ops links, attaches tracing programs, and opens the matching hidraw node. `detach_bpf()` centralizes close/detach/destroy cleanup.

## Control flow
Fixture setup calls `setup_uhid()` with the shared test report descriptor. Tests then choose either `LOAD_BPF` for syscall-style BPF program tests or `LOAD_PROGRAMS()` for struct_ops hooks. Event tests inject UHID input with `uhid_send_event()`, read from `hidraw`, and assert mutations performed by BPF. Raw request and output report tests trigger kernel paths via `HIDIOCGFEATURE` or `write()`, validating filter errno, transformed return sizes, and no-recursion behavior. The report descriptor test attaches `hid_rdesc_fixup`, then re-reads the descriptor through hidraw.

## State and persistence
State is intentionally transient: synthetic devices live only for the fixture, BPF links are destroyed at teardown, and only one temporary BPF pin path (`/sys/fs/bpf/hid_first_event`) is used and immediately removed. Shared BPF data variables such as `callback_check` and `callback2_check` are read through the skeleton to prove program execution.

## Dependencies and integration points
This file depends on libbpf, kselftest harness macros, `hid_common.h`, the generated BPF skeleton, `/dev/uhid`, `/dev/hidraw*`, sysfs HID discovery, and kernel support for HID-BPF kfuncs and struct_ops. It integrates with `progs/hid.c` by name conventions linking `hid_*` programs to struct_ops maps.

## Risks and test signals
Risk concentrates around ordering assumptions, sysfs/hidraw discovery races, kernel feature availability, and error-code contracts. The tests provide strong signals for attach lifecycle, multi-program ordering, changed report IDs, user-triggered BPF syscalls, raw/output report filtering, recursion guards, workqueue event injection, and descriptor rewriting. Failures here usually indicate kernel HID-BPF ABI regressions rather than ordinary userspace logic bugs.
