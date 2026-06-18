<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skbuff_ref.h -->
# sources/distributed-fs/ceph-client/include/linux/skbuff_ref.h

## Purpose
`skbuff_ref.h` isolates small inline helpers for taking and dropping references on skb page fragments. It complements `skbuff.h` by centralizing fragment refcount behavior, including optional page-pool recycling for receive pages.

## Important APIs, Types, and Functions
The exported inline helpers are `__skb_frag_ref()`, `skb_frag_ref()`, `skb_page_unref()`, `__skb_frag_unref()`, and `skb_frag_unref()`. The only out-of-line declaration is `napi_pp_put_page(netmem_ref netmem)`, compiled under page-pool support through `skb_page_unref()`. The helpers operate on `skb_frag_t`, `netmem_ref`, `struct sk_buff`, and `skb_shared_info`.

## Control Flow
Reference acquisition is direct: `__skb_frag_ref()` obtains the fragment netmem via `skb_frag_netmem()` and calls `get_netmem()`, while `skb_frag_ref()` selects `skb_shinfo(skb)->frags[f]`. Release flow uses `skb_page_unref()`: with `CONFIG_PAGE_POOL`, a recyclable fragment first tries `napi_pp_put_page()`; if recycling succeeds, normal release is skipped. Otherwise `put_netmem()` drops the underlying reference. `skb_frag_unref()` avoids unref for managed zerocopy skbs because those fragment references are owned by the zerocopy `ubuf_info` lifecycle rather than by normal skb fragment ownership.

## State and Persistence Behavior
The file manages transient reference counts for fragment backing memory. It does not store state itself. The relevant persistent state is the fragment's `netmem_ref`, the skb's shared-info fragment array, `skb->pp_recycle`, and zerocopy flags in `skb_shared_info`.

## Dependencies and Integration Points
It includes `linux/skbuff.h` and depends on the `netmem` abstraction, page pool support, NAPI recycling, and zerocopy metadata. It is used by skb clone/copy/free paths and drivers that duplicate or release paged fragments.

## Risks and Test Signals
The primary risk is ownership mismatch: dropping a managed zerocopy fragment, failing to recycle page-pool memory, or leaking references by missing `skb_frag_unref()`. Test signals include page refcount leaks, page_pool recycling stats, KASAN use-after-free reports, zerocopy send completion tests, and RX stress tests that clone and free fragmented skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skbuff_ref.h -->
