# sources/distributed-fs/ceph-client/kernel/bpf/crypto.c

## Purpose
`crypto.c` exposes kernel crypto operations to selected BPF program types through BTF kfuncs. It manages a registry of `struct bpf_crypto_type` providers, creates refcounted `struct bpf_crypto_ctx` objects from BPF-provided parameters, and implements encrypt/decrypt calls over BPF dynptr buffers.

## Important APIs, types, and functions
`struct bpf_crypto_params` is the BPF ABI for context creation: operation `type`, algorithm name, key material, key length, and optional authentication size. `struct bpf_crypto_ctx` stores the selected provider, provider transform pointer, IV/state length, RCU head, and refcount. `bpf_crypto_register_type()` and `bpf_crypto_unregister_type()` maintain the global provider list under `bpf_crypto_types_sem` and are exported GPL symbols for crypto provider modules. `bpf_crypto_ctx_create()` is a sleepable acquire kfunc for `BPF_PROG_TYPE_SYSCALL`; `bpf_crypto_ctx_acquire()` and `bpf_crypto_ctx_release()` implement kptr-style ownership; `bpf_crypto_encrypt()` and `bpf_crypto_decrypt()` are RCU kfuncs for sched cls, sched act, and XDP.

## Control flow
Provider registration rejects duplicate names, allocates a list node, and links it under a write semaphore. Context creation validates the parameter size and reserved bytes, finds a provider by name with `try_module_get()`, checks algorithm support, authsize compatibility, key length, allocates the context, allocates the provider transform, optionally sets authsize, sets the key, rejects transforms still reporting `CRYPTO_TFM_NEED_KEY`, calculates `siv_len`, and returns a refcount-one object. Any failure unwinds transform, context, and module references. Encrypt/decrypt calls funnel through `bpf_crypto_crypt()`, which validates dynptr mutability and sizes, maps source, destination, and optional state/IV dynptr memory, checks `siv_len`, then dispatches to the provider's `encrypt` or `decrypt` method.

## State and persistence behavior
The provider registry is global process-lifetime kernel state guarded by an rwsem. Crypto contexts are heap objects whose lifetime is explicit through BPF kfunc acquire/release semantics and map kptr destructors. Final release uses `call_rcu()` before freeing the transform and dropping the provider module reference, so BPF-side RCU readers can finish safely.

## Dependencies and integration points
The file depends on BTF kfunc registration, BPF dynptr internals, the Linux crypto API abstraction in `linux/bpf_crypto.h`, module reference counting, and BPF memory/kptr destructor infrastructure. `crypto_kfunc_init()` registers init kfuncs for syscall programs, encrypt/decrypt kfuncs for XDP and TC program types, and a destructor kfunc for `struct bpf_crypto_ctx`.

## Risks and test signals
Risk is concentrated around ABI validation, object lifetime, and dynptr mutability. Useful tests should cover malformed `bpf_crypto_params`, missing or duplicate providers, module unload after context creation, authsize mismatch, zero/oversized keys, wrong SIV length, readonly destination dynptr rejection, successful encryption/decryption round trips, kptr map storage, acquire/release balancing, and RCU-safe use from XDP/TC. Provider unregister while contexts still exist should not free provider code because each context holds a module reference.
