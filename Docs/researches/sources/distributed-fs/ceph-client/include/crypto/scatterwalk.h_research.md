# sources/distributed-fs/ceph-client/include/crypto/scatterwalk.h

Purpose: defines scatterlist walking and copy helpers used by crypto code to process segmented buffers safely.

Important APIs, types, and flow: inline helpers initialize walks at an SG entry or byte position, clamp available bytes to page boundaries and remaining segment length, expose current SG lists, map/unmap current pages, advance within chained SGs, flush destination dcache pages, and mark source/destination completion. Copy helpers move bytes between linear buffers and scatterwalks or SG lists, map-and-copy fixed ranges, and fast-forward an SG view with `scatterwalk_ffwd()`.

State and persistence: `struct scatter_walk` state is transient traversal state over caller-owned SGs. No persistence exists.

Dependencies and integration: depends on scatterlists, highmem/page mapping, chain markers, and cache maintenance. It is central to skcipher, ahash, AEAD, and compression walk code.

Risks and test signals: off-by-one page/segment advancement, incorrect dcache flushing, and SG chain handling can corrupt data or leak stale cache contents. Signals include crypto self-tests with highly fragmented SGs, unaligned offsets, highmem pages, chained SG lists, in-place transforms, and KASAN/KMSAN coverage.
