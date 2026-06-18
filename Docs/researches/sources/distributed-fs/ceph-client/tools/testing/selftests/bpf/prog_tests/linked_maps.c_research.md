<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_maps.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_maps.c

Purpose: validates that linked BPF object files resolve map definitions and weak map references consistently across compilation units.

Important APIs and functions: `test_linked_maps()` uses the generated `linked_maps` skeleton. It opens and loads the combined object, attaches it, triggers a syscall probe path with `syscall(SYS_getpgid)`, then reads BSS outputs.

Control flow: open/load, attach, trigger, assert three outputs, destroy skeleton. Failure paths jump to cleanup after attach/load problems.

State and persistence: all observable state is in skeleton BSS fields: `output_first1`, `output_second1`, and `output_weak1`. No persistent kernel state remains after `linked_maps__destroy()`.

Dependencies and integration: depends on `linked_maps.skel.h`, `test_progs.h`, and a traceable syscall trigger. It is a libbpf linker integration test, not a networking test.

Risks and test signals: expected values `2000`, `2`, and `2` signal correct strong/weak map symbol resolution. Risks are accidental changes to BPF-side constants or attach points that make `getpgid` stop triggering the programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_maps.c -->
