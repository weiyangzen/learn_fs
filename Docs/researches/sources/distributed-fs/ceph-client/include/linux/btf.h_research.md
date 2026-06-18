## sources/distributed-fs/ceph-client/include/linux/btf.h

**Purpose:** This header is the kernel-internal BPF Type Format interface. It declares BTF object lifecycle, lookup, display, type inspection, kfunc registration/filtering, field parsing, BPF struct-ops integration, and config-gated stubs when BPF syscall support is absent.

**Important APIs/types/functions:** Key macros include `BTF_TYPE_EMIT`, `BTF_TYPE_EMIT_ENUM`, kfunc flags `KF_*`, `__bpf_kfunc`, kfunc diagnostic wrappers, and `stringify_struct()`. Types include `struct btf`, `btf_kfunc_id_set`, `btf_id_dtor_kfunc`, `btf_struct_meta`, `btf_field_desc`, and `btf_field_iter`. Functions cover `btf_get/put`, `btf_new_fd`, `btf_get_by_fd`, `btf_get_info_by_fd`, type resolution (`btf_type_id_size`, `btf_type_skip_modifiers`, `btf_resolve_size`), object formatting, ID lookup, kfunc allow checks, BTF relocation, and field iteration.

**Control flow, state, persistence:** Inline helpers decode `struct btf_type` metadata from UAPI layouts and traverse variable-length member/array/enum payloads. ID-set helpers use binary search over sorted arrays. Actual BTF object state, refcounts, module ownership, and verifier decisions live in BPF/BTF implementation files. Feature-disabled builds return safe stubs such as `NULL`, `-EOPNOTSUPP`, `-ENOENT`, or no-op success for registration.

**Dependencies/integration:** Depends on `linux/bsearch.h`, `linux/btf_ids.h`, BPF UAPI headers, module/file operations, seq files, verifier logs, and optional `CONFIG_BPF_SYSCALL`/`CONFIG_BPF_JIT`.

**Risks and test signals:** Risks are stale BTF kind assumptions, unsorted ID sets, unsafe raw object display, incorrect kfunc flags that weaken verifier guarantees, and build differences across config gates. Test signals include BPF verifier selftests, kfunc registration tests, BTF pretty-print output, module BTF load/unload, CO-RE relocation, and no-BPF config builds.
