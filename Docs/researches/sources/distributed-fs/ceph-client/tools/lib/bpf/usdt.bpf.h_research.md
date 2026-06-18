## sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.bpf.h

Purpose: Provides BPF-side helpers, maps, and macros for libbpf USDT probe programs.

Important APIs/types: `struct __bpf_usdt_arg_spec` and `struct __bpf_usdt_spec` mirror user-space `usdt.c`. Weak maps `__bpf_usdt_specs` and `__bpf_usdt_ip_to_spec_id` hold argument specifications and fallback IP-to-spec mappings. Helpers include `bpf_usdt_arg_cnt()`, `bpf_usdt_arg_size()`, `bpf_usdt_arg()`, `bpf_usdt_cookie()`, and `BPF_USDT()` handler wrapper.

Control flow: Runtime lookup obtains a spec ID from BPF cookie when available, otherwise from current IP. Argument fetch validates bounds, decodes constant/register/register-deref/SIB modes, reads pt_regs or user memory, applies endian-size normalization and sign extension, and returns a `long`.

State/persistence: Persistent state is in BPF maps populated by libbpf during attach. The header itself is weak-map based so user objects include support maps automatically.

Dependencies/integration: Depends on BPF helpers, tracing register macros, kernel config extern `LINUX_HAS_BPF_COOKIE`, and exact layout agreement with `usdt.c`.

Risks: Layout drift between BPF and user-space structs breaks argument decoding. Unsupported arch/register encodings are rejected in user space. Without BPF cookie support, IP map sizing and collisions matter. BPF verifier bounds are protected by `barrier_var()`.

Test signals: USDT selftests should cover all arg modes, signed and unsigned 1/2/4/8-byte values, big/little endian behavior, BPF cookie and IP-map paths, cookie retrieval, argument count/size helpers, and `BPF_USDT()` macro expansion.
