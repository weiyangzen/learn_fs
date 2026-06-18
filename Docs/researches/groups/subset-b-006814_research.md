# Group Research: subset-b-006814

This grouped report covers the exact manifest entries for `subset-b-006814` and is split into source-tree-aligned per-file reports by the worker.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_based.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_based.c

Research item: `subset-b-006814` ordinal `1`. Source size: 5088 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_based.c_research.md`.

## Purpose
The program records libbpf/clang CO-RE relocation observations into global data so user-space selftests can compare target-kernel BTF behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_core_read`, `bpf_core_type_exists`, `bpf_core_type_matches`, `bpf_core_type_size`
- Declared maps: None visible in this compact source.
- Key local types: `struct a_struct`, `struct a_complex_struct`, `struct core_reloc_type_based_output`, `enum an_enum`, `typedef named_struct_typedef`, `typedef anon_struct_typedef`, `typedef struct_ptr_typedef`, `typedef int_typedef`, `typedef enum_typedef`, `typedef void_ptr_typedef`, `typedef restrict_ptr_typedef`, `typedef func_proto_typedef`, `typedef arr_typedef`
- Main functions/subprograms: `test_core_type_based`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `test_core_type_based`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `stdint.h`, `stdbool.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Regressions usually show up as changed output fields, skipped clang builtins, or verifier/libbpf relocation failures before the program attaches.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_core_reloc_type_based.c` is a test fixture for CO-RE relocation and BTF type metadata selftest. Test signals are: feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_core_read.h>` | `char _license[] SEC("license") = "GPL";` | `SEC("raw_tracepoint/sys_enter")` | `out->struct_exists = bpf_core_type_exists(struct a_struct);` | `out->complex_struct_exists = bpf_core_type_exists(struct a_complex_struct);` | `out->union_exists = bpf_core_type_exists(union a_union);` | `out->enum_exists = bpf_core_type_exists(enum an_enum);` | `out->typedef_named_struct_exists = bpf_core_type_exists(named_struct_typedef);` | `out->typedef_anon_struct_exists = bpf_core_type_exists(anon_struct_typedef);` | and 31 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_based.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_id.c

Research item: `subset-b-006814` ordinal `2`. Source size: 3334 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_id.c_research.md`.

## Purpose
The program records libbpf/clang CO-RE relocation observations into global data so user-space selftests can compare target-kernel BTF behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_core_read`, `bpf_core_type_id_local`, `bpf_core_type_id_kernel`
- Declared maps: None visible in this compact source.
- Key local types: `struct a_struct`, `struct core_reloc_type_id_output`, `enum an_enum`, `typedef named_struct_typedef`, `typedef func_proto_typedef`, `typedef arr_typedef`
- Main functions/subprograms: `test_core_type_id`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `test_core_type_id`.

## State And Persistence Behavior
Global data/control fields include `_license`, `t1`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `stdint.h`, `stdbool.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Regressions usually show up as changed output fields, skipped clang builtins, or verifier/libbpf relocation failures before the program attaches.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_core_reloc_type_id.c` is a test fixture for CO-RE relocation and BTF type metadata selftest. Test signals are: feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_core_read.h>` | `char _license[] SEC("license") = "GPL";` | `SEC("raw_tracepoint/sys_enter")` | `out->local_anon_struct = bpf_core_type_id_local(struct { int marker_field; });` | `out->local_anon_union = bpf_core_type_id_local(union { int marker_field; });` | `out->local_anon_enum = bpf_core_type_id_local(enum { MARKER_ENUM_VAL = 123 });` | `out->local_anon_func_proto_ptr = bpf_core_type_id_local(_Bool(*)(int));` | `out->local_anon_void_ptr = bpf_core_type_id_local(void *);` | `out->local_anon_arr = bpf_core_type_id_local(_Bool[47]);` | and 14 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_type_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_retro.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_retro.c

Research item: `subset-b-006814` ordinal `3`. Source size: 1005 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_retro.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/raw_syscalls/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_core_read`, `bpf_get_current_task`, `bpf_get_current_pid_tgid`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Declared maps: `exp_tgid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `results: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: `struct task_struct`
- Main functions/subprograms: `handle_sys_enter`

## Control Flow
Entry programs are attached through `tp/raw_syscalls/sys_enter`. Control is organized around `handle_sys_enter`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `exp_tgid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `results: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_core_retro.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_core_read.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} exp_tgid_map SEC(".maps");` | `} results SEC(".maps");` | `SEC("tp/raw_syscalls/sys_enter")` | `struct task_struct *task = (void *)bpf_get_current_task();` | `int real_tgid = bpf_get_current_pid_tgid() >> 32;` | `int *exp_tgid = bpf_map_lookup_elem(&exp_tgid_map, &zero);` | `bpf_map_update_elem(&results, &zero, &tgid, 0);` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_retro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ctx.c

Research item: `subset-b-006814` ordinal `4`. Source size: 1026 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ctx.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `syscall`, `fentry/bpf_testmod_test_hardirq_fn`, `fentry/bpf_testmod_test_softirq_fn`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_experimental`, `bpf_kfunc_trigger_ctx_check`, `bpf_prog_test_run`, `bpf_in_task`, `bpf_testmod_test_hardirq_fn`, `bpf_in_hardirq`, `bpf_testmod_test_softirq_fn`, `bpf_in_serving_softirq`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `bpf_kfunc_trigger_ctx_check`, `trigger_all_contexts`, `BPF_PROG`

## Control Flow
Entry programs are attached through `syscall`, `fentry/bpf_testmod_test_hardirq_fn`, `fentry/bpf_testmod_test_softirq_fn`. Control is organized around `bpf_kfunc_trigger_ctx_check`, `trigger_all_contexts`, `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `count_hardirq`, `count_softirq`, `count_task`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_experimental.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ctx.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_experimental.h"` | `char _license[] SEC("license") = "GPL";` | `extern void bpf_kfunc_trigger_ctx_check(void) __ksym;` | `/* Triggered via bpf_prog_test_run from user-space */` | `SEC("syscall")` | `if (bpf_in_task())` | `bpf_kfunc_trigger_ctx_check();` | `SEC("fentry/bpf_testmod_test_hardirq_fn")` | and 3 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_custom_sec_handlers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_custom_sec_handlers.c

Research item: `subset-b-006814` ordinal `5`. Source size: 935 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_custom_sec_handlers.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `abc`, `abc/whatever`, `custom`, `custom/something`, `kprobe`, `xyz/blah`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_copy_from_user`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `abc1`, `abc2`, `custom1`, `custom2`, `kprobe1`, `xyz`

## Control Flow
Entry programs are attached through `abc`, `abc/whatever`, `custom`, `custom/something`, `kprobe`, `xyz/blah`. Control is organized around `abc1`, `abc2`, `custom1`, `custom2`, `kprobe1`, `xyz`.

## State And Persistence Behavior
Global data/control fields include `abc1_called`, `abc2_called`, `custom1_called`, `custom2_called`, `kprobe1_called`, `xyz_called`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_custom_sec_handlers.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("abc")` | `SEC("abc/whatever")` | `SEC("custom")` | `SEC("custom/something")` | `SEC("kprobe")` | `SEC("xyz/blah")` | `bpf_copy_from_user(&whatever, sizeof(whatever), NULL);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_custom_sec_handlers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path.c

Research item: `subset-b-006814` ordinal `6`. Source size: 1725 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path.c_research.md`.

## Purpose
The code exercises `bpf_d_path` or related path helpers against kernel pointer arguments and validates allowed memory classes and type checks. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `fentry/security_inode_getattr`, `fentry/filp_close`, `fentry/vfs_fallocate`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_current_pid_tgid`, `bpf_d_path`
- Declared maps: None visible in this compact source.
- Key local types: `struct path`, `struct kstat`, `struct file`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `fentry/security_inode_getattr`, `fentry/filp_close`, `fentry/vfs_fallocate`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `cnt_stat`, `cnt_close`, `paths_stat`, `paths_close`, `rets_stat`, `rets_close`, `called_stat`, `called_close`, `path_match_fallocate`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risk is centered on helper availability, BTF type identity, writable versus read-only memory checks, and tracepoint/kprobe context compatibility.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_d_path.c` is a test fixture for d_path helper and verifier access selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("fentry/security_inode_getattr")` | `pid_t pid = bpf_get_current_pid_tgid() >> 32;` | `ret = bpf_d_path(path, paths_stat[cnt], MAX_PATH_LEN);` | `SEC("fentry/filp_close")` | `ret = bpf_d_path(&file->f_path,` | `SEC("fentry/vfs_fallocate")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_rdonly_mem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_rdonly_mem.c

Research item: `subset-b-006814` ordinal `7`. Source size: 717 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_rdonly_mem.c_research.md`.

## Purpose
The code exercises `bpf_d_path` or related path helpers against kernel pointer arguments and validates allowed memory classes and type checks. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `fentry/security_inode_getattr`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_prog_active`, `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`, `bpf_d_path`
- Declared maps: None visible in this compact source.
- Key local types: `struct path`, `struct kstat`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `fentry/security_inode_getattr`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risk is centered on helper availability, BTF type identity, writable versus read-only memory checks, and tracepoint/kprobe context compatibility.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_d_path_check_rdonly_mem.c` is a test fixture for d_path helper and verifier access selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `extern const int bpf_prog_active __ksym;` | `SEC("fentry/security_inode_getattr")` | `cpu = bpf_get_smp_processor_id();` | `active = (void *)bpf_per_cpu_ptr(&bpf_prog_active, cpu);` | `bpf_d_path(path, active, sizeof(int));` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_rdonly_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_types.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_types.c

Research item: `subset-b-006814` ordinal `8`. Source size: 756 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_types.c_research.md`.

## Purpose
The code exercises `bpf_d_path` or related path helpers against kernel pointer arguments and validates allowed memory classes and type checks. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `fentry/security_inode_getattr`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_prog_active`, `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`, `bpf_ringbuf_submit`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF, max 1 << 12`
- Key local types: `struct path`, `struct kstat`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `fentry/security_inode_getattr`. Control is organized around `BPF_PROG`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF, max 1 << 12`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risk is centered on helper availability, BTF type identity, writable versus read-only memory checks, and tracepoint/kprobe context compatibility.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_d_path_check_types.c` is a test fixture for d_path helper and verifier access selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `extern const int bpf_prog_active __ksym;` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | `SEC("fentry/security_inode_getattr")` | `cpu = bpf_get_smp_processor_id();` | `active = (void *)bpf_per_cpu_ptr(&bpf_prog_active, cpu);` | `bpf_ringbuf_submit(active, 0);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_d_path_check_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_deny_namespace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_deny_namespace.c

Research item: `subset-b-006814` ordinal `9`. Source size: 627 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_deny_namespace.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/userns_create`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`
- Declared maps: None visible in this compact source.
- Key local types: `struct cred`, `typedef kernel_cap_t`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/userns_create`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `errno.h`, `linux/capability.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_deny_namespace.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `char _license[] SEC("license") = "GPL";` | `SEC("lsm.s/userns_create")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_deny_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_dst_clear.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_dst_clear.c

Research item: `subset-b-006814` ordinal `10`. Source size: 1344 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_dst_clear.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc/egress`
- BPF helpers/macros used: `bpf_tracing_net`, `bpf_helpers`, `bpf_endian`, `bpf_cast_to_kern_ctx`, `bpf_skb_load_bytes`, `bpf_skb_adjust_room`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`, `struct sk_buff`, `struct iphdr`, `struct udphdr`
- Main functions/subprograms: `dst_clear`

## Control Flow
Entry programs are attached through `tc/egress`. Control is organized around `dst_clear`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `had_dst`, `dst_cleared`, `__license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `vmlinux.h`, `bpf_tracing_net.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_dst_clear.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include "bpf_tracing_net.h"` | `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `void *bpf_cast_to_kern_ctx(void *) __ksym;` | `SEC("tc/egress")` | `if (skb->protocol != __bpf_constant_htons(ETH_P_IP))` | `return TC_ACT_OK;` | `if (bpf_skb_load_bytes(skb, ETH_HLEN, &iph, sizeof(iph)))` | `if (bpf_skb_load_bytes(skb, ETH_HLEN + sizeof(iph), &udph, sizeof(udph)))` | `if (udph.dest != __bpf_constant_htons(UDP_TEST_PORT))` | and 4 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_dst_clear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_enable_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_enable_stats.c

Research item: `subset-b-006814` ordinal `11`. Source size: 339 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_enable_stats.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `test_enable_stats`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `test_enable_stats`.

## State And Persistence Behavior
Global data/control fields include `_license`, `count`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `stdint.h`, `linux/types.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_enable_stats.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `SEC("raw_tracepoint/sys_enter")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_enable_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_endian.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_endian.c

Research item: `subset-b-006814` ordinal `12`. Source size: 700 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_endian.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `sys_enter`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `sys_enter`.

## State And Persistence Behavior
Global data/control fields include `in16`, `in32`, `in64`, `out16`, `out32`, `out64`, `const16`, `const32`, `const64`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_endian.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `SEC("raw_tp/sys_enter")` | `const16 = ___bpf_swab16(IN16);` | `const32 = ___bpf_swab32(IN32);` | `const64 = ___bpf_swab64(IN64);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_endian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fill_link_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fill_link_info.c

Research item: `subset-b-006814` ordinal `13`. Source size: 1078 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fill_link_info.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `kprobe`, `uprobe`, `tracepoint`, `perf_event`, `kprobe.multi`, `uprobe.multi`
- BPF helpers/macros used: `bpf_tracing`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `unused`, `BPF_PROG`, `event_run`

## Control Flow
Entry programs are attached through `kprobe`, `uprobe`, `tracepoint`, `perf_event`, `kprobe.multi`, `uprobe.multi`. Control is organized around `unused`, `BPF_PROG`, `event_run`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_tracing.h`, `stdbool.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_fill_link_info.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `SEC("kprobe")` | `SEC("uprobe")` | `SEC("tracepoint")` | `SEC("perf_event")` | `SEC("kprobe.multi")` | `SEC("uprobe.multi")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fill_link_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fsverity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fsverity.c

Research item: `subset-b-006814` ordinal `14`. Source size: 1100 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fsverity.c_research.md`.

## Purpose
The program attaches to file-security hooks or tracing points to validate xattr, fsverity, and inode metadata helper behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/file_open`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_kfuncs`, `bpf_dynptr`, `bpf_get_current_pid_tgid`, `bpf_dynptr_from_mem`, `bpf_get_fsverity_digest`
- Declared maps: None visible in this compact source.
- Key local types: `struct fsverity_digest`, `struct file`, `struct bpf_dynptr`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/file_open`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `expected_digest`, `digest`, `monitored_pid`, `got_fsverity`, `digest_matches`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_kfuncs.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Kernel VFS, LSM hook signature, and helper permission changes can alter verifier acceptance or expected errno/data capture.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_fsverity.c` is a test fixture for LSM/file metadata BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_kfuncs.h"` | `char _license[] SEC("license") = "GPL";` | `SEC("lsm.s/file_open")` | `struct bpf_dynptr digest_ptr;` | `pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_dynptr_from_mem(digest, sizeof(digest), 0, &digest_ptr);` | `ret = bpf_get_fsverity_digest(f, &digest_ptr);`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fsverity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp.c

Research item: `subset-b-006814` ordinal `15`. Source size: 3092 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_stack_build_id`, `bpf_get_stack`, `bpf_prog1`, `bpf_map_lookup_elem`, `bpf_get_current_pid_tgid`, `bpf_perf_event_output`
- Declared maps: `perfmap: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 2`, `stackdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value struct stack_trace_t`, `rawdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64[2 * MAX_STACK_RAWTP]`
- Key local types: `struct stack_trace_t`, `struct bpf_stack_build_id`
- Main functions/subprograms: `bpf_prog1`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `bpf_prog1`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `perfmap: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 2`, `stackdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value struct stack_trace_t`, `rawdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64[2 * MAX_STACK_RAWTP]`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_get_stack_rawtp.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `struct bpf_stack_build_id user_stack_buildid[MAX_STACK_RAWTP];` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} perfmap SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} stackdata_map SEC(".maps");` | `*   usize = bpf_get_stack(ctx, raw_data, max_len, BPF_F_USER_STACK);` | `*   ksize = bpf_get_stack(ctx, raw_data + usize, max_len - usize, 0);` | `} rawdata_map SEC(".maps");` | `SEC("raw_tracepoint/sys_enter")` | and 13 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp_err.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp_err.c

Research item: `subset-b-006814` ordinal `16`. Source size: 438 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp_err.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_prog2`, `bpf_get_stack`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `bpf_prog2`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `bpf_prog2`. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_get_stack_rawtp_err.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("raw_tracepoint/sys_enter")` | `int bpf_prog2(void *ctx)` | `error = bpf_get_stack(ctx, stack, 0, -1);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_xattr.c

Research item: `subset-b-006814` ordinal `17`. Source size: 1947 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_xattr.c_research.md`.

## Purpose
The program attaches to file-security hooks or tracing points to validate xattr, fsverity, and inode metadata helper behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/file_open`, `lsm.s/inode_getxattr`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_kfuncs`, `bpf_misc`, `bpf_dynptr`, `bpf_get_current_pid_tgid`, `bpf_dynptr_from_mem`, `bpf_get_file_xattr`, `bpf_strncmp`, `bpf_get_dentry_xattr`
- Declared maps: None visible in this compact source.
- Key local types: `struct file`, `struct bpf_dynptr`, `struct dentry`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/file_open`, `lsm.s/inode_getxattr`. Control is organized around `BPF_PROG`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `monitored_pid`, `found_xattr_from_file`, `found_xattr_from_dentry`, `expected_value`, `value1`, `value2`, `xattr_names`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_kfuncs.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Kernel VFS, LSM hook signature, and helper permission changes can alter verifier acceptance or expected errno/data capture.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_get_xattr.c` is a test fixture for LSM/file metadata BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_kfuncs.h"` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `SEC("lsm.s/file_open")` | `struct bpf_dynptr value_ptr;` | `pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_dynptr_from_mem(value1, sizeof(value1), 0, &value_ptr);` | `ret = bpf_get_file_xattr(f, xattr_names[i], &value_ptr);` | and 5 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_data.c

Research item: `subset-b-006814` ordinal `18`. Source size: 2401 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_data.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_update_elem`
- Declared maps: `result_number: BPF_MAP_TYPE_ARRAY, max 11, key __u32, value __u64`, `result_string: BPF_MAP_TYPE_ARRAY, max 5`, `result_struct: BPF_MAP_TYPE_ARRAY, max 5, key __u32, value struct foo`
- Key local types: `struct foo`, `struct __sk_buff`
- Main functions/subprograms: `load_static_data`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `load_static_data`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `result_number: BPF_MAP_TYPE_ARRAY, max 11, key __u32, value __u64`, `result_string: BPF_MAP_TYPE_ARRAY, max 5`, `result_struct: BPF_MAP_TYPE_ARRAY, max 5, key __u32, value struct foo`. Global data/control fields include `num2`, `num5`, `num6`, `str0`, `struct0`, `struct2`, `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `linux/pkt_cls.h`, `string.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_data.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} result_number SEC(".maps");` | `} result_string SEC(".maps");` | `} result_struct SEC(".maps");` | `bpf_map_update_elem(&result_##map, &key, var, 0);	\` | `SEC("tc")` | `return TC_ACT_OK;` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func1.c

Research item: `subset-b-006814` ordinal `19`. Source size: 1032 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func1.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f0`, `f1`, `f3`, `f2`, `global_func1`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f0`, `f1`, `f3`, `f2`, `global_func1`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func1.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__failure __msg("combined stack size of 3 calls is")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func10.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func10.c

Research item: `subset-b-006814` ordinal `20`. Source size: 601 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func10.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct Small`, `struct Big`, `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func10`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func10`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func10.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `return bpf_get_prandom_u32() < big->y;` | `SEC("cgroup_skb/ingress")` | `__failure __msg("invalid read from stack")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func11.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func11.c

Research item: `subset-b-006814` ordinal `21`. Source size: 409 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func11.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct S`, `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func11`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func11`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func11.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `return s ? bpf_get_prandom_u32() < s->x : 0;` | `SEC("cgroup_skb/ingress")` | `__failure __msg("Caller passes invalid args into func#1")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func12.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func12.c

Research item: `subset-b-006814` ordinal `22`. Source size: 424 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func12.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct S`, `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func12`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func12`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func12.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `return bpf_get_prandom_u32() < s->x;` | `SEC("cgroup_skb/ingress")` | `__failure __msg("invalid mem access 'mem_or_null'")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func13.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func13.c

Research item: `subset-b-006814` ordinal `23`. Source size: 460 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func13.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct S`, `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func13`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func13`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func13.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `return bpf_get_prandom_u32() < s->x;` | `SEC("cgroup_skb/ingress")` | `__failure __msg("Caller passes invalid args into func#1")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func14.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func14.c

Research item: `subset-b-006814` ordinal `24`. Source size: 421 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func14.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct S`, `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func14`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func14`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func14.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `return bpf_get_prandom_u32() < *(const int *) s;` | `SEC("cgroup_skb/ingress")` | `__failure __msg("reference type('FWD S') size cannot be determined")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func15.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func15.c

Research item: `subset-b-006814` ordinal `25`. Source size: 1539 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func15.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func15`, `global_func15_tricky_pruning`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func15`, `global_func15_tricky_pruning`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func15.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `*v = bpf_get_prandom_u32();` | `SEC("cgroup_skb/ingress")` | `__failure __msg("At program exit the register R0 has ")` | `__failure` | `__msg("mark_precise: frame0: regs=r0 stack= before 2: (b7) r0 = 1")` | `__msg("mark_precise: frame0: regs=r0 stack= before 0: (85) call bpf_get_prandom_u32#7")` | `__msg("At program exit the register R0 has ")` | `"call %[bpf_get_prandom_u32];"` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func16.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func16.c

Research item: `subset-b-006814` ordinal `26`. Source size: 366 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func16.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func16`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func16`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func16.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("cgroup_skb/ingress")` | `__success`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func17.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func17.c

Research item: `subset-b-006814` ordinal `27`. Source size: 350 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func17.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func17`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `foo`, `global_func17`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func17.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__failure __msg("Caller passes invalid args into func#1")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func2.c

Research item: `subset-b-006814` ordinal `28`. Source size: 912 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func2.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f0`, `f1`, `f3`, `f2`, `global_func2`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f0`, `f1`, `f3`, `f2`, `global_func2`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func2.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__success`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func3.c

Research item: `subset-b-006814` ordinal `29`. Source size: 1026 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func3.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f1`, `f2`, `f3`, `f4`, `f5`, `f6`, `f7`, `f8`, `global_func3`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f1`, `f2`, `f3`, `f4`, `f5`, `f6`, `f7`, `f8`, `global_func3`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func3.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__failure __msg("the call stack of 9 frames")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func4.c

Research item: `subset-b-006814` ordinal `30`. Source size: 855 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func4.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f1`, `f2`, `f3`, `f4`, `f5`, `f6`, `f7`, `global_func4`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f1`, `f2`, `f3`, `f4`, `f5`, `f6`, `f7`, `global_func4`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func4.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__success`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func5.c

Research item: `subset-b-006814` ordinal `31`. Source size: 657 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func5.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f1`, `f3`, `f2`, `global_func5`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f1`, `f3`, `f2`, `global_func5`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func5.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__failure __msg("expects pointer to ctx")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func6.c

Research item: `subset-b-006814` ordinal `32`. Source size: 649 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func6.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f1`, `f3`, `f2`, `global_func6`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `f1`, `f3`, `f2`, `global_func6`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func6.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__failure __msg("modified ctx ptr R2")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func7.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func7.c

Research item: `subset-b-006814` ordinal `33`. Source size: 340 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func7.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func7`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `foo`, `global_func7`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func7.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `__success`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func8.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func8.c

Research item: `subset-b-006814` ordinal `34`. Source size: 368 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func8.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `foo`, `global_func8`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `global_func8`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func8.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `return bpf_get_prandom_u32();` | `SEC("cgroup_skb/ingress")` | `__success`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func9.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func9.c

Research item: `subset-b-006814` ordinal `35`. Source size: 1579 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func9.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_prandom_u32`, `bpf_map_lookup_elem`
- Declared maps: `map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct S`
- Key local types: `struct S`, `struct C`, `struct __sk_buff`, `enum E`
- Main functions/subprograms: `foo`, `bar`, `baz`, `qux`, `quux`, `quuz`, `global_func9`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `foo`, `bar`, `baz`, `qux`, `quux`, `quuz`, `global_func9`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct S`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func9.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} map SEC(".maps");` | `return bpf_get_prandom_u32() < s->x;` | `*x &= bpf_get_prandom_u32();` | `SEC("cgroup_skb/ingress")` | `__success` | `const struct S *s = bpf_map_lookup_elem(&map, &key);`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_args.c

Research item: `subset-b-006814` ordinal `36`. Source size: 1213 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_args.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_update_elem`
- Declared maps: `values: BPF_MAP_TYPE_ARRAY, max 7, key __u32, value int`
- Key local types: `struct S`, `struct __sk_buff`
- Main functions/subprograms: `save_value`, `foo`, `bar`, `baz`, `test_cls`

## Control Flow
Entry programs are attached through `cgroup_skb/ingress`. Control is organized around `save_value`, `foo`, `bar`, `baz`, `test_cls`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `values: BPF_MAP_TYPE_ARRAY, max 7, key __u32, value int`. Global data/control fields include `global_variable`, `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func_args.c` is a test fixture for BPF global function verifier selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} values SEC(".maps");` | `bpf_map_update_elem(&values, &index, &value, 0);` | `SEC("cgroup_skb/ingress")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_ctx_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_ctx_args.c

Research item: `subset-b-006814` ordinal `37`. Source size: 3618 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_ctx_args.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?kprobe`, `?raw_tp`, `?perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_core_read`, `bpf_misc`, `bpf_user_pt_regs_t`, `bpf_get_stack`, `bpf_target_s390`, `bpf_raw_tracepoint_args`, `bpf_perf_event_data`
- Declared maps: None visible in this compact source.
- Key local types: `struct type`, `struct bpf_user_pt_regs_t`, `struct hack`, `struct types`, `struct pt_regs`, `struct bpf_raw_tracepoint_args`, `struct bpf_perf_event_data`, `struct my_struct`
- Main functions/subprograms: `kprobe_typedef_ctx_subprog`, `kprobe_typedef_ctx`, `kprobe_struct_ctx_subprog`, `kprobe_resolved_ctx`, `kprobe_workaround_ctx_subprog`, `kprobe_workaround_ctx`, `raw_tp_ctx_subprog`, `raw_tp_ctx`, `raw_tp_writable_ctx_subprog`, `raw_tp_writable_ctx`, `perf_event_ctx_subprog`, `perf_event_ctx`, `subprog_ctx_tag`, `subprog_multi_ctx_tags`, `arg_tag_ctx_raw_tp`, `arg_tag_ctx_perf`, and 1 more.

## Control Flow
Entry programs are attached through `?kprobe`, `?raw_tp`, `?perf_event`. Control is organized around `kprobe_typedef_ctx_subprog`, `kprobe_typedef_ctx`, `kprobe_struct_ctx_subprog`, `kprobe_resolved_ctx`, `kprobe_workaround_ctx_subprog`, `kprobe_workaround_ctx`, `raw_tp_ctx_subprog`, `raw_tp_ctx`, `raw_tp_writable_ctx_subprog`, `raw_tp_writable_ctx`, `perf_event_ctx_subprog`, `perf_event_ctx`, and 5 more.. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`.
Local test dependencies: `vmlinux.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func_ctx_args.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `__weak int kprobe_typedef_ctx_subprog(bpf_user_pt_regs_t *ctx)` | `return bpf_get_stack(ctx, &stack, sizeof(stack), 0);` | `SEC("?kprobe")` | `__success` | `* typedef user_pt_regs bpf_user_pt_regs_t;` | and 15 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_ctx_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_deep_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_deep_stack.c

Research item: `subset-b-006814` ordinal `38`. Source size: 2704 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_deep_stack.c_research.md`.

## Purpose
The file stresses subprogram calls, argument typing, context propagation, stack accounting, return-value bounds, and verifier diagnostics for global functions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `syscall`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `f0`, `XCAT`, `global_func_deep_stack_success`, `global_func_deep_stack_fail`

## Control Flow
Entry programs are attached through `syscall`. Control is organized around `f0`, `XCAT`, `global_func_deep_stack_success`, `global_func_deep_stack_fail`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Expected failures are as important as successful loads; changes can invalidate precise verifier log substrings or call-depth assumptions.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_func_deep_stack.c` is a test fixture for BPF global function verifier selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("syscall")` | `__success` | `__failure __msg("combined stack size of 34 calls")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_func_deep_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_map_resize.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_map_resize.c

Research item: `subset-b-006814` ordinal `39`. Source size: 2301 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_map_resize.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `.data.custom`, `.data.non_array`, `.data.array_not_last`, `.data.percpu_arr`, `tp/syscalls/sys_enter_getpid`, `tp/syscalls/sys_enter_getuid`, `struct_ops/test_1`, `.struct_ops.link`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_current_pid_tgid`, `bpf_get_smp_processor_id`, `bpf_testmod_ops`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_testmod_ops`
- Main functions/subprograms: `SEC`, `bss_array_sum`, `data_array_sum`, `BPF_PROG`

## Control Flow
Entry programs are attached through `.data.custom`, `.data.non_array`, `.data.array_not_last`, `.data.percpu_arr`, `tp/syscalls/sys_enter_getpid`, `tp/syscalls/sys_enter_getuid`, `struct_ops/test_1`, `.struct_ops.link`. Control is organized around `SEC`, `bss_array_sum`, `data_array_sum`, `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `sum`, `array`, `my_array`, `my_array_first`, `percpu_arr`, `version_sink`, `st_ops_resize`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_global_map_resize.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `char _license[] SEC("license") = "GPL";` | `int my_array[1] SEC(".data.custom");` | `int my_int SEC(".data.non_array");` | `int my_array_first[1] SEC(".data.array_not_last");` | `int my_int_last SEC(".data.array_not_last");` | `int percpu_arr[1] SEC(".data.percpu_arr");` | `SEC("tp/syscalls/sys_enter_getpid")` | `if (pid != (bpf_get_current_pid_tgid() >> 32))` | and 6 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_global_map_resize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_hash_large_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_hash_large_key.c

Research item: `subset-b-006814` ordinal `40`. Source size: 793 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_hash_large_key.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_hash_large_key_test`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Declared maps: `hash_map: BPF_MAP_TYPE_HASH, max 2, key struct bigelement, value __u32`, `key_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value struct bigelement`
- Key local types: `struct bigelement`
- Main functions/subprograms: `bpf_hash_large_key_test`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `bpf_hash_large_key_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `hash_map: BPF_MAP_TYPE_HASH, max 2, key struct bigelement, value __u32`, `key_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value struct bigelement`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_hash_large_key.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} hash_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} key_map SEC(".maps");` | `SEC("raw_tracepoint/sys_enter")` | `int bpf_hash_large_key_test(void *ctx)` | `key = bpf_map_lookup_elem(&key_map, &zero);` | `if (bpf_map_update_elem(&hash_map, key, &value, BPF_ANY))`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_hash_large_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_helper_restricted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_helper_restricted.c

Research item: `subset-b-006814` ordinal `41`. Source size: 1820 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_helper_restricted.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?raw_tp/sys_enter`, `?tp/syscalls/sys_enter_nanosleep`, `?kprobe`, `?perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_timer`, `bpf_spin_lock`, `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_timer_cancel`, `bpf_spin_unlock`
- Declared maps: `timers: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct timer`, `locks: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct lock`
- Key local types: `struct timer`, `struct bpf_timer`, `struct lock`, `struct bpf_spin_lock`
- Main functions/subprograms: `timer_cb`, `timer_work`, `spin_lock_work`, `raw_tp_timer`, `tp_timer`, `kprobe_timer`, `perf_event_timer`, `raw_tp_spin_lock`, `tp_spin_lock`, `kprobe_spin_lock`, `perf_event_spin_lock`

## Control Flow
Entry programs are attached through `?raw_tp/sys_enter`, `?tp/syscalls/sys_enter_nanosleep`, `?kprobe`, `?perf_event`. Control is organized around `timer_cb`, `timer_work`, `spin_lock_work`, `raw_tp_timer`, `tp_timer`, `kprobe_timer`, `perf_event_timer`, `raw_tp_spin_lock`, `tp_spin_lock`, `kprobe_spin_lock`, `perf_event_spin_lock`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `timers: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct timer`, `locks: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct lock`. Global data/control fields include `LICENSE`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `time.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_helper_restricted.c` is a test fixture for BPF map operation selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `struct bpf_timer t;` | `struct bpf_spin_lock l;` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} timers SEC(".maps");` | `} locks SEC(".maps");` | `timer  = bpf_map_lookup_elem(&timers, &key);` | `bpf_timer_init(&timer->t, &timers, CLOCK_MONOTONIC);` | `bpf_timer_set_callback(&timer->t, timer_cb);` | `bpf_timer_start(&timer->t, 10E9, 0);` | and 9 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_helper_restricted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_jhash.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_jhash.h

Research item: `subset-b-006814` ordinal `42`. Source size: 2124 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_jhash.h_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: None visible in this compact source.
- Declared maps: None visible in this compact source.
- Key local types: `typedef u32`
- Main functions/subprograms: `rol32`, `jhash`, `jhash2`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `rol32`, `jhash`, `jhash2`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `features.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_jhash.h` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: No concentrated marker lines; rely on the API/function lists above.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_jhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kernel_flag.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kernel_flag.c

Research item: `subset-b-006814` ordinal `43`. Source size: 550 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kernel_flag.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/bpf`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_attr`, `bpf_get_current_pid_tgid`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/bpf`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `monitored_tid`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_kernel_flag.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `char _license[] SEC("license") = "GPL";` | `SEC("lsm.s/bpf")` | `int BPF_PROG(bpf, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)` | `tid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kernel_flag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_dynptr_param.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_dynptr_param.c

Research item: `subset-b-006814` ordinal `44`. Source size: 2093 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_dynptr_param.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?lsm.s/bpf`, `lsm.s/bpf`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_misc`, `bpf_key`, `bpf_lookup_system_key`, `bpf_key_put`, `bpf_verify_pkcs7_signature`, `bpf_dynptr`, `bpf_attr`, `bpf_get_current_pid_tgid`, `bpf_map_lookup_elem`, `bpf_dynptr_from_mem`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF, max 4096`, `array_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u32`
- Key local types: `struct bpf_key`, `struct bpf_dynptr`
- Main functions/subprograms: `bpf_key_put`, `bpf_verify_pkcs7_signature`, `BPF_PROG`

## Control Flow
Entry programs are attached through `?lsm.s/bpf`, `lsm.s/bpf`. Control is organized around `bpf_key_put`, `bpf_verify_pkcs7_signature`, `BPF_PROG`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF, max 4096`, `array_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u32`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_kfunc_dynptr_param.c` is a test fixture for BPF map operation selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_misc.h"` | `extern struct bpf_key *bpf_lookup_system_key(__u64 id) __ksym;` | `extern void bpf_key_put(struct bpf_key *key) __ksym;` | `extern int bpf_verify_pkcs7_signature(struct bpf_dynptr *data_ptr,` | `struct bpf_dynptr *sig_ptr,` | `struct bpf_key *trusted_keyring) __ksym;` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | and 22 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_dynptr_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_param_nullable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_param_nullable.c

Research item: `subset-b-006814` ordinal `45`. Source size: 874 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_param_nullable.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_kfuncs`, `bpf_testmod_kfunc`, `bpf_dynptr`, `bpf_dynptr_from_skb`, `bpf_kfunc_dynptr_test`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`, `struct bpf_dynptr`
- Main functions/subprograms: `kfunc_dynptr_nullable_test1`, `kfunc_dynptr_nullable_test2`, `kfunc_dynptr_nullable_test3`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `kfunc_dynptr_nullable_test1`, `kfunc_dynptr_nullable_test2`, `kfunc_dynptr_nullable_test3`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`, `bpf_kfuncs.h`, `../test_kmods/bpf_testmod_kfunc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_kfunc_param_nullable.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `#include "bpf_kfuncs.h"` | `#include "../test_kmods/bpf_testmod_kfunc.h"` | `SEC("tc")` | `struct bpf_dynptr data;` | `bpf_dynptr_from_skb(skb, 0, &data);` | `bpf_kfunc_dynptr_test(&data, NULL);` | `bpf_kfunc_dynptr_test(&data, &data);` | `__failure __msg("Possibly NULL pointer passed to trusted arg0")` | and 2 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_kfunc_param_nullable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms.c

Research item: `subset-b-006814` ordinal `46`. Source size: 825 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_link_fops`, `bpf_link_fops1`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler`.

## State And Persistence Behavior
Global data/control fields include `out__bpf_link_fops`, `out__bpf_link_fops1`, `out__btf_size`, `out__per_cpu_start`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stdbool.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__u64 out__bpf_link_fops = -1;` | `__u64 out__bpf_link_fops1 = -1;` | `extern const void bpf_link_fops __ksym;` | `extern const void bpf_link_fops1 __ksym __weak;` | `SEC("raw_tp/sys_enter")` | `out__bpf_link_fops = (__u64)&bpf_link_fops;` | `out__bpf_link_fops1 = (__u64)&bpf_link_fops1;` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf.c

Research item: `subset-b-006814` ordinal `47`. Source size: 1408 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_prog_active`, `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`, `bpf_this_cpu_ptr`
- Declared maps: None visible in this compact source.
- Key local types: `struct fields`, `struct rq`, `struct type`
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `out__runqueues_addr`, `out__bpf_prog_active_addr`, `out__rq_cpu`, `out__bpf_prog_active`, `out__this_rq_cpu`, `out__this_bpf_prog_active`, `out__cpu_0_rq_cpu`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms_btf.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__u64 out__bpf_prog_active_addr = -1;` | `int out__bpf_prog_active = -1; /* percpu int */` | `int out__this_bpf_prog_active = -1;` | `extern const int bpf_prog_active __ksym; /* int type global var. */` | `SEC("raw_tp/sys_enter")` | `out__bpf_prog_active_addr = (__u64)&bpf_prog_active;` | `cpu = bpf_get_smp_processor_id();` | `/* test bpf_per_cpu_ptr() */` | `rq = (struct rq *)bpf_per_cpu_ptr(&runqueues, cpu);` | and 8 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_null_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_null_check.c

Research item: `subset-b-006814` ordinal `48`. Source size: 715 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_null_check.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_prog_active`, `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`
- Declared maps: None visible in this compact source.
- Key local types: `struct rq`, `struct type`
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms_btf_null_check.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `extern const int bpf_prog_active __ksym; /* int type global var. */` | `SEC("raw_tp/sys_enter")` | `cpu = bpf_get_smp_processor_id();` | `rq = (struct rq *)bpf_per_cpu_ptr(&runqueues, cpu);` | `active = (int *)bpf_per_cpu_ptr(&bpf_prog_active, cpu);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_null_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_write_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_write_check.c

Research item: `subset-b-006814` ordinal `49`. Source size: 824 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_write_check.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_prog_active`, `bpf_get_smp_processor_id`, `bpf_per_cpu_ptr`, `bpf_this_cpu_ptr`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handler1`, `write_active`, `handler2`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler1`, `write_active`, `handler2`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms_btf_write_check.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `extern const int bpf_prog_active __ksym; /* int type global var. */` | `SEC("raw_tp/sys_enter")` | `cpu = bpf_get_smp_processor_id();` | `active = (int *)bpf_per_cpu_ptr(&bpf_prog_active, cpu);` | `active = bpf_this_cpu_ptr(&bpf_prog_active);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_btf_write_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_module.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_module.c

Research item: `subset-b-006814` ordinal `50`. Source size: 1329 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_module.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_testmod_ksym_percpu`, `bpf_testmod_test_mod_kfunc`, `bpf_testmod_invalid_mod_kfunc`, `bpf_this_cpu_ptr`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `bpf_testmod_test_mod_kfunc`, `bpf_testmod_invalid_mod_kfunc`, `load`, `load_256`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `bpf_testmod_test_mod_kfunc`, `bpf_testmod_invalid_mod_kfunc`, `load`, `load_256`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `out_bpf_testmod_ksym`, `LICENSE`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms_module.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `extern const int bpf_testmod_ksym_percpu __ksym;` | `extern void bpf_testmod_test_mod_kfunc(int i) __ksym;` | `extern void bpf_testmod_invalid_mod_kfunc(void) __ksym __weak;` | `int out_bpf_testmod_ksym = 0;` | `SEC("tc")` | `bpf_testmod_invalid_mod_kfunc();` | `bpf_testmod_test_mod_kfunc(42);` | `out_bpf_testmod_ksym = *(int *)bpf_this_cpu_ptr(&bpf_testmod_ksym_percpu);` | `REPEAT_256(bpf_testmod_test_mod_kfunc(42););` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_weak.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_weak.c

Research item: `subset-b-006814` ordinal `51`. Source size: 1854 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_weak.c_research.md`.

## Purpose
The file validates BPF access to typed kernel symbols or kfunc calls, including nullable parameters, dynptr parameters, module symbols, and weak references. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_prog_active`, `bpf_task_acquire`, `bpf_testmod_test_mod_kfunc`, `bpf_link_fops1`, `bpf_link_fops2`, `bpf_per_cpu_ptr`, `bpf_ksym_exists`
- Declared maps: None visible in this compact source.
- Key local types: `struct rq`, `struct task_struct`
- Main functions/subprograms: `bpf_testmod_test_mod_kfunc`, `invalid_kfunc`, `pass_handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `bpf_testmod_test_mod_kfunc`, `invalid_kfunc`, `pass_handler`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `out__existing_typed`, `out__existing_typeless`, `out__non_existent_typeless`, `out__non_existent_typed`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
BTF availability, module load state, nullable contract enforcement, and read/write restrictions can change load outcomes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ksyms_weak.c` is a test fixture for kernel symbol/kfunc/BTF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `extern const void bpf_prog_active __ksym __weak; /* typeless */` | `struct task_struct *bpf_task_acquire(struct task_struct *p) __ksym __weak;` | `void bpf_testmod_test_mod_kfunc(int i) __ksym __weak;` | `extern const void bpf_link_fops1 __ksym __weak;` | `extern const int bpf_link_fops2 __ksym __weak;` | `SEC("raw_tp/sys_enter")` | `rq = (struct rq *)bpf_per_cpu_ptr(&runqueues, 0);` | `if (rq && bpf_ksym_exists(&runqueues))` | `out__existing_typeless = (__u64)&bpf_prog_active;` | and 10 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ksyms_weak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb.c

Research item: `subset-b-006814` ordinal `52`. Source size: 10880 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb.c_research.md`.

## Purpose
The program parses Ethernet/IP/TCP/UDP/ICMP traffic, looks up VIP/backend maps, updates per-CPU stats, and rewrites or redirects packets in TC/XDP style paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_map_lookup_elem`, `bpf_tunnel_key`, `bpf_ntohs`, `bpf_skb_set_tunnel_key`, `bpf_redirect`, `bpf_htons`
- Declared maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`
- Key local types: `struct packet_description`, `struct ctl_value`, `struct vip_meta`, `struct real_definition`, `struct vip_stats`, `struct eth_hdr`, `struct vip`, `struct icmp6hdr`, `struct ipv6hdr`, `struct icmphdr`, `struct iphdr`, `struct udphdr`, `struct tcphdr`, `struct __sk_buff`, and 2 more.
- Main functions/subprograms: `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/pkt_cls.h`, `linux/bpf.h`, `linux/in.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/icmp.h`, `linux/icmpv6.h`, `linux/tcp.h`, and 3 more..
Local test dependencies: `test_iptunnel_common.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Bounds checks, endian conversion, checksum updates, dynptr handling, and map value layout are the main compatibility risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_l4lb.c` is a test fixture for packet parser and L4 load-balancer selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} vip_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} ch_rings SEC(".maps");` | `} reals SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} stats SEC(".maps");` | `} ctl_array SEC(".maps");` | and 18 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline.c

Research item: `subset-b-006814` ordinal `53`. Source size: 10814 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline.c_research.md`.

## Purpose
The program parses Ethernet/IP/TCP/UDP/ICMP traffic, looks up VIP/backend maps, updates per-CPU stats, and rewrites or redirects packets in TC/XDP style paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_map_lookup_elem`, `bpf_tunnel_key`, `bpf_ntohs`, `bpf_skb_set_tunnel_key`, `bpf_redirect`, `bpf_htons`
- Declared maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`
- Key local types: `struct packet_description`, `struct ctl_value`, `struct vip_meta`, `struct real_definition`, `struct vip_stats`, `struct eth_hdr`, `struct vip`, `struct icmp6hdr`, `struct ipv6hdr`, `struct icmphdr`, `struct iphdr`, `struct udphdr`, `struct tcphdr`, `struct __sk_buff`, and 2 more.
- Main functions/subprograms: `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/pkt_cls.h`, `linux/bpf.h`, `linux/in.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/icmp.h`, `linux/icmpv6.h`, `linux/tcp.h`, and 3 more..
Local test dependencies: `test_iptunnel_common.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Bounds checks, endian conversion, checksum updates, dynptr handling, and map value layout are the main compatibility risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_l4lb_noinline.c` is a test fixture for packet parser and L4 load-balancer selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} vip_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} ch_rings SEC(".maps");` | `} reals SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} stats SEC(".maps");` | `} ctl_array SEC(".maps");` | and 18 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline_dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline_dynptr.c

Research item: `subset-b-006814` ordinal `54`. Source size: 11417 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline_dynptr.c_research.md`.

## Purpose
The program parses Ethernet/IP/TCP/UDP/ICMP traffic, looks up VIP/backend maps, updates per-CPU stats, and rewrites or redirects packets in TC/XDP style paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_kfuncs`, `bpf_map_lookup_elem`, `bpf_dynptr`, `bpf_dynptr_slice`, `bpf_tunnel_key`, `bpf_ntohs`, `bpf_skb_set_tunnel_key`, `bpf_redirect`, `bpf_dynptr_from_skb`, `bpf_dynptr_slice_rdwr`, `bpf_htons`, `bpf_dynptr_write`
- Declared maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`
- Key local types: `struct packet_description`, `struct ctl_value`, `struct vip_meta`, `struct real_definition`, `struct vip_stats`, `struct eth_hdr`, `struct vip`, `struct bpf_dynptr`, `struct ipv6hdr`, `struct icmp6hdr`, `struct iphdr`, `struct icmphdr`, `struct udphdr`, `struct tcphdr`, and 3 more.
- Main functions/subprograms: `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/pkt_cls.h`, `linux/bpf.h`, `linux/in.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/icmp.h`, `linux/icmpv6.h`, `linux/tcp.h`, and 3 more..
Local test dependencies: `test_iptunnel_common.h`, `bpf_kfuncs.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Bounds checks, endian conversion, checksum updates, dynptr handling, and map value layout are the main compatibility risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_l4lb_noinline_dynptr.c` is a test fixture for packet parser and L4 load-balancer selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_kfuncs.h"` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} vip_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} ch_rings SEC(".maps");` | `} reals SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} stats SEC(".maps");` | and 35 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb_noinline_dynptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ldsx_insn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ldsx_insn.c

Research item: `subset-b-006814` ordinal `55`. Source size: 2431 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ldsx_insn.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?raw_tp/sys_enter`, `?fentry/bpf_testmod_test_arg_ptr_to_struct`, `?cgroup/getsockopt`, `?tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_testmod_struct_arg_1`, `bpf_testmod_test_arg_ptr_to_struct`, `bpf_sockopt`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_testmod_struct_arg_1`, `struct bpf_sockopt`, `struct __sk_buff`
- Main functions/subprograms: `rdonly_map_prog`, `map_val_prog`, `BPF_PROG2`, `_getsockopt`, `_tc`

## Control Flow
Entry programs are attached through `?raw_tp/sys_enter`, `?fentry/bpf_testmod_test_arg_ptr_to_struct`, `?cgroup/getsockopt`, `?tc`. Control is organized around `rdonly_map_prog`, `map_val_prog`, `BPF_PROG2`, `_getsockopt`, `_tc`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `val2`, `val4`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ldsx_insn.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior, feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("?raw_tp/sys_enter")` | `struct bpf_testmod_struct_arg_1 {` | `SEC("?fentry/bpf_testmod_test_arg_ptr_to_struct")` | `int BPF_PROG2(test_ptr_struct_arg, struct bpf_testmod_struct_arg_1 *, p)` | `SEC("?cgroup/getsockopt")` | `int _getsockopt(volatile struct bpf_sockopt *ctx)` | `SEC("?tc")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ldsx_insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_legacy_printk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_legacy_printk.c

Research item: `subset-b-006814` ordinal `56`. Source size: 1623 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_legacy_printk.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/raw_syscalls/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_get_current_pid_tgid`, `bpf_printk`
- Declared maps: `my_pid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `res_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handle_legacy`, `handle_modern`

## Control Flow
Entry programs are attached through `tp/raw_syscalls/sys_enter`. Control is organized around `handle_legacy`, `handle_modern`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `my_pid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `res_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `LICENSE`, `my_pid_var`, `res_var`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_legacy_printk.c` is a test fixture for BPF map operation selftest. Test signals are: trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char LICENSE[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} my_pid_map SEC(".maps");` | `} res_map SEC(".maps");` | `SEC("tp/raw_syscalls/sys_enter")` | `my_pid = bpf_map_lookup_elem(&my_pid_map, &zero);` | `cur_pid = bpf_get_current_pid_tgid() >> 32;` | `my_res = bpf_map_lookup_elem(&res_map, &zero);` | `/* use bpf_printk() in combination with BPF_NO_GLOBAL_DATA to` | and 3 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_legacy_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_libbpf_get_fd_by_id_opts.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_libbpf_get_fd_by_id_opts.c

Research item: `subset-b-006814` ordinal `57`. Source size: 706 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_libbpf_get_fd_by_id_opts.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm/bpf_map`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_map`
- Declared maps: `data_input: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u32`
- Key local types: `struct bpf_map`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm/bpf_map`. Control is organized around `BPF_PROG`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `data_input: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u32`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_libbpf_get_fd_by_id_opts.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} data_input SEC(".maps");` | `char _license[] SEC("license") = "GPL";` | `SEC("lsm/bpf_map")` | `int BPF_PROG(check_access, struct bpf_map *map, fmode_t fmode)` | `if (map != (struct bpf_map *)&data_input)`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_libbpf_get_fd_by_id_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_link_pinning.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_link_pinning.c

Research item: `subset-b-006814` ordinal `58`. Source size: 379 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_link_pinning.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`, `tp_btf/sys_enter`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `raw_tp_prog`, `tp_btf_prog`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`, `tp_btf/sys_enter`. Control is organized around `raw_tp_prog`, `tp_btf_prog`.

## State And Persistence Behavior
Global data/control fields include `in`, `out`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stdbool.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_link_pinning.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("raw_tp/sys_enter")` | `SEC("tp_btf/sys_enter")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_link_pinning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lirc_mode2_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lirc_mode2_kern.c

Research item: `subset-b-006814` ordinal `59`. Source size: 567 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lirc_mode2_kern.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lirc_mode2`
- BPF helpers/macros used: `bpf_helpers`, `bpf_decoder`, `bpf_rc_keydown`, `bpf_rc_pointer_rel`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `bpf_decoder`

## Control Flow
Entry programs are attached through `lirc_mode2`. Control is organized around `bpf_decoder`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `linux/lirc.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lirc_mode2_kern.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("lirc_mode2")` | `int bpf_decoder(unsigned int *sample)` | `bpf_rc_keydown(sample, 0x40, duration & 0xffff, 0);` | `bpf_rc_pointer_rel(sample, (duration >> 8) & 0xff,` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lirc_mode2_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_buf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_buf.c

Research item: `subset-b-006814` ordinal `60`. Source size: 407 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_buf.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `good_prog`, `bad_prog`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `good_prog`, `bad_prog`.

## State And Persistence Behavior
Global data/control fields include `a`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_log_buf.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("raw_tp/sys_enter")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_fixup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_fixup.c

Research item: `subset-b-006814` ordinal `61`. Source size: 1492 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_fixup.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_core_read`, `bpf_core_field_size`, `bpf_map_lookup_elem`, `bpf_nonexistent_kfunc`
- Declared maps: `existing_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `missing_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: `struct task_struct___bad`
- Main functions/subprograms: `bad_relo`, `bad_subprog`, `bad_relo_subprog`, `use_missing_map`, `bpf_nonexistent_kfunc`, `use_missing_kfunc`

## Control Flow
Entry programs are attached through `?raw_tp/sys_enter`. Control is organized around `bad_relo`, `bad_subprog`, `bad_relo_subprog`, `use_missing_map`, `bpf_nonexistent_kfunc`, `use_missing_kfunc`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `existing_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `missing_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_log_fixup.c` is a test fixture for BPF map operation selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_core_read.h>` | `SEC("?raw_tp/sys_enter")` | `return bpf_core_field_size(t->fake_field);` | `return bad_subprog() + bpf_core_field_size(t->pid);` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} existing_map SEC(".maps");` | `} missing_map SEC(".maps");` | `value = bpf_map_lookup_elem(&existing_map, &zero);` | `value = bpf_map_lookup_elem(&missing_map, &zero);` | and 3 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_log_fixup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_and_delete.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_and_delete.c

Research item: `subset-b-006814` ordinal `62`. Source size: 547 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_and_delete.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getpgid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_lookup_and_delete_test`, `bpf_get_current_pid_tgid`, `bpf_map_update_elem`
- Declared maps: `hash_map: BPF_MAP_TYPE_HASH, max 2, key __u64, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `bpf_lookup_and_delete_test`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getpgid`. Control is organized around `bpf_lookup_and_delete_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `hash_map: BPF_MAP_TYPE_HASH, max 2, key __u64, value __u64`. Global data/control fields include `set_pid`, `set_key`, `set_value`, `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lookup_and_delete.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} hash_map SEC(".maps");` | `SEC("tp/syscalls/sys_enter_getpgid")` | `int bpf_lookup_and_delete_test(const void *ctx)` | `if (set_pid == bpf_get_current_pid_tgid() >> 32)` | `bpf_map_update_elem(&hash_map, &set_key, &set_value, BPF_NOEXIST);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_and_delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_key.c

Research item: `subset-b-006814` ordinal `63`. Source size: 956 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_key.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/bpf`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_key`, `bpf_lookup_user_key`, `bpf_lookup_system_key`, `bpf_key_put`, `bpf_attr`, `bpf_get_current_pid_tgid`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_key`
- Main functions/subprograms: `bpf_key_put`, `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/bpf`. Control is organized around `bpf_key_put`, `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `monitored_pid`, `key_serial`, `key_id`, `flags`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lookup_key.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `char _license[] SEC("license") = "GPL";` | `extern struct bpf_key *bpf_lookup_user_key(__s32 serial, __u64 flags) __ksym;` | `extern struct bpf_key *bpf_lookup_system_key(__u64 id) __ksym;` | `extern void bpf_key_put(struct bpf_key *key) __ksym;` | `SEC("lsm.s/bpf")` | `int BPF_PROG(bpf, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)` | `struct bpf_key *bkey;` | `pid = bpf_get_current_pid_tgid() >> 32;` | and 3 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_ip_encap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_ip_encap.c

Research item: `subset-b-006814` ordinal `64`. Source size: 1984 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_ip_encap.c_research.md`.

## Purpose
The file attaches LWT or seg6local programs that inspect skb metadata, adjust tunnel headers, redirect traffic, or validate reroute behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `encap_gre`, `encap_gre6`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_lwt_encap_gre`, `bpf_htons`, `bpf_lwt_push_encap`, `bpf_lwt_encap_gre6`
- Declared maps: None visible in this compact source.
- Key local types: `struct grehdr`, `struct __sk_buff`, `struct encap_hdr`, `struct iphdr`, `struct ipv6hdr`
- Main functions/subprograms: `bpf_lwt_encap_gre`, `bpf_lwt_encap_gre6`

## Control Flow
Entry programs are attached through `encap_gre`, `encap_gre6`. Control is organized around `bpf_lwt_encap_gre`, `bpf_lwt_encap_gre6`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/ip.h`, `linux/ipv6.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Network namespace setup, helper availability, skb headroom/tailroom checks, and route action return codes drive test stability.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lwt_ip_encap.c` is a test fixture for lightweight tunnel and SRv6 BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `SEC("encap_gre")` | `int bpf_lwt_encap_gre(struct __sk_buff *skb)` | `hdr.iph.tot_len = bpf_htons(skb->len + sizeof(struct encap_hdr));` | `err = bpf_lwt_push_encap(skb, BPF_LWT_ENCAP_IP, &hdr,` | `SEC("encap_gre6")` | `int bpf_lwt_encap_gre6(struct __sk_buff *skb)` | `hdr.ip6hdr.payload_len = bpf_htons(skb->len + sizeof(struct grehdr));` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_ip_encap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_redirect.c

Research item: `subset-b-006814` ordinal `65`. Source size: 1909 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_redirect.c_research.md`.

## Purpose
The file attaches LWT or seg6local programs that inspect skb metadata, adjust tunnel headers, redirect traffic, or validate reroute behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `redir_ingress`, `redir_egress`, `redir_egress_nomac`, `redir_ingress_nomac`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_skb_change_head`, `bpf_skb_store_bytes`, `bpf_ntohl`, `bpf_redirect`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`, `struct iphdr`
- Main functions/subprograms: `prepend_dummy_mac`, `get_redirect_target`, `test_lwt_redirect_in`, `test_lwt_redirect_out`, `test_lwt_redirect_out_nomac`, `test_lwt_redirect_in_nomac`

## Control Flow
Entry programs are attached through `redir_ingress`, `redir_egress`, `redir_egress_nomac`, `redir_ingress_nomac`. Control is organized around `prepend_dummy_mac`, `get_redirect_target`, `test_lwt_redirect_in`, `test_lwt_redirect_out`, `test_lwt_redirect_out_nomac`, `test_lwt_redirect_in_nomac`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`, `linux/ip.h`, `linux/if_ether.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Network namespace setup, helper availability, skb headroom/tailroom checks, and route action return codes drive test stability.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lwt_redirect.c` is a test fixture for lightweight tunnel and SRv6 BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `if (bpf_skb_change_head(skb, ETH_HLEN, 0))` | `if (bpf_skb_store_bytes(skb, 0, mac, sizeof(mac), 0))` | `return bpf_ntohl(iph->daddr) & 0xff;` | `SEC("redir_ingress")` | `return bpf_redirect(target, BPF_F_INGRESS);` | `SEC("redir_egress")` | `return bpf_redirect(target, 0);` | `SEC("redir_egress_nomac")` | and 2 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_reroute.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_reroute.c

Research item: `subset-b-006814` ordinal `66`. Source size: 795 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_reroute.c_research.md`.

## Purpose
The file attaches LWT or seg6local programs that inspect skb metadata, adjust tunnel headers, redirect traffic, or validate reroute behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lwt_xmit`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_ntohl`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`, `struct iphdr`
- Main functions/subprograms: `test_lwt_reroute`

## Control Flow
Entry programs are attached through `lwt_xmit`. Control is organized around `test_lwt_reroute`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `inttypes.h`, `linux/bpf.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`, `linux/if_ether.h`, `linux/ip.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Network namespace setup, helper availability, skb headroom/tailroom checks, and route action return codes drive test stability.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lwt_reroute.c` is a test fixture for lightweight tunnel and SRv6 BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `SEC("lwt_xmit")` | `skb->mark = bpf_ntohl(iph->daddr) & 0xff;` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_reroute.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_seg6local.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_seg6local.c

Research item: `subset-b-006814` ordinal `67`. Source size: 9964 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_seg6local.c_research.md`.

## Purpose
The file attaches LWT or seg6local programs that inspect skb metadata, adjust tunnel headers, redirect traffic, or validate reroute behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `encap_srh`, `add_egr_x`, `pop_egr`, `inspect_t`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_compiler`, `bpf_lwt_seg6_adjust_srh`, `bpf_lwt_seg6_store_bytes`, `bpf_skb_load_bytes`, `bpf_be64_to_cpu`, `bpf_cpu_to_be64`, `bpf_lwt_push_encap`, `bpf_lwt_seg6_action`, `bpf_htons`
- Declared maps: None visible in this compact source.
- Key local types: `struct ip6_t`, `struct ip6_addr_t`, `struct ip6_srh_t`, `struct sr6_tlv_t`, `struct __sk_buff`
- Main functions/subprograms: `update_tlv_pad`, `is_valid_tlv_boundary`, `add_tlv`, `delete_tlv`, `has_egr_tlv`, `__encap_srh`, `__add_egr_x`, `__pop_egr`, `__inspect_t`

## Control Flow
Entry programs are attached through `encap_srh`, `add_egr_x`, `pop_egr`, `inspect_t`. Control is organized around `update_tlv_pad`, `is_valid_tlv_boundary`, `add_tlv`, `delete_tlv`, `has_egr_tlv`, `__encap_srh`, `__add_egr_x`, `__pop_egr`, `__inspect_t`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `__license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `inttypes.h`, `errno.h`, `linux/seg6_local.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `bpf_compiler.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Network namespace setup, helper availability, skb headroom/tailroom checks, and route action return codes drive test stability.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lwt_seg6local.c` is a test fixture for lightweight tunnel and SRv6 BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_compiler.h"` | `err = bpf_lwt_seg6_adjust_srh(skb, pad_off,` | `err = bpf_lwt_seg6_store_bytes(skb, pad_off,` | `err = bpf_skb_load_bytes(skb, cur_off, &tlv, sizeof(tlv));` | `err = bpf_lwt_seg6_adjust_srh(skb, tlv_off, sizeof(*itlv) + itlv->len);` | `err = bpf_lwt_seg6_store_bytes(skb, tlv_off, (void *)itlv, tlv_size);` | `err = bpf_skb_load_bytes(skb, tlv_off, &tlv, sizeof(tlv));` | `err = bpf_lwt_seg6_adjust_srh(skb, tlv_off, -(sizeof(tlv) + tlv.len));` | and 21 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lwt_seg6local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map.c

Research item: `subset-b-006814` ordinal `68`. Source size: 1679 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Declared maps: `mim_array: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1, key __u32, value __u32`, `mim_hash: BPF_MAP_TYPE_HASH_OF_MAPS, max 1, key int, value __u32`, `mim_array_pe: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1`, `mim_hash_pe: BPF_MAP_TYPE_HASH_OF_MAPS, max 1`
- Key local types: `struct perf_event_array`, `struct xdp_md`
- Main functions/subprograms: `xdp_mimtest0`

## Control Flow
Entry programs are attached through `xdp`. Control is organized around `xdp_mimtest0`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `mim_array: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1, key __u32, value __u32`, `mim_hash: BPF_MAP_TYPE_HASH_OF_MAPS, max 1, key int, value __u32`, `mim_array_pe: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1`, `mim_hash_pe: BPF_MAP_TYPE_HASH_OF_MAPS, max 1`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `linux/types.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_in_map.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY_OF_MAPS);` | `} mim_array SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_HASH_OF_MAPS);` | `} mim_hash SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} inner_map0 SEC(".maps");` | `} mim_array_pe SEC(".maps") = {` | `} mim_hash_pe SEC(".maps") = {` | `SEC("xdp")` | and 7 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map_invalid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map_invalid.c

Research item: `subset-b-006814` ordinal `69`. Source size: 552 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map_invalid.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: `mim: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 0`
- Key local types: `struct inner`, `struct xdp_md`
- Main functions/subprograms: `xdp_noop0`

## Control Flow
Entry programs are attached through `xdp`. Control is organized around `xdp_noop0`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `mim: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 0`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_in_map_invalid.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `__uint(type, BPF_MAP_TYPE_ARRAY_OF_MAPS);` | `} mim SEC(".maps");` | `SEC("xdp")` | `return XDP_PASS;` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map_invalid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_init.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_init.c

Research item: `subset-b-006814` ordinal `70`. Source size: 752 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_init.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getpgid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_get_current_pid_tgid`, `bpf_map_update_elem`
- Declared maps: `hashmap1: BPF_MAP_TYPE_PERCPU_HASH, max 2, key __u64, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `sysenter_getpgid`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getpgid`. Control is organized around `sysenter_getpgid`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `hashmap1: BPF_MAP_TYPE_PERCPU_HASH, max 2, key __u64, value __u64`. Global data/control fields include `inKey`, `inValue`, `inPid`, `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_init.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_PERCPU_HASH);` | `} hashmap1 SEC(".maps");` | `SEC("tp/syscalls/sys_enter_getpgid")` | `int cur_pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_map_update_elem(&hashmap1, &inKey, &inValue, BPF_NOEXIST);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lock.c

Research item: `subset-b-006814` ordinal `71`. Source size: 1253 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lock.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup/skb`
- BPF helpers/macros used: `bpf_helpers`, `bpf_spin_lock`, `bpf_map_lock_test`, `bpf_get_prandom_u32`, `bpf_map_lookup_elem`, `bpf_spin_unlock`
- Declared maps: `hash_map: BPF_MAP_TYPE_HASH, max 1, key __u32, value struct hmap_elem`, `array_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value struct array_elem`
- Key local types: `struct hmap_elem`, `struct bpf_spin_lock`, `struct array_elem`, `struct __sk_buff`
- Main functions/subprograms: `bpf_map_lock_test`

## Control Flow
Entry programs are attached through `cgroup/skb`. Control is organized around `bpf_map_lock_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `hash_map: BPF_MAP_TYPE_HASH, max 1, key __u32, value struct hmap_elem`, `array_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value struct array_elem`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `linux/version.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_lock.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `struct bpf_spin_lock lock;` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} hash_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} array_map SEC(".maps");` | `SEC("cgroup/skb")` | `int bpf_map_lock_test(struct __sk_buff *skb)` | `int rnd = bpf_get_prandom_u32();` | `val = bpf_map_lookup_elem(&hash_map, &key);` | and 6 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lookup_percpu_elem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lookup_percpu_elem.c

Research item: `subset-b-006814` ordinal `72`. Source size: 1719 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lookup_percpu_elem.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getuid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_percpu_elem`, `bpf_get_current_pid_tgid`, `bpf_loop`
- Declared maps: `percpu_array_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64`, `percpu_hash_map: BPF_MAP_TYPE_PERCPU_HASH, max 1, key __u64, value __u64`, `percpu_lru_hash_map: BPF_MAP_TYPE_LRU_PERCPU_HASH, max 1, key __u64, value __u64`
- Key local types: `struct read_percpu_elem_ctx`
- Main functions/subprograms: `read_percpu_elem_callback`, `sysenter_getuid`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getuid`. Control is organized around `read_percpu_elem_callback`, `sysenter_getuid`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use. The control flow includes helper-mediated dispatch or bounded looping, so the verifier must preserve state across helper boundaries.

## State And Persistence Behavior
Maps: `percpu_array_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64`, `percpu_hash_map: BPF_MAP_TYPE_PERCPU_HASH, max 1, key __u64, value __u64`, `percpu_lru_hash_map: BPF_MAP_TYPE_LRU_PERCPU_HASH, max 1, key __u64, value __u64`. Global data/control fields include `percpu_array_elem_sum`, `percpu_hash_elem_sum`, `percpu_lru_hash_elem_sum`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_lookup_percpu_elem.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} percpu_array_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_HASH);` | `} percpu_hash_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_LRU_PERCPU_HASH);` | `} percpu_lru_hash_map SEC(".maps");` | `value = bpf_map_lookup_percpu_elem(ctx->map, &key, index);` | `SEC("tp/syscalls/sys_enter_getuid")` | `if (my_pid != (bpf_get_current_pid_tgid() >> 32))` | and 2 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lookup_percpu_elem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_ops.c

Research item: `subset-b-006814` ordinal `73`. Source size: 2531 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_ops.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getpid`, `tp/syscalls/sys_enter_getppid`, `tp/syscalls/sys_enter_getuid`, `tp/syscalls/sys_enter_geteuid`, `tp/syscalls/sys_enter_getgid`, `tp/syscalls/sys_enter_gettid`, `tp/syscalls/sys_enter_getpgid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_get_current_pid_tgid`, `bpf_map_update_elem`, `bpf_map_delete_elem`, `bpf_map_push_elem`, `bpf_map_pop_elem`, `bpf_map_peek_elem`, `bpf_for_each_map_elem`
- Declared maps: `hash_map: BPF_MAP_TYPE_HASH, max 1, key int, value int`, `stack_map: BPF_MAP_TYPE_STACK, max 1`, `array_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `callback`, `map_update`, `map_delete`, `map_push`, `map_pop`, `map_peek`, `map_for_each_pass`, `map_for_each_fail`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getpid`, `tp/syscalls/sys_enter_getppid`, `tp/syscalls/sys_enter_getuid`, `tp/syscalls/sys_enter_geteuid`, `tp/syscalls/sys_enter_getgid`, `tp/syscalls/sys_enter_gettid`, `tp/syscalls/sys_enter_getpgid`. Control is organized around `callback`, `map_update`, `map_delete`, `map_push`, `map_pop`, `map_peek`, `map_for_each_pass`, `map_for_each_fail`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `hash_map: BPF_MAP_TYPE_HASH, max 1, key int, value int`, `stack_map: BPF_MAP_TYPE_STACK, max 1`, `array_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `_license`, `err`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_ops.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} hash_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_STACK);` | `} stack_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} array_map SEC(".maps");` | `SEC("tp/syscalls/sys_enter_getpid")` | `if (pid != (bpf_get_current_pid_tgid() >> 32))` | and 13 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_migrate_reuseport.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_migrate_reuseport.c

Research item: `subset-b-006814` ordinal `74`. Source size: 2838 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_migrate_reuseport.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`, `sk_reuseport/migrate`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_ntohs`, `bpf_get_socket_cookie`, `bpf_map_lookup_elem`, `bpf_sk_select_reuseport`
- Declared maps: `reuseport_map: BPF_MAP_TYPE_REUSEPORT_SOCKARRAY, max 256, key int, value __u64`, `migrate_map: BPF_MAP_TYPE_HASH, max 256, key __u64, value int`
- Key local types: `struct xdp_md`, `struct ethhdr`, `struct tcphdr`, `struct iphdr`, `struct ipv6hdr`, `struct sk_reuseport_md`
- Main functions/subprograms: `drop_ack`, `migrate_reuseport`

## Control Flow
Entry programs are attached through `xdp`, `sk_reuseport/migrate`. Control is organized around `drop_ack`, `migrate_reuseport`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `reuseport_map: BPF_MAP_TYPE_REUSEPORT_SOCKARRAY, max 256, key int, value __u64`, `migrate_map: BPF_MAP_TYPE_HASH, max 256, key __u64, value int`. Global data/control fields include `migrated_at_close`, `migrated_at_close_fastopen`, `migrated_at_send_synack`, `migrated_at_recv_ack`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/tcp.h`, `linux/in.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_migrate_reuseport.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `*        return SK_PASS without selecting a listener.` | `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_REUSEPORT_SOCKARRAY);` | `} reuseport_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} migrate_map SEC(".maps");` | `SEC("xdp")` | `switch (bpf_ntohs(eth->h_proto)) {` | `return XDP_DROP;` | and 8 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_migrate_reuseport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_misc_tcp_hdr_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_misc_tcp_hdr_options.c

Research item: `subset-b-006814` ordinal `75`. Source size: 8877 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_misc_tcp_hdr_options.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sockops`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_sock_ops`, `bpf_load_hdr_opt`, `bpf_getsockopt`, `bpf_reserve_hdr_opt`, `bpf_store_hdr_opt`, `bpf_sock_ops_kern`, `bpf_sock_ops_cb_flags_set`, `bpf_sock_ops_cb_flags`, `bpf_setsockopt`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_sock_ops`, `struct tcphdr`, `struct ipv6hdr`, `struct tcp_exprm_opt`, `struct tcp_opt`
- Main functions/subprograms: `__check_active_hdr_in`, `check_active_syn_in`, `check_active_hdr_in`, `active_opt_len`, `write_active_opt`, `handle_hdr_opt_len`, `handle_write_hdr_opt`, `handle_parse_hdr`, `handle_passive_estab`, `misc_estab`

## Control Flow
Entry programs are attached through `sockops`. Control is organized around `__check_active_hdr_in`, `check_active_syn_in`, `check_active_hdr_in`, `active_opt_len`, `write_active_opt`, `handle_hdr_opt_len`, `handle_write_hdr_opt`, `handle_parse_hdr`, `handle_passive_estab`, `misc_estab`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `last_addr16_n`, `active_lport_n`, `active_lport_h`, `passive_lport_n`, `passive_lport_h`, `nodelay_est_ok`, `nodelay_hdr_len_reject`, `nodelay_write_hdr_reject`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `errno.h`, `stdbool.h`, `sys/types.h`, `sys/socket.h`, `linux/ipv6.h`, `linux/tcp.h`, `linux/socket.h`, `linux/bpf.h`, `linux/types.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `test_tcp_hdr_options.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_misc_tcp_hdr_options.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__u16 last_addr16_n = __bpf_htons(1);` | `static int __check_active_hdr_in(struct bpf_sock_ops *skops, bool check_syn)` | `ret = bpf_load_hdr_opt(skops, &hdr.reg_opt, 2, load_flags);` | `ret = bpf_load_hdr_opt(skops, &hdr.reg_opt, sizeof(hdr.reg_opt),` | `ret = bpf_load_hdr_opt(skops, &hdr.exprm_opt, sizeof(hdr.exprm_opt),` | `hdr.exprm_opt.magic = __bpf_htons(0xeB9F);` | `hdr.exprm_opt.magic != __bpf_htons(0xeB9F))` | `ret = bpf_getsockopt(skops, SOL_TCP, TCP_BPF_SYN_IP, &hdr.ip6,` | and 29 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_misc_tcp_hdr_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_mmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_mmap.c

Research item: `subset-b-006814` ordinal `76`. Source size: 1057 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_mmap.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_update_elem`, `bpf_map_lookup_elem`
- Declared maps: `rdonly_map: BPF_MAP_TYPE_ARRAY, key __u32, value char`, `data_map: BPF_MAP_TYPE_ARRAY, key __u32, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `test_mmap`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `test_mmap`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `rdonly_map: BPF_MAP_TYPE_ARRAY, key __u32, value char`, `data_map: BPF_MAP_TYPE_ARRAY, key __u32, value __u64`. Global data/control fields include `_license`, `in_val`, `out_val`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `stdint.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_mmap.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} rdonly_map SEC(".maps");` | `} data_map SEC(".maps");` | `SEC("raw_tracepoint/sys_enter")` | `bpf_map_update_elem(&data_map, &two, (const void *)&in_val, 0);` | `p = bpf_map_lookup_elem(&data_map, &zero);` | `bpf_map_update_elem(&data_map, &one, &val, 0);` | `bpf_map_update_elem(&data_map, &far, &val, 0);`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_module_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_module_attach.c

Research item: `subset-b-006814` ordinal `77`. Source size: 2999 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_module_attach.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?raw_tp/bpf_testmod_test_read`, `?raw_tp/bpf_testmod_test_write_bare_tp`, `?raw_tp.w/bpf_testmod_test_writable_bare_tp`, `?tp_btf/bpf_testmod_test_read`, `?fentry/bpf_testmod_test_read`, `?fentry`, `?fentry/bpf_testmod:bpf_testmod_test_read`, `?fexit/bpf_testmod_test_read`, `?fexit/bpf_testmod_return_ptr`, `?fmod_ret/bpf_testmod_test_read`, `?kprobe.multi/bpf_testmod_test_read`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_core_read`, `bpf_testmod`, `bpf_testmod_test_read`, `bpf_testmod_test_read_ctx`, `bpf_testmod_test_write_bare_tp`, `bpf_testmod_test_write_ctx`, `bpf_testmod_test_writable_bare_tp`, `bpf_testmod_test_writable_ctx`, `bpf_testmod_return_ptr`, `bpf_probe_read_kernel`
- Declared maps: None visible in this compact source.
- Key local types: `struct task_struct`, `struct bpf_testmod_test_read_ctx`, `struct bpf_testmod_test_write_ctx`, `struct bpf_testmod_test_writable_ctx`, `struct file`, `struct kobject`, `struct bin_attribute`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `?raw_tp/bpf_testmod_test_read`, `?raw_tp/bpf_testmod_test_write_bare_tp`, `?raw_tp.w/bpf_testmod_test_writable_bare_tp`, `?tp_btf/bpf_testmod_test_read`, `?fentry/bpf_testmod_test_read`, `?fentry`, `?fentry/bpf_testmod:bpf_testmod_test_read`, `?fexit/bpf_testmod_test_read`, `?fexit/bpf_testmod_return_ptr`, `?fmod_ret/bpf_testmod_test_read`, and 1 more.. Control is organized around `BPF_PROG`.

## State And Persistence Behavior
Global data/control fields include `sz`, `raw_tp_writable_bare_in_val`, `raw_tp_writable_bare_early_ret`, `raw_tp_writable_bare_out_val`, `retval`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`.
Local test dependencies: `vmlinux.h`, `../test_kmods/bpf_testmod.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_module_attach.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include "../test_kmods/bpf_testmod.h"` | `SEC("?raw_tp/bpf_testmod_test_read")` | `struct task_struct *task, struct bpf_testmod_test_read_ctx *read_ctx)` | `SEC("?raw_tp/bpf_testmod_test_write_bare_tp")` | `struct task_struct *task, struct bpf_testmod_test_write_ctx *write_ctx)` | `SEC("?raw_tp.w/bpf_testmod_test_writable_bare_tp")` | `struct bpf_testmod_test_writable_ctx *writable)` | and 11 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_module_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_netfilter_link_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_netfilter_link_attach.c

Research item: `subset-b-006814` ordinal `78`. Source size: 247 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_netfilter_link_attach.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `netfilter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_nf_ctx`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_nf_ctx`
- Main functions/subprograms: `nf_link_attach_test`

## Control Flow
Entry programs are attached through `netfilter`. Control is organized around `nf_link_attach_test`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_netfilter_link_attach.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("netfilter")` | `int nf_link_attach_test(struct bpf_nf_ctx *ctx)` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_netfilter_link_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ns_current_pid_tgid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ns_current_pid_tgid.c

Research item: `subset-b-006814` ordinal `79`. Source size: 936 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ns_current_pid_tgid.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?tracepoint/syscalls/sys_enter_nanosleep`, `?cgroup/bind4`, `?sk_msg`
- BPF helpers/macros used: `bpf_helpers`, `bpf_pidns_info`, `bpf_get_ns_current_pid_tgid`, `bpf_sock_addr`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u32`
- Key local types: `struct bpf_pidns_info`, `struct bpf_sock_addr`, `struct sk_msg_md`
- Main functions/subprograms: `get_pid_tgid`, `tp_handler`, `cgroup_bind4`, `sk_msg`

## Control Flow
Entry programs are attached through `?tracepoint/syscalls/sys_enter_nanosleep`, `?cgroup/bind4`, `?sk_msg`. Control is organized around `get_pid_tgid`, `tp_handler`, `cgroup_bind4`, `sk_msg`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u32`. Global data/control fields include `user_pid`, `user_tgid`, `dev`, `ino`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `stdint.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ns_current_pid_tgid.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `struct bpf_pidns_info nsdata;` | `if (bpf_get_ns_current_pid_tgid(dev, ino, &nsdata, sizeof(struct bpf_pidns_info)))` | `SEC("?tracepoint/syscalls/sys_enter_nanosleep")` | `SEC("?cgroup/bind4")` | `int cgroup_bind4(struct bpf_sock_addr *ctx)` | `SEC("?sk_msg")` | `return SK_PASS;` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ns_current_pid_tgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_obj_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_obj_id.c

Research item: `subset-b-006814` ordinal `80`. Source size: 478 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_obj_id.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_map_lookup_elem`
- Declared maps: `test_map_id: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `test_obj_id`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `test_obj_id`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `test_map_id: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u64`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_obj_id.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} test_map_id SEC(".maps");` | `SEC("raw_tp/sys_enter")` | `value = bpf_map_lookup_elem(&test_map_id, &key);`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_obj_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_overhead.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_overhead.c

Research item: `subset-b-006814` ordinal `81`. Source size: 758 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_overhead.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `kprobe/__set_task_comm`, `kretprobe/__set_task_comm`, `raw_tp/task_rename`, `fentry/__set_task_comm`, `fexit/__set_task_comm`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_raw_tracepoint_args`
- Declared maps: None visible in this compact source.
- Key local types: `struct task_struct`, `struct bpf_raw_tracepoint_args`
- Main functions/subprograms: `BPF_KPROBE`, `BPF_KRETPROBE`, `prog3`, `BPF_PROG`

## Control Flow
Entry programs are attached through `kprobe/__set_task_comm`, `kretprobe/__set_task_comm`, `raw_tp/task_rename`, `fentry/__set_task_comm`, `fexit/__set_task_comm`. Control is organized around `BPF_KPROBE`, `BPF_KRETPROBE`, `prog3`, `BPF_PROG`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_overhead.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("kprobe/__set_task_comm")` | `SEC("kretprobe/__set_task_comm")` | `SEC("raw_tp/task_rename")` | `int prog3(struct bpf_raw_tracepoint_args *ctx)` | `SEC("fentry/__set_task_comm")` | `SEC("fexit/__set_task_comm")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_overhead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt.c

Research item: `subset-b-006814` ordinal `82`. Source size: 2859 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: None visible in this compact source.
- Key local types: `struct hdr_opt_state`, `struct xdp_md`, `struct tcphdr`, `struct ethhdr`, `struct ipv6hdr`
- Main functions/subprograms: `parse_hdr_opt`, `xdp_ingress_v6`

## Control Flow
Entry programs are attached through `xdp`. Control is organized around `parse_hdr_opt`, `xdp_ingress_v6`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `tcp_hdr_opt_kind_tpr`, `tcp_hdr_opt_len_tpr`, `tcp_hdr_opt_max_opt_checks`, `server_id`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `linux/tcp.h`, `stdbool.h`, `linux/ipv6.h`, `linux/if_ether.h`.
Local test dependencies: `test_tcp_hdr_options.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_parse_tcp_hdr_opt.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `SEC("xdp")` | `return XDP_DROP;` | `return XDP_PASS;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt_dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt_dynptr.c

Research item: `subset-b-006814` ordinal `83`. Source size: 2636 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt_dynptr.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`
- BPF helpers/macros used: `bpf_helpers`, `bpf_kfuncs`, `bpf_dynptr`, `bpf_dynptr_slice`, `bpf_dynptr_from_xdp`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_dynptr`, `struct xdp_md`, `struct tcphdr`, `struct ethhdr`, `struct ipv6hdr`
- Main functions/subprograms: `parse_hdr_opt`, `xdp_ingress_v6`

## Control Flow
Entry programs are attached through `xdp`. Control is organized around `parse_hdr_opt`, `xdp_ingress_v6`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `tcp_hdr_opt_kind_tpr`, `tcp_hdr_opt_len_tpr`, `tcp_hdr_opt_max_opt_checks`, `server_id`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `linux/tcp.h`, `stdbool.h`, `linux/ipv6.h`, `linux/if_ether.h`.
Local test dependencies: `test_tcp_hdr_options.h`, `bpf_kfuncs.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_parse_tcp_hdr_opt_dynptr.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_kfuncs.h"` | `char _license[] SEC("license") = "GPL";` | `static int parse_hdr_opt(struct bpf_dynptr *ptr, __u32 *off, __u8 *hdr_bytes_remaining,` | `data = bpf_dynptr_slice(ptr, *off, buffer, sizeof(buffer));` | `SEC("xdp")` | `struct bpf_dynptr ptr;` | `bpf_dynptr_from_xdp(xdp, 0, &ptr);` | `tcp_hdr = bpf_dynptr_slice(&ptr, off, buffer, sizeof(buffer));` | `return XDP_DROP;` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_parse_tcp_hdr_opt_dynptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pe_preserve_elems.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pe_preserve_elems.c

Research item: `subset-b-006814` ordinal `84`. Source size: 841 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pe_preserve_elems.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sched_switch`, `raw_tp/task_rename`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_perf_event_value`, `bpf_perf_event_read_value`
- Declared maps: `array_1: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`, `array_2: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`
- Key local types: `struct bpf_perf_event_value`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `raw_tp/sched_switch`, `raw_tp/task_rename`. Control is organized around `BPF_PROG`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `array_1: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`, `array_2: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`. Global data/control fields include `LICENSE`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pe_preserve_elems.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} array_1 SEC(".maps");` | `} array_2 SEC(".maps");` | `SEC("raw_tp/sched_switch")` | `struct bpf_perf_event_value val;` | `return bpf_perf_event_read_value(&array_1, 0, &val, sizeof(val));` | `SEC("raw_tp/task_rename")` | `return bpf_perf_event_read_value(&array_2, 0, &val, sizeof(val));` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pe_preserve_elems.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_branches.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_branches.c

Research item: `subset-b-006814` ordinal `85`. Source size: 1109 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_branches.c_research.md`.

## Purpose
The code attaches to perf or trace events and reports counters/samples through perf buffer or link infrastructure. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_read_branch_records`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `perf_branches`

## Control Flow
Entry programs are attached through `perf_event`. Control is organized around `perf_branches`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `valid`, `run_cnt`, `required_size_out`, `written_stack_out`, `written_global_out`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/ptrace.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Test results depend on perf event availability, CPU context, stack/sample flags, and link detach semantics.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_perf_branches.c` is a test fixture for perf-event BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("perf_event")` | `written_stack = bpf_read_branch_records(ctx, entries, sizeof(entries), 0);` | `required_size = bpf_read_branch_records(ctx, NULL, 0,` | `written_global = bpf_read_branch_records(ctx, fpbe, sizeof(fpbe), 0);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_branches.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_buffer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_buffer.c

Research item: `subset-b-006814` ordinal `86`. Source size: 884 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_buffer.c_research.md`.

## Purpose
The code attaches to perf or trace events and reports counters/samples through perf buffer or link infrastructure. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/raw_syscalls/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_smp_processor_id`, `bpf_map_lookup_elem`, `bpf_get_current_pid_tgid`, `bpf_perf_event_output`
- Declared maps: `my_pid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `perf_buf_map: BPF_MAP_TYPE_PERF_EVENT_ARRAY, key int, value int`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handle_sys_enter`

## Control Flow
Entry programs are attached through `tp/raw_syscalls/sys_enter`. Control is organized around `handle_sys_enter`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `my_pid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `perf_buf_map: BPF_MAP_TYPE_PERF_EVENT_ARRAY, key int, value int`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/ptrace.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Test results depend on perf event availability, CPU context, stack/sample flags, and link detach semantics.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_perf_buffer.c` is a test fixture for perf-event BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} my_pid_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} perf_buf_map SEC(".maps");` | `SEC("tp/raw_syscalls/sys_enter")` | `int cpu = bpf_get_smp_processor_id();` | `my_pid = bpf_map_lookup_elem(&my_pid_map, &zero);` | `cur_pid = bpf_get_current_pid_tgid() >> 32;` | and 2 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_link.c

Research item: `subset-b-006814` ordinal `87`. Source size: 311 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_link.c_research.md`.

## Purpose
The code attaches to perf or trace events and reports counters/samples through perf buffer or link infrastructure. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`
- Declared maps: None visible in this compact source.
- Key local types: `struct pt_regs`
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `perf_event`. Control is organized around `handler`.

## State And Persistence Behavior
Global data/control fields include `run_cnt`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Test results depend on perf event availability, CPU context, stack/sample flags, and link detach semantics.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_perf_link.c` is a test fixture for perf-event BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("perf_event")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_skip.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_skip.c

Research item: `subset-b-006814` ordinal `88`. Source size: 324 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_skip.c_research.md`.

## Purpose
The code attaches to perf or trace events and reports counters/samples through perf buffer or link infrastructure. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_perf_event_data`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_perf_event_data`
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `perf_event`. Control is organized around `handler`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Test results depend on perf event availability, CPU context, stack/sample flags, and link detach semantics.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_perf_skip.c` is a test fixture for perf-event BPF selftest. Test signals are: feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("perf_event")` | `int handler(struct bpf_perf_event_data *data)` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_skip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning.c

Research item: `subset-b-006814` ordinal `89`. Source size: 617 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: `pinmap: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u64`, `nopinmap: BPF_MAP_TYPE_HASH, max 1, key __u32, value __u64`, `nopinmap2: BPF_MAP_TYPE_HASH, max 1, key __u32, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `pinmap: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u64`, `nopinmap: BPF_MAP_TYPE_HASH, max 1, key __u32, value __u64`, `nopinmap2: BPF_MAP_TYPE_HASH, max 1, key __u32, value __u64`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pinning.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} pinmap SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} nopinmap SEC(".maps");` | `} nopinmap2 SEC(".maps");` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_devmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_devmap.c

Research item: `subset-b-006814` ordinal `90`. Source size: 443 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_devmap.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: `pinmap1: BPF_MAP_TYPE_DEVMAP, max 1, key __u32, value __u32`, `pinmap2: BPF_MAP_TYPE_DEVMAP, max 2, key __u32, value __u32`
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `pinmap1: BPF_MAP_TYPE_DEVMAP, max 1, key __u32, value __u32`, `pinmap2: BPF_MAP_TYPE_DEVMAP, max 2, key __u32, value __u32`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pinning_devmap.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_DEVMAP);` | `} pinmap1 SEC(".maps");` | `} pinmap2 SEC(".maps");`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_devmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_htab.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_htab.c

Research item: `subset-b-006814` ordinal `91`. Source size: 528 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_htab.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`, `bpf_timer`
- Declared maps: `timer_prealloc: BPF_MAP_TYPE_HASH, max 1, key __u32, value struct timer_val`, `timer_no_prealloc: BPF_MAP_TYPE_HASH, max 1, key __u32, value struct timer_val`
- Key local types: `struct timer_val`, `struct bpf_timer`
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `timer_prealloc: BPF_MAP_TYPE_HASH, max 1, key __u32, value struct timer_val`, `timer_no_prealloc: BPF_MAP_TYPE_HASH, max 1, key __u32, value struct timer_val`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pinning_htab.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `struct bpf_timer timer;` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} timer_prealloc SEC(".maps");` | `} timer_no_prealloc SEC(".maps");`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_htab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_invalid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_invalid.c

Research item: `subset-b-006814` ordinal `92`. Source size: 305 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_invalid.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: `nopinmap3: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `nopinmap3: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u64`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pinning_invalid.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} nopinmap3 SEC(".maps");` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pinning_invalid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_access.c

Research item: `subset-b-006814` ordinal `93`. Source size: 3791 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_access.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_misc`, `bpf_htons`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`, `struct tcphdr`, `struct ethhdr`, `struct ipv6hdr`, `struct iphdr`
- Main functions/subprograms: `test_pkt_access_subprog1`, `test_pkt_access_subprog2`, `get_skb_len`, `get_constant`, `get_skb_ifindex`, `test_pkt_access_subprog3`, `test_pkt_write_access_subprog`, `test_pkt_access`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `test_pkt_access_subprog1`, `test_pkt_access_subprog2`, `get_skb_len`, `get_constant`, `get_skb_ifindex`, `test_pkt_access_subprog3`, `test_pkt_write_access_subprog`, `test_pkt_access`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/if_packet.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/in.h`, `linux/tcp.h`, `linux/pkt_cls.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pkt_access.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `return TC_ACT_SHOT;` | `if (eth->h_proto == bpf_htons(ETH_P_IP)) {` | `} else if (eth->h_proto == bpf_htons(ETH_P_IPV6)) {` | `return TC_ACT_OK;` | `return TC_ACT_UNSPEC;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_md_access.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_md_access.c

Research item: `subset-b-006814` ordinal `94`. Source size: 1127 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_md_access.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `test_pkt_md_access`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `test_pkt_md_access`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/pkt_cls.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pkt_md_access.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `return TC_ACT_SHOT;				\` | `SEC("tc")` | `return TC_ACT_OK;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_md_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_read_user_str.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_read_user_str.c

Research item: `subset-b-006814` ordinal `95`. Source size: 462 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_read_user_str.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tracepoint/syscalls/sys_enter_nanosleep`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_current_pid_tgid`, `bpf_probe_read_user_str`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `on_write`

## Control Flow
Entry programs are attached through `tracepoint/syscalls/sys_enter_nanosleep`. Control is organized around `on_write`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `ret`, `buf`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `sys/types.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_probe_read_user_str.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("tracepoint/syscalls/sys_enter_nanosleep")` | `if (pid != (bpf_get_current_pid_tgid() >> 32))` | `ret = bpf_probe_read_user_str(buf, sizeof(buf), user_ptr);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_read_user_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_user.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_user.c

Research item: `subset-b-006814` ordinal `96`. Source size: 1217 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_user.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `ksyscall/connect`, `ksyscall/socketcall`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_core_read`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_probe_read_user`, `bpf_probe_write_user`, `bpf_target_s390`
- Declared maps: None visible in this compact source.
- Key local types: `struct test_pro_bss`, `struct sockaddr_in`
- Main functions/subprograms: `handle_sys_connect_common`, `BPF_KSYSCALL`

## Control Flow
Entry programs are attached through `ksyscall/connect`, `ksyscall/socketcall`. Control is organized around `handle_sys_connect_common`, `BPF_KSYSCALL`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `bss`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`.
Local test dependencies: `vmlinux.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_probe_user.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include "bpf_misc.h"` | `__u32 cur = bpf_get_current_pid_tgid() >> 32;` | `bpf_probe_read_user(&bss.old, sizeof(bss.old), uservaddr);` | `bpf_probe_write_user(uservaddr, &new, sizeof(new));` | `SEC("ksyscall/connect")` | `#if defined(bpf_target_s390)` | `SEC("ksyscall/socketcall")` | and 2 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_probe_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_prog_array_init.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_prog_array_init.c

Research item: `subset-b-006814` ordinal `97`. Source size: 693 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_prog_array_init.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_current_pid_tgid`, `bpf_tail_call`
- Declared maps: `prog_array_init: BPF_MAP_TYPE_PROG_ARRAY, max 2`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `tailcall_1`, `entry`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `tailcall_1`, `entry`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use. The control flow includes helper-mediated dispatch or bounded looping, so the verifier must preserve state across helper boundaries.

## State And Persistence Behavior
Maps: `prog_array_init: BPF_MAP_TYPE_PROG_ARRAY, max 2`. Global data/control fields include `value`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_prog_array_init.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("raw_tp/sys_enter")` | `__uint(type, BPF_MAP_TYPE_PROG_ARRAY);` | `} prog_array_init SEC(".maps") = {` | `pid_t pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_tail_call(ctx, &prog_array_init, 1);`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_prog_array_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ptr_untrusted.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ptr_untrusted.c

Research item: `subset-b-006814` ordinal `98`. Source size: 561 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ptr_untrusted.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/bpf`, `raw_tracepoint`
- BPF helpers/macros used: `bpf_tracing`, `bpf_attr`, `bpf_copy_from_user`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/bpf`, `raw_tracepoint`. Control is organized around `BPF_PROG`.

## State And Persistence Behavior
Global data/control fields include `tp_name`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ptr_untrusted.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `SEC("lsm.s/bpf")` | `int BPF_PROG(lsm_run, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)` | `bpf_copy_from_user(tp_name, sizeof(tp_name) - 1,` | `SEC("raw_tracepoint")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ptr_untrusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_map.c

Research item: `subset-b-006814` ordinal `99`. Source size: 150 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_map.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: None visible in this compact source.
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers None visible in this compact source..
Local test dependencies: `test_queue_stack_map.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_queue_map.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#define MAP_TYPE BPF_MAP_TYPE_QUEUE`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_stack_map.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_stack_map.h

Research item: `subset-b-006814` ordinal `100`. Source size: 1176 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_stack_map.h_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_pop_elem`, `bpf_map_push_elem`
- Declared maps: `map_in: MAP_TYPE, max 32`, `map_out: MAP_TYPE, max 32`
- Key local types: `struct __sk_buff`, `struct ethhdr`, `struct iphdr`
- Main functions/subprograms: `_test`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `map_in: MAP_TYPE, max 32`, `map_out: MAP_TYPE, max 32`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/pkt_cls.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_queue_stack_map.h` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `} map_in SEC(".maps");` | `} map_out SEC(".maps");` | `SEC("tc")` | `return TC_ACT_SHOT;` | `err = bpf_map_pop_elem(&map_in, &value);` | `err = bpf_map_push_elem(&map_out, &iph->saddr, 0);` | `return TC_ACT_OK;` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_queue_stack_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_raw_tp_test_run.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_raw_tp_test_run.c

Research item: `subset-b-006814` ordinal `101`. Source size: 488 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_raw_tp_test_run.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/task_rename`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_smp_processor_id`
- Declared maps: None visible in this compact source.
- Key local types: `struct task_struct`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `raw_tp/task_rename`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `count`, `on_cpu`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_raw_tp_test_run.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("raw_tp/task_rename")` | `on_cpu = bpf_get_smp_processor_id();` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_raw_tp_test_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_rdonly_maps.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_rdonly_maps.c

Research item: `subset-b-006814` ordinal `102`. Source size: 1757 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_rdonly_maps.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter:skip_loop`, `raw_tracepoint/sys_enter:part_loop`, `raw_tracepoint/sys_enter:full_loop`
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`
- Declared maps: None visible in this compact source.
- Key local types: `struct pt_regs`
- Main functions/subprograms: `skip_loop`, `part_loop`, `full_loop`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter:skip_loop`, `raw_tracepoint/sys_enter:part_loop`, `raw_tracepoint/sys_enter:full_loop`. Control is organized around `skip_loop`, `part_loop`, `full_loop`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/ptrace.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_rdonly_maps.c` is a test fixture for BPF map operation selftest. Test signals are: feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `SEC("raw_tracepoint/sys_enter:skip_loop")` | `SEC("raw_tracepoint/sys_enter:part_loop")` | `SEC("raw_tracepoint/sys_enter:full_loop")` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_rdonly_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf.c

Research item: `subset-b-006814` ordinal `103`. Source size: 1596 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf.c_research.md`.

## Purpose
The program reserves, writes, submits, discards, or queries ring-buffer records to validate event delivery and verifier rules. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_ringbuf_reserve`, `bpf_get_current_comm`, `bpf_ringbuf_output`, `bpf_ringbuf_discard`, `bpf_ringbuf_submit`, `bpf_ringbuf_query`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`
- Key local types: `struct sample`
- Main functions/subprograms: `test_ringbuf`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `test_ringbuf`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`. Global data/control fields include `_license`, `pid`, `value`, `flags`, `total`, `discarded`, `dropped`, `avail_data`, `ring_size`, `cons_pos`, and 2 more.. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Record lifetime, alignment, busy/discard paths, and map key restrictions are the important failure modes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ringbuf.c` is a test fixture for ring buffer map/helper selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | `SEC("fentry/" SYS_PREFIX "sys_getpgid")` | `int cur_pid = bpf_get_current_pid_tgid() >> 32;` | `sample = bpf_ringbuf_reserve(&ringbuf, sizeof(*sample), 0);` | `bpf_get_current_comm(sample->comm, sizeof(sample->comm));` | `bpf_ringbuf_output(&ringbuf, sample, sizeof(*sample), flags);` | and 6 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_map_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_map_key.c

Research item: `subset-b-006814` ordinal `104`. Source size: 1670 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_map_key.c_research.md`.

## Purpose
The program reserves, writes, submits, discards, or queries ring-buffer records to validate event delivery and verifier rules. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_ringbuf_reserve`, `bpf_get_current_comm`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_ringbuf_submit`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`, `hash_map: BPF_MAP_TYPE_HASH, max 1000, key struct sample, value int`
- Key local types: `struct sample`
- Main functions/subprograms: `test_ringbuf_mem_map_key`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `test_ringbuf_mem_map_key`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`, `hash_map: BPF_MAP_TYPE_HASH, max 1000, key struct sample, value int`. Global data/control fields include `_license`, `pid`, `seq`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Record lifetime, alignment, busy/discard paths, and map key restrictions are the important failure modes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ringbuf_map_key.c` is a test fixture for ring buffer map/helper selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} hash_map SEC(".maps");` | `SEC("fentry/" SYS_PREFIX "sys_getpgid")` | `int cur_pid = bpf_get_current_pid_tgid() >> 32;` | `sample = bpf_ringbuf_reserve(&ringbuf, sizeof(*sample), 0);` | and 6 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_map_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_multi.c

Research item: `subset-b-006814` ordinal `105`. Source size: 1547 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_multi.c_research.md`.

## Purpose
The program reserves, writes, submits, discards, or queries ring-buffer records to validate event delivery and verifier rules. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getpgid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_get_current_pid_tgid`, `bpf_map_lookup_elem`, `bpf_ringbuf_reserve`, `bpf_get_current_comm`, `bpf_ringbuf_submit`
- Declared maps: `ringbuf_arr: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 4`, `ringbuf_hash: BPF_MAP_TYPE_HASH_OF_MAPS, max 1`
- Key local types: `struct sample`, `struct ringbuf_map`
- Main functions/subprograms: `test_ringbuf`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getpgid`. Control is organized around `test_ringbuf`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf_arr: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 4`, `ringbuf_hash: BPF_MAP_TYPE_HASH_OF_MAPS, max 1`. Global data/control fields include `_license`, `pid`, `target_ring`, `value`, `total`, `dropped`, `skipped`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Record lifetime, alignment, busy/discard paths, and map key restrictions are the important failure modes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ringbuf_multi.c` is a test fixture for ring buffer map/helper selftest. Test signals are: feature/clang availability can mark the selftest skipped.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf1 SEC(".maps"),` | `ringbuf2 SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY_OF_MAPS);` | `} ringbuf_arr SEC(".maps") = {` | `__uint(type, BPF_MAP_TYPE_HASH_OF_MAPS);` | `} ringbuf_hash SEC(".maps") = {` | `SEC("tp/syscalls/sys_enter_getpgid")` | and 5 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_n.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_n.c

Research item: `subset-b-006814` ordinal `106`. Source size: 860 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_n.c_research.md`.

## Purpose
The program reserves, writes, submits, discards, or queries ring-buffer records to validate event delivery and verifier rules. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_ringbuf_reserve`, `bpf_get_current_comm`, `bpf_ringbuf_submit`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`
- Key local types: `struct sample`
- Main functions/subprograms: `test_ringbuf_n`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `test_ringbuf_n`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`. Global data/control fields include `_license`, `pid`, `value`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `sched.h`, `unistd.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Record lifetime, alignment, busy/discard paths, and map key restrictions are the important failure modes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ringbuf_n.c` is a test fixture for ring buffer map/helper selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `#define TASK_COMM_LEN 16` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | `SEC("fentry/" SYS_PREFIX "sys_getpgid")` | `int cur_pid = bpf_get_current_pid_tgid() >> 32;` | `sample = bpf_ringbuf_reserve(&ringbuf, sizeof(*sample), 0);` | `bpf_get_current_comm(sample->comm, sizeof(sample->comm));` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_n.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_overwrite.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_overwrite.c

Research item: `subset-b-006814` ordinal `107`. Source size: 2182 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_overwrite.c_research.md`.

## Purpose
The program reserves, writes, submits, discards, or queries ring-buffer records to validate event delivery and verifier rules. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_ringbuf_reserve`, `bpf_ringbuf_discard`, `bpf_ringbuf_submit`, `bpf_ringbuf_query`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `test_overwrite_ringbuf`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `test_overwrite_ringbuf`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`. Global data/control fields include `_license`, `pid`, `reserve1_fail`, `reserve2_fail`, `reserve3_fail`, `reserve4_fail`, `reserve5_fail`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Record lifetime, alignment, busy/discard paths, and map key restrictions are the important failure modes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ringbuf_overwrite.c` is a test fixture for ring buffer map/helper selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | `SEC("fentry/" SYS_PREFIX "sys_getpgid")` | `int cur_pid = bpf_get_current_pid_tgid() >> 32;` | `rec1 = bpf_ringbuf_reserve(&ringbuf, LEN1, 0);` | `rec2 = bpf_ringbuf_reserve(&ringbuf, LEN2, 0);` | `bpf_ringbuf_discard(rec1, 0);` | and 14 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_overwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_write.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_write.c

Research item: `subset-b-006814` ordinal `108`. Source size: 941 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_write.c_research.md`.

## Purpose
The program reserves, writes, submits, discards, or queries ring-buffer records to validate event delivery and verifier rules. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: `bpf_helpers`, `bpf_misc`, `bpf_get_current_pid_tgid`, `bpf_ringbuf_reserve`, `bpf_ringbuf_discard`
- Declared maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `test_ringbuf_write`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `test_ringbuf_write`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `ringbuf: BPF_MAP_TYPE_RINGBUF`. Global data/control fields include `_license`, `pid`, `passed`, `discarded`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Record lifetime, alignment, busy/discard paths, and map key restrictions are the important failure modes.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ringbuf_write.c` is a test fixture for ring buffer map/helper selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `__uint(type, BPF_MAP_TYPE_RINGBUF);` | `} ringbuf SEC(".maps");` | `SEC("fentry/" SYS_PREFIX "sys_getpgid")` | `int *foo, cur_pid = bpf_get_current_pid_tgid() >> 32;` | `sample1 = bpf_ringbuf_reserve(&ringbuf, 0x30000, 0);` | `sample2 = bpf_ringbuf_reserve(&ringbuf, 0x30000, 0);` | `bpf_ringbuf_discard(sample1, 0);` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ringbuf_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_seg6_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_seg6_loop.c

Research item: `subset-b-006814` ordinal `109`. Source size: 6149 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_seg6_loop.c_research.md`.

## Purpose
The file attaches LWT or seg6local programs that inspect skb metadata, adjust tunnel headers, redirect traffic, or validate reroute behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lwt_seg6local`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_compiler`, `bpf_lwt_seg6_adjust_srh`, `bpf_lwt_seg6_store_bytes`, `bpf_skb_load_bytes`, `bpf_cpu_to_be64`, `bpf_lwt_seg6_action`
- Declared maps: None visible in this compact source.
- Key local types: `struct ip6_t`, `struct ip6_addr_t`, `struct ip6_srh_t`, `struct sr6_tlv_t`, `struct __sk_buff`
- Main functions/subprograms: `update_tlv_pad`, `is_valid_tlv_boundary`, `add_tlv`, `__add_egr_x`

## Control Flow
Entry programs are attached through `lwt_seg6local`. Control is organized around `update_tlv_pad`, `is_valid_tlv_boundary`, `add_tlv`, `__add_egr_x`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `__license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `inttypes.h`, `errno.h`, `linux/seg6_local.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `bpf_compiler.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Network namespace setup, helper availability, skb headroom/tailroom checks, and route action return codes drive test stability.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_seg6_loop.c` is a test fixture for lightweight tunnel and SRv6 BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_compiler.h"` | `err = bpf_lwt_seg6_adjust_srh(skb, pad_off,` | `err = bpf_lwt_seg6_store_bytes(skb, pad_off,` | `err = bpf_skb_load_bytes(skb, cur_off, &tlv, sizeof(tlv));` | `err = bpf_lwt_seg6_adjust_srh(skb, tlv_off, sizeof(*itlv) + itlv->len);` | `err = bpf_lwt_seg6_store_bytes(skb, tlv_off, (void *)itlv, tlv_size);` | `SEC("lwt_seg6local")` | `err = bpf_lwt_seg6_store_bytes(skb, offset,` | and 4 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_seg6_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_select_reuseport_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_select_reuseport_kern.c

Research item: `subset-b-006814` ordinal `110`. Source size: 4589 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_select_reuseport_kern.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_reuseport`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_skb_load_bytes_relative`, `bpf_prog`, `bpf_skb_load_bytes`, `bpf_map_lookup_elem`, `bpf_sk_select_reuseport`, `bpf_map_update_elem`
- Declared maps: `outer_map: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1, key __u32, value __u32`, `result_map: BPF_MAP_TYPE_ARRAY, max NR_RESULTS, key __u32, value __u32`, `tmp_index_ovr_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value int`, `linum_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u32`, `data_check_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct data_check`
- Key local types: `struct data_check`, `struct sk_reuseport_md`, `struct cmd`, `struct iphdr`, `struct ipv6hdr`, `struct tcphdr`, `struct udphdr`, `enum result`
- Main functions/subprograms: `_select_by_skb_data`

## Control Flow
Entry programs are attached through `sk_reuseport`. Control is organized around `_select_by_skb_data`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `outer_map: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1, key __u32, value __u32`, `result_map: BPF_MAP_TYPE_ARRAY, max NR_RESULTS, key __u32, value __u32`, `tmp_index_ovr_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value int`, `linum_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value __u32`, `data_check_map: BPF_MAP_TYPE_ARRAY, max 1, key __u32, value struct data_check`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/in.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/tcp.h`, `linux/udp.h`, `linux/bpf.h`, `linux/types.h`, `linux/if_ether.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `test_select_reuseport_common.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_select_reuseport_kern.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY_OF_MAPS);` | `} outer_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} result_map SEC(".maps");` | `} tmp_index_ovr_map SEC(".maps");` | `} linum_map SEC(".maps");` | `} data_check_map SEC(".maps");` | `SEC("sk_reuseport")` | and 17 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_select_reuseport_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_send_signal_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_send_signal_kern.c

Research item: `subset-b-006814` ordinal `111`. Source size: 1531 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_send_signal_kern.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tracepoint/syscalls/sys_enter_nanosleep`, `tracepoint/sched/sched_switch`, `perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_task_from_pid`, `bpf_task_release`, `bpf_send_signal_task`, `bpf_send_signal_test`, `bpf_get_current_pid_tgid`, `bpf_send_signal_thread`, `bpf_send_signal`
- Declared maps: None visible in this compact source.
- Key local types: `struct task_struct`, `enum pid_type`
- Main functions/subprograms: `bpf_task_release`, `bpf_send_signal_task`, `bpf_send_signal_test`, `send_signal_tp`, `send_signal_tp_sched`, `send_signal_perf`

## Control Flow
Entry programs are attached through `tracepoint/syscalls/sys_enter_nanosleep`, `tracepoint/sched/sched_switch`, `perf_event`. Control is organized around `bpf_task_release`, `bpf_send_signal_task`, `bpf_send_signal_test`, `send_signal_tp`, `send_signal_tp_sched`, `send_signal_perf`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `sig`, `__license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `linux/version.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_send_signal_kern.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `struct task_struct *bpf_task_from_pid(int pid) __ksym;` | `void bpf_task_release(struct task_struct *p) __ksym;` | `int bpf_send_signal_task(struct task_struct *task, int sig, enum pid_type type, u64 value) __ksym;` | `static __always_inline int bpf_send_signal_test(void *ctx)` | `if ((bpf_get_current_pid_tgid() >> 32) == pid) {` | `target_task = bpf_task_from_pid(target_pid);` | `ret = bpf_send_signal_task(target_task, sig, PIDTYPE_PID, value);` | `ret = bpf_send_signal_thread(sig);` | `ret = bpf_send_signal_task(target_task, sig, PIDTYPE_TGID, value);` | and 7 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_send_signal_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_set_remove_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_set_remove_xattr.c

Research item: `subset-b-006814` ordinal `112`. Source size: 3662 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_set_remove_xattr.c_research.md`.

## Purpose
The program attaches to file-security hooks or tracing points to validate xattr, fsverity, and inode metadata helper behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/inode_getxattr`, `lsm.s/inode_setxattr`
- BPF helpers/macros used: `bpf_tracing`, `bpf_kfuncs`, `bpf_misc`, `bpf_probe_read_kernel`, `bpf_strncmp`, `bpf_set_dentry_xattr`, `bpf_remove_dentry_xattr`, `bpf_dynptr`, `bpf_get_current_pid_tgid`, `bpf_dynptr_from_mem`, `bpf_get_dentry_xattr`, `bpf_set_dentry_xattr_locked`, `bpf_remove_dentry_xattr_locked`
- Declared maps: None visible in this compact source.
- Key local types: `struct dentry`, `struct bpf_dynptr`, `struct mnt_idmap`
- Main functions/subprograms: `name_match_foo`, `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/inode_getxattr`, `lsm.s/inode_setxattr`. Control is organized around `name_match_foo`, `BPF_PROG`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `monitored_pid`, `xattr_foo`, `xattr_bar`, `xattr_selinux`, `value_bar`, `read_value`, `set_security_bpf_bar_success`, `remove_security_bpf_bar_success`, `set_security_selinux_fail`, and 6 more.. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_kfuncs.h`, `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Kernel VFS, LSM hook signature, and helper permission changes can alter verifier acceptance or expected errno/data capture.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_set_remove_xattr.c` is a test fixture for LSM/file metadata BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `#include "bpf_kfuncs.h"` | `#include "bpf_misc.h"` | `char _license[] SEC("license") = "GPL";` | `bool set_security_bpf_bar_success;` | `bool remove_security_bpf_bar_success;` | `bpf_probe_read_kernel(name_buf, sizeof(name_buf), name);` | `return !bpf_strncmp(name_buf, sizeof(xattr_foo), xattr_foo);` | `/* Test bpf_set_dentry_xattr and bpf_remove_dentry_xattr */` | `SEC("lsm.s/inode_getxattr")` | and 17 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_set_remove_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sig_in_xattr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sig_in_xattr.c

Research item: `subset-b-006814` ordinal `113`. Source size: 2726 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sig_in_xattr.c_research.md`.

## Purpose
The program attaches to file-security hooks or tracing points to validate xattr, fsverity, and inode metadata helper behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/file_open`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_kfuncs`, `bpf_get_fsverity_digest`, `bpf_dynptr`, `bpf_key`, `bpf_get_current_pid_tgid`, `bpf_dynptr_from_mem`, `bpf_get_file_xattr`, `bpf_lookup_user_key`, `bpf_verify_pkcs7_signature`, `bpf_key_put`
- Declared maps: None visible in this compact source.
- Key local types: `struct fsverity_digest`, `struct file`, `struct bpf_dynptr`, `struct bpf_key`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/file_open`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`, `digest`, `monitored_pid`, `sig`, `sig_size`, `user_keyring_serial`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_kfuncs.h`, `err.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Kernel VFS, LSM hook signature, and helper permission changes can alter verifier acceptance or expected errno/data capture.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sig_in_xattr.c` is a test fixture for LSM/file metadata BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_kfuncs.h"` | `char _license[] SEC("license") = "GPL";` | `* and the rest of it is filled by bpf_get_fsverity_digest.` | `SEC("lsm.s/file_open")` | `struct bpf_dynptr digest_ptr, sig_ptr;` | `struct bpf_key *trusted_keyring;` | `pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_dynptr_from_mem(digest + MAGIC_SIZE, sizeof(digest) - MAGIC_SIZE, 0, &digest_ptr);` | and 7 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sig_in_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_siphash.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_siphash.h

Research item: `subset-b-006814` ordinal `114`. Source size: 1514 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_siphash.h_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: None visible in this compact source.
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `rol64`, `siphash_2u64`

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section. Control is organized around `rol64`, `siphash_2u64`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers None visible in this compact source..
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_siphash.h` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: No concentrated marker lines; rely on the API/function lists above.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_siphash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign.c

Research item: `subset-b-006814` ordinal `115`. Source size: 4562 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `maps`, `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_misc`, `bpf_elf_map`, `bpf_sock_tuple`, `bpf_htons`, `bpf_sock`, `bpf_sk_lookup_udp`, `bpf_map_lookup_elem`, `bpf_sk_assign`, `bpf_sk_release`, `bpf_skc_lookup_tcp`, `bpf_sk_assign_test`
- Declared maps: `server_map: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value __u64`
- Key local types: `struct bpf_elf_map`, `struct bpf_sock_tuple`, `struct __sk_buff`, `struct ethhdr`, `struct iphdr`, `struct ipv6hdr`, `struct bpf_sock`
- Main functions/subprograms: `get_tuple`, `handle_udp`, `handle_tcp`, `bpf_sk_assign_test`

## Control Flow
Entry programs are attached through `maps`, `tc`. Control is organized around `get_tuple`, `handle_udp`, `handle_tcp`, `bpf_sk_assign_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `server_map: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value __u64`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state. Socket references acquired from maps or helpers are explicitly released to satisfy verifier lifetime rules.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/in.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/pkt_cls.h`, `linux/tcp.h`, `sys/socket.h`, `bpf/bpf_helpers.h`, and 1 more..
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_assign.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_misc.h"` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} server_map SEC(".maps");` | `/* Must match struct bpf_elf_map layout from iproute2 */` | `} server_map SEC("maps") = {` | `.type = BPF_MAP_TYPE_SOCKMAP,` | `char _license[] SEC("license") = "GPL";` | `static inline struct bpf_sock_tuple *` | and 23 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign_libbpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign_libbpf.c

Research item: `subset-b-006814` ordinal `116`. Source size: 93 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign_libbpf.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: None visible in this compact source.
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers None visible in this compact source..
Local test dependencies: `test_sk_assign.c`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_assign_libbpf.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: No concentrated marker lines; rely on the API/function lists above.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign_libbpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup.c

Research item: `subset-b-006814` ordinal `117`. Source size: 18993 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_lookup`, `sk_reuseport`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_sk_lookup`, `bpf_sock`, `bpf_map_lookup_elem`, `bpf_sk_assign`, `bpf_sk_release`, `bpf_sk_select_reuseport`, `bpf_printk`, `bpf_map_update_elem`
- Declared maps: `redir_map: BPF_MAP_TYPE_SOCKMAP, max MAX_SOCKS, key __u32, value __u64`, `run_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value int`
- Key local types: `struct bpf_sk_lookup`, `struct sk_reuseport_md`, `struct bpf_sock`
- Main functions/subprograms: `lookup_pass`, `lookup_drop`, `check_ifindex`, `reuseport_pass`, `reuseport_drop`, `redir_port`, `redir_ip4`, `redir_ip6`, `select_sock_a`, `select_sock_a_no_reuseport`, `select_sock_b`, `sk_assign_eexist`, `sk_assign_replace_flag`, `sk_assign_null`, `access_ctx_sk`, `ctx_narrow_access`, and 8 more.

## Control Flow
Entry programs are attached through `sk_lookup`, `sk_reuseport`. Control is organized around `lookup_pass`, `lookup_drop`, `check_ifindex`, `reuseport_pass`, `reuseport_drop`, `redir_port`, `redir_ip4`, `redir_ip6`, `select_sock_a`, `select_sock_a_no_reuseport`, `select_sock_b`, `sk_assign_eexist`, and 12 more.. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `redir_map: BPF_MAP_TYPE_SOCKMAP, max MAX_SOCKS, key __u32, value __u64`, `run_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value int`. Global data/control fields include `KEY_PROG1`, `KEY_PROG2`, `PROG_DONE`, `KEY_SERVER_A`, `KEY_SERVER_B`, `SRC_PORT`, `SRC_IP4`, `SRC_IP6`, `DST_PORT`, `DST_IP4`, and 2 more.. The program deliberately persists observations through maps or event buffers for user-space assertions. Socket references acquired from maps or helpers are explicitly released to satisfy verifier lifetime rules.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `stdbool.h`, `stddef.h`, `linux/bpf.h`, `linux/in.h`, `sys/socket.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_lookup.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `bpf_htonl((((__u32)(a) & 0xffU) << 24) |	\` | `{ bpf_htonl(aaaa), bpf_htonl(bbbb), bpf_htonl(cccc), bpf_htonl(dddd) }` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} redir_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} run_map SEC(".maps");` | `static const __u16 SRC_PORT = bpf_htons(8008);` | `SEC("sk_lookup")` | and 56 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup_kern.c

Research item: `subset-b-006814` ordinal `118`. Source size: 4038 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup_kern.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `?tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_sock_tuple`, `bpf_htons`, `bpf_sock`, `bpf_sk_lookup_tcp`, `bpf_printk`, `bpf_sk_release`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_sock_tuple`, `struct iphdr`, `struct ipv6hdr`, `struct __sk_buff`, `struct ethhdr`, `struct bpf_sock`
- Main functions/subprograms: `sk_lookup_success`, `sk_lookup_success_simple`, `err_use_after_free`, `err_modify_sk_pointer`, `err_modify_sk_or_null_pointer`, `err_no_release`, `err_release_twice`, `err_release_unchecked`, `lookup_no_release`, `err_no_release_subcall`

## Control Flow
Entry programs are attached through `?tc`. Control is organized around `sk_lookup_success`, `sk_lookup_success_simple`, `err_use_after_free`, `err_modify_sk_pointer`, `err_modify_sk_or_null_pointer`, `err_no_release`, `err_release_twice`, `err_release_unchecked`, `lookup_no_release`, `err_no_release_subcall`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness. Socket references acquired from maps or helpers are explicitly released to satisfy verifier lifetime rules.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/in.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/pkt_cls.h`, `linux/tcp.h`, `sys/socket.h`, `bpf/bpf_helpers.h`, and 1 more..
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_lookup_kern.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: embedded verifier annotations (`__success`, `__failure`, `__msg`, or similar) define expected load behavior, trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `char _license[] SEC("license") = "GPL";` | `static struct bpf_sock_tuple *get_tuple(void *data, __u64 nh_off,` | `struct bpf_sock_tuple *result;` | `if (eth_proto == bpf_htons(ETH_P_IP)) {` | `result = (struct bpf_sock_tuple *)&iph->saddr;` | `} else if (eth_proto == bpf_htons(ETH_P_IPV6)) {` | `result = (struct bpf_sock_tuple *)&ip6h->saddr;` | `SEC("?tc")` | and 10 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_lookup_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_trace_itself.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_trace_itself.c

Research item: `subset-b-006814` ordinal `119`. Source size: 581 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_trace_itself.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `fentry/bpf_sk_storage_free`
- BPF helpers/macros used: `bpf_tracing`, `bpf_helpers`, `bpf_sk_storage_free`, `bpf_sk_storage_get`
- Declared maps: `sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value int`
- Key local types: `struct sock`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `fentry/bpf_sk_storage_free`. Control is organized around `BPF_PROG`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value int`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_storage_trace_itself.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SK_STORAGE);` | `} sk_stg_map SEC(".maps");` | `SEC("fentry/bpf_sk_storage_free")` | `int BPF_PROG(trace_bpf_sk_storage_free, struct sock *sk)` | `value = bpf_sk_storage_get(&sk_stg_map, sk, 0,` | `BPF_SK_STORAGE_GET_F_CREATE);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_trace_itself.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_tracing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_tracing.c

Research item: `subset-b-006814` ordinal `120`. Source size: 2306 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_tracing.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp_btf/inet_sock_set_state`, `fentry/inet_csk_listen_start`, `fentry/tcp_connect`, `fexit/inet_csk_accept`, `tp_btf/tcp_retransmit_synack`, `tp_btf/tcp_bad_csum`
- BPF helpers/macros used: `bpf_tracing`, `bpf_core_read`, `bpf_helpers`, `bpf_sk_storage_get`, `bpf_sk_storage_delete`, `bpf_get_current_pid_tgid`, `bpf_get_current_task`, `bpf_core_read_str`
- Declared maps: `sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value struct sk_stg`, `del_sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value int`
- Key local types: `struct sk_stg`, `struct sock`, `struct task_struct`, `struct proto_accept_arg`, `struct request_sock`, `struct sk_buff`
- Main functions/subprograms: `BPF_PROG`, `set_task_info`

## Control Flow
Entry programs are attached through `tp_btf/inet_sock_set_state`, `fentry/inet_csk_listen_start`, `fentry/tcp_connect`, `fexit/inet_csk_accept`, `tp_btf/tcp_retransmit_synack`, `tp_btf/tcp_bad_csum`. Control is organized around `BPF_PROG`, `set_task_info`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value struct sk_stg`, `del_sk_stg_map: BPF_MAP_TYPE_SK_STORAGE, key int, value int`. Global data/control fields include `task_comm`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_storage_tracing.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `#include <bpf/bpf_core_read.h>` | `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SK_STORAGE);` | `} sk_stg_map SEC(".maps");` | `} del_sk_stg_map SEC(".maps");` | `SEC("tp_btf/inet_sock_set_state")` | `stg = bpf_sk_storage_get(&sk_stg_map, sk, 0,` | `BPF_SK_STORAGE_GET_F_CREATE);` | `bpf_sk_storage_delete(&del_sk_stg_map, sk);` | and 13 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_storage_tracing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_ctx.c

Research item: `subset-b-006814` ordinal `121`. Source size: 618 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_ctx.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_compiler`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `process`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `process`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: `bpf_compiler.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_skb_ctx.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include "bpf_compiler.h"` | `char _license[] SEC("license") = "GPL";` | `SEC("tc")`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_helpers.c

Research item: `subset-b-006814` ordinal `122`. Source size: 643 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_helpers.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_get_current_task`, `bpf_probe_read_kernel`, `bpf_probe_read_kernel_str`
- Declared maps: `cgroup_map: BPF_MAP_TYPE_CGROUP_ARRAY, max 1, key u32, value u32`
- Key local types: `struct __sk_buff`, `struct task_struct`
- Main functions/subprograms: `test_skb_helpers`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `test_skb_helpers`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `cgroup_map: BPF_MAP_TYPE_CGROUP_ARRAY, max 1, key u32, value u32`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_skb_helpers.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_CGROUP_ARRAY);` | `} cgroup_map SEC(".maps");` | `char _license[] SEC("license") = "GPL";` | `SEC("tc")` | `task = (struct task_struct *)bpf_get_current_task();` | `bpf_probe_read_kernel(&tpid , sizeof(tpid), &task->tgid);` | `bpf_probe_read_kernel_str(&comm, sizeof(comm), &task->comm);`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skb_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skc_to_unix_sock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skc_to_unix_sock.c

Research item: `subset-b-006814` ordinal `123`. Source size: 840 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skc_to_unix_sock.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `fentry/unix_listen`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_tracing_net`, `bpf_get_current_pid_tgid`, `bpf_skc_to_unix_sock`
- Declared maps: None visible in this compact source.
- Key local types: `struct socket`, `struct unix_sock`, `struct sockaddr_un`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `fentry/unix_listen`. Control is organized around `BPF_PROG`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `path`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`, `bpf_tracing_net.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_skc_to_unix_sock.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `#include "bpf_tracing_net.h"` | `SEC("fentry/unix_listen")` | `pid_t pid = bpf_get_current_pid_tgid() >> 32;` | `unix_sk = (struct unix_sock *)bpf_skc_to_unix_sock(sock->sk);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skc_to_unix_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skeleton.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skeleton.c

Research item: `subset-b-006814` ordinal `124`. Source size: 1906 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skeleton.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `.data.read_mostly`, `.rodata.dyn`, `.data.dyn`, `.data.non_mmapable`, `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_syscall`, `bpf_map_update_elem`
- Declared maps: `my_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value struct my_value`
- Key local types: `struct s`, `struct my_value`
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `.data.read_mostly`, `.rodata.dyn`, `.data.dyn`, `.data.non_mmapable`, `raw_tp/sys_enter`. Control is organized around `handler`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `my_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value struct my_value`. Global data/control fields include `in1`, `in3`, `in5`, `out1`, `out3`, `out6`, `bpf_syscall`, `kern_ver`, `out5`, `out_dynarr`, and 3 more.. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stdbool.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_skeleton.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#define __read_mostly SEC(".data.read_mostly")` | `bool bpf_syscall = 0;` | `const volatile int in_dynarr_sz SEC(".rodata.dyn");` | `const volatile int in_dynarr[4] SEC(".rodata.dyn") = { -1, -2, -3, -4 };` | `int out_dynarr[4] SEC(".data.dyn") = { 1, 2, 3, 4 };` | `__hidden int zero_key SEC(".data.non_mmapable");` | `static struct my_value zero_value SEC(".data.non_mmapable");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} my_map SEC(".maps");` | and 4 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skeleton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skmsg_load_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skmsg_load_helpers.c

Research item: `subset-b-006814` ordinal `125`. Source size: 1570 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skmsg_load_helpers.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_msg`, `sk_skb/stream_verdict`
- BPF helpers/macros used: `bpf_helpers`, `bpf_get_current_task`, `bpf_get_current_pid_tgid`, `bpf_sk_storage_get`, `bpf_probe_read_kernel`, `bpf_sk_storage_delete`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `sock_hash: BPF_MAP_TYPE_SOCKHASH, max 2, key __u32, value __u64`, `socket_storage: BPF_MAP_TYPE_SK_STORAGE, key __u32, value __u64`
- Key local types: `struct sk_msg_md`, `struct task_struct`, `struct __sk_buff`
- Main functions/subprograms: `prog_msg_verdict_common`, `prog_msg_verdict`, `prog_msg_verdict_clone`, `prog_msg_verdict_clone2`, `prog_skb_verdict`

## Control Flow
Entry programs are attached through `sk_msg`, `sk_skb/stream_verdict`. Control is organized around `prog_msg_verdict_common`, `prog_msg_verdict`, `prog_msg_verdict_clone`, `prog_msg_verdict_clone2`, `prog_skb_verdict`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `sock_hash: BPF_MAP_TYPE_SOCKHASH, max 2, key __u32, value __u64`, `socket_storage: BPF_MAP_TYPE_SK_STORAGE, key __u32, value __u64`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_skmsg_load_helpers.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_SOCKHASH);` | `} sock_hash SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_SK_STORAGE);` | `} socket_storage SEC(".maps");` | `struct task_struct *task = (struct task_struct *)bpf_get_current_task();` | `int verdict = SK_PASS;` | `pid = bpf_get_current_pid_tgid() >> 32;` | and 9 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_skmsg_load_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf.c

Research item: `subset-b-006814` ordinal `126`. Source size: 2025 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_get_current_pid_tgid`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `pid`, `num_out`, `num_ret`, `ip_out`, `ip_ret`, `sym_out`, `sym_ret`, `addr_out`, `addr_ret`, `str_out`, and 9 more.. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_snprintf.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("raw_tp/sys_enter")` | `if ((int)bpf_get_current_pid_tgid() != pid)` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf_single.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf_single.c

Research item: `subset-b-006814` ordinal `127`. Source size: 414 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf_single.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_snprintf`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `handler`.

## State And Persistence Behavior
Global data/control fields include `fmt`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_snprintf_single.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("raw_tp/sys_enter")` | `bpf_snprintf(NULL, 0, fmt, &arg, sizeof(arg));` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_snprintf_single.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sock_fields.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sock_fields.c

Research item: `subset-b-006814` ordinal `128`. Source size: 7500 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sock_fields.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `cgroup_skb/egress`, `cgroup_skb/ingress`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_linum_array_idx`, `bpf_spinlock_cnt`, `bpf_spin_lock`, `bpf_tcp_sock`, `bpf_sock`, `bpf_htonl`, `bpf_map_update_elem`, `bpf_ntohs`, `bpf_sk_fullsock`, `bpf_skc_to_tcp_sock`, `bpf_sk_cgroup_id`, `bpf_sk_ancestor_cgroup_id`, `bpf_sk_storage_get`, `bpf_spin_unlock`, and 1 more.
- Declared maps: `linum_map: BPF_MAP_TYPE_ARRAY, max __NR_BPF_LINUM_ARRAY_IDX, key __u32, value __u32`, `sk_pkt_out_cnt: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`, `sk_pkt_out_cnt10: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`
- Key local types: `struct bpf_spinlock_cnt`, `struct bpf_spin_lock`, `struct tcp_sock`, `struct bpf_tcp_sock`, `struct sockaddr_in6`, `struct bpf_sock`, `struct __sk_buff`, `enum bpf_linum_array_idx`
- Main functions/subprograms: `is_loopback6`, `skcpy`, `tpcpy`, `egress_read_sock_fields`, `ingress_read_sock_fields`, `sk_dst_port__load_word`, `sk_dst_port__load_half`, `sk_dst_port__load_byte`, `read_sk_dst_port`

## Control Flow
Entry programs are attached through `cgroup_skb/egress`, `cgroup_skb/ingress`. Control is organized around `is_loopback6`, `skcpy`, `tpcpy`, `egress_read_sock_fields`, `ingress_read_sock_fields`, `sk_dst_port__load_word`, `sk_dst_port__load_half`, `sk_dst_port__load_byte`, `read_sk_dst_port`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `linum_map: BPF_MAP_TYPE_ARRAY, max __NR_BPF_LINUM_ARRAY_IDX, key __u32, value __u32`, `sk_pkt_out_cnt: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`, `sk_pkt_out_cnt10: BPF_MAP_TYPE_SK_STORAGE, key int, value struct bpf_spinlock_cnt`. Global data/control fields include `listen_tp`, `srv_sa6`, `cli_tp`, `srv_tp`, `listen_sk`, `srv_sk`, `cli_sk`, `parent_cg_id`, `child_cg_id`, `lsndtime`, and 1 more.. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `netinet/in.h`, `stdbool.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sock_fields.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `enum bpf_linum_array_idx {` | `READ_SK_DST_PORT_LINUM_IDX,` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} linum_map SEC(".maps");` | `struct bpf_spinlock_cnt {` | `struct bpf_spin_lock lock;` | `__uint(type, BPF_MAP_TYPE_SK_STORAGE);` | `__type(value, struct bpf_spinlock_cnt);` | and 45 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sock_fields.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockhash_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockhash_kern.c

Research item: `subset-b-006814` ordinal `129`. Source size: 187 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockhash_kern.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: None visible in this compact source.
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers None visible in this compact source..
Local test dependencies: `./test_sockmap_kern.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockhash_kern.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#define TEST_MAP_TYPE BPF_MAP_TYPE_SOCKHASH`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockhash_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_change_tail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_change_tail.c

Research item: `subset-b-006814` ordinal `130`. Source size: 1085 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_change_tail.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb`
- BPF helpers/macros used: `bpf_helpers`, `bpf_skb_pull_data`, `bpf_skb_change_tail`
- Declared maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value int`
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `prog_skb_verdict`

## Control Flow
Entry programs are attached through `sk_skb`. Control is organized around `prog_skb_verdict`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value int`. Global data/control fields include `change_tail_ret`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_change_tail.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map_rx SEC(".maps");` | `SEC("sk_skb")` | `bpf_skb_pull_data(skb, 1);` | `return SK_PASS;` | `change_tail_ret = bpf_skb_change_tail(skb, skb->len - 1, 0);` | `change_tail_ret = bpf_skb_change_tail(skb, skb->len + 1, 0);` | `change_tail_ret = bpf_skb_change_tail(skb, BPF_SKB_MAX_LEN, 0);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_change_tail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_drop_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_drop_prog.c

Research item: `subset-b-006814` ordinal `131`. Source size: 625 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_drop_prog.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`
- Declared maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_tx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_msg: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `prog_skb_verdict`

## Control Flow
Entry programs are attached through `sk_skb`. Control is organized around `prog_skb_verdict`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_tx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_msg: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_drop_prog.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map_rx SEC(".maps");` | `} sock_map_tx SEC(".maps");` | `} sock_map_msg SEC(".maps");` | `SEC("sk_skb")` | `return SK_DROP;` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_drop_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_invalid_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_invalid_update.c

Research item: `subset-b-006814` ordinal `132`. Source size: 453 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_invalid_update.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sockops`
- BPF helpers/macros used: `bpf_helpers`, `bpf_sockmap`, `bpf_sock_ops`, `bpf_map_update_elem`
- Declared maps: `map: BPF_MAP_TYPE_SOCKMAP, max 1, key __u32, value __u64`
- Key local types: `struct bpf_sock_ops`
- Main functions/subprograms: `bpf_sockmap`

## Control Flow
Entry programs are attached through `sockops`. Control is organized around `bpf_sockmap`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `map: BPF_MAP_TYPE_SOCKMAP, max 1, key __u32, value __u64`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_invalid_update.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} map SEC(".maps");` | `SEC("sockops")` | `int bpf_sockmap(struct bpf_sock_ops *skops)` | `bpf_map_update_elem(&map, &key, skops->sk, 0);` | `char _license[] SEC("license") = "GPL";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_invalid_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.c

Research item: `subset-b-006814` ordinal `133`. Source size: 187 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: None visible in this compact source.
- BPF helpers/macros used: None visible in this compact source.
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: None visible in this compact source.

## Control Flow
This file is primarily a shared header or compile-time fixture with no direct BPF attach section.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers None visible in this compact source..
Local test dependencies: `./test_sockmap_kern.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_kern.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#define TEST_MAP_TYPE BPF_MAP_TYPE_SOCKMAP`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.h

Research item: `subset-b-006814` ordinal `134`. Source size: 8877 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.h_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sockops`, `sk_msg`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_misc`, `bpf_printk`, `bpf_prog1`, `bpf_map_lookup_elem`, `bpf_prog2`, `bpf_sk_redirect_map`, `bpf_sk_redirect_hash`, `bpf_write_pass`, `bpf_skb_pull_data`, `bpf_prog3`, `bpf_skb_adjust_room`, `bpf_sockmap`, `bpf_sock_ops`, `bpf_sock_map_update`, and 14 more.
- Declared maps: `sock_map: TEST_MAP_TYPE, max 20`, `sock_map_txmsg: TEST_MAP_TYPE, max 20`, `sock_map_redir: TEST_MAP_TYPE, max 20`, `sock_apply_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_cork_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_bytes: BPF_MAP_TYPE_ARRAY, max 6, key int, value int`, `sock_redir_flags: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_skb_opts: BPF_MAP_TYPE_ARRAY, max 3, key int, value int`, `tls_sock_map: TEST_MAP_TYPE, max 20`
- Key local types: `struct __sk_buff`, `struct bpf_sock_ops`, `struct sk_msg_md`
- Main functions/subprograms: `bpf_prog1`, `bpf_prog2`, `bpf_write_pass`, `bpf_prog3`, `bpf_sockmap`, `bpf_prog4`, `bpf_prog6`, `bpf_prog8`, `bpf_prog9`, `bpf_prog10`

## Control Flow
Entry programs are attached through `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sockops`, `sk_msg`. Control is organized around `bpf_prog1`, `bpf_prog2`, `bpf_write_pass`, `bpf_prog3`, `bpf_sockmap`, `bpf_prog4`, `bpf_prog6`, `bpf_prog8`, `bpf_prog9`, `bpf_prog10`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: TEST_MAP_TYPE, max 20`, `sock_map_txmsg: TEST_MAP_TYPE, max 20`, `sock_map_redir: TEST_MAP_TYPE, max 20`, `sock_apply_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_cork_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_bytes: BPF_MAP_TYPE_ARRAY, max 6, key int, value int`, `sock_redir_flags: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_skb_opts: BPF_MAP_TYPE_ARRAY, max 3, key int, value int`, and 1 more.. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/if_packet.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/in.h`, `linux/udp.h`, `linux/tcp.h`, `linux/pkt_cls.h`, `sys/socket.h`, and 2 more..
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_kern.h` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_misc.h"` | `* The bpf_printk is verbose and prints information as connections` | `} sock_map SEC(".maps");` | `} sock_map_txmsg SEC(".maps");` | `} sock_map_redir SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} sock_apply_bytes SEC(".maps");` | `} sock_cork_bytes SEC(".maps");` | and 55 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_ktls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_ktls.c

Research item: `subset-b-006814` ordinal `135`. Source size: 830 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_ktls.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_msg`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_msg_cork_bytes`, `bpf_msg_push_data`, `bpf_msg_pop_data`, `bpf_msg_apply_bytes`, `bpf_msg_redirect_map`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`
- Key local types: `struct sk_msg_md`
- Main functions/subprograms: `prog_sk_policy`, `prog_sk_policy_redir`

## Control Flow
Entry programs are attached through `sk_msg`. Control is organized around `prog_sk_policy`, `prog_sk_policy_redir`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`. Global data/control fields include `cork_byte`, `push_start`, `push_end`, `apply_bytes`, `pop_start`, `pop_end`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_ktls.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `SEC("sk_msg")` | `bpf_msg_cork_bytes(msg, cork_byte);` | `bpf_msg_push_data(msg, push_start, push_end, 0);` | `bpf_msg_pop_data(msg, pop_start, pop_end, 0);` | `return SK_PASS;` | `bpf_msg_apply_bytes(msg, apply_bytes);` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_ktls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_listen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_listen.c

Research item: `subset-b-006814` ordinal `136`. Source size: 2841 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_listen.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sk_skb`, `sk_msg`, `sk_reuseport`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_sk_redirect_map`, `bpf_sk_redirect_hash`, `bpf_msg_redirect_map`, `bpf_msg_redirect_hash`, `bpf_sk_select_reuseport`
- Declared maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `nop_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `sock_hash: BPF_MAP_TYPE_SOCKHASH, max 2, key __u32, value __u64`, `verdict_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value unsigned int`, `parser_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: `struct __sk_buff`, `struct sk_msg_md`, `struct sk_reuseport_md`
- Main functions/subprograms: `prog_stream_parser`, `prog_stream_verdict`, `prog_skb_verdict`, `prog_msg_verdict`, `prog_reuseport`

## Control Flow
Entry programs are attached through `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sk_skb`, `sk_msg`, `sk_reuseport`. Control is organized around `prog_stream_parser`, `prog_stream_verdict`, `prog_skb_verdict`, `prog_msg_verdict`, `prog_reuseport`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `nop_map: BPF_MAP_TYPE_SOCKMAP, max 2, key __u32, value __u64`, `sock_hash: BPF_MAP_TYPE_SOCKHASH, max 2, key __u32, value __u64`, `verdict_map: BPF_MAP_TYPE_ARRAY, max 2, key int, value unsigned int`, `parser_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `test_sockmap`, `test_ingress`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `errno.h`, `stdbool.h`, `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_listen.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map SEC(".maps");` | `} nop_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_SOCKHASH);` | `} sock_hash SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} verdict_map SEC(".maps");` | `} parser_map SEC(".maps");` | `SEC("sk_skb/stream_parser")` | and 16 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_pass_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_pass_prog.c

Research item: `subset-b-006814` ordinal `137`. Source size: 1149 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_pass_prog.c_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb/stream_verdict`, `sk_skb/stream_parser`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_sk_redirect_map`
- Declared maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_tx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_msg: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `prog_skb_verdict`, `prog_skb_verdict_clone`, `prog_skb_parser`, `prog_skb_verdict_ingress`, `prog_skb_verdict_ingress_strp`

## Control Flow
Entry programs are attached through `sk_skb/stream_verdict`, `sk_skb/stream_parser`. Control is organized around `prog_skb_verdict`, `prog_skb_verdict_clone`, `prog_skb_parser`, `prog_skb_verdict_ingress`, `prog_skb_verdict_ingress_strp`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `sock_map_rx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_tx: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`, `sock_map_msg: BPF_MAP_TYPE_SOCKMAP, max 20, key int, value int`. Global data/control fields include `clone_called`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_pass_prog.c` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} sock_map_rx SEC(".maps");` | `} sock_map_tx SEC(".maps");` | `} sock_map_msg SEC(".maps");` | `SEC("sk_skb/stream_verdict")` | `return SK_PASS;` | `SEC("sk_skb/stream_parser")` | `return bpf_sk_redirect_map(skb, &sock_map_rx, one, BPF_F_INGRESS);` | and 1 more marker lines

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_pass_prog.c -->
