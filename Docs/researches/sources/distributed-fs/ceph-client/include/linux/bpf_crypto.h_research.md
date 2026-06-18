# sources/distributed-fs/ceph-client/include/linux/bpf_crypto.h

Purpose: Declares a pluggable crypto provider interface for BPF crypto kfunc/helper support. It lets crypto implementations register an algorithm family with BPF without exposing concrete transform internals.

Important APIs/types/functions: `struct bpf_crypto_type` contains callbacks to allocate/free transforms, check algorithm availability, set key and authentication size, encrypt/decrypt buffers with an IV, report IV/state sizes, read transform flags, hold the owning module, and publish a short provider name. `bpf_crypto_register_type()` and `bpf_crypto_unregister_type()` manage provider registration.

Control flow: A provider fills `bpf_crypto_type`, registers it, and BPF crypto logic later resolves algorithms through the registered type, allocates transforms, configures keys/auth size, invokes encrypt/decrypt, and releases the transform. Module ownership is expected to pin provider code while used.

State/persistence: Provider registrations persist until unregister. Per-transform state is opaque `void *tfm` owned by the provider callbacks. The type structure is const from the caller perspective and includes module/name identity.

Dependencies/integration: Depends on kernel crypto providers, BPF kfunc/helper implementation, module lifetime management, and UAPI-visible BPF crypto behavior elsewhere.

Risks/test signals: Risks include module unload races, mismatched IV/auth/key sizes, algorithm-name validation issues, transform leaks, and provider callback behavior differences. Test signals include BPF crypto selftests for register/unregister, encrypt/decrypt known-answer vectors, unsupported algorithm handling, module unload under active use, and fault injection for allocation/setkey failures.
