# sources/distributed-fs/ceph-client/crypto/scatterwalk.c

Purpose: provides scatterlist walking and copying helpers used by crypto algorithms and templates.

Important APIs and functions: exported functions include `scatterwalk_skip()`, `memcpy_from_scatterwalk()`, `memcpy_to_scatterwalk()`, `memcpy_from_sglist()`, `memcpy_to_sglist()`, `memcpy_sglist()`, and `scatterwalk_ffwd()`.

Control flow: skip advances a scatter walk by consuming entries until the target offset is reached. Copy helpers repeatedly map walk segments with `scatterwalk_next()`, copy bytes, and mark source or destination completion. `memcpy_sglist()` copies between two scatterlists, handling no-op exact-overlap cases, highmem page mapping, same-page different-offset copies, dcache flushes, and multi-entry advancement. `scatterwalk_ffwd()` returns a scatterlist view advanced by `len`, either the original entry when exact or a two-entry chained temporary starting inside the current page.

State and persistence: no persistent state is kept. Walk state is caller-owned and updated in place. Temporary chained scatterlists are caller-provided.

Dependencies and integration points: depends on scatterlist APIs, highmem mapping, page cache helpers, and crypto scatterwalk inline helpers. Used by AEAD templates such as `krb5enc` and `seqiv`, plus compression and SG bridge code.

Risks: partial overlap beyond exact same-memory no-op is unsupported in `memcpy_sglist()`. Highmem handling must not cross page boundaries without mapping each page. `scatterwalk_ffwd()` assumes the source list contains enough length. Cache flush correctness matters on non-coherent architectures.

Test signals: copies across SG entry boundaries, highmem pages, same-page overlap/no-op, zero-length NULL cases, advanced views in templates, and dcache-sensitive architectures.
