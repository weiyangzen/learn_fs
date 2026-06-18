# sources/distributed-fs/ceph-client/kernel/bpf/cgroup_iter.c

## Purpose
`cgroup_iter.c` implements BPF iterator support for cgroup hierarchies and open-coded cgroup subsystem-state iterators exposed as kfuncs. It lets iterator programs walk descendants in pre-order or post-order, ancestors, a single cgroup, or direct children, and emits `struct cgroup *` context values to BPF.

## Important APIs, types, and functions
Important types are `struct bpf_iter__cgroup`, `struct cgroup_iter_priv`, opaque `struct bpf_iter_css`, and internal `struct bpf_iter_css_kern`. The seq-file path is implemented by `cgroup_iter_seq_start()`, `cgroup_iter_seq_next()`, `cgroup_iter_seq_stop()`, and `cgroup_iter_seq_show()`. Target registration uses `bpf_cgroup_reg_info` and `bpf_cgroup_iter_init()`. Attach and metadata functions are `bpf_iter_attach_cgroup()`, `bpf_iter_detach_cgroup()`, `bpf_iter_cgroup_show_fdinfo()`, and `bpf_iter_cgroup_fill_link_info()`. Kfuncs are `bpf_iter_css_new()`, `bpf_iter_css_next()`, and `bpf_iter_css_destroy()`.

## Control flow
Iterator attach validates the requested order, resolves either a cgroup fd, cgroup id, or root path, and stores a referenced start cgroup in iterator aux data. Seq initialization takes an additional CSS reference for the read session. `start()` locks the cgroup hierarchy and refuses multi-session reads: if user space resumes after `pos > 0` before the walk completed, it returns `-EOPNOTSUPP`. `next()` advances using the cgroup core traversal helper matching the selected order. `show()` skips dead cgroups, prepares `bpf_iter_meta`, and runs the iterator program; nonzero program return sets `terminate`. `stop()` unlocks and, on normal completion, calls the program once with a NULL cgroup for epilogue processing.

## State and persistence
Iterator state is per-link and per-read-session only. Aux data holds the start cgroup and traversal order for the link. Seq private state holds `start_css`, `visited_all`, `terminate`, and `order`. CSS references keep the start node alive during iteration. The kfunc iterator stores start, current position, and flags in the opaque object supplied by the BPF program. No persistent storage exists.

## Dependencies and integration points
This file depends on cgroup traversal APIs, `cgroup_mutex`, seq-file based BPF iterator infrastructure, BTF IDs for `struct cgroup`, fdinfo/link-info reporting, and verifier context metadata using `PTR_TO_BTF_ID_OR_NULL | PTR_TRUSTED`. The kfunc iterator depends on BPF kfunc registration elsewhere and on the same CSS traversal helpers.

## Risks and test signals
Risks include the single-session seq limitation surprising readers, dead cgroups being skipped silently, holding `cgroup_mutex` while running iterator programs, refcount imbalance between attach and seq init/fini, namespace-sensitive fdinfo paths, and opaque iterator size/alignment drift. Test signals include all five traversal orders, fd-vs-id-vs-root attach, invalid order rejection, early termination, NULL final callback, dead cgroup skip, partial reads returning `-EOPNOTSUPP`, fdinfo path under cgroup namespaces, and kfunc iterator behavior for descendants, children, and ancestors.
