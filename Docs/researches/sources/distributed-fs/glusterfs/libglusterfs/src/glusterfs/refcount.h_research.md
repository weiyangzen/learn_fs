# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/refcount.h

Purpose: `refcount.h` provides a small embedded atomic reference-counting helper with a release callback and convenience macros for structures that include `GF_REF_DECL`.

Important APIs and types: `gf_ref_t` contains an atomic `cnt`, a `gf_ref_release_t`, and release data. `_gf_ref_init` initializes a refcount, `_gf_ref_get` attempts to acquire a reference, and `_gf_ref_put` drops one and invokes release when the count reaches zero. Macros `GF_REF_INIT`, `GF_REF_GET`, and `GF_REF_PUT` operate on embedded `_ref` members.

Control flow and state: state is per-object. The release callback receives the owning object pointer when used through the macros. `_gf_ref_get` returns NULL/0 when a reference cannot be taken, protecting against resurrecting a dead object if implemented with compare-and-swap semantics.

Dependencies and integration: depends on Gluster atomics. It is a common primitive for async graph, inode, fd, rpc, or transport objects that outlive a single stack frame.

Risks: finalizer reentrancy and object ownership are outside the header. Callers must avoid using objects after `GF_REF_PUT` returns zero. Missing initial reference or unbalanced get/put causes leaks or premature destruction.

Test signals: concurrent get/put race tests, release-called-once assertions, get-after-zero behavior, and sanitizer coverage around finalizer paths are important.
