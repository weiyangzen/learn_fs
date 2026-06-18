# sources/distributed-fs/ceph-client/kernel/bpf/trampoline.c

## Purpose

`trampoline.c` manages BPF trampolines used by fentry, fexit, fmod_ret, fsession, LSM, and freplace programs. It maps attach targets to generated executable trampoline images, patches kernel call sites through ftrace direct calls or architecture text pokes, tracks attached programs, and provides enter/exit routines for recursion, RCU, migration, sleepable execution, and runtime statistics.

## Important APIs, Types, And Functions

- Registries and locking: `trampoline_key_table`, `trampoline_ip_table`, and `trampoline_mutex` map trampoline keys and IPs to `struct bpf_trampoline`; each trampoline also has `tr->mutex`.
- Capability check: `bpf_prog_has_trampoline()` identifies tracing/LSM program attach types that use trampolines.
- Image symbols: `bpf_image_ksym_init()`, `bpf_image_ksym_add()`, and `bpf_image_ksym_del()` publish trampoline images to BPF kallsyms and perf ksymbol events.
- Ftrace/direct ops: `direct_ops_alloc/free/add/del/mod()`, `bpf_tramp_ftrace_ops_func()`, `register_fentry()`, `modify_fentry()`, and `unregister_fentry()` abstract config-specific call-site patching.
- Lookup and lifecycle: `bpf_trampoline_lookup()`, `bpf_trampoline_get()`, and `bpf_trampoline_put()`.
- Image lifecycle: `bpf_tramp_image_alloc()`, `bpf_tramp_image_put()`, and RCU/percpu-ref callbacks free generated executable code after readers are gone.
- Program attach: `bpf_trampoline_link_prog()`, `__bpf_trampoline_link_prog()`, `bpf_trampoline_unlink_prog()`, and `bpf_attach_type_to_tramp()`.
- Cgroup LSM shim support: `bpf_trampoline_link_cgroup_shim()` and `bpf_trampoline_unlink_cgroup_shim()`.
- Runtime hooks: `bpf_trampoline_enter()`, `bpf_trampoline_exit()`, `__bpf_prog_enter*()`, `__bpf_prog_exit*()`, `__bpf_tramp_enter()`, and `__bpf_tramp_exit()`.
- Weak arch hooks: `arch_prepare_bpf_trampoline()`, `arch_alloc_bpf_trampoline()`, `arch_free_bpf_trampoline()`, `arch_protect_bpf_trampoline()`, and `arch_bpf_trampoline_size()`.

## Control Flow

`bpf_trampoline_get()` obtains or creates a trampoline by key and target IP, initializes the function model/address from attach-target metadata, and returns a refcounted object. Linking a program classifies it as fentry, fexit, modify-return, fsession, LSM modify-return/fexit, or freplace. Freplace is exclusive: it rejects existing fentry/fexit users, marks the target program extended, and patches the target directly to jump to the replacement. Other kinds are inserted into per-kind hlist arrays and trigger `bpf_trampoline_update()`.

`bpf_trampoline_update()` snapshots attached links, derives flags for call-original, restore-registers, skip-frame, IP-argument, shared IPMODIFY, and tail-call context, asks the architecture for image size, allocates executable memory, prepares and protects the trampoline image, and then registers or modifies the call site. When replacing an old image, it publishes the new one first and retires the old one through `bpf_tramp_image_put()`.

Image retirement is multi-stage. Trampolines that call the original function patch their epilogue path to avoid fexit execution, wait for Tasks RCU and/or percpu refs around original-function execution, then free through workqueue and RCU. Fentry-only images use RCU Tasks Trace and Tasks RCU to cover sleepable and non-sleepable code regions.

Runtime enter/exit functions are selected based on program sleepability, recursion tracking, and LSM cgroup shim status. They set BPF run context, acquire the right RCU flavor, disable migration where needed, update stats under the static key, and restore state on exit.

## State And Persistence Behavior

Each trampoline persists while refcounted by attached links or lookup users. It stores target key/IP/function model, current image, flags, direct ftrace ops, extension program, per-kind attached link lists, and counts. Generated images persist separately until all possible executing contexts have passed the required grace periods. Freplace marks target program aux state (`is_extended`) while active.

## Dependencies And Integration Points

This file is used by tracing and extension attach paths in `syscall.c`. It integrates with ftrace direct-call APIs, architecture BPF trampoline generation, BTF attach target models, BPF verifier attach checks, JIT executable memory accounting, BPF kallsyms, perf ksymbol events, RCU/RCU Tasks/RCU Tasks Trace, percpu refs, static calls/ftrace IPMODIFY sharing, BPF LSM cgroup shims, and BPF runtime stats.

## Risks And Edge Cases

The main risks are live-code patching races, incompatible ftrace IPMODIFY sharing, stale executable images, and exclusivity violations between freplace and fentry/fexit. Lock ordering is subtle: normal order is trampoline mutex before ftrace direct mutex before ftrace lock, but ftrace callbacks sometimes require trylocking to avoid deadlock. Grace-period selection must match whether trampoline code can sleep, call original functions, or execute fexit/fmod_ret sections. Architecture weak defaults return `-ENOTSUPP`; each supported architecture must implement size, prepare, allocation/protection, and text-poke semantics correctly.

## Test Signals

Tests should cover fentry, fexit, fmod_ret, fsession, LSM, and freplace attachment and detachment; freplace rejection when target programs are tail-call entries or already have fentry/fexit; concurrent attach/detach/update under ftrace direct-call configs; sleepable tracing programs; runtime stats; recursion miss accounting; cgroup LSM shim reuse and release; module target lifetime; and architecture-specific trampoline image bounds and cleanup under stress.
