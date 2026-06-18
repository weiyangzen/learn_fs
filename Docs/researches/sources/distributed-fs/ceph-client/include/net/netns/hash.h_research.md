# sources/distributed-fs/ceph-client/include/net/netns/hash.h

Purpose: Stores per-network-namespace hash seeds for networking hash functions.

Important APIs/types/functions: `struct netns_hash` contains a single `u32 mix` value.

Control flow: Namespace setup initializes `mix`; hashing code combines it with tuple or object data to avoid shared global hash behavior across namespaces.

State and persistence: Runtime per-net randomization state.

Dependencies/integration: Depends on net namespace initialization and consumers that need per-net hash salt.

Risks/test signals: Test seed initialization, namespace isolation, deterministic behavior only where expected, and no zero/uninitialized use.
