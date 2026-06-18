# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/flow_dissector_load.h

Purpose: inline loader for flow dissector BPF objects with program-array population.

Important APIs and functions: `bpf_flow_load(obj, path, prog_name, map_name, keys_map_name, prog_fd, keys_fd)` loads an object as `BPF_PROG_TYPE_FLOW_DISSECTOR`, finds the main program by name, finds a prog-array map, optionally finds a keys map, and fills the prog-array with all non-main program fds.

Control flow: load object, resolve main program fd, resolve map fds, iterate all programs, and update the prog-array sequentially.

State and persistence: loaded BPF object and maps persist through the returned object pointer and file descriptors; caller owns lifetime.

Dependencies and integration points: uses `bpf_prog_test_load()` from `testing_helpers.h`, libbpf object/program/map iteration, and `bpf_map_update_elem`.

Risks: assumes all non-main programs should be inserted in iteration order; does not check `bpf_map_update_elem` errors; returns generic `-1` for many lookup failures.

Test signals: flow dissector tests can verify object load, main fd, optional keys map fd, and tail-call program array population.
