# subset-b-006810 research

Grouped source-tree-aligned research for the requested BPF selftest sources. The reconciliation lane can split each exact BEGIN/END block into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_sleepable.c

## Purpose
`cgrp_ls_sleepable.c` is a cgroup iterator/typed tracepoint selftest for cgroup local storage and cgroup1 lookup kfuncs. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2772 bytes across 125 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: task/cgroup/time/function metadata helpers; task or cgroup reference kfuncs.
- Helper/kfunc calls: `bpf_cgroup_release`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`, `bpf_task_get_cgroup1`.
Map/type declarations observed:
- line 11 declares map type `BPF_MAP_TYPE_CGRP_STORAGE`
Attach sections and exported entry points:
- line 8 `SEC("license")` -> struct {
- line 15 `SEC(".maps")` -> int target_hid;
- line 27 `SEC("?iter.s/cgroup")` -> int cgroup_iter(struct bpf_iter__cgroup *ctx)
- line 56 `SEC("SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")")` -> int cgrp1_no_rcu_lock(void *ctx)
- line 76 `SEC("SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")")` -> int no_rcu_lock(void *ctx)
- line 90 `SEC("SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")")` -> int yes_rcu_lock(void *ctx)
Key functions/subprograms:
- line 28 `cgroup_iter`: `int cgroup_iter(struct bpf_iter__cgroup *ctx)`
- line 43 `__no_rcu_lock`: `static void __no_rcu_lock(struct cgroup *cgrp)`
- line 57 `cgrp1_no_rcu_lock`: `int cgrp1_no_rcu_lock(void *ctx)`
- line 77 `no_rcu_lock`: `int no_rcu_lock(void *ctx)`
- line 91 `yes_rcu_lock`: `int yes_rcu_lock(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `?iter.s/cgroup`, `SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")`, `SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")`, `SEC("?fentry.s/" SYS_PREFIX "sys_getpgid")`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `cgroup_iter`, `__no_rcu_lock`, `cgrp1_no_rcu_lock`, `no_rcu_lock`, `yes_rcu_lock`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 17 `__s32 target_pid;`
- line 18 `__u64 cgroup_id;`
- line 19 `int target_hid;`
- line 20 `bool is_cgroup1;`
- line 31 `long *ptr;`
- line 45 `long *ptr;`
- line 95 `long *ptr;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_sleepable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_tp_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_tp_btf.c

## Purpose
`cgrp_ls_tp_btf.c` is a cgroup iterator/typed tracepoint selftest for cgroup local storage and cgroup1 lookup kfuncs. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2644 bytes across 126 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `MAGIC_VALUE`.
- BPF API surface: task/cgroup/time/function metadata helpers; task or cgroup reference kfuncs.
- Helper/kfunc calls: `bpf_cgroup_release`, `bpf_cgrp_storage_delete`, `bpf_cgrp_storage_get`, `bpf_get_current_task_btf`, `bpf_task_get_cgroup1`.
Map/type declarations observed:
- line 11 declares map type `BPF_MAP_TYPE_CGRP_STORAGE`
- line 18 declares map type `BPF_MAP_TYPE_CGRP_STORAGE`
Attach sections and exported entry points:
- line 8 `SEC("license")` -> struct {
- line 15 `SEC(".maps")` -> struct {
- line 22 `SEC(".maps")` -> #define MAGIC_VALUE 0xabcd1234
- line 66 `SEC("tp_btf/sys_enter")` -> int BPF_PROG(on_enter, struct pt_regs *regs, long id)
- line 104 `SEC("tp_btf/sys_exit")` -> int BPF_PROG(on_exit, struct pt_regs *regs, long id)
Key functions/subprograms:
- line 36 `__on_enter`: `static void __on_enter(struct pt_regs *regs, long id, struct cgroup *cgrp)`
- line 67 `BPF_PROG`: `int BPF_PROG(on_enter, struct pt_regs *regs, long id)`
- line 90 `__on_exit`: `static void __on_exit(struct pt_regs *regs, long id, struct cgroup *cgrp)`
- line 105 `BPF_PROG`: `int BPF_PROG(on_exit, struct pt_regs *regs, long id)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `tp_btf/sys_enter`, `tp_btf/sys_exit`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `__on_enter`, `BPF_PROG`, `__on_exit`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 27 `int mismatch_cnt = 0;`
- line 28 `int enter_cnt = 0;`
- line 29 `int exit_cnt = 0;`
- line 30 `int target_hid = 0;`
- line 31 `bool is_cgroup1 = 0;`
- line 38 `long *ptr;`
- line 39 `int err;`
- line 92 `long *ptr;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cgrp_ls_tp_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/clone_attach_btf_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/clone_attach_btf_id.c

## Purpose
`clone_attach_btf_id.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 271 bytes across 13 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(fentry_handler, int a)
- line 9 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(fentry_handler, int a)
Key functions/subprograms:
- line 10 `BPF_PROG`: `int BPF_PROG(fentry_handler, int a)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_fentry_test1`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/clone_attach_btf_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/compute_live_registers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/compute_live_registers.c

## Purpose
`compute_live_registers.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 10424 bytes across 481 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `"../../../include/linux/filter.h"`, `"bpf_arena_common.h"`, `"bpf_misc.h"`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_arena_alloc_pages`.
Map/type declarations observed:
- line 10 declares map type `BPF_MAP_TYPE_ARRAY`
- line 17 declares map type `BPF_MAP_TYPE_ARENA`
Attach sections and exported entry points:
- line 14 `SEC(".maps")` -> struct {
- line 20 `SEC(".maps")` -> next declaration
- line 22 `SEC("socket")` -> next declaration
- line 54 `SEC("socket")` -> next declaration
- line 77 `SEC("socket")` -> next declaration
- line 100 `SEC("socket")` -> next declaration
- line 117 `SEC("socket")` -> next declaration
- line 132 `SEC("socket")` -> next declaration
- line 168 `SEC("socket")` -> next declaration
- line 193 `SEC("socket")` -> {
- line 212 `SEC("socket")` -> {
- line 227 `SEC("socket")` -> {
- plus 10 more entries of the same pattern.
Key functions/subprograms:
- line 36 `assign_chain`: `__naked void assign_chain(void)`
- line 38 `volatile`: `asm volatile (`
- line 63 `arithmetics`: `__naked void arithmetics(void)`
- line 65 `volatile`: `asm volatile (`
- line 85 `store`: `__naked void store(void)`
- line 87 `volatile`: `asm volatile (`
- line 105 `load`: `__naked void load(void)`
- line 107 `volatile`: `asm volatile (`
- line 122 `endian`: `__naked void endian(void)`
- line 124 `volatile`: `asm volatile (`
- line 141 `atomic`: `__naked void atomic(void)`
- line 143 `volatile`: `asm volatile (`
- plus 29 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `.maps`, `socket`, `socket`, `socket`, `socket`, `socket`, `socket` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `assign_chain`, `volatile`, `arithmetics`, `volatile`, `store`, `volatile`, `load`, `volatile` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.

## Test Signals
- Expected verifier messages include ` 0: .......... (b7) r0 = 42`, ` 1: 0......... (bf) r1 = r0`, ` 2: .1........ (bf) r2 = r1`, ` 3: ..2....... (bf) r3 = r2`, ` 4: ...3...... (bf) r4 = r3`, plus 90 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/compute_live_registers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_dropper.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_dropper.c

## Purpose
`connect4_dropper.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 519 bytes across 28 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/stddef.h>`, `<linux/bpf.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `VERDICT_REJECT`, `VERDICT_PROCEED`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_htons`.
Attach sections and exported entry points:
- line 18 `SEC("cgroup/connect4")` -> int connect_v4_dropper(struct bpf_sock_addr *ctx)
- line 28 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 19 `connect_v4_dropper`: `int connect_v4_dropper(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect4`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_v4_dropper`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `int port;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_dropper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_prog.c

## Purpose
`connect4_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4577 bytes across 203 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/stddef.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<linux/tcp.h>`, `<linux/if.h>`, `<errno.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `SRC_REWRITE_IP4`, `DST_REWRITE_IP4`, `DST_REWRITE_PORT4`, `TCP_CA_NAME_MAX`, `TCP_NOTSENT_LOWAT`, `IFNAMSIZ`, `SOL_TCP`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_getsockopt`, `bpf_htonl`, `bpf_htons`, `bpf_setsockopt`, `bpf_sk_lookup_tcp`, `bpf_sk_lookup_udp`, `bpf_sk_release`, `bpf_strncmp`.
Attach sections and exported entry points:
- line 143 `SEC("cgroup/connect4")` -> int connect_v4_prog(struct bpf_sock_addr *ctx)
- line 197 `SEC("cgroup/connect4")` -> int connect_v4_deny_prog(struct bpf_sock_addr *ctx)
- line 203 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 41 `do_bind`: `int do_bind(struct bpf_sock_addr *ctx)`
- line 55 `verify_cc`: `static __inline int verify_cc(struct bpf_sock_addr *ctx,`
- line 69 `set_cc`: `static __inline int set_cc(struct bpf_sock_addr *ctx)`
- line 84 `bind_to_device`: `static __inline int bind_to_device(struct bpf_sock_addr *ctx)`
- line 107 `set_keepalive`: `static __inline int set_keepalive(struct bpf_sock_addr *ctx)`
- line 131 `set_notsent_lowat`: `static __inline int set_notsent_lowat(struct bpf_sock_addr *ctx)`
- line 144 `connect_v4_prog`: `int connect_v4_prog(struct bpf_sock_addr *ctx)`
- line 198 `connect_v4_deny_prog`: `int connect_v4_deny_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect4`, `cgroup/connect4`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `do_bind`, `verify_cc`, `set_cc`, `bind_to_device`, `set_keepalive`, `set_notsent_lowat`, `connect_v4_prog`, `connect_v4_deny_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 58 `char buf[TCP_CA_NAME_MAX];`
- line 86 `char veth1[IFNAMSIZ] = "test_sock_addr1";`
- line 87 `char veth2[IFNAMSIZ] = "test_sock_addr2";`
- line 88 `char missing[IFNAMSIZ] = "nonexistent_dev";`
- line 89 `char del_bind[IFNAMSIZ] = "";`
- line 109 `int zero = 0, one = 1;`
- line 133 `int lowat = 65535;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect6_prog.c

## Purpose
`connect6_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2563 bytes across 99 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/stddef.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `SRC_REWRITE_IP6_0`, `SRC_REWRITE_IP6_1`, `SRC_REWRITE_IP6_2`, `SRC_REWRITE_IP6_3`, `DST_REWRITE_IP6_0`, `DST_REWRITE_IP6_1`, `DST_REWRITE_IP6_2`, `DST_REWRITE_IP6_3`, `DST_REWRITE_PORT6`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`, `bpf_htons`, `bpf_sk_lookup_tcp`, `bpf_sk_lookup_udp`, `bpf_sk_release`.
Attach sections and exported entry points:
- line 27 `SEC("cgroup/connect6")` -> int connect_v6_prog(struct bpf_sock_addr *ctx)
- line 93 `SEC("cgroup/connect6")` -> int connect_v6_deny_prog(struct bpf_sock_addr *ctx)
- line 99 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 28 `connect_v6_prog`: `int connect_v6_prog(struct bpf_sock_addr *ctx)`
- line 94 `connect_v6_deny_prog`: `int connect_v6_deny_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect6`, `cgroup/connect6`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_v6_prog`, `connect_v6_deny_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect6_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port4.c

## Purpose
`connect_force_port4.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1991 bytes across 92 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<stdbool.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf_sockopt_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`, `bpf_htons`, `bpf_sk_storage_get`.
Map/type declarations observed:
- line 25 declares map type `BPF_MAP_TYPE_SK_STORAGE`
Attach sections and exported entry points:
- line 15 `SEC("license")` -> struct svc_addr {
- line 29 `SEC(".maps")` -> int connect4(struct bpf_sock_addr *ctx)
- line 31 `SEC("cgroup/connect4")` -> int connect4(struct bpf_sock_addr *ctx)
- line 61 `SEC("cgroup/getsockname4")` -> int getsockname4(struct bpf_sock_addr *ctx)
- line 75 `SEC("cgroup/getpeername4")` -> int getpeername4(struct bpf_sock_addr *ctx)
Key functions/subprograms:
- line 32 `connect4`: `int connect4(struct bpf_sock_addr *ctx)`
- line 62 `getsockname4`: `int getsockname4(struct bpf_sock_addr *ctx)`
- line 76 `getpeername4`: `int getpeername4(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `cgroup/connect4`, `cgroup/getsockname4`, `cgroup/getpeername4`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect4`, `getsockname4`, `getpeername4`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 17 `__u16 port = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port6.c

## Purpose
`connect_force_port6.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2356 bytes across 103 lines.

## Important APIs, Types, and Functions
- Dependencies: `<string.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<linux/in6.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf_sockopt_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`, `bpf_htons`, `bpf_sk_storage_get`.
Map/type declarations observed:
- line 24 declares map type `BPF_MAP_TYPE_SK_STORAGE`
Attach sections and exported entry points:
- line 14 `SEC("license")` -> struct svc_addr {
- line 28 `SEC(".maps")` -> int connect6(struct bpf_sock_addr *ctx)
- line 30 `SEC("cgroup/connect6")` -> int connect6(struct bpf_sock_addr *ctx)
- line 66 `SEC("cgroup/getsockname6")` -> int getsockname6(struct bpf_sock_addr *ctx)
- line 83 `SEC("cgroup/getpeername6")` -> int getpeername6(struct bpf_sock_addr *ctx)
Key functions/subprograms:
- line 31 `connect6`: `int connect6(struct bpf_sock_addr *ctx)`
- line 67 `getsockname6`: `int getsockname6(struct bpf_sock_addr *ctx)`
- line 84 `getpeername6`: `int getpeername6(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `cgroup/connect6`, `cgroup/getsockname6`, `cgroup/getpeername6`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect6`, `getsockname6`, `getpeername6`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `__u16 port = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_force_port6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_ping.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_ping.c

## Purpose
`connect_ping.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1056 bytes across 53 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<netinet/in.h>`, `<sys/socket.h>`.
- Important macros/constants: `BINDADDR_V6`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`, `bpf_htonl`.
Attach sections and exported entry points:
- line 21 `SEC("cgroup/connect4")` -> int connect_v4_prog(struct bpf_sock_addr *ctx)
- line 37 `SEC("cgroup/connect6")` -> int connect_v6_prog(struct bpf_sock_addr *ctx)
- line 53 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 22 `connect_v4_prog`: `int connect_v4_prog(struct bpf_sock_addr *ctx)`
- line 38 `connect_v6_prog`: `int connect_v6_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect4`, `cgroup/connect6`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_v4_prog`, `connect_v6_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `__u32 do_bind = 0;`
- line 17 `__u32 has_error = 0;`
- line 18 `__u32 invocations_v4 = 0;`
- line 19 `__u32 invocations_v6 = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_unix_prog.c

## Purpose
`connect_unix_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1136 bytes across 45 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- BPF API surface: socket option/address helpers.
- Helper/kfunc calls: `bpf_cast_to_kern_ctx`, `bpf_core_cast`, `bpf_sock_addr_set_sun_path`.
Attach sections and exported entry points:
- line 13 `SEC("cgroup/connect_unix")` -> int connect_unix_prog(struct bpf_sock_addr *ctx)
- line 39 `SEC("cgroup/connect_unix")` -> int connect_unix_deny_prog(struct bpf_sock_addr *ctx)
- line 45 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `connect_unix_prog`: `int connect_unix_prog(struct bpf_sock_addr *ctx)`
- line 40 `connect_unix_deny_prog`: `int connect_unix_deny_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/connect_unix`, `cgroup/connect_unix`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `connect_unix_prog`, `connect_unix_deny_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `__u8 SERVUN_REWRITE_ADDRESS[] = "\0bpf_cgroup_unix_test_rewrite";`
- line 20 `int ret;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/connect_unix_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern.c

## Purpose
`core_kern.c` is a CO-RE runtime program validating BTF type reads, trace/fentry/fexit attachment, and prototype relocations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3034 bytes across 120 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_core_read.h>`, `"test_jhash.h"`.
- Important macros/constants: `ATTR`, `C`, `C30`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_core_type_exists`, `bpf_get_prandom_u32`, `bpf_map_lookup_elem`.
Map/type declarations observed:
- line 13 declares map type `BPF_MAP_TYPE_ARRAY`
- line 20 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 17 `SEC(".maps")` -> struct {
- line 24 `SEC(".maps")` -> static __noinline int randmap(int v, const struct net_device *dev)
- line 42 `SEC("tp_btf/xdp_devmap_xmit")` -> int BPF_PROG(tp_xdp_devmap_xmit_multi, const struct net_device
- line 50 `SEC("fentry/eth_type_trans")` -> int BPF_PROG(fentry_eth_type_trans, struct sk_buff *skb,
- line 57 `SEC("fexit/eth_type_trans")` -> int BPF_PROG(fexit_eth_type_trans, struct sk_buff *skb,
- line 74 `SEC("tc")` -> int balancer_ingress(struct __sk_buff *ctx)
- line 110 `SEC("raw_tracepoint/sys_enter")` -> int core_relo_proto(void *ctx)
- line 120 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 26 `randmap`: `static __noinline int randmap(int v, const struct net_device *dev)`
- line 43 `BPF_PROG`: `int BPF_PROG(tp_xdp_devmap_xmit_multi, const struct net_device`
- line 51 `BPF_PROG`: `int BPF_PROG(fentry_eth_type_trans, struct sk_buff *skb,`
- line 58 `BPF_PROG`: `int BPF_PROG(fexit_eth_type_trans, struct sk_buff *skb,`
- line 75 `balancer_ingress`: `int balancer_ingress(struct __sk_buff *ctx)`
- line 111 `core_relo_proto`: `int core_relo_proto(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `.maps`, `tp_btf/xdp_devmap_xmit`, `fentry/eth_type_trans`, `fexit/eth_type_trans`, `tc`, `raw_tracepoint/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `randmap`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `balancer_ingress`, `core_relo_proto`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 30 `int *val;`
- line 64 `volatile const int never;`
- line 67 `int len;`
- line 79 `void *ptr;`
- line 80 `int nh_off, i = 0;`
- line 108 `int proto_out[3];`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern_overflow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern_overflow.c

## Purpose
`core_kern_overflow.c` is a CO-RE runtime program validating BTF type reads, trace/fentry/fexit attachment, and prototype relocations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 522 bytes across 22 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_core_read.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_core_type_exists`.
Attach sections and exported entry points:
- line 14 `SEC("raw_tracepoint/sys_enter")` -> int core_relo_proto(void *ctx)
- line 22 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 15 `core_relo_proto`: `int core_relo_proto(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `raw_tracepoint/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `core_relo_proto`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `int proto_out;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_kern_overflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_reloc_types.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_reloc_types.h

## Purpose
`core_reloc_types.h` is a CO-RE fixture header defining source and target BTF shapes for field, enum, type-id, and type-based relocations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 27717 bytes across 1363 lines.

## Important APIs, Types, and Functions
- Dependencies: `<stdint.h>`, `<stdbool.h>`.
- Important macros/constants: `__bpf_aligned`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Key functions/subprograms:
- line 4 `preserce_ptr_sz_fn`: `void preserce_ptr_sz_fn(long x) {}`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
There is no direct BPF attach entry in this file. Control flow is compile-time inclusion: other objects consume its declarations/macros/types so that clang, BTF generation, libbpf CO-RE relocation, or the verifier sees the intended shapes.
Local flow is organized through `preserce_ptr_sz_fn`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int valid[10];`
- line 15 `int comm_len;`
- line 16 `bool local_task_struct_matches;`
- line 24 `long long len;`
- line 25 `long long off;`
- line 26 `int read_ctx_sz;`
- line 27 `bool read_ctx_exists;`
- line 28 `bool buf_exists;`
- line 29 `bool len_exists;`
- line 30 `bool off_exists;`
- plus 248 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Signal is compile/load-time BTF or declaration availability for other selftest objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/core_reloc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_common.h

## Purpose
`cpumask_common.h` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4228 bytes across 129 lines.

## Important APIs, Types, and Functions
- Dependencies: `"errno.h"`, `<stdbool.h>`.
- Important macros/constants: `_CPUMASK_COMMON_H`, `CPUMASK_KPTR_FIELDS_MAX`, `private`.
- BPF API surface: map lookup/update/delete or map-side state; cpumask ownership/query/mutation kfuncs.
- Helper/kfunc calls: `bpf_cpumask_acquire`, `bpf_cpumask_and`, `bpf_cpumask_any_and_distribute`, `bpf_cpumask_any_distribute`, `bpf_cpumask_clear`, `bpf_cpumask_clear_cpu`, `bpf_cpumask_copy`, `bpf_cpumask_create`, `bpf_cpumask_empty`, `bpf_cpumask_equal`, `bpf_cpumask_first`, `bpf_cpumask_first_and`, `bpf_cpumask_first_zero`, `bpf_cpumask_full`, `bpf_cpumask_intersects`, `bpf_cpumask_or`, `bpf_cpumask_populate`, `bpf_cpumask_release`, plus 13 more.
Map/type declarations observed:
- line 25 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 17 `SEC("#define private(name) SEC(".bss." #name) __attribute__((aligned(8)))")` -> private(MASK) static struct bpf_cpumask __kptr * global_mask;
- line 29 `SEC(".maps")` -> struct bpf_cpumask *bpf_cpumask_create(void) __ksym __weak;
Key functions/subprograms:
- line 36 `bpf_cpumask_first_and`: `u32 bpf_cpumask_first_and(const struct cpumask *src1,`
- line 45 `bpf_cpumask_and`: `bool bpf_cpumask_and(struct bpf_cpumask *cpumask,`
- line 48 `bpf_cpumask_or`: `void bpf_cpumask_or(struct bpf_cpumask *cpumask,`
- line 51 `bpf_cpumask_xor`: `void bpf_cpumask_xor(struct bpf_cpumask *cpumask,`
- line 61 `bpf_cpumask_any_and_distribute`: `u32 bpf_cpumask_any_and_distribute(const struct cpumask *src1,`
- line 100 `cpumask_map_insert`: `static inline int cpumask_map_insert(struct bpf_cpumask *mask)`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `#define private(name) SEC(".bss." #name) __attribute__((aligned(8)))`, `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_cpumask_first_and`, `bpf_cpumask_and`, `bpf_cpumask_or`, `bpf_cpumask_xor`, `bpf_cpumask_any_and_distribute`, `cpumask_map_insert`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 15 `int err;`
- line 95 `u32 key = 0;`
- line 103 `long status;`
- line 105 `u32 key = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Cpumask cases depend on trusted pointer tracking, nullability, and exact ownership/release rules.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_failure.c

## Purpose
`cpumask_failure.c` is a negative cpumask kfunc verifier suite for trusted pointer, nullable, ownership, and reference rules. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 5774 bytes across 262 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `"bpf_misc.h"`, `"cpumask_common.h"`.
- BPF API surface: cpumask ownership/query/mutation kfuncs.
- Helper/kfunc calls: `bpf_cpumask_acquire`, `bpf_cpumask_create`, `bpf_cpumask_empty`, `bpf_cpumask_populate`, `bpf_cpumask_release`, `bpf_cpumask_set_cpu`, `bpf_cpumask_test_cpu`, `bpf_kptr_xchg`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`.
Attach sections and exported entry points:
- line 11 `SEC("license")` -> struct kptr_nested_array_2 {
- line 34 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_alloc_no_release, struct task_struct *task, u64 clone_flags)
- line 47 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_alloc_double_release, struct task_struct *task, u64 clone_flags)
- line 62 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_acquire_wrong_cpumask, struct task_struct *task, u64 clone_flags)
- line 75 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_mutate_cpumask, struct task_struct *task, u64 clone_flags)
- line 85 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_insert_remove_no_release, struct task_struct *task, u64 clone_flags)
- line 109 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_cpumask_null, struct task_struct *task, u64 clone_flags)
- line 119 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_global_mask_out_of_rcu, struct task_struct *task, u64 clone_flags)
- line 153 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_global_mask_no_null_check, struct task_struct *task, u64 clone_flags)
- line 181 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_global_mask_rcu_no_null_check, struct task_struct *task, u64 clone_flags)
- line 206 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_invalid_nested_array, struct task_struct *task, u64 clone_flags)
- line 226 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_populate_invalid_destination, struct task_struct *task, u64 clone_flags)
- plus 1 more entries of the same pattern.
Key functions/subprograms:
- line 35 `__msg`: `__failure __msg("Unreleased reference")`
- line 36 `BPF_PROG`: `int BPF_PROG(test_alloc_no_release, struct task_struct *task, u64 clone_flags)`
- line 48 `__msg`: `__failure __msg("NULL pointer passed to trusted arg0")`
- line 49 `BPF_PROG`: `int BPF_PROG(test_alloc_double_release, struct task_struct *task, u64 clone_flags)`
- line 63 `__msg`: `__failure __msg("must be referenced")`
- line 64 `BPF_PROG`: `int BPF_PROG(test_acquire_wrong_cpumask, struct task_struct *task, u64 clone_flags)`
- line 76 `__msg`: `__failure __msg("bpf_cpumask_set_cpu args#1 expected pointer to STRUCT bpf_cpumask")`
- line 77 `BPF_PROG`: `int BPF_PROG(test_mutate_cpumask, struct task_struct *task, u64 clone_flags)`
- line 86 `__msg`: `__failure __msg("Unreleased reference")`
- line 87 `BPF_PROG`: `int BPF_PROG(test_insert_remove_no_release, struct task_struct *task, u64 clone_flags)`
- line 110 `__msg`: `__failure __msg("NULL pointer passed to trusted arg0")`
- line 111 `BPF_PROG`: `int BPF_PROG(test_cpumask_null, struct task_struct *task, u64 clone_flags)`
- plus 12 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `__msg`, `BPF_PROG`, `__msg`, `BPF_PROG`, `__msg`, `BPF_PROG`, `__msg`, `BPF_PROG` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 231 `u64 bits;`
- line 232 `int ret;`
- line 247 `int ret;`
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Cpumask cases depend on trusted pointer tracking, nullability, and exact ownership/release rules.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `Unreleased reference`, `NULL pointer passed to trusted arg0`, `must be referenced`, `bpf_cpumask_set_cpu args#1 expected pointer to STRUCT bpf_cpumask`, `Unreleased reference`, plus 7 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_success.c

## Purpose
`cpumask_success.c` is a positive cpumask kfunc suite for allocation, mutation, map storage, kptr exchange, and RCU-safe use. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 18458 bytes across 890 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `"bpf_misc.h"`, `"cpumask_common.h"`.
- Important macros/constants: `CPUMASK_TEST_MASKLEN`.
- BPF API surface: task/cgroup/time/function metadata helpers; cpumask ownership/query/mutation kfuncs.
- Helper/kfunc calls: `bpf_cpumask_and`, `bpf_cpumask_any_and_distribute`, `bpf_cpumask_any_distribute`, `bpf_cpumask_clear`, `bpf_cpumask_clear_cpu`, `bpf_cpumask_copy`, `bpf_cpumask_create`, `bpf_cpumask_empty`, `bpf_cpumask_equal`, `bpf_cpumask_first`, `bpf_cpumask_first_and`, `bpf_cpumask_first_zero`, `bpf_cpumask_full`, `bpf_cpumask_intersects`, `bpf_cpumask_or`, `bpf_cpumask_populate`, `bpf_cpumask_release`, `bpf_cpumask_set_cpu`, plus 13 more.
Attach sections and exported entry points:
- line 11 `SEC("license")` -> int pid, nr_cpus;
- line 138 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_alloc_free_cpumask, struct task_struct *task, u64 clone_flags)
- line 154 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_set_clear_cpu, struct task_struct *task, u64 clone_flags)
- line 183 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_setall_clear_cpu, struct task_struct *task, u64 clone_flags)
- line 212 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_first_firstzero_cpu, struct task_struct *task, u64 clone_flags)
- line 251 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_firstand_nocpu, struct task_struct *task, u64 clone_flags)
- line 283 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_test_and_set_clear, struct task_struct *task, u64 clone_flags)
- line 315 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_and_or_xor, struct task_struct *task, u64 clone_flags)
- line 362 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_intersects_subset, struct task_struct *task, u64 clone_flags)
- line 404 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_copy_any_anyand, struct task_struct *task, u64 clone_flags)
- line 458 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_insert_leave, struct task_struct *task, u64 clone_flags)
- line 473 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(test_insert_remove_release, struct task_struct *task, u64 clone_flags)
- plus 12 more entries of the same pattern.
Key functions/subprograms:
- line 88 `is_test_task`: `static bool is_test_task(void)`
- line 95 `create_cpumask_set`: `static bool create_cpumask_set(struct bpf_cpumask **out1,`
- line 139 `BPF_PROG`: `int BPF_PROG(test_alloc_free_cpumask, struct task_struct *task, u64 clone_flags)`
- line 155 `BPF_PROG`: `int BPF_PROG(test_set_clear_cpu, struct task_struct *task, u64 clone_flags)`
- line 184 `BPF_PROG`: `int BPF_PROG(test_setall_clear_cpu, struct task_struct *task, u64 clone_flags)`
- line 213 `BPF_PROG`: `int BPF_PROG(test_first_firstzero_cpu, struct task_struct *task, u64 clone_flags)`
- line 252 `BPF_PROG`: `int BPF_PROG(test_firstand_nocpu, struct task_struct *task, u64 clone_flags)`
- line 284 `BPF_PROG`: `int BPF_PROG(test_test_and_set_clear, struct task_struct *task, u64 clone_flags)`
- line 316 `BPF_PROG`: `int BPF_PROG(test_and_or_xor, struct task_struct *task, u64 clone_flags)`
- line 363 `BPF_PROG`: `int BPF_PROG(test_intersects_subset, struct task_struct *task, u64 clone_flags)`
- line 405 `BPF_PROG`: `int BPF_PROG(test_copy_any_anyand, struct task_struct *task, u64 clone_flags)`
- line 459 `BPF_PROG`: `int BPF_PROG(test_insert_leave, struct task_struct *task, u64 clone_flags)`
- plus 14 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask`, `tp_btf/task_newtask` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `is_test_task`, `create_cpumask_set`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int pid, nr_cpus;`
- line 25 `int dummy;`
- line 35 `int dummy;`
- line 40 `int dummy;`
- line 45 `long dummy;`
- line 50 `long dummy[2];`
- line 55 `int dummy;`
- line 60 `long dummy;`
- line 65 `long dummy[2];`
- line 70 `int dummy;`
- plus 13 more entries of the same pattern.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Cpumask cases depend on trusted pointer tracking, nullability, and exact ownership/release rules.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/cpumask_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_basic.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_basic.c

## Purpose
`crypto_basic.c` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1141 bytes across 68 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`, `"crypto_common.h"`.
- BPF API surface: crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_acquire`, `bpf_crypto_ctx_create`, `bpf_crypto_ctx_release`.
Attach sections and exported entry points:
- line 12 `SEC("syscall")` -> int crypto_release(void *ctx)
- line 38 `SEC("syscall")` -> int crypto_acquire(void *ctx)
- line 68 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `crypto_release`: `int crypto_release(void *ctx)`
- line 39 `__msg`: `__failure __msg("Unreleased reference")`
- line 40 `crypto_acquire`: `int crypto_acquire(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `syscall`, `syscall`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `crypto_release`, `__msg`, `crypto_acquire`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `int status;`
- line 22 `int err = 0;`
- line 48 `int err = 0;`
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `Unreleased reference`.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_basic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_bench.c

## Purpose
`crypto_bench.c` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2011 bytes across 107 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `"bpf_tracing_net.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`, `"crypto_common.h"`.
- BPF API surface: dynptr construction/access/mutation helpers; crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_create`, `bpf_crypto_decrypt`, `bpf_crypto_encrypt`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`.
Attach sections and exported entry points:
- line 21 `SEC("syscall")` -> int crypto_setup(void *args)
- line 55 `SEC("tc")` -> int crypto_encrypt(struct __sk_buff *skb)
- line 83 `SEC("tc")` -> int crypto_decrypt(struct __sk_buff *skb)
- line 107 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 22 `crypto_setup`: `int crypto_setup(void *args)`
- line 56 `crypto_encrypt`: `int crypto_encrypt(struct __sk_buff *skb)`
- line 84 `crypto_decrypt`: `int crypto_decrypt(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `syscall`, `tc`, `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `crypto_setup`, `crypto_encrypt`, `crypto_decrypt`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `const volatile unsigned int len = 16;`
- line 14 `char cipher[128] = {};`
- line 15 `u32 key_len, authsize;`
- line 16 `char dst[256] = {};`
- line 17 `u8 key[256] = {};`
- line 18 `long hits = 0;`
- line 19 `int status;`
- line 30 `int err = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_common.h

## Purpose
`crypto_common.h` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1735 bytes across 66 lines.

## Important APIs, Types, and Functions
- Dependencies: `"errno.h"`, `<stdbool.h>`.
- Important macros/constants: `_CRYPTO_COMMON_H`.
- BPF API surface: map lookup/update/delete or map-side state; crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_acquire`, `bpf_crypto_ctx_create`, `bpf_crypto_ctx_release`, `bpf_crypto_decrypt`, `bpf_crypto_encrypt`, `bpf_kptr_xchg`, `bpf_map_lookup_elem`, `bpf_map_update_elem`.
Map/type declarations observed:
- line 24 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 28 `SEC(".maps")` -> static inline struct __crypto_ctx_value *crypto_ctx_value_lookup(void)
Key functions/subprograms:
- line 14 `bpf_crypto_encrypt`: `int bpf_crypto_encrypt(struct bpf_crypto_ctx *ctx, const struct bpf_dynptr *src,`
- line 16 `bpf_crypto_decrypt`: `int bpf_crypto_decrypt(struct bpf_crypto_ctx *ctx, const struct bpf_dynptr *src,`
- line 37 `crypto_ctx_insert`: `static inline int crypto_ctx_insert(struct bpf_crypto_ctx *ctx)`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_crypto_encrypt`, `bpf_crypto_decrypt`, `crypto_ctx_insert`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 32 `u32 key = 0;`
- line 41 `u32 key = 0;`
- line 42 `int err;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_sanity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_sanity.c

## Purpose
`crypto_sanity.c` is a BPF crypto kfunc selftest for transform setup and encrypt/decrypt operations. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3848 bytes across 179 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `"bpf_tracing_net.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`, `"crypto_common.h"`.
- BPF API surface: dynptr construction/access/mutation helpers; crypto transform kfuncs.
- Helper/kfunc calls: `bpf_crypto_ctx_create`, `bpf_crypto_decrypt`, `bpf_crypto_encrypt`, `bpf_dynptr_adjust`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`, `bpf_skb_load_bytes`, `bpf_skb_pull_data`.
Attach sections and exported entry points:
- line 53 `SEC("syscall")` -> int skb_crypto_setup(void *ctx)
- line 85 `SEC("tc")` -> int decrypt_sanity(struct __sk_buff *skb)
- line 132 `SEC("tc")` -> int encrypt_sanity(struct __sk_buff *skb)
- line 179 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 20 `skb_dynptr_validate`: `static int skb_dynptr_validate(struct __sk_buff *skb, struct bpf_dynptr *psrc)`
- line 54 `skb_crypto_setup`: `int skb_crypto_setup(void *ctx)`
- line 86 `decrypt_sanity`: `int decrypt_sanity(struct __sk_buff *skb)`
- line 133 `encrypt_sanity`: `int encrypt_sanity(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `syscall`, `tc`, `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `skb_dynptr_validate`, `skb_crypto_setup`, `decrypt_sanity`, `encrypt_sanity`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 14 `u16 udp_test_port = 7777;`
- line 15 `u32 authsize, key_len;`
- line 16 `char algo[128] = {};`
- line 17 `char dst[16] = {}, dst_bad[8] = {};`
- line 18 `int status;`
- line 24 `u32 offset;`
- line 62 `int err;`
- line 91 `int err;`
- line 138 `int err;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.
- Crypto tests depend on algorithm availability and balanced acquire/release of crypto contexts.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/crypto_sanity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/csum_diff_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/csum_diff_test.c

## Purpose
`csum_diff_test.c` is a checksum-helper selftest around `bpf_csum_diff`. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1192 bytes across 42 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/types.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `BUFF_SZ`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_csum_diff`.
Attach sections and exported entry points:
- line 19 `SEC("license")` -> int compute_checksum(void *ctx)
- line 21 `SEC("tc")` -> int compute_checksum(void *ctx)
Key functions/subprograms:
- line 22 `compute_checksum`: `int compute_checksum(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `compute_checksum`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `char to_buff[BUFF_SZ];`
- line 12 `const volatile unsigned int to_buff_len = 0;`
- line 13 `char from_buff[BUFF_SZ];`
- line 14 `const volatile unsigned int from_buff_len = 0;`
- line 24 `int to_len_half = to_buff_len / 2;`
- line 25 `int from_len_half = from_buff_len / 2;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/csum_diff_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/decap_sanity.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/decap_sanity.c

## Purpose
`decap_sanity.c` is a packet decapsulation sanity selftest for skb/tunnel metadata changes. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1716 bytes across 68 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `"bpf_tracing_net.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- Important macros/constants: `UDP_TEST_PORT`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_cast_to_kern_ctx`, `bpf_skb_adjust_room`, `bpf_skb_load_bytes`.
Attach sections and exported entry points:
- line 31 `SEC("tc")` -> int decap_sanity(struct __sk_buff *skb)
- line 68 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 16 `skb_headlen`: `static unsigned int skb_headlen(const struct sk_buff *skb)`
- line 21 `skb_headroom`: `static unsigned int skb_headroom(const struct sk_buff *skb)`
- line 26 `skb_checksum_start_offset`: `static int skb_checksum_start_offset(const struct sk_buff *skb)`
- line 32 `decap_sanity`: `int decap_sanity(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `skb_headlen`, `skb_headroom`, `skb_checksum_start_offset`, `decap_sanity`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `bool init_csum_partial = false;`
- line 13 `bool final_csum_none = false;`
- line 14 `bool broken_csum_start = false;`
- line 37 `int err;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/decap_sanity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dev_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dev_cgroup.c

## Purpose
`dev_cgroup.c` is a cgroup device-access policy selftest returning allow or deny from device metadata. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1185 bytes across 59 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<linux/version.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_prog1`, `bpf_trace_printk`.
Attach sections and exported entry points:
- line 12 `SEC("cgroup/dev")` -> int bpf_prog1(struct bpf_cgroup_dev_ctx *ctx)
- line 59 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `bpf_prog1`: `int bpf_prog1(struct bpf_cgroup_dev_ctx *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/dev`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_prog1`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 18 `char fmt[] = " %d:%d \n";`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dev_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dmabuf_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dmabuf_iter.c

## Purpose
`dmabuf_iter.c` is a BPF iterator selftest that emits DMA-BUF metadata through seq output. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2341 bytes across 101 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_core_read.h>`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `DMA_BUF_NAME_LEN`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_core_read`, `bpf_for`, `bpf_for_each`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_probe_read_kernel_str`.
Map/type declarations observed:
- line 13 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 10 `SEC("license")` -> struct {
- line 17 `SEC(".maps")` -> /*
- line 30 `SEC("iter/dmabuf")` -> int dmabuf_collector(struct bpf_iter__dmabuf *ctx)
- line 62 `SEC("syscall")` -> int iter_dmabuf_for_each(const void *ctx)
Key functions/subprograms:
- line 23 `sanitize_string`: `static void sanitize_string(char *src, size_t size)`
- line 31 `dmabuf_collector`: `int dmabuf_collector(struct bpf_iter__dmabuf *ctx)`
- line 63 `iter_dmabuf_for_each`: `int iter_dmabuf_for_each(const void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `iter/dmabuf`, `syscall`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `sanitize_string`, `dmabuf_collector`, `iter_dmabuf_for_each`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 38 `char name[DMA_BUF_NAME_LEN] = {'\0'};`
- line 68 `char name[DMA_BUF_NAME_LEN];`
- line 70 `bool *found;`
- line 71 `long len;`
- line 72 `int i;`
- line 94 `bool t = true;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- CO-RE/BTF fixtures are sensitive to type names, anonymous type shape, enum values, typedef spelling, and field layout.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dmabuf_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_fail.c

## Purpose
`dummy_st_ops_fail.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 751 bytes across 27 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> int BPF_PROG(test_unsupported_field_sleepable,
- line 12 `SEC("struct_ops.s/test_2")` -> int BPF_PROG(test_unsupported_field_sleepable,
- line 22 `SEC(".struct_ops")` -> struct bpf_dummy_ops dummy_1 = {
Key functions/subprograms:
- line 13 `__msg`: `__failure __msg("attach to unsupported member test_2 of struct bpf_dummy_ops")`
- line 14 `BPF_PROG`: `int BPF_PROG(test_unsupported_field_sleepable,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops.s/test_2`, `.struct_ops`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `__msg`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `attach to unsupported member test_2 of struct bpf_dummy_ops`.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_success.c

## Purpose
`dummy_st_ops_success.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1311 bytes across 56 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test_1, struct bpf_dummy_ops_state *state)
- line 9 `SEC("struct_ops/test_1")` -> int BPF_PROG(test_1, struct bpf_dummy_ops_state *state)
- line 33 `SEC("struct_ops/test_2")` -> int BPF_PROG(test_2, struct bpf_dummy_ops_state *state, int a1, unsigned short a2,
- line 45 `SEC("struct_ops.s/test_sleepable")` -> int BPF_PROG(test_sleepable, struct bpf_dummy_ops_state *state)
- line 51 `SEC(".struct_ops")` -> struct bpf_dummy_ops dummy_1 = {
Key functions/subprograms:
- line 10 `BPF_PROG`: `int BPF_PROG(test_1, struct bpf_dummy_ops_state *state)`
- line 20 `volatile`: `asm volatile (`
- line 34 `BPF_PROG`: `int BPF_PROG(test_2, struct bpf_dummy_ops_state *state, int a1, unsigned short a2,`
- line 46 `BPF_PROG`: `int BPF_PROG(test_sleepable, struct bpf_dummy_ops_state *state)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops/test_1`, `struct_ops/test_2`, `struct_ops.s/test_sleepable`, `.struct_ops`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `volatile`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `int ret;`
- line 31 `__u64 test_2_args[5];`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dummy_st_ops_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_fail.c

## Purpose
`dynptr_fail.c` is a negative dynptr verifier suite covering invalid dynptr state, bounds, helper argument, and reference-lifetime cases. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 45226 bytes across 2110 lines.

## Important APIs, Types, and Functions
- Dependencies: `<errno.h>`, `<string.h>`, `<stdbool.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<linux/if_ether.h>`, `"bpf_misc.h"`, `"bpf_kfuncs.h"`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers; bounded callback iteration.
- Helper/kfunc calls: `bpf_dynptr_adjust`, `bpf_dynptr_clone`, `bpf_dynptr_data`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`, `bpf_dynptr_from_skb_meta`, `bpf_dynptr_from_xdp`, `bpf_dynptr_is_null`, `bpf_dynptr_is_rdonly`, `bpf_dynptr_read`, `bpf_dynptr_size`, `bpf_dynptr_slice`, `bpf_dynptr_slice_rdwr`, `bpf_dynptr_write`, `bpf_get_current_comm`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, plus 8 more.
Map/type declarations observed:
- line 22 declares map type `BPF_MAP_TYPE_ARRAY`
- line 29 declares map type `BPF_MAP_TYPE_ARRAY`
- line 36 declares map type `BPF_MAP_TYPE_ARRAY`
- line 43 declares map type `BPF_MAP_TYPE_ARRAY`
- line 56 declares map type `BPF_MAP_TYPE_RINGBUF`
Attach sections and exported entry points:
- line 14 `SEC("license")` -> struct test_info {
- line 26 `SEC(".maps")` -> struct {
- line 33 `SEC(".maps")` -> struct {
- line 40 `SEC(".maps")` -> struct {
- line 47 `SEC(".maps")` -> struct sample {
- line 58 `SEC(".maps")` -> int err, val;
- line 80 `SEC("?raw_tp")` -> int ringbuf_missing_release1(void *ctx)
- line 93 `SEC("?raw_tp")` -> int ringbuf_missing_release2(void *ctx)
- line 129 `SEC("?raw_tp")` -> int ringbuf_missing_release_callback(void *ctx)
- line 138 `SEC("?raw_tp")` -> int ringbuf_release_uninit_dynptr(void *ctx)
- line 151 `SEC("?raw_tp")` -> int use_after_invalid(void *ctx)
- line 171 `SEC("?raw_tp")` -> int ringbuf_invalid_api(void *ctx)
- plus 85 more entries of the same pattern.
Key functions/subprograms:
- line 62 `get_map_val_dynptr`: `static int get_map_val_dynptr(struct bpf_dynptr *ptr)`
- line 81 `__msg`: `__failure __msg("Unreleased reference id=2")`
- line 82 `ringbuf_missing_release1`: `int ringbuf_missing_release1(void *ctx)`
- line 94 `__msg`: `__failure __msg("Unreleased reference id=4")`
- line 95 `ringbuf_missing_release2`: `int ringbuf_missing_release2(void *ctx)`
- line 117 `missing_release_callback_fn`: `static int missing_release_callback_fn(__u32 index, void *data)`
- line 130 `__msg`: `__failure __msg("Unreleased reference id")`
- line 131 `ringbuf_missing_release_callback`: `int ringbuf_missing_release_callback(void *ctx)`
- line 139 `__msg`: `__failure __msg("arg 1 is an unacquired reference")`
- line 140 `ringbuf_release_uninit_dynptr`: `int ringbuf_release_uninit_dynptr(void *ctx)`
- line 152 `__msg`: `__failure __msg("Expected an initialized dynptr as arg #2")`
- line 153 `use_after_invalid`: `int use_after_invalid(void *ctx)`
- plus 177 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `?raw_tp`, `?raw_tp` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `get_map_val_dynptr`, `__msg`, `ringbuf_missing_release1`, `__msg`, `ringbuf_missing_release2`, `missing_release_callback_fn`, `__msg`, `ringbuf_missing_release_callback` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 17 `int x;`
- line 50 `int pid;`
- line 51 `long value;`
- line 52 `char comm[16];`
- line 60 `int err, val;`
- line 64 `__u32 key = 0, *map_val;`
- line 156 `char read_data[64];`
- line 199 `int key = 0;`
- line 217 `int key = 0;`
- line 235 `void *data;`
- plus 47 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Uses `__success` annotations; a passing test is successful verifier load despite nearby edge cases.
- Expected verifier messages include `Unreleased reference id=2`, `Unreleased reference id=4`, `Unreleased reference id`, `arg 1 is an unacquired reference`, `Expected an initialized dynptr as arg #2`, plus 81 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_success.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_success.c

## Purpose
`dynptr_success.c` is a positive dynptr suite covering local, ring-buffer, skb, xdp, clone, copy, adjust, memset, and probe-read cases. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 25338 bytes across 1137 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<string.h>`, `<stdbool.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"errno.h"`.
- Important macros/constants: `PAGE_SIZE_64K`, `DYNPTR_MEMSET_VAL`, `min_t`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers; bounded callback iteration.
- Helper/kfunc calls: `bpf_copy_data_from_user_task`, `bpf_copy_data_from_user_task_str`, `bpf_copy_from_user_task_dynptr`, `bpf_copy_from_user_task_str_dynptr`, `bpf_dynptr_adjust`, `bpf_dynptr_clone`, `bpf_dynptr_copy`, `bpf_dynptr_data`, `bpf_dynptr_from_mem`, `bpf_dynptr_from_skb`, `bpf_dynptr_from_skb_meta`, `bpf_dynptr_from_xdp`, `bpf_dynptr_is_null`, `bpf_dynptr_is_rdonly`, `bpf_dynptr_memset`, `bpf_dynptr_read`, `bpf_dynptr_size`, `bpf_dynptr_slice`, plus 15 more.
Map/type declarations observed:
- line 26 declares map type `BPF_MAP_TYPE_RINGBUF`
- line 31 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 14 `SEC("license")` -> int pid, err, val;
- line 28 `SEC(".maps")` -> struct {
- line 35 `SEC(".maps")` -> int test_read_write(void *ctx)
- line 37 `SEC("?tp/syscalls/sys_enter_nanosleep")` -> int test_read_write(void *ctx)
- line 68 `SEC("?tp/syscalls/sys_enter_nanosleep")` -> int test_dynptr_data(void *ctx)
- line 138 `SEC("?tp/syscalls/sys_enter_nanosleep")` -> int test_ringbuf(void *ctx)
- line 171 `SEC("?cgroup_skb/egress")` -> int test_skb_readonly(struct __sk_buff *skb)
- line 193 `SEC("?cgroup_skb/egress")` -> int test_dynptr_skb_data(struct __sk_buff *skb)
- line 214 `SEC("?tc")` -> int test_dynptr_skb_meta_data(struct __sk_buff *skb)
- line 237 `SEC("?tc")` -> int test_dynptr_skb_meta_flags(struct __sk_buff *skb)
- line 269 `SEC("tp/syscalls/sys_enter_nanosleep")` -> int test_adjust(void *ctx)
- line 321 `SEC("tp/syscalls/sys_enter_nanosleep")` -> int test_adjust_err(void *ctx)
- plus 25 more entries of the same pattern.
Key functions/subprograms:
- line 38 `test_read_write`: `int test_read_write(void *ctx)`
- line 69 `test_dynptr_data`: `int test_dynptr_data(void *ctx)`
- line 123 `ringbuf_callback`: `static int ringbuf_callback(__u32 index, void *data)`
- line 139 `test_ringbuf`: `int test_ringbuf(void *ctx)`
- line 172 `test_skb_readonly`: `int test_skb_readonly(struct __sk_buff *skb)`
- line 194 `test_dynptr_skb_data`: `int test_dynptr_skb_data(struct __sk_buff *skb)`
- line 215 `test_dynptr_skb_meta_data`: `int test_dynptr_skb_meta_data(struct __sk_buff *skb)`
- line 238 `test_dynptr_skb_meta_flags`: `int test_dynptr_skb_meta_flags(struct __sk_buff *skb)`
- line 270 `test_adjust`: `int test_adjust(void *ctx)`
- line 322 `test_adjust_err`: `int test_adjust_err(void *ctx)`
- line 380 `test_zero_size_dynptr`: `int test_zero_size_dynptr(void *ctx)`
- line 430 `test_dynptr_is_null`: `int test_dynptr_is_null(void *ctx)`
- plus 32 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `?tp/syscalls/sys_enter_nanosleep`, `?tp/syscalls/sys_enter_nanosleep`, `?tp/syscalls/sys_enter_nanosleep`, `?cgroup_skb/egress`, `?cgroup_skb/egress` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_read_write`, `test_dynptr_data`, `ringbuf_callback`, `test_ringbuf`, `test_skb_readonly`, `test_dynptr_skb_data`, `test_dynptr_skb_meta_data`, `test_dynptr_skb_meta_flags` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `int pid, err, val;`
- line 19 `int pid;`
- line 20 `int seq;`
- line 21 `long value;`
- line 22 `char comm[16];`
- line 40 `char write_data[64] = "hello there, world!!";`
- line 41 `char read_data[64] = {};`
- line 43 `int i;`
- line 71 `__u32 key = 0, val = 235, *map_val;`
- line 73 `__u32 map_val_size;`
- plus 55 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/dynptr_success.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/empty_skb.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/empty_skb.c

## Purpose
`empty_skb.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 817 bytes across 44 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_clone_redirect`, `bpf_skb_adjust_room`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> int ifindex;
- line 11 `SEC("lwt_xmit")` -> int redirect_ingress(struct __sk_buff *skb)
- line 18 `SEC("lwt_xmit")` -> int redirect_egress(struct __sk_buff *skb)
- line 25 `SEC("tc")` -> int tc_redirect_ingress(struct __sk_buff *skb)
- line 32 `SEC("tc")` -> int tc_redirect_egress(struct __sk_buff *skb)
- line 39 `SEC("tc")` -> int tc_adjust_room(struct __sk_buff *skb)
Key functions/subprograms:
- line 12 `redirect_ingress`: `int redirect_ingress(struct __sk_buff *skb)`
- line 19 `redirect_egress`: `int redirect_egress(struct __sk_buff *skb)`
- line 26 `tc_redirect_ingress`: `int tc_redirect_ingress(struct __sk_buff *skb)`
- line 33 `tc_redirect_egress`: `int tc_redirect_egress(struct __sk_buff *skb)`
- line 40 `tc_adjust_room`: `int tc_adjust_room(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `lwt_xmit`, `lwt_xmit`, `tc`, `tc`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `redirect_ingress`, `redirect_egress`, `tc_redirect_ingress`, `tc_redirect_egress`, `tc_adjust_room`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 8 `int ifindex;`
- line 9 `int ret;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/empty_skb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_exit.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_exit.c

## Purpose
`epilogue_exit.c` is a struct_ops epilogue selftest covering return-value handling through direct calls, subprograms, or tail calls. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1940 bytes across 82 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"../test_kmods/bpf_testmod.h"`, `"../test_kmods/bpf_testmod_kfunc.h"`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_kfunc_st_ops_test_epilogue`.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> /* save __u64 *ctx to stack */
- line 42 `SEC("struct_ops/test_epilogue_exit")` -> {
- line 61 `SEC(".struct_ops.link")` -> struct bpf_testmod_st_ops epilogue_exit = {
- line 66 `SEC("syscall")` -> int syscall_epilogue_exit0(void *ctx)
- line 75 `SEC("syscall")` -> int syscall_epilogue_exit1(void *ctx)
Key functions/subprograms:
- line 43 `test_epilogue_exit`: `__naked int test_epilogue_exit(void)`
- line 45 `volatile`: `asm volatile (`
- line 68 `syscall_epilogue_exit0`: `int syscall_epilogue_exit0(void *ctx)`
- line 77 `syscall_epilogue_exit1`: `int syscall_epilogue_exit1(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops/test_epilogue_exit`, `.struct_ops.link`, `syscall`, `syscall`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_epilogue_exit`, `volatile`, `syscall_epilogue_exit0`, `syscall_epilogue_exit1`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Uses `__success` annotations; a passing test is successful verifier load despite nearby edge cases.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_tailcall.c

## Purpose
`epilogue_tailcall.c` is a struct_ops epilogue selftest covering return-value handling through direct calls, subprograms, or tail calls. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1323 bytes across 58 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"../test_kmods/bpf_testmod.h"`, `"../test_kmods/bpf_testmod_kfunc.h"`.
- BPF API surface: program-array dispatch.
- Helper/kfunc calls: `bpf_kfunc_st_ops_test_epilogue`, `bpf_tail_call`.
Map/type declarations observed:
- line 26 declares map type `BPF_MAP_TYPE_PROG_ARRAY`
Attach sections and exported entry points:
- line 10 `SEC("license")` -> static __noinline __used int subprog(struct st_ops_args *args)
- line 18 `SEC("struct_ops/test_epilogue_subprog")` -> int BPF_PROG(test_epilogue_subprog, struct st_ops_args *args)
- line 31 `SEC(".maps")` -> .values = {
- line 37 `SEC("struct_ops/test_epilogue_tailcall")` -> int test_epilogue_tailcall(unsigned long long *ctx)
- line 44 `SEC(".struct_ops.link")` -> struct bpf_testmod_st_ops epilogue_tailcall = {
- line 49 `SEC(".struct_ops.link")` -> struct bpf_testmod_st_ops epilogue_subprog = {
- line 54 `SEC("syscall")` -> int syscall_epilogue_tailcall(struct st_ops_args *args)
Key functions/subprograms:
- line 12 `subprog`: `static __noinline __used int subprog(struct st_ops_args *args)`
- line 19 `BPF_PROG`: `int BPF_PROG(test_epilogue_subprog, struct st_ops_args *args)`
- line 38 `test_epilogue_tailcall`: `int test_epilogue_tailcall(unsigned long long *ctx)`
- line 55 `syscall_epilogue_tailcall`: `int syscall_epilogue_tailcall(struct st_ops_args *args)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `struct_ops/test_epilogue_subprog`, `.maps`, `struct_ops/test_epilogue_tailcall`, `.struct_ops.link`, `.struct_ops.link`, `syscall`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `subprog`, `BPF_PROG`, `test_epilogue_tailcall`, `syscall_epilogue_tailcall`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/epilogue_tailcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/err.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/err.h

## Purpose
`err.h` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 592 bytes across 28 lines.

## Important APIs, Types, and Functions
- Dependencies: no include directives.
- Important macros/constants: `__ERR_H__`, `MAX_ERRNO`, `IS_ERR_VALUE`, `__STR`, `set_if_not_errno_or_zero`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Key functions/subprograms:
- line 12 `volatile`: `asm volatile ("if %0 s< -4095 goto +1\n" \`
- line 18 `IS_ERR_OR_NULL`: `static inline int IS_ERR_OR_NULL(const void *ptr)`
- line 23 `PTR_ERR`: `static inline long PTR_ERR(const void *ptr)`
- Header fixture content: 0 struct/union/enum/typedef markers provide BTF type material for consumers.

## Control Flow
There is no direct BPF attach entry in this file. Control flow is compile-time inclusion: other objects consume its declarations/macros/types so that clang, BTF generation, libbpf CO-RE relocation, or the verifier sees the intended shapes.
Local flow is organized through `volatile`, `IS_ERR_OR_NULL`, `PTR_ERR`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Signal is compile/load-time BTF or declaration availability for other selftest objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions.c

## Purpose
`exceptions.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 7384 bytes across 382 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `<bpf/bpf_endian.h>`, `"bpf_misc.h"`, `"bpf_experimental.h"`.
- Important macros/constants: `ETH_P_IP`, `check_assert`.
- BPF API surface: exception unwinding; program-array dispatch.
- Helper/kfunc calls: `bpf_assert`, `bpf_assert_range`, `bpf_assert_range_with`, `bpf_assert_with`, `bpf_cmp_unlikely`, `bpf_ktime_get_ns`, `bpf_ntohs`, `bpf_tail_call_static`, `bpf_throw`.
Map/type declarations observed:
- line 15 declares map type `BPF_MAP_TYPE_PROG_ARRAY`
Attach sections and exported entry points:
- line 19 `SEC(".maps")` -> static __noinline int static_func(u64 i)
- line 45 `SEC("tc")` -> int exception_throw_always_1(struct __sk_buff *ctx)
- line 56 `SEC("tc")` -> int exception_throw_always_2(struct __sk_buff *ctx)
- line 62 `SEC("tc")` -> int exception_throw_unwind_1(struct __sk_buff *ctx)
- line 68 `SEC("tc")` -> int exception_throw_unwind_2(struct __sk_buff *ctx)
- line 74 `SEC("tc")` -> int exception_throw_default(struct __sk_buff *ctx)
- line 81 `SEC("tc")` -> int exception_throw_default_value(struct __sk_buff *ctx)
- line 88 `SEC("tc")` -> int exception_tail_call_target(struct __sk_buff *ctx)
- line 104 `SEC("tc")` -> int exception_tail_call(struct __sk_buff *ctx) {
- line 118 `SEC("tc")` -> int exception_throw_from_void_global(struct __sk_buff *ctx)
- line 138 `SEC("tc")` -> int exception_ext(struct __sk_buff *ctx)
- line 164 `SEC("tc")` -> int exception_ext_mod_cb_runtime(struct __sk_buff *ctx)
- plus 7 more entries of the same pattern.
Key functions/subprograms:
- line 21 `static_func`: `static __noinline int static_func(u64 i)`
- line 27 `global2static_simple`: `__noinline int global2static_simple(u64 i)`
- line 33 `global2static`: `__noinline int global2static(u64 i)`
- line 40 `static2global`: `static __noinline int static2global(u64 i)`
- line 46 `exception_throw_always_1`: `int exception_throw_always_1(struct __sk_buff *ctx)`
- line 57 `exception_throw_always_2`: `int exception_throw_always_2(struct __sk_buff *ctx)`
- line 63 `exception_throw_unwind_1`: `int exception_throw_unwind_1(struct __sk_buff *ctx)`
- line 69 `exception_throw_unwind_2`: `int exception_throw_unwind_2(struct __sk_buff *ctx)`
- line 75 `exception_throw_default`: `int exception_throw_default(struct __sk_buff *ctx)`
- line 82 `exception_throw_default_value`: `int exception_throw_default_value(struct __sk_buff *ctx)`
- line 89 `exception_tail_call_target`: `int exception_tail_call_target(struct __sk_buff *ctx)`
- line 96 `exception_tail_call_subprog`: `int exception_tail_call_subprog(struct __sk_buff *ctx)`
- plus 31 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `static_func`, `global2static_simple`, `global2static`, `static2global`, `exception_throw_always_1`, `exception_throw_always_2`, `exception_throw_unwind_1`, `exception_throw_unwind_2` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Exception paths deliberately leave normal fall-through through `bpf_throw`, so expected behavior includes unwind/default-return handling as well as rejection in unsafe contexts.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 98 `volatile int ret = 10;`
- line 106 `volatile int ret = 0;`
- line 128 `volatile int ret = 0;`
- line 146 `volatile int ret = 0;`
- line 217 `volatile u64 cookie = c;`
- line 225 `volatile u64 cookie = c;`
- line 233 `volatile s64 cookie = c;`
- line 241 `volatile s64 cookie = c;`
- line 249 `volatile s64 cookie = c;`
- line 257 `volatile s64 cookie = c;`
- plus 6 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Exception cases are sensitive to lock, RCU, preemption, IRQ, callback, and reference-lifetime restrictions.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_assert.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_assert.c

## Purpose
`exceptions_assert.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4020 bytes across 135 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<limits.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `<bpf/bpf_endian.h>`, `"bpf_misc.h"`, `"bpf_experimental.h"`.
- Important macros/constants: `check_assert`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_assert`, `bpf_assert_range`, `bpf_assert_with`, `bpf_cmp_unlikely`, `bpf_ktime_get_ns`.
Attach sections and exported entry points:
- line 12 `SEC("?tc")` -> int check_assert_##name(void *ctx) \
- line 60 `SEC("?tc")` -> int check_assert_range_s64(struct __sk_buff *ctx)
- line 76 `SEC("?tc")` -> int check_assert_range_u64(struct __sk_buff *ctx)
- line 87 `SEC("?tc")` -> int check_assert_single_range_s64(struct __sk_buff *ctx)
- line 104 `SEC("?tc")` -> int check_assert_single_range_u64(struct __sk_buff *ctx)
- line 115 `SEC("?tc")` -> int check_assert_generic(struct __sk_buff *ctx)
- line 127 `SEC("?fentry/bpf_check")` -> int check_assert_with_return(void *ctx)
- line 135 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 63 `check_assert_range_s64`: `int check_assert_range_s64(struct __sk_buff *ctx)`
- line 79 `check_assert_range_u64`: `int check_assert_range_u64(struct __sk_buff *ctx)`
- line 90 `check_assert_single_range_s64`: `int check_assert_single_range_s64(struct __sk_buff *ctx)`
- line 107 `check_assert_single_range_u64`: `int check_assert_single_range_u64(struct __sk_buff *ctx)`
- line 118 `check_assert_generic`: `int check_assert_generic(struct __sk_buff *ctx)`
- line 128 `__msg`: `__failure __msg("At program exit the register R1 has smin=64 smax=64")`
- line 129 `check_assert_with_return`: `int check_assert_with_return(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?fentry/bpf_check`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `check_assert_range_s64`, `check_assert_range_u64`, `check_assert_single_range_s64`, `check_assert_single_range_u64`, `check_assert_generic`, `__msg`, `check_assert_with_return`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 66 `s64 num;`
- line 81 `u64 num = ctx->len;`
- line 93 `s64 num;`
- line 109 `u64 num = ctx->len;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `R{{.}}=0xffffffff80000000`, `R{{.}}=0x7fffffff`, `R{{.}}=0`, `R{{.}}=0x8000000000000000`, `R{{.}}=0x7fffffffffffffff`, plus 18 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_assert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_ext.c

## Purpose
`exceptions_ext.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 940 bytes across 72 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `"bpf_experimental.h"`.
- BPF API surface: exception unwinding.
- Helper/kfunc calls: `bpf_throw`.
Attach sections and exported entry points:
- line 6 `SEC("?fentry")` -> int pfentry(void *ctx)
- line 12 `SEC("?fentry")` -> int throwing_fentry(void *ctx)
- line 24 `SEC("?freplace")` -> int extension(struct __sk_buff *ctx)
- line 30 `SEC("?freplace")` -> int throwing_exception_cb_extension(u64 cookie)
- line 38 `SEC("?freplace")` -> int throwing_extension(struct __sk_buff *ctx)
- line 46 `SEC("?fexit")` -> int pfexit(void *ctx)
- line 52 `SEC("?fexit")` -> int throwing_fexit(void *ctx)
- line 59 `SEC("?fmod_ret")` -> int pfmod_ret(void *ctx)
- line 65 `SEC("?fmod_ret")` -> int throwing_fmod_ret(void *ctx)
- line 72 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 7 `pfentry`: `int pfentry(void *ctx)`
- line 13 `throwing_fentry`: `int throwing_fentry(void *ctx)`
- line 19 `exception_cb`: `__noinline int exception_cb(u64 cookie)`
- line 25 `extension`: `int extension(struct __sk_buff *ctx)`
- line 32 `throwing_exception_cb_extension`: `int throwing_exception_cb_extension(u64 cookie)`
- line 40 `throwing_extension`: `int throwing_extension(struct __sk_buff *ctx)`
- line 47 `pfexit`: `int pfexit(void *ctx)`
- line 53 `throwing_fexit`: `int throwing_fexit(void *ctx)`
- line 60 `pfmod_ret`: `int pfmod_ret(void *ctx)`
- line 66 `throwing_fmod_ret`: `int throwing_fmod_ret(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `?fentry`, `?fentry`, `?freplace`, `?freplace`, `?freplace`, `?fexit`, `?fexit`, `?fmod_ret` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `pfentry`, `throwing_fentry`, `exception_cb`, `extension`, `throwing_exception_cb_extension`, `throwing_extension`, `pfexit`, `throwing_fexit` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Exception paths deliberately leave normal fall-through through `bpf_throw`, so expected behavior includes unwind/default-return handling as well as rejection in unsafe contexts.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Exception cases are sensitive to lock, RCU, preemption, IRQ, callback, and reference-lifetime restrictions.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_fail.c

## Purpose
`exceptions_fail.c` is a BPF exception selftest for throw, unwind, assertion, callback, and verifier-rejection semantics. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 8207 bytes across 427 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `"bpf_misc.h"`, `"bpf_experimental.h"`.
- Important macros/constants: `private`.
- BPF API surface: map lookup/update/delete or map-side state; exception unwinding; bounded callback iteration.
- Helper/kfunc calls: `bpf_local_irq_restore`, `bpf_local_irq_save`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_preempt_disable`, `bpf_preempt_enable`, `bpf_rbtree_add`, `bpf_rcu_read_lock`, `bpf_rcu_read_unlock`, `bpf_spin_lock`, `bpf_spin_unlock`, `bpf_throw`, `bpf_timer_set_callback`.
Map/type declarations observed:
- line 28 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 17 `SEC("#define private(name) SEC(".bss." #name) __hidden __attribute__((aligned(8)))")` -> struct foo {
- line 32 `SEC(".maps")` -> private(A) struct bpf_spin_lock lock;
- line 61 `SEC("?tc")` -> int reject_exception_cb_type_1(struct __sk_buff *ctx)
- line 70 `SEC("?tc")` -> int reject_exception_cb_type_2(struct __sk_buff *ctx)
- line 79 `SEC("?tc")` -> int reject_exception_cb_type_3(struct __sk_buff *ctx)
- line 88 `SEC("?tc")` -> int reject_exception_cb_type_4(struct __sk_buff *ctx)
- line 97 `SEC("?tc")` -> int reject_exception_cb_type_5(struct __sk_buff *ctx)
- line 113 `SEC("?tc")` -> int reject_async_callback_throw(struct __sk_buff *ctx)
- line 135 `SEC("?tc")` -> int reject_with_lock(void *ctx)
- line 144 `SEC("?tc")` -> int reject_subprog_with_lock(void *ctx)
- line 151 `SEC("?tc")` -> int reject_with_rcu_read_lock(void *ctx)
- line 167 `SEC("?tc")` -> int reject_subprog_with_rcu_read_lock(void *ctx)
- plus 18 more entries of the same pattern.
Key functions/subprograms:
- line 42 `exception_cb_bad_ret_type2`: `__noinline void exception_cb_bad_ret_type2(u64 cookie)`
- line 46 `exception_cb_bad_arg_0`: `__noinline int exception_cb_bad_arg_0(void)`
- line 51 `exception_cb_bad_arg_2`: `__noinline int exception_cb_bad_arg_2(int a, int b)`
- line 56 `exception_cb_ok_arg_small`: `__noinline int exception_cb_ok_arg_small(int a)`
- line 63 `__msg`: `__failure __msg("Global function exception_cb_bad_ret_type1() return value not void or scalar.")`
- line 64 `reject_exception_cb_type_1`: `int reject_exception_cb_type_1(struct __sk_buff *ctx)`
- line 72 `__msg`: `__failure __msg("exception cb only supports single integer argument")`
- line 73 `reject_exception_cb_type_2`: `int reject_exception_cb_type_2(struct __sk_buff *ctx)`
- line 81 `__msg`: `__failure __msg("exception cb only supports single integer argument")`
- line 82 `reject_exception_cb_type_3`: `int reject_exception_cb_type_3(struct __sk_buff *ctx)`
- line 91 `reject_exception_cb_type_4`: `int reject_exception_cb_type_4(struct __sk_buff *ctx)`
- line 99 `__msg`: `__failure __msg("exception cb cannot return void")`
- plus 62 more entries of the same pattern.

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `#define private(name) SEC(".bss." #name) __hidden __attribute__((aligned(8)))`, `.maps`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `exception_cb_bad_ret_type2`, `exception_cb_bad_arg_0`, `exception_cb_bad_arg_2`, `exception_cb_ok_arg_small`, `__msg`, `reject_exception_cb_type_1`, `__msg`, `reject_exception_cb_type_2` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.
Exception paths deliberately leave normal fall-through through `bpf_throw`, so expected behavior includes unwind/default-return handling as well as rejection in unsafe contexts.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 127 `volatile int ret = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Exception cases are sensitive to lock, RCU, preemption, IRQ, callback, and reference-lifetime restrictions.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Uses `__success` annotations; a passing test is successful verifier load despite nearby edge cases.
- Expected verifier messages include `Global function exception_cb_bad_ret_type1() return value not void or scalar.`, `exception cb only supports single integer argument`, `exception cb only supports single integer argument`, `exception cb cannot return void`, `cannot be called from callback subprog`, plus 21 more.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exceptions_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exhandler_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exhandler_kern.c

## Purpose
`exhandler_kern.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1422 bytes across 52 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_core_read.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_pid_tgid`.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> unsigned int exception_triggered;
- line 18 `SEC("tp_btf/task_newtask")` -> int BPF_PROG(trace_task_newtask, struct task_struct *task, u64 clone_flags)
Key functions/subprograms:
- line 19 `BPF_PROG`: `int BPF_PROG(trace_task_newtask, struct task_struct *task, u64 clone_flags)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `tp_btf/task_newtask`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int test_pid;`
- line 23 `void *func;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/exhandler_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fd_htab_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fd_htab_lookup.c

## Purpose
`fd_htab_lookup.c` is a hash-map selftest or benchmark covering lookup, update, delete, reuse, or memory pressure behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 569 bytes across 25 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Map/type declarations observed:
- line 9 declares map type `BPF_MAP_TYPE_ARRAY`
- line 16 declares map type `BPF_MAP_TYPE_HASH_OF_MAPS`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct inner_map_type {
- line 13 `SEC(".maps")` -> struct {
- line 21 `SEC(".maps")` -> .values = {

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fd_htab_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_many_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_many_args.c

## Purpose
`fentry_many_args.c` is an fentry tracing selftest validating typed argument capture and recursion behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1176 bytes across 39 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,
- line 10 `SEC("fentry/bpf_testmod_fentry_test7")` -> int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,
- line 20 `SEC("fentry/bpf_testmod_fentry_test11")` -> int BPF_PROG(test2, __u64 a, void *b, short c, int d, void *e, char f,
- line 31 `SEC("fentry/bpf_testmod_fentry_test11")` -> int BPF_PROG(test3, __u64 a, __u64 b, __u64 c, __u64 d, __u64 e, __u64 f,
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,`
- line 21 `BPF_PROG`: `int BPF_PROG(test2, __u64 a, void *b, short c, int d, void *e, char f,`
- line 32 `BPF_PROG`: `int BPF_PROG(test3, __u64 a, __u64 b, __u64 c, __u64 d, __u64 e, __u64 f,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_testmod_fentry_test7`, `fentry/bpf_testmod_fentry_test11`, `fentry/bpf_testmod_fentry_test11`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 19 `__u64 test2_result = 0;`
- line 30 `__u64 test3_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_many_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive.c

## Purpose
`fentry_recursive.c` is an fentry tracing selftest validating typed argument capture and recursion behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 334 bytes across 14 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> /* Dummy fentry bpf prog for testing fentry attachment chains */
- line 10 `SEC("fentry/XXX")` -> int BPF_PROG(recursive_attach, int a)
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(recursive_attach, int a)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/XXX`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive_target.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive_target.c

## Purpose
`fentry_recursive_target.c` is an fentry tracing selftest validating typed argument capture and recursion behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 578 bytes across 25 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> /* Dummy fentry bpf prog for testing fentry attachment chains. It's going to be
- line 12 `SEC("fentry/bpf_testmod_fentry_test1")` -> int BPF_PROG(test1, int a)
- line 21 `SEC("raw_tp/sys_enter")` -> int BPF_PROG(fentry_target, struct pt_regs *regs, long id)
Key functions/subprograms:
- line 13 `BPF_PROG`: `int BPF_PROG(test1, int a)`
- line 22 `BPF_PROG`: `int BPF_PROG(fentry_target, struct pt_regs *regs, long id)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_testmod_fentry_test1`, `raw_tp/sys_enter`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_recursive_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_test.c

## Purpose
`fentry_test.c` is an fentry tracing selftest validating typed argument capture and recursion behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1630 bytes across 79 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1, int a)
- line 10 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(test1, int a)
- line 18 `SEC("fentry/bpf_fentry_test2")` -> int BPF_PROG(test2, int a, __u64 b)
- line 26 `SEC("fentry/bpf_fentry_test3")` -> int BPF_PROG(test3, char a, int b, __u64 c)
- line 34 `SEC("fentry/bpf_fentry_test4")` -> int BPF_PROG(test4, void *a, char b, int c, __u64 d)
- line 42 `SEC("fentry/bpf_fentry_test5")` -> int BPF_PROG(test5, __u64 a, void *b, short c, int d, __u64 e)
- line 51 `SEC("fentry/bpf_fentry_test6")` -> int BPF_PROG(test6, __u64 a, void *b, short c, int d, void * e, __u64 f)
- line 64 `SEC("fentry/bpf_fentry_test7")` -> int BPF_PROG(test7, struct bpf_fentry_test_t *arg)
- line 73 `SEC("fentry/bpf_fentry_test8")` -> int BPF_PROG(test8, struct bpf_fentry_test_t *arg)
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1, int a)`
- line 19 `BPF_PROG`: `int BPF_PROG(test2, int a, __u64 b)`
- line 27 `BPF_PROG`: `int BPF_PROG(test3, char a, int b, __u64 c)`
- line 35 `BPF_PROG`: `int BPF_PROG(test4, void *a, char b, int c, __u64 d)`
- line 43 `BPF_PROG`: `int BPF_PROG(test5, __u64 a, void *b, short c, int d, __u64 e)`
- line 52 `BPF_PROG`: `int BPF_PROG(test6, __u64 a, void *b, short c, int d, void * e, __u64 f)`
- line 65 `BPF_PROG`: `int BPF_PROG(test7, struct bpf_fentry_test_t *arg)`
- line 74 `BPF_PROG`: `int BPF_PROG(test8, struct bpf_fentry_test_t *arg)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_fentry_test1`, `fentry/bpf_fentry_test2`, `fentry/bpf_fentry_test3`, `fentry/bpf_fentry_test4`, `fentry/bpf_fentry_test5`, `fentry/bpf_fentry_test6`, `fentry/bpf_fentry_test7` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 17 `__u64 test2_result = 0;`
- line 25 `__u64 test3_result = 0;`
- line 33 `__u64 test4_result = 0;`
- line 41 `__u64 test5_result = 0;`
- line 50 `__u64 test6_result = 0;`
- line 63 `__u64 test7_result = 0;`
- line 72 `__u64 test8_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fentry_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf.c

## Purpose
`fexit_bpf2bpf.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 4285 bytes across 179 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/stddef.h>`, `<linux/if_ether.h>`, `<linux/ipv6.h>`, `<linux/bpf.h>`, `<linux/tcp.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_probe_read_kernel`, `bpf_prog_test_load`, `bpf_skb_load_bytes`.
Attach sections and exported entry points:
- line 17 `SEC("fexit/test_pkt_access")` -> int BPF_PROG(test_main, struct sk_buff *skb, int ret)
- line 32 `SEC("fexit/test_pkt_access_subprog1")` -> int BPF_PROG(test_subprog1, struct sk_buff *skb, int ret)
- line 65 `SEC("fexit/test_pkt_access_subprog2")` -> int test_subprog2(struct args_subprog2 *ctx)
- line 89 `SEC("fexit/test_pkt_access_subprog3")` -> int BPF_PROG(test_subprog3, int val, struct sk_buff *skb, int ret)
- line 104 `SEC("freplace/get_skb_len")` -> int new_get_skb_len(struct __sk_buff *skb)
- line 116 `SEC("freplace/get_skb_ifindex")` -> int new_get_skb_ifindex(int val, struct __sk_buff *skb, int var)
- line 146 `SEC("freplace/get_constant")` -> int new_get_constant(long val)
- line 156 `SEC("freplace/test_pkt_write_access_subprog")` -> int new_test_pkt_write_access_subprog(struct __sk_buff *skb, __u32 off)
- line 179 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 18 `BPF_PROG`: `int BPF_PROG(test_main, struct sk_buff *skb, int ret)`
- line 33 `BPF_PROG`: `int BPF_PROG(test_subprog1, struct sk_buff *skb, int ret)`
- line 66 `test_subprog2`: `int test_subprog2(struct args_subprog2 *ctx)`
- line 90 `BPF_PROG`: `int BPF_PROG(test_subprog3, int val, struct sk_buff *skb, int ret)`
- line 105 `new_get_skb_len`: `int new_get_skb_len(struct __sk_buff *skb)`
- line 117 `new_get_skb_ifindex`: `int new_get_skb_ifindex(int val, struct __sk_buff *skb, int var)`
- line 147 `new_get_constant`: `int new_get_constant(long val)`
- line 157 `new_test_pkt_write_access_subprog`: `int new_test_pkt_write_access_subprog(struct __sk_buff *skb, __u32 off)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `fexit/test_pkt_access`, `fexit/test_pkt_access_subprog1`, `fexit/test_pkt_access_subprog2`, `fexit/test_pkt_access_subprog3`, `freplace/get_skb_len`, `freplace/get_skb_ifindex`, `freplace/get_constant`, `freplace/test_pkt_write_access_subprog` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `test_subprog2`, `BPF_PROG`, `new_get_skb_len`, `new_get_skb_ifindex`, `new_get_constant`, `new_test_pkt_write_access_subprog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 16 `__u64 test_result = 0;`
- line 20 `int len;`
- line 31 `__u64 test_result_subprog1 = 0;`
- line 35 `int len;`
- line 61 `__u64 args[5];`
- line 62 `__u64 ret;`
- line 64 `__u64 test_result_subprog2 = 0;`
- line 69 `__u64 ret;`
- line 70 `int len;`
- line 88 `__u64 test_result_subprog3 = 0;`
- plus 7 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf_simple.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf_simple.c

## Purpose
`fexit_bpf2bpf_simple.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 488 bytes across 27 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 13 `SEC("fexit/test_pkt_md_access")` -> int BPF_PROG(test_main2, struct sk_buff *skb, int ret)
- line 27 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `BPF_PROG`: `int BPF_PROG(test_main2, struct sk_buff *skb, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `fexit/test_pkt_md_access`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `__u64 test_result = 0;`
- line 16 `int len;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_bpf2bpf_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_many_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_many_args.c

## Purpose
`fexit_many_args.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1250 bytes across 40 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,
- line 10 `SEC("fexit/bpf_testmod_fentry_test7")` -> int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,
- line 20 `SEC("fexit/bpf_testmod_fentry_test11")` -> int BPF_PROG(test2, __u64 a, void *b, short c, int d, void *e, char f,
- line 32 `SEC("fexit/bpf_testmod_fentry_test11")` -> int BPF_PROG(test3, __u64 a, __u64 b, __u64 c, __u64 d, __u64 e, __u64 f,
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1, __u64 a, void *b, short c, int d, void *e, char f,`
- line 21 `BPF_PROG`: `int BPF_PROG(test2, __u64 a, void *b, short c, int d, void *e, char f,`
- line 33 `BPF_PROG`: `int BPF_PROG(test3, __u64 a, __u64 b, __u64 c, __u64 d, __u64 e, __u64 f,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fexit/bpf_testmod_fentry_test7`, `fexit/bpf_testmod_fentry_test11`, `fexit/bpf_testmod_fentry_test11`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 19 `__u64 test2_result = 0;`
- line 31 `__u64 test3_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_many_args.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_sleep.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_sleep.c

## Purpose
`fexit_sleep.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 589 bytes across 32 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_pid_tgid`.
Attach sections and exported entry points:
- line 8 `SEC("license")` -> int pid = 0;
- line 14 `SEC("SEC("fentry/" SYS_PREFIX "sys_nanosleep")")` -> int nanosleep_fentry(void *ctx)
- line 24 `SEC("SEC("fexit/" SYS_PREFIX "sys_nanosleep")")` -> int nanosleep_fexit(void *ctx)
Key functions/subprograms:
- line 15 `nanosleep_fentry`: `int nanosleep_fentry(void *ctx)`
- line 25 `nanosleep_fexit`: `int nanosleep_fexit(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `SEC("fentry/" SYS_PREFIX "sys_nanosleep")`, `SEC("fexit/" SYS_PREFIX "sys_nanosleep")`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `nanosleep_fentry`, `nanosleep_fexit`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int pid = 0;`
- line 11 `int fentry_cnt = 0;`
- line 12 `int fexit_cnt = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_test.c

## Purpose
`fexit_test.c` is an fexit tracing selftest validating return-value and BPF-to-BPF instrumentation behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1748 bytes across 80 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1, int a, int ret)
- line 10 `SEC("fexit/bpf_fentry_test1")` -> int BPF_PROG(test1, int a, int ret)
- line 18 `SEC("fexit/bpf_fentry_test2")` -> int BPF_PROG(test2, int a, __u64 b, int ret)
- line 26 `SEC("fexit/bpf_fentry_test3")` -> int BPF_PROG(test3, char a, int b, __u64 c, int ret)
- line 34 `SEC("fexit/bpf_fentry_test4")` -> int BPF_PROG(test4, void *a, char b, int c, __u64 d, int ret)
- line 43 `SEC("fexit/bpf_fentry_test5")` -> int BPF_PROG(test5, __u64 a, void *b, short c, int d, __u64 e, int ret)
- line 52 `SEC("fexit/bpf_fentry_test6")` -> int BPF_PROG(test6, __u64 a, void *b, short c, int d, void *e, __u64 f, int ret)
- line 65 `SEC("fexit/bpf_fentry_test7")` -> int BPF_PROG(test7, struct bpf_fentry_test_t *arg)
- line 74 `SEC("fexit/bpf_fentry_test8")` -> int BPF_PROG(test8, struct bpf_fentry_test_t *arg)
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1, int a, int ret)`
- line 19 `BPF_PROG`: `int BPF_PROG(test2, int a, __u64 b, int ret)`
- line 27 `BPF_PROG`: `int BPF_PROG(test3, char a, int b, __u64 c, int ret)`
- line 35 `BPF_PROG`: `int BPF_PROG(test4, void *a, char b, int c, __u64 d, int ret)`
- line 44 `BPF_PROG`: `int BPF_PROG(test5, __u64 a, void *b, short c, int d, __u64 e, int ret)`
- line 53 `BPF_PROG`: `int BPF_PROG(test6, __u64 a, void *b, short c, int d, void *e, __u64 f, int ret)`
- line 66 `BPF_PROG`: `int BPF_PROG(test7, struct bpf_fentry_test_t *arg)`
- line 75 `BPF_PROG`: `int BPF_PROG(test8, struct bpf_fentry_test_t *arg)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fexit/bpf_fentry_test1`, `fexit/bpf_fentry_test2`, `fexit/bpf_fentry_test3`, `fexit/bpf_fentry_test4`, `fexit/bpf_fentry_test5`, `fexit/bpf_fentry_test6`, `fexit/bpf_fentry_test7` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 17 `__u64 test2_result = 0;`
- line 25 `__u64 test3_result = 0;`
- line 33 `__u64 test4_result = 0;`
- line 42 `__u64 test5_result = 0;`
- line 51 `__u64 test6_result = 0;`
- line 64 `__u64 test7_result = 0;`
- line 73 `__u64 test8_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fexit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fib_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fib_lookup.c

## Purpose
`fib_lookup.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 496 bytes across 22 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/types.h>`, `<linux/bpf.h>`, `<linux/pkt_cls.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_fib_lookup`.
Attach sections and exported entry points:
- line 13 `SEC("tc")` -> int fib_lookup(struct __sk_buff *skb)
- line 22 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `fib_lookup`: `int fib_lookup(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `tc`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `fib_lookup`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int fib_lookup_ret = 0;`
- line 11 `int lookup_flags = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fib_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader.c

## Purpose
`file_reader.c` is a file-dynptr selftest using LSM hooks and dynptr reads against kernel file contents. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3538 bytes across 145 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<string.h>`, `<stdbool.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`, `"errno.h"`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers; task or cgroup reference kfuncs.
- Helper/kfunc calls: `bpf_dynptr_adjust`, `bpf_dynptr_file_discard`, `bpf_dynptr_from_file`, `bpf_dynptr_read`, `bpf_for`, `bpf_get_current_pid_tgid`, `bpf_get_current_task_btf`, `bpf_get_task_exe_file`, `bpf_map_lookup_elem`, `bpf_put_file`, `bpf_task_work_schedule_signal`.
Map/type declarations observed:
- line 14 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 11 `SEC("license")` -> struct {
- line 18 `SEC(".maps")` -> struct elem {
- line 34 `SEC("lsm/file_open")` -> int on_open_expect_fault(void *c)
- line 65 `SEC("lsm/file_open")` -> int on_open_validate_file_read(void *c)
Key functions/subprograms:
- line 35 `on_open_expect_fault`: `int on_open_expect_fault(void *c)`
- line 66 `on_open_validate_file_read`: `int on_open_validate_file_read(void *c)`
- line 85 `task_work_callback`: `static int task_work_callback(struct bpf_map *map, void *key, void *value)`
- line 100 `verify_dynptr_read`: `static int verify_dynptr_read(struct bpf_dynptr *ptr, u32 off, char *user_buf, u32 len)`
- line 116 `validate_file_read`: `static int validate_file_read(struct file *file)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `lsm/file_open`, `lsm/file_open`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `on_open_expect_fault`, `on_open_validate_file_read`, `task_work_callback`, `verify_dynptr_read`, `validate_file_read`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 25 `char user_buf[256000];`
- line 26 `char tmp_buf[256000];`
- line 28 `int pid = 0;`
- line 29 `int err, run_success = 0;`
- line 39 `int local_err = 1;`
- line 70 `int key = 0;`
- line 102 `int i;`
- line 119 `int loc_err = 1, off;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- BPF LSM hooks may require sleepable attachment and kernel security/IMA configuration.

## Risks and Edge Cases
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader_fail.c

## Purpose
`file_reader_fail.c` is a file-dynptr selftest using LSM hooks and dynptr reads against kernel file contents. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1047 bytes across 52 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<string.h>`, `<stdbool.h>`, `<bpf/bpf_tracing.h>`, `"bpf_misc.h"`.
- BPF API surface: task/cgroup/time/function metadata helpers; dynptr construction/access/mutation helpers.
- Helper/kfunc calls: `bpf_dynptr_file_discard`, `bpf_dynptr_from_file`, `bpf_dynptr_from_xdp`, `bpf_get_current_task_btf`, `bpf_get_task_exe_file`.
Attach sections and exported entry points:
- line 10 `SEC("license")` -> int err;
- line 15 `SEC("lsm/file_open")` -> int on_nanosleep_unreleased_ref(void *ctx)
- line 31 `SEC("xdp")` -> int xdp_wrong_dynptr_type(struct xdp_md *xdp)
- line 43 `SEC("xdp")` -> int xdp_no_dynptr_type(struct xdp_md *xdp)
Key functions/subprograms:
- line 18 `on_nanosleep_unreleased_ref`: `int on_nanosleep_unreleased_ref(void *ctx)`
- line 34 `xdp_wrong_dynptr_type`: `int xdp_wrong_dynptr_type(struct xdp_md *xdp)`
- line 46 `xdp_no_dynptr_type`: `int xdp_no_dynptr_type(struct xdp_md *xdp)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `lsm/file_open`, `xdp`, `xdp`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `on_nanosleep_unreleased_ref`, `xdp_wrong_dynptr_type`, `xdp_no_dynptr_type`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `int err;`
- line 13 `void *user_ptr;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- BPF LSM hooks may require sleepable attachment and kernel security/IMA configuration.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- Expected verifier failures/messages are part of the test contract; diagnostic text and annotation drift can break the harness.
- Dynptr behavior depends on initialized state, read-only flags, offset/length bounds, packet linearity, and dynptr type.

## Test Signals
- Uses `__failure` annotations; a passing test is verifier rejection with expected diagnostics.
- Expected verifier messages include `Unreleased reference id=`, `Expected a dynptr of type file as arg #0`, `Expected an initialized dynptr as arg #0`.
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/file_reader_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma.c

## Purpose
`find_vma.c` is a bpf_find_vma selftest checking callback behavior and verifier rejection paths. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1535 bytes across 69 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `VM_EXEC`, `DNAME_INLINE_LEN`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_find_vma`, `bpf_get_current_task_btf`, `bpf_probe_read_kernel_str`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> struct callback_ctx {
- line 37 `SEC("raw_tp/sys_enter")` -> int handle_getpid(void)
- line 53 `SEC("perf_event")` -> int handle_pe(void)
Key functions/subprograms:
- line 23 `check_vma`: `static long check_vma(struct task_struct *task, struct vm_area_struct *vma,`
- line 38 `handle_getpid`: `int handle_getpid(void)`
- line 54 `handle_pe`: `int handle_pe(void)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `raw_tp/sys_enter`, `perf_event`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `check_vma`, `handle_getpid`, `handle_pe`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int dummy;`
- line 17 `char d_iname[DNAME_INLINE_LEN] = {0};`
- line 18 `__u32 found_vm_exec = 0;`
- line 19 `__u64 addr = 0;`
- line 20 `int find_zero_ret = -1;`
- line 21 `int find_addr_ret = -1;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail1.c

## Purpose
`find_vma_fail1.c` is a bpf_find_vma selftest checking callback behavior and verifier rejection paths. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 628 bytes across 30 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `vm_flags`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_find_vma`, `bpf_get_current_task_btf`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> struct callback_ctx {
- line 22 `SEC("raw_tp/sys_enter")` -> int handle_getpid(void)
Key functions/subprograms:
- line 13 `write_vma`: `static long write_vma(struct task_struct *task, struct vm_area_struct *vma,`
- line 23 `handle_getpid`: `int handle_getpid(void)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `raw_tp/sys_enter`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `write_vma`, `handle_getpid`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `int dummy;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail2.c

## Purpose
`find_vma_fail2.c` is a bpf_find_vma selftest checking callback behavior and verifier rejection paths. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 587 bytes across 29 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_find_vma`, `bpf_get_current_task_btf`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct callback_ctx {
- line 21 `SEC("raw_tp/sys_enter")` -> int handle_getpid(void)
Key functions/subprograms:
- line 12 `write_task`: `static long write_task(struct task_struct *task, struct vm_area_struct *vma,`
- line 22 `handle_getpid`: `int handle_getpid(void)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `raw_tp/sys_enter`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `write_task`, `handle_getpid`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `int dummy;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/find_vma_fail2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fmod_ret_freplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fmod_ret_freplace.c

## Purpose
`fmod_ret_freplace.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 319 bytes across 14 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("fmod_ret/security_new_get_constant")` -> int BPF_PROG(fmod_ret_test, long val, int ret)
- line 14 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 8 `BPF_PROG`: `int BPF_PROG(fmod_ret_test, long val, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `fmod_ret/security_new_get_constant`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 6 `volatile __u64 test_fmod_ret = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fmod_ret_freplace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_array_map_elem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_array_map_elem.c

## Purpose
`for_each_array_map_elem.c` is a bpf_for_each_map_elem callback-iteration selftest. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1472 bytes across 73 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers; map-element callback iteration.
- Helper/kfunc calls: `bpf_for_each_map_elem`, `bpf_get_smp_processor_id`.
Map/type declarations observed:
- line 9 declares map type `BPF_MAP_TYPE_ARRAY`
- line 16 declares map type `BPF_MAP_TYPE_PERCPU_ARRAY`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct {
- line 13 `SEC(".maps")` -> struct {
- line 20 `SEC(".maps")` -> struct callback_ctx {
- line 60 `SEC("tc")` -> int test_pkt_access(struct __sk_buff *skb)
Key functions/subprograms:
- line 61 `test_pkt_access`: `int test_pkt_access(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_pkt_access`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 23 `int output;`
- line 26 `const volatile int bypass_unused = 1;`
- line 46 `__u32 cpu = 0;`
- line 47 `__u64 percpu_val = 0;`
- line 58 `u32 arraymap_output = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_array_map_elem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_map_elem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_map_elem.c

## Purpose
`for_each_hash_map_elem.c` is a bpf_for_each_map_elem callback-iteration selftest. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1855 bytes across 95 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; map-element callback iteration.
- Helper/kfunc calls: `bpf_for_each_map_elem`, `bpf_get_smp_processor_id`, `bpf_map_delete_elem`.
Map/type declarations observed:
- line 9 declares map type `BPF_MAP_TYPE_HASH`
- line 16 declares map type `BPF_MAP_TYPE_PERCPU_HASH`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct {
- line 13 `SEC(".maps")` -> struct {
- line 20 `SEC(".maps")` -> struct callback_ctx {
- line 81 `SEC("tc")` -> int test_pkt_access(struct __sk_buff *skb)
Key functions/subprograms:
- line 82 `test_pkt_access`: `int test_pkt_access(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_pkt_access`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 24 `int input;`
- line 25 `int output;`
- line 33 `__u32 k;`
- line 34 `__u64 v;`
- line 51 `__u32 cpu = 0;`
- line 52 `__u32 percpu_called = 0;`
- line 53 `__u32 percpu_key = 0;`
- line 54 `__u64 percpu_val = 0;`
- line 55 `int percpu_output = 0;`
- line 77 `int hashmap_output = 0;`
- plus 2 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_map_elem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_modify.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_modify.c

## Purpose
`for_each_hash_modify.c` is a bpf_for_each_map_elem callback-iteration selftest. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 597 bytes across 30 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state; map-element callback iteration.
- Helper/kfunc calls: `bpf_for_each_map_elem`, `bpf_map_delete_elem`, `bpf_map_update_elem`.
Map/type declarations observed:
- line 9 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct {
- line 13 `SEC(".maps")` -> static int cb(struct bpf_map *map, __u64 *key, __u64 *val, void *arg)
- line 22 `SEC("tc")` -> int test_pkt_access(struct __sk_buff *skb)
Key functions/subprograms:
- line 15 `cb`: `static int cb(struct bpf_map *map, __u64 *key, __u64 *val, void *arg)`
- line 23 `test_pkt_access`: `int test_pkt_access(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `cb`, `test_pkt_access`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_hash_modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_map_elem_write_key.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_map_elem_write_key.c

## Purpose
`for_each_map_elem_write_key.c` is a bpf_for_each_map_elem callback-iteration selftest. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 558 bytes across 27 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers; map-element callback iteration.
- Helper/kfunc calls: `bpf_for_each_map_elem`, `bpf_get_current_comm`.
Map/type declarations observed:
- line 6 declares map type `BPF_MAP_TYPE_ARRAY`
Attach sections and exported entry points:
- line 10 `SEC(".maps")` -> static __u64
- line 20 `SEC("raw_tp/sys_enter")` -> int test_map_key_write(const void *ctx)
- line 27 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 21 `test_map_key_write`: `int test_map_key_write(const void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `raw_tp/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_map_key_write`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_map_elem_write_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_multi_maps.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_multi_maps.c

## Purpose
`for_each_multi_maps.c` is a bpf_for_each_map_elem callback-iteration selftest. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 919 bytes across 49 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map-element callback iteration.
- Helper/kfunc calls: `bpf_for_each_map_elem`.
Map/type declarations observed:
- line 8 declares map type `BPF_MAP_TYPE_ARRAY`
- line 15 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 5 `SEC("license")` -> struct {
- line 12 `SEC(".maps")` -> struct {
- line 19 `SEC(".maps")` -> struct callback_ctx {
- line 36 `SEC("tc")` -> int test_pkt_access(struct __sk_buff *skb)
Key functions/subprograms:
- line 37 `test_pkt_access`: `int test_pkt_access(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`, `tc`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_pkt_access`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 22 `int output;`
- line 25 `u32 data_output = 0;`
- line 26 `int use_array = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/for_each_multi_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/free_timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/free_timer.c

## Purpose
`free_timer.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1800 bytes across 81 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<time.h>`, `<bpf/bpf_tracing.h>`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `MAX_ENTRIES`.
- BPF API surface: map lookup/update/delete or map-side state; bounded callback iteration.
- Helper/kfunc calls: `bpf_for`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`.
Map/type declarations observed:
- line 25 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 29 `SEC(".maps")` -> static int timer_cb(void *map, void *key, struct map_value *value)
- line 67 `SEC("syscall")` -> int BPF_PROG(start_timer)
- line 74 `SEC("syscall")` -> int BPF_PROG(overwrite_timer)
- line 81 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 31 `timer_cb`: `static int timer_cb(void *map, void *key, struct map_value *value)`
- line 41 `start_cb`: `static int start_cb(int key)`
- line 57 `overwrite_cb`: `static int overwrite_cb(int key)`
- line 68 `BPF_PROG`: `int BPF_PROG(start_timer)`
- line 75 `BPF_PROG`: `int BPF_PROG(overwrite_timer)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `syscall`, `syscall`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `timer_cb`, `start_cb`, `overwrite_cb`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 33 `volatile int sum = 0;`
- line 34 `int i;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.
The file exercises explicit reference/lifetime behavior; accepted paths must release or transfer ownership, while failure variants intentionally leave or misuse references.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/free_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_attach_probe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_attach_probe.c

## Purpose
`freplace_attach_probe.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 757 bytes across 40 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/ptrace.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `VAR_NUM`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_map_lookup_elem`, `bpf_spin_lock`, `bpf_spin_unlock`.
Map/type declarations observed:
- line 17 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 21 `SEC(".maps")` -> int new_handle_kprobe(struct pt_regs *ctx)
- line 23 `SEC("freplace/handle_kprobe")` -> int new_handle_kprobe(struct pt_regs *ctx)
- line 40 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 24 `new_handle_kprobe`: `int new_handle_kprobe(struct pt_regs *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `freplace/handle_kprobe`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `new_handle_kprobe`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 13 `int var[VAR_NUM];`
- line 27 `int key = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_attach_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_cls_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_cls_redirect.c

## Purpose
`freplace_cls_redirect.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 722 bytes across 34 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/stddef.h>`, `<linux/bpf.h>`, `<linux/pkt_cls.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_sk_release`.
Map/type declarations observed:
- line 11 declares map type `BPF_MAP_TYPE_SOCKMAP`
Attach sections and exported entry points:
- line 15 `SEC(".maps")` -> int freplace_cls_redirect_test(struct __sk_buff *skb)
- line 17 `SEC("freplace/cls_redirect")` -> int freplace_cls_redirect_test(struct __sk_buff *skb)
- line 34 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 18 `freplace_cls_redirect_test`: `int freplace_cls_redirect_test(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `freplace/cls_redirect`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `freplace_cls_redirect_test`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 20 `int ret = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_cls_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_connect4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_connect4.c

## Purpose
`freplace_connect4.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 385 bytes across 18 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/stddef.h>`, `<linux/ipv6.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_bind`.
Attach sections and exported entry points:
- line 9 `SEC("freplace/do_bind")` -> int new_do_bind(struct bpf_sock_addr *ctx)
- line 18 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 10 `new_do_bind`: `int new_do_bind(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/do_bind`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `new_do_bind`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_connect4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_connect_v4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_connect_v4_prog.c

## Purpose
`freplace_connect_v4_prog.c` is a cgroup socket-address selftest that rewrites, denies, binds, or probes connect-time socket fields. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 427 bytes across 19 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/stddef.h>`, `<linux/ipv6.h>`, `<linux/bpf.h>`, `<linux/in.h>`, `<sys/socket.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 12 `SEC("freplace/connect_v4_prog")` -> int new_connect_v4_prog(struct bpf_sock_addr *ctx)
- line 19 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `new_connect_v4_prog`: `int new_connect_v4_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/connect_v4_prog`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `new_connect_v4_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_connect_v4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_dead_global_func.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_dead_global_func.c

## Purpose
`freplace_dead_global_func.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 185 bytes across 11 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 5 `SEC("freplace")` -> int freplace_prog(void)
- line 11 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 6 `freplace_prog`: `int freplace_prog(void)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `freplace_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_dead_global_func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_get_constant.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_get_constant.c

## Purpose
`freplace_get_constant.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 396 bytes across 15 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 7 `SEC("freplace/get_constant")` -> int security_new_get_constant(long val)
- line 15 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 8 `security_new_get_constant`: `int security_new_get_constant(long val)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/get_constant`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `security_new_get_constant`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 6 `volatile __u64 test_get_constant = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_get_constant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_global_func.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_global_func.c

## Purpose
`freplace_global_func.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 354 bytes across 18 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 12 `SEC("freplace/test_pkt_access")` -> int new_test_pkt_access(struct __sk_buff *skb)
- line 18 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 6 `test_ctx_global_func`: `int test_ctx_global_func(struct __sk_buff *skb)`
- line 13 `new_test_pkt_access`: `int new_test_pkt_access(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/test_pkt_access`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_ctx_global_func`, `new_test_pkt_access`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 8 `volatile int retval = 1;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_global_func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_int_with_void.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_int_with_void.c

## Purpose
`freplace_int_with_void.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 246 bytes across 11 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<linux/pkt_cls.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 6 `SEC("freplace/global_func2")` -> void test_freplace_int_with_void(struct __sk_buff *skb)
- line 11 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 7 `test_freplace_int_with_void`: `void test_freplace_int_with_void(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/global_func2`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_freplace_int_with_void`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_int_with_void.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_progmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_progmap.c

## Purpose
`freplace_progmap.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 473 bytes across 24 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_redirect_map`.
Map/type declarations observed:
- line 6 declares map type `BPF_MAP_TYPE_CPUMAP`
Attach sections and exported entry points:
- line 10 `SEC(".maps")` -> int xdp_drop_prog(struct xdp_md *ctx)
- line 12 `SEC("xdp/cpumap")` -> int xdp_drop_prog(struct xdp_md *ctx)
- line 18 `SEC("freplace")` -> int xdp_cpumap_prog(struct xdp_md *ctx)
- line 24 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 13 `xdp_drop_prog`: `int xdp_drop_prog(struct xdp_md *ctx)`
- line 19 `xdp_cpumap_prog`: `int xdp_cpumap_prog(struct xdp_md *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `xdp/cpumap`, `freplace`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `xdp_drop_prog`, `xdp_cpumap_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_progmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_unreliable_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_unreliable_prog.c

## Purpose
`freplace_unreliable_prog.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 612 bytes across 20 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 8 `SEC("freplace/btf_unreliable_kprobe")` -> /* context type is what BPF verifier expects for kprobe context, but target
- line 20 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 15 `replace_btf_unreliable_kprobe`: `int replace_btf_unreliable_kprobe(bpf_user_pt_regs_t *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/btf_unreliable_kprobe`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `replace_btf_unreliable_kprobe`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_unreliable_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_void.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_void.c

## Purpose
`freplace_void.c` is a BPF-to-BPF function replacement or modify-return selftest checking target signature and attach behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 201 bytes across 10 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Attach sections and exported entry points:
- line 5 `SEC("freplace/foo")` -> void test_freplace_void(struct __sk_buff *skb)
- line 10 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 6 `test_freplace_void`: `void test_freplace_void(struct __sk_buff *skb)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `freplace/foo`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `test_freplace_void`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Packet contexts (`tc`, `xdp`, `lwt`, cgroup skb) make data/meta bounds and return codes verifier-sensitive.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/freplace_void.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fsession_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fsession_test.c

## Purpose
`fsession_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3788 bytes across 179 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_func_ip`, `bpf_session_cookie`, `bpf_session_is_return`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> next declaration
- line 12 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test1, int a, int ret)
- line 29 `SEC("fsession/bpf_fentry_test3")` -> int BPF_PROG(test2, char a, int b, __u64 c, int ret)
- line 46 `SEC("fsession/bpf_fentry_test4")` -> int BPF_PROG(test3, void *a, char b, int c, __u64 d, int ret)
- line 63 `SEC("fsession/bpf_fentry_test5")` -> int BPF_PROG(test4, __u64 a, void *b, short c, int d, __u64 e, int ret)
- line 82 `SEC("fsession/bpf_fentry_test7")` -> int BPF_PROG(test5, struct bpf_fentry_test_t *arg, int ret)
- line 100 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test6, int a)
- line 114 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test7, int a)
- line 132 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test8, int a)
- line 150 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test9, int a, int ret)
- line 166 `SEC("fexit/bpf_fentry_test1")` -> int BPF_PROG(test10, int a, int ret)
- line 174 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(test11, int a)
Key functions/subprograms:
- line 13 `BPF_PROG`: `int BPF_PROG(test1, int a, int ret)`
- line 30 `BPF_PROG`: `int BPF_PROG(test2, char a, int b, __u64 c, int ret)`
- line 47 `BPF_PROG`: `int BPF_PROG(test3, void *a, char b, int c, __u64 d, int ret)`
- line 64 `BPF_PROG`: `int BPF_PROG(test4, __u64 a, void *b, short c, int d, __u64 e, int ret)`
- line 83 `BPF_PROG`: `int BPF_PROG(test5, struct bpf_fentry_test_t *arg, int ret)`
- line 101 `BPF_PROG`: `int BPF_PROG(test6, int a)`
- line 115 `BPF_PROG`: `int BPF_PROG(test7, int a)`
- line 133 `BPF_PROG`: `int BPF_PROG(test8, int a)`
- line 151 `BPF_PROG`: `int BPF_PROG(test9, int a, int ret)`
- line 167 `BPF_PROG`: `int BPF_PROG(test10, int a, int ret)`
- line 175 `BPF_PROG`: `int BPF_PROG(test11, int a)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fsession/bpf_fentry_test1`, `fsession/bpf_fentry_test3`, `fsession/bpf_fentry_test4`, `fsession/bpf_fentry_test5`, `fsession/bpf_fentry_test7`, `fsession/bpf_fentry_test1`, `fsession/bpf_fentry_test1` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_entry_result = 0;`
- line 10 `__u64 test1_exit_result = 0;`
- line 26 `__u64 test2_entry_result = 0;`
- line 27 `__u64 test2_exit_result = 0;`
- line 43 `__u64 test3_entry_result = 0;`
- line 44 `__u64 test3_exit_result = 0;`
- line 60 `__u64 test4_entry_result = 0;`
- line 61 `__u64 test4_exit_result = 0;`
- line 79 `__u64 test5_entry_result = 0;`
- line 80 `__u64 test5_exit_result = 0;`
- plus 10 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/fsession_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_branch_snapshot.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_branch_snapshot.c

## Purpose
`get_branch_snapshot.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 907 bytes across 40 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `ENTRY_CNT`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_branch_snapshot`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int wasted_entries = 0;
- line 23 `SEC("fexit/bpf_testmod_loop_test")` -> int BPF_PROG(test1, int n, int ret)
Key functions/subprograms:
- line 18 `gbs_in_range`: `static inline bool gbs_in_range(__u64 val)`
- line 24 `BPF_PROG`: `int BPF_PROG(test1, int n, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fexit/bpf_testmod_loop_test`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `gbs_in_range`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_hits = 0;`
- line 10 `__u64 address_low = 0;`
- line 11 `__u64 address_high = 0;`
- line 12 `int wasted_entries = 0;`
- line 13 `long total_entries = 0;`
- line 26 `long i;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_branch_snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_cgroup_id_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_cgroup_id_kern.c

## Purpose
`get_cgroup_id_kern.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 387 bytes across 21 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_cgroup_id`, `bpf_get_current_pid_tgid`.
Attach sections and exported entry points:
- line 10 `SEC("tracepoint/syscalls/sys_enter_nanosleep")` -> int trace(void *ctx)
- line 21 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 11 `trace`: `int trace(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `tracepoint/syscalls/sys_enter_nanosleep`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `trace`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 7 `__u64 cg_id;`
- line 8 `__u64 expected_pid;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_cgroup_id_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_fsession_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_fsession_test.c

## Purpose
`get_func_args_fsession_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 785 bytes across 37 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<errno.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_func_arg`, `bpf_get_func_arg_cnt`, `bpf_get_func_ret`, `bpf_session_is_return`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1)
- line 11 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test1)
Key functions/subprograms:
- line 12 `BPF_PROG`: `int BPF_PROG(test1)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fsession/bpf_fentry_test1`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 15 `__u64 a = 0, z = 0, ret = 0;`
- line 16 `__s64 err;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_fsession_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_test.c

## Purpose
`get_func_args_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 3750 bytes across 167 lines.

## Important APIs, Types, and Functions
- Dependencies: `<vmlinux.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`, `<errno.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_func_arg`, `bpf_get_func_arg_cnt`, `bpf_get_func_ret`.
Attach sections and exported entry points:
- line 7 `SEC("license")` -> int BPF_PROG(test1)
- line 10 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(test1)
- line 43 `SEC("fexit/bpf_fentry_test2")` -> int BPF_PROG(test2)
- line 70 `SEC("fmod_ret/bpf_modify_return_test")` -> int BPF_PROG(fmod_ret_test, int _a, int *_b, int _ret)
- line 99 `SEC("fexit/bpf_modify_return_test")` -> int BPF_PROG(fexit_test, int _a, int *_b, int _ret)
- line 126 `SEC("tp_btf/bpf_testmod_fentry_test1_tp")` -> int BPF_PROG(tp_test1)
- line 146 `SEC("tp_btf/bpf_testmod_fentry_test2_tp")` -> int BPF_PROG(tp_test2)
Key functions/subprograms:
- line 11 `BPF_PROG`: `int BPF_PROG(test1)`
- line 44 `BPF_PROG`: `int BPF_PROG(test2)`
- line 71 `BPF_PROG`: `int BPF_PROG(fmod_ret_test, int _a, int *_b, int _ret)`
- line 100 `BPF_PROG`: `int BPF_PROG(fexit_test, int _a, int *_b, int _ret)`
- line 127 `BPF_PROG`: `int BPF_PROG(tp_test1)`
- line 147 `BPF_PROG`: `int BPF_PROG(tp_test2)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_fentry_test1`, `fexit/bpf_fentry_test2`, `fmod_ret/bpf_modify_return_test`, `fexit/bpf_modify_return_test`, `tp_btf/bpf_testmod_fentry_test1_tp`, `tp_btf/bpf_testmod_fentry_test2_tp`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 9 `__u64 test1_result = 0;`
- line 14 `__u64 a = 0, z = 0, ret = 0;`
- line 15 `__s64 err;`
- line 42 `__u64 test2_result = 0;`
- line 47 `__u64 a = 0, b = 0, z = 0, ret = 0;`
- line 48 `__s64 err;`
- line 69 `__u64 test3_result = 0;`
- line 74 `__u64 a = 0, b = 0, z = 0, ret = 0;`
- line 75 `__s64 err;`
- line 98 `__u64 test4_result = 0;`
- plus 8 more entries of the same pattern.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Several symbols or hooks integrate with `bpf_testmod`; the kernel test module must be available for those attach points.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_args_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_fsession_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_fsession_test.c

## Purpose
`get_func_ip_fsession_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 497 bytes across 21 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_func_ip`, `bpf_session_is_return`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> next declaration
- line 11 `SEC("fsession/bpf_fentry_test1")` -> int BPF_PROG(test1, int a)
Key functions/subprograms:
- line 12 `BPF_PROG`: `int BPF_PROG(test1, int a)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fsession/bpf_fentry_test1`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 8 `__u64 test1_entry_result = 0;`
- line 9 `__u64 test1_exit_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_fsession_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_test.c

## Purpose
`get_func_ip_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2232 bytes across 105 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_fentry_test1`, `bpf_get_func_ip`, `bpf_modify_return_test`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> extern int bpf_fentry_test1(int a) __ksym;
- line 26 `SEC("fentry/bpf_fentry_test1")` -> int BPF_PROG(test1, int a)
- line 36 `SEC("fexit/bpf_fentry_test2")` -> int BPF_PROG(test2, int a)
- line 46 `SEC("kprobe/bpf_fentry_test3")` -> int test3(struct pt_regs *ctx)
- line 56 `SEC("kretprobe/bpf_fentry_test4")` -> int BPF_KRETPROBE(test4)
- line 66 `SEC("fmod_ret/bpf_modify_return_test")` -> int BPF_PROG(test5, int a, int *b, int ret)
- line 76 `SEC("?kprobe")` -> int test6(struct pt_regs *ctx)
- line 88 `SEC("uprobe//proc/self/exe:uprobe_trigger")` -> int BPF_UPROBE(test7)
- line 98 `SEC("uretprobe//proc/self/exe:uprobe_trigger")` -> int BPF_URETPROBE(test8, int ret)
Key functions/subprograms:
- line 20 `unused`: `int unused(void)`
- line 27 `BPF_PROG`: `int BPF_PROG(test1, int a)`
- line 37 `BPF_PROG`: `int BPF_PROG(test2, int a)`
- line 47 `test3`: `int test3(struct pt_regs *ctx)`
- line 57 `BPF_KRETPROBE`: `int BPF_KRETPROBE(test4)`
- line 67 `BPF_PROG`: `int BPF_PROG(test5, int a, int *b, int ret)`
- line 77 `test6`: `int test6(struct pt_regs *ctx)`
- line 89 `BPF_UPROBE`: `int BPF_UPROBE(test7)`
- line 99 `BPF_URETPROBE`: `int BPF_URETPROBE(test8, int ret)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `fentry/bpf_fentry_test1`, `fexit/bpf_fentry_test2`, `kprobe/bpf_fentry_test3`, `kretprobe/bpf_fentry_test4`, `fmod_ret/bpf_modify_return_test`, `?kprobe`, `uprobe//proc/self/exe:uprobe_trigger` and additional sections. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `unused`, `BPF_PROG`, `BPF_PROG`, `test3`, `BPF_KRETPROBE`, `BPF_PROG`, `test6`, `BPF_UPROBE` and related helper subprograms. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 25 `__u64 test1_result = 0;`
- line 35 `__u64 test2_result = 0;`
- line 45 `__u64 test3_result = 0;`
- line 55 `__u64 test4_result = 0;`
- line 65 `__u64 test5_result = 0;`
- line 75 `__u64 test6_result = 0;`
- line 87 `__u64 test7_result = 0;`
- line 97 `__u64 test8_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_uprobe_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_uprobe_test.c

## Purpose
`get_func_ip_uprobe_test.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 421 bytes across 18 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_func_ip`.
Attach sections and exported entry points:
- line 6 `SEC("license")` -> unsigned long uprobe_trigger_body;
- line 11 `SEC("uprobe//proc/self/exe:uprobe_trigger_body+1")` -> int BPF_UPROBE(test1)
Key functions/subprograms:
- line 12 `BPF_UPROBE`: `int BPF_UPROBE(test1)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `uprobe//proc/self/exe:uprobe_trigger_body+1`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `BPF_UPROBE`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 10 `__u64 test1_result = 0;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/get_func_ip_uprobe_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername4_prog.c

## Purpose
`getpeername4_prog.c` is a cgroup sock_addr selftest that rewrites returned peer addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 558 bytes across 24 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- Important macros/constants: `REWRITE_ADDRESS_IP4`, `REWRITE_ADDRESS_PORT4`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_htonl`, `bpf_htons`.
Attach sections and exported entry points:
- line 15 `SEC("cgroup/getpeername4")` -> int getpeername_v4_prog(struct bpf_sock_addr *ctx)
- line 24 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 16 `getpeername_v4_prog`: `int getpeername_v4_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getpeername4`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getpeername_v4_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername6_prog.c

## Purpose
`getpeername6_prog.c` is a cgroup sock_addr selftest that rewrites returned peer addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 832 bytes across 31 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- Important macros/constants: `REWRITE_ADDRESS_IP6_0`, `REWRITE_ADDRESS_IP6_1`, `REWRITE_ADDRESS_IP6_2`, `REWRITE_ADDRESS_IP6_3`, `REWRITE_ADDRESS_PORT6`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_htonl`, `bpf_htons`.
Attach sections and exported entry points:
- line 19 `SEC("cgroup/getpeername6")` -> int getpeername_v6_prog(struct bpf_sock_addr *ctx)
- line 31 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 20 `getpeername_v6_prog`: `int getpeername_v6_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getpeername6`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getpeername_v6_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername6_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername_unix_prog.c

## Purpose
`getpeername_unix_prog.c` is a cgroup sock_addr selftest that rewrites returned peer addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1019 bytes across 38 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- BPF API surface: socket option/address helpers.
- Helper/kfunc calls: `bpf_cast_to_kern_ctx`, `bpf_core_cast`, `bpf_sock_addr_set_sun_path`.
Attach sections and exported entry points:
- line 13 `SEC("cgroup/getpeername_unix")` -> int getpeername_unix_prog(struct bpf_sock_addr *ctx)
- line 38 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `getpeername_unix_prog`: `int getpeername_unix_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getpeername_unix`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getpeername_unix_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `__u8 SERVUN_REWRITE_ADDRESS[] = "\0bpf_cgroup_unix_test_rewrite";`
- line 20 `int ret;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getpeername_unix_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname4_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname4_prog.c

## Purpose
`getsockname4_prog.c` is a cgroup sock_addr selftest that rewrites returned local socket addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 558 bytes across 24 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- Important macros/constants: `REWRITE_ADDRESS_IP4`, `REWRITE_ADDRESS_PORT4`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_htonl`, `bpf_htons`.
Attach sections and exported entry points:
- line 15 `SEC("cgroup/getsockname4")` -> int getsockname_v4_prog(struct bpf_sock_addr *ctx)
- line 24 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 16 `getsockname_v4_prog`: `int getsockname_v4_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getsockname4`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getsockname_v4_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname4_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname6_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname6_prog.c

## Purpose
`getsockname6_prog.c` is a cgroup sock_addr selftest that rewrites returned local socket addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 832 bytes across 31 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_endian.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- Important macros/constants: `REWRITE_ADDRESS_IP6_0`, `REWRITE_ADDRESS_IP6_1`, `REWRITE_ADDRESS_IP6_2`, `REWRITE_ADDRESS_IP6_3`, `REWRITE_ADDRESS_PORT6`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
- Helper/kfunc calls: `bpf_htonl`, `bpf_htons`.
Attach sections and exported entry points:
- line 19 `SEC("cgroup/getsockname6")` -> int getsockname_v6_prog(struct bpf_sock_addr *ctx)
- line 31 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 20 `getsockname_v6_prog`: `int getsockname_v6_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getsockname6`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getsockname_v6_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
No obvious mutable scalar globals were found; state is stack-local, attach-context-local, or represented as type metadata.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname6_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname_unix_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname_unix_prog.c

## Purpose
`getsockname_unix_prog.c` is a cgroup sock_addr selftest that rewrites returned local socket addresses. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1019 bytes across 38 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<string.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_core_read.h>`, `"bpf_kfuncs.h"`.
- BPF API surface: socket option/address helpers.
- Helper/kfunc calls: `bpf_cast_to_kern_ctx`, `bpf_core_cast`, `bpf_sock_addr_set_sun_path`.
Attach sections and exported entry points:
- line 13 `SEC("cgroup/getsockname_unix")` -> int getsockname_unix_prog(struct bpf_sock_addr *ctx)
- line 38 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 14 `getsockname_unix_prog`: `int getsockname_unix_prog(struct bpf_sock_addr *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `cgroup/getsockname_unix`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `getsockname_unix_prog`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 11 `__u8 SERVUN_REWRITE_ADDRESS[] = "\0bpf_cgroup_unix_test_rewrite";`
- line 20 `int ret;`

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- Cgroup attach points require a prepared cgroup and are observed through socket or packet operations.

## Risks and Edge Cases
- Socket address rewrites must preserve network byte order and only touch fields valid for the attach type and family.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/getsockname_unix_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_mem_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_mem_bench.c

## Purpose
`htab_mem_bench.c` is a hash-map selftest or benchmark covering lookup, update, delete, reuse, or memory pressure behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 2256 bytes across 105 lines.

## Important APIs, Types, and Functions
- Dependencies: `<stdbool.h>`, `<errno.h>`, `<linux/types.h>`, `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- Important macros/constants: `OP_BATCH`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers; bounded callback iteration.
- Helper/kfunc calls: `bpf_get_smp_processor_id`, `bpf_loop`, `bpf_map_delete_elem`, `bpf_map_update_elem`.
Map/type declarations observed:
- line 18 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 21 `SEC(".maps")` -> unsigned char zeroed_value[4096];
- line 23 `SEC("license")` -> unsigned char zeroed_value[4096];
- line 55 `SEC("?tp/syscalls/sys_enter_getpgid")` -> int overwrite(void *ctx)
- line 67 `SEC("?tp/syscalls/sys_enter_getpgid")` -> int batch_add_batch_del(void *ctx)
- line 83 `SEC("?tp/syscalls/sys_enter_getpgid")` -> int add_only(void *ctx)
- line 95 `SEC("?tp/syscalls/sys_enter_getppid")` -> int del_only(void *ctx)
Key functions/subprograms:
- line 29 `write_htab`: `static int write_htab(unsigned int i, struct update_ctx *ctx, unsigned int flags)`
- line 37 `overwrite_htab`: `static int overwrite_htab(unsigned int i, struct update_ctx *ctx)`
- line 42 `newwrite_htab`: `static int newwrite_htab(unsigned int i, struct update_ctx *ctx)`
- line 47 `del_htab`: `static int del_htab(unsigned int i, struct update_ctx *ctx)`
- line 56 `overwrite`: `int overwrite(void *ctx)`
- line 68 `batch_add_batch_del`: `int batch_add_batch_del(void *ctx)`
- line 84 `add_only`: `int add_only(void *ctx)`
- line 96 `del_only`: `int del_only(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `license`, `?tp/syscalls/sys_enter_getpgid`, `?tp/syscalls/sys_enter_getpgid`, `?tp/syscalls/sys_enter_getpgid`, `?tp/syscalls/sys_enter_getppid`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `write_htab`, `overwrite_htab`, `newwrite_htab`, `del_htab`, `overwrite`, `batch_add_batch_del`, `add_only`, `del_only`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.
Callback iteration is central to the flow; callback prototypes, mutation permissions, and bounded iteration counts are part of what the verifier is testing.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 27 `long op_cnt = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_mem_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_reuse.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_reuse.c

## Purpose
`htab_reuse.c` is a hash-map selftest or benchmark covering lookup, update, delete, reuse, or memory pressure behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 775 bytes across 35 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- Important macros/constants: `HTAB_NDATA`.
- BPF API surface: section attach ABI, BTF metadata, return values, or declarations rather than many explicit helper calls.
Map/type declarations observed:
- line 14 declares map type `BPF_MAP_TYPE_HASH`
- line 30 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 6 `SEC("license")` -> struct htab_val {
- line 19 `SEC(".maps")` -> #define HTAB_NDATA 256
- line 35 `SEC(".maps")` -> next declaration

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `.maps`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 25 `__u32 seq;`
- line 26 `__u64 data[HTAB_NDATA];`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_update.c

## Purpose
`htab_update.c` is a hash-map selftest or benchmark covering lookup, update, delete, reuse, or memory pressure behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 763 bytes across 36 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: map lookup/update/delete or map-side state; task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_pid_tgid`, `bpf_map_update_elem`, `bpf_obj_free_fields`.
Map/type declarations observed:
- line 16 declares map type `BPF_MAP_TYPE_HASH`
Attach sections and exported entry points:
- line 7 `SEC("license")` -> /* Map value type: has BTF-managed field (bpf_timer) */
- line 20 `SEC(".maps")` -> int pid = 0;
- line 25 `SEC("?fentry/bpf_obj_free_fields")` -> int bpf_obj_free_fields(void *ctx)
Key functions/subprograms:
- line 26 `bpf_obj_free_fields`: `int bpf_obj_free_fields(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `license`, `.maps`, `?fentry/bpf_obj_free_fields`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `bpf_obj_free_fields`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `__u64 payload;`
- line 22 `int pid = 0;`
- line 23 `int update_err = 0;`
- line 28 `__u32 key = 0;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/htab_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ima.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ima.c

## Purpose
`ima.c` is a sleepable BPF LSM/IMA selftest for file hash measurement and optional deny behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 1822 bytes across 103 lines.

## Important APIs, Types, and Functions
- Dependencies: `"vmlinux.h"`, `<errno.h>`, `<bpf/bpf_helpers.h>`, `<bpf/bpf_tracing.h>`.
- BPF API surface: task/cgroup/time/function metadata helpers.
- Helper/kfunc calls: `bpf_get_current_pid_tgid`, `bpf_ima_file_hash`, `bpf_ima_inode_hash`, `bpf_ringbuf_reserve`, `bpf_ringbuf_submit`.
Map/type declarations observed:
- line 15 declares map type `BPF_MAP_TYPE_RINGBUF`
Attach sections and exported entry points:
- line 17 `SEC(".maps")` -> bool use_ima_file_hash;
- line 19 `SEC("license")` -> bool use_ima_file_hash;
- line 66 `SEC("lsm.s/bprm_committed_creds")` -> void BPF_PROG(bprm_committed_creds, struct linux_binprm *bprm)
- line 72 `SEC("lsm.s/bprm_creds_for_exec")` -> int BPF_PROG(bprm_creds_for_exec, struct linux_binprm *bprm)
- line 82 `SEC("lsm.s/kernel_read_file")` -> int BPF_PROG(kernel_read_file, struct file *file, enum kernel_read_file_id id,
Key functions/subprograms:
- line 26 `ima_test_common`: `static void ima_test_common(struct file *file)`
- line 55 `ima_test_deny`: `static int ima_test_deny(void)`
- line 67 `BPF_PROG`: `void BPF_PROG(bprm_committed_creds, struct linux_binprm *bprm)`
- line 73 `BPF_PROG`: `int BPF_PROG(bprm_creds_for_exec, struct linux_binprm *bprm)`
- line 83 `BPF_PROG`: `int BPF_PROG(kernel_read_file, struct file *file, enum kernel_read_file_id id,`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `license`, `lsm.s/bprm_committed_creds`, `lsm.s/bprm_creds_for_exec`, `lsm.s/kernel_read_file`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `ima_test_common`, `ima_test_deny`, `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 12 `u32 monitored_pid = 0;`
- line 21 `bool use_ima_file_hash;`
- line 22 `bool enable_bprm_creds_for_exec;`
- line 23 `bool enable_kernel_read_file;`
- line 24 `bool test_deny;`
- line 28 `u64 ima_hash = 0;`
- line 29 `u64 *sample;`
- line 30 `int ret;`
- line 31 `u32 pid;`
- line 57 `u32 pid;`
- plus 1 more entries of the same pattern.
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.
- BPF LSM hooks may require sleepable attachment and kernel security/IMA configuration.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ima.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/inner_array_lookup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/inner_array_lookup.c

## Purpose
`inner_array_lookup.c` is a small eBPF selftest object used to validate verifier, helper, map, attach, or BTF behavior. It belongs to the Linux BPF selftest program corpus vendored under the Ceph client source tree, so its purpose is verifier/runtime coverage rather than Ceph production filesystem logic. The file was read completely for this note; size is 802 bytes across 45 lines.

## Important APIs, Types, and Functions
- Dependencies: `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`.
- BPF API surface: map lookup/update/delete or map-side state.
- Helper/kfunc calls: `bpf_map_lookup_elem`.
Map/type declarations observed:
- line 7 declares map type `BPF_MAP_TYPE_ARRAY`
- line 14 declares map type `BPF_MAP_TYPE_HASH_OF_MAPS`
Attach sections and exported entry points:
- line 11 `SEC(".maps")` -> struct outer_map {
- line 18 `SEC(".maps")` -> .values = {
- line 24 `SEC("raw_tp/sys_enter")` -> int handle__sys_enter(void *ctx)
- line 45 `SEC("license")` -> next declaration
Key functions/subprograms:
- line 25 `handle__sys_enter`: `int handle__sys_enter(void *ctx)`

## Control Flow
User-space loads the object and attaches programs by `SEC` name. The primary runtime entry sections are `.maps`, `.maps`, `raw_tp/sys_enter`, `license`. Each entry uses the attach-specific context, performs bounded checks or helper/kfunc calls, records result state in globals/maps when needed, and returns the expected verifier/runtime verdict for that attach type.
Local flow is organized through `handle__sys_enter`. Error returns are generally checked immediately because verifier tests rely on precise path state and reference lifetime accounting.

## State and Persistence Behavior
Object-local globals/BSS provide harness-visible state:
- line 27 `int outer_key = 2, inner_key = 3;`
- line 28 `int *val;`
- line 29 `void *map;`
BPF maps persist while the object is loaded and carry fixture data, counters, callback state, program arrays, object references, or map-in-map handles between the BPF side and the user-space harness.

## Dependencies and Integration Points
- Linux BPF selftest skeleton/loading code selects programs by section/function name and reads BSS/map state after triggering the relevant kernel path.
- Kernel verifier, BTF IDs, helper/kfunc availability, and program-type-specific context rules are part of the API contract.

## Risks and Edge Cases
- The main drift risk is mismatch with the user-space selftest harness for section names, globals, maps, return codes, or expected side effects.

## Test Signals
- Runtime signal comes from attaching the listed sections, triggering the relevant syscall/socket/packet/LSM/testmod path, and reading globals/maps.
- Map contents are part of the observable state for callbacks, references, counters, or fixture data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/inner_array_lookup.c -->
