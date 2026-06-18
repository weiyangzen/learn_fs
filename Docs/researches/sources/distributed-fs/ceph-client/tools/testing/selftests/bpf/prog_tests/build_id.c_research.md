# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/build_id.c

## Purpose
This serial test validates build-ID collection from BPF stack traces for uprobes, contrasting no-fault and sleepable helpers when the target executable's build ID is resident or paged out.

## APIs, Types, and Functions
It uses `test_build_id.skel.h`, `read_build_id`, `bpf_program__attach`, `system("./uprobe_multi ...")`, and `struct bpf_stack_build_id`. `print_stack` formats stack frames for verbose output. `subtest_nofault` and `subtest_sleepable` attach different BPF programs and inspect skeleton BSS stack buffers.

## Control Flow
`serial_test_build_id` reads the expected build ID from the `uprobe_multi` binary, then runs three subtests. The no-fault path attaches a uprobe, triggers either paged-in or paged-out executable behavior, checks the BPF result length, and expects either `BPF_STACK_BUILD_ID_VALID` with matching bytes or `BPF_STACK_BUILD_ID_IP` when the build ID is not resident. The sleepable path triggers paged-out behavior but expects valid build ID collection.

## State, Dependencies, and Integration
State is skeleton BSS plus the target process image state influenced by `uprobe_multi`. The test depends on the `uprobe_multi` helper binary, build IDs in ELF notes, uprobe attach support, and stack build-ID helper behavior.

## Risks and Test Signals
Signals are stack frame status and build-ID byte equality. Risks include missing helper binary, build IDs stripped from test binaries, paging behavior differences, and uprobe attach permissions.
