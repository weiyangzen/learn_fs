<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skbuff.h -->
# sources/distributed-fs/ceph-client/include/linux/skbuff.h

## Purpose
`skbuff.h` is the central public header for Linux kernel socket buffers. It defines the `struct sk_buff` metadata object, the shared data trailer `struct skb_shared_info`, fragment descriptors, queue heads, timestamp/checksum/GSO constants, and a large set of inline helpers used by the networking stack and network drivers to allocate, clone, queue, reshape, checksum, timestamp, and free packet buffers. In this Ceph client source tree it is kernel infrastructure rather than Ceph-specific code, but Ceph networking indirectly relies on its contracts through sockets, TCP, and message transport paths.

## Important APIs, Types, and Functions
The main types are `struct sk_buff`, `struct sk_buff_head`, `skb_frag_t`, `struct skb_shared_info`, `struct skb_shared_hwtstamps`, `struct ubuf_info`, `struct ubuf_info_msgzc`, `struct skb_seq_state`, and optional `struct skb_ext`. `struct sk_buff` stores ownership, device, timestamps, control buffer, routing destination, netfilter state, packet lengths, checksum state, hash state, VLAN/encapsulation headers, header offsets, linear data pointers, truesize, and reference count. `struct skb_shared_info` lives at the end of the data allocation and stores fragment arrays, GSO metadata, tx timestamp flags, zerocopy state, dataref, and frag lists.

Allocation and lifetime APIs include `__alloc_skb()`, `alloc_skb()`, `alloc_skb_fclone()`, `build_skb()`, `napi_build_skb()`, `netdev_alloc_skb()`, `napi_alloc_skb()`, `skb_clone()`, `skb_copy()`, `__pskb_copy()`, `pskb_expand_head()`, `skb_unclone()`, `skb_share_check()`, `skb_unshare()`, `kfree_skb_reason()`, `kfree_skb()`, `consume_skb()`, `skb_unref()`, and `skb_data_unref()`. Queue APIs include `skb_queue_head_init()`, `__skb_queue_head()`, `skb_queue_head()`, `__skb_queue_tail()`, `skb_queue_tail()`, `skb_dequeue()`, `skb_unlink()`, splicing helpers, and queue/rbtree walk macros.

Data geometry helpers include `skb_headlen()`, `skb_pagelen()`, `skb_put()`, `__skb_put()`, `skb_push()`, `__skb_push()`, `skb_pull()`, `pskb_may_pull()`, `pskb_pull()`, `skb_reserve()`, `skb_headroom()`, `skb_tailroom()`, `skb_trim()`, `pskb_trim()`, `skb_linearize()`, `skb_cow()`, and `skb_cow_head()`. Header helpers cover MAC/network/transport and inner header offset tracking. Fragment helpers include `skb_fill_page_desc()`, `skb_add_rx_frag()`, `skb_frag_page()`, `skb_frag_netmem()`, `skb_frag_dma_map()`, `skb_can_coalesce()`, and page-pool/XDP copy-on-write entry points.

Checksum and offload helpers define `CHECKSUM_NONE`, `CHECKSUM_UNNECESSARY`, `CHECKSUM_COMPLETE`, `CHECKSUM_PARTIAL`, `SKB_GSO_*`, `skb_csum_unnecessary()`, `skb_checksum_complete()`, `skb_checksum_validate*()`, `skb_remcsum_process()`, `skb_partial_csum_set()`, `skb_checksum_setup()`, `lco_csum()`, and helpers that update checksums after push/pull/trim. Timestamp helpers include `skb_hwtstamps()`, `skb_tx_timestamp()`, `skb_tstamp_tx()`, `skb_set_delivery_time()`, and `skb_tstamp_cond()`. Optional integration helpers cover netfilter connection tracking, security marks, XFRM secpath, BPF redirection metadata, and `CONFIG_SKB_EXTENSIONS`.

## Control Flow
The header is mostly declarations and inline control paths. Allocation starts with an skb metadata object plus a data area whose tail contains `skb_shared_info`. Append/prepend/remove operations mutate `data`, `tail`, `len`, `data_len`, and header offsets while enforcing linear/nonlinear constraints. When requested bytes are not in the linear head, `pskb_may_pull_reason()` expands the linear area via `__pskb_pull_tail()` and returns a drop reason on short packet or allocation failure.

Reference control splits into skb object references (`users`) and shared-data references (`skb_shared_info.dataref`). `skb_unref()` decides whether the skb metadata can be freed; `skb_data_unref()` handles cloned data and payload-only clones using the high half of `dataref`. Headerless transport clones use `__skb_header_release()` to mark payload-only references and preserve writable headroom for lower layers. Copy-on-write paths call `pskb_expand_head()` when data or headers are shared or headroom is insufficient.

Queue flow uses `struct sk_buff_head` as a sentinel whose first two members match `sk_buff` list links. Lockless variants use `READ_ONCE`/`WRITE_ONCE`; public queue operations have locking counterparts implemented out of line. Zerocopy flow attaches `ubuf_info` through `skb_shared_info.destructor_arg`, increments refs through `net_zcopy_get()`, and completes via `uarg->ops->complete()` from `skb_zcopy_clear()`. Checksum flow uses `ip_summed`, `csum`, `csum_start`, and `csum_offset`; mutations either adjust `CHECKSUM_COMPLETE` or fall back to `CHECKSUM_NONE`.

## State and Persistence Behavior
All state is in live kernel memory and is transient per packet. The object may persist across queues, retransmit structures, socket error queues, NAPI processing, driver rings, or deferred free lists until the final reference is released. Persistent-looking fields such as `mark`, `priority`, `secmark`, VLAN data, hash, timestamp, destination pointer, and netfilter state are packet metadata propagated across networking layers. No on-disk persistence exists.

Concurrency is caller-sensitive. Queue locks protect `sk_buff_head`; RCU is required when using noref destination entries; reference counts protect shared skb objects and data; fragments may be page-backed, netmem-backed, unreadable device memory, or page-pool recyclable. Header comments explicitly warn that peeked queue entries and non-refcounted dst pointers are volatile.

## Dependencies and Integration Points
This header depends on core kernel types, refcounting, atomics, spinlocks, RCU, DMA mapping, flow dissectors, checksum helpers, page fragments, netmem, netdevice features, drop reasons, sockets, BPF, netfilter, XFRM, traffic control, NAPI, GRO/GSO, page_pool, and optional timestamping. Network drivers integrate through allocation helpers, DMA mapping, checksum/GSO feature checks, RX hash setters, RX queue recording, timestamp completion, and free/recycle helpers. Protocol stacks integrate through header offset helpers, skb queues, datagram copy/receive APIs, COW helpers, and checksum validation.

## Risks and Test Signals
Major risks are stale or missing reference ownership, wrong checksum state after packet mutation, writing into cloned data without COW, using queue peek references without locks, invalid header offsets, assuming nonlinear data is contiguous, mishandling page-pool recycling, DMA mapping unreadable net_iov fragments incorrectly, or confusing noref dst pointers with refcounted pointers. Useful signals are `CONFIG_DEBUG_NET` warnings and dumps, KASAN/KMSAN/KCSAN reports, refcount splats, lockdep around queue locks, packetdrill or selftests covering checksum/GSO/fragmentation, driver tests that exercise RX fragment coalescing and DMA mapping, and BPF/netfilter/tc tests that clone, redirect, and mutate skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skbuff.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skmsg.h -->
# sources/distributed-fs/ceph-client/include/linux/skmsg.h

## Purpose
`skmsg.h` defines the kernel socket-message and psock infrastructure used by BPF sockmap/sockhash and stream parser/verdict paths. It represents message payloads as scatterlists, tracks BPF programs attached to sockets, and provides helpers for queuing, receiving, redirecting, and freeing messages.

## Important APIs, Types, and Functions
Core types are `struct sk_msg_sg`, `struct sk_msg`, `struct sk_psock_progs`, `struct sk_psock_link`, `struct sk_psock_work_state`, and `struct sk_psock`. `sk_msg_sg` is a ring of scatterlist elements with `start`, `curr`, `end`, `size`, `copybreak`, and a bitmap marking copied entries. `sk_msg` embeds `sk_msg_sg` first for UAPI assumptions, adds BPF-visible `data`/`data_end`, cork/apply counters, flags, skb pointer, redirect socket, owning socket, and list linkage. `sk_psock` stores the attached socket, redirect socket, BPF programs and links, optional stream parser state, ingress skb/message queues, locks, total queued message length, protocol callback backups, work items, and refcount.

Important functions include `sk_msg_alloc()`, `sk_msg_clone()`, `sk_msg_trim()`, `sk_msg_free*()`, `sk_msg_return*()`, `sk_msg_zerocopy_from_iter()`, `sk_msg_memcopy_from_iter()`, `sk_msg_recvmsg()`, `__sk_msg_recvmsg()`, `sk_msg_is_readable()`, `sk_psock_init()`, `sk_psock_stop()`, `sk_psock_msg_verdict()`, `sk_psock_drop()`, and optional stream-parser functions. Inline helpers initialize ring state, move scatterlist bytes, compute data pointers, add pages, set/clear copy bits, queue/dequeue ingress messages, manage psock refs, restore protocol callbacks, report errors, and handle skb BPF redirection flags.

## Control Flow
Message flow starts by initializing an `sk_msg`, filling its scatterlist from copied or zerocopy iter data, and exposing the current element through `data`/`data_end` unless it is marked copied. Ring iteration wraps at `NR_MSG_FRAG_IDS`, allowing partitioned scatterlists and crypto chaining entries. Verdict flow runs through psock state and BPF programs; messages may be passed, dropped, or redirected.

Ingress queue flow is protected by `psock->ingress_lock`. `sk_psock_queue_msg()` appends to `ingress_msg` only while `SK_PSOCK_TX_ENABLED` is set; otherwise it frees the message. Dequeue/peek helpers update `msg_tot_len` with `WRITE_ONCE` so ioctl-style lockless readers can use `READ_ONCE`. Refcount flow uses `sk_psock_get()` under RCU and `sk_psock_put()` to call `sk_psock_drop()` on the last reference. Program replacement uses `xchg()` or `cmpxchg()` to safely drop old BPF program references.

## State and Persistence Behavior
State is per socket and per message, all in memory. `sk_psock` persists while attached to a socket and holds saved protocol callbacks so teardown can restore socket behavior. Queued ingress messages and skbs persist until received, dropped, or psock teardown. BPF program references and links persist in `sk_psock_progs` until explicitly replaced or dropped. There is no disk persistence.

## Dependencies and Integration Points
The header depends on BPF, filters, scatterlists, skbuffs, socket internals, TCP, and stream parser infrastructure. It integrates with sockmap/sockhash, TLS stream parser support, BPF verdict programs, socket callbacks (`data_ready`, `write_space`, `close`, `destroy`, `unhash`), skb redirection metadata (`_sk_redir`), and memory allocation helpers such as `kzalloc_obj()`.

## Risks and Test Signals
Key risks are scatterlist ring wrap mistakes, incorrect copy-bit handling, message length accounting races, psock refcount misuse, failing to restore socket protocol callbacks, BPF program reference leaks, and stale redirect socket pointers. Useful signals are BPF sockmap selftests, strparser/TLS tests, KASAN/KCSAN reports, refcount warnings, lockdep around `ingress_lock` and callback locks, and tests that exercise corking, redirect, drop, recvmsg, and psock teardown while traffic is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/skmsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slab.h -->
# sources/distributed-fs/ceph-client/include/linux/slab.h

## Purpose
`slab.h` is the public kernel memory allocation API for slab caches, `kmalloc()` families, typed object allocation helpers, `kvmalloc()` fallbacks, and corresponding free/barrier functions. It abstracts allocator implementation details behind a stable interface used by nearly every kernel subsystem, including networking and filesystem clients.

## Important APIs, Types, and Functions
The file defines slab flag bits and public flags such as `SLAB_CONSISTENCY_CHECKS`, `SLAB_RED_ZONE`, `SLAB_POISON`, `SLAB_HWCACHE_ALIGN`, `SLAB_CACHE_DMA`, `SLAB_CACHE_DMA32`, `SLAB_STORE_USER`, `SLAB_PANIC`, `SLAB_TYPESAFE_BY_RCU`, `SLAB_TRACE`, `SLAB_NOLEAKTRACE`, `SLAB_NO_MERGE`, `SLAB_ACCOUNT`, `SLAB_KASAN`, `SLAB_SKIP_KFENCE`, `SLAB_RECLAIM_ACCOUNT`, `SLAB_NO_OBJ_EXT`, and `SLAB_OBJ_EXT_IN_OBJ`. It defines `ZERO_SIZE_PTR` and `ZERO_OR_NULL_PTR()` for zero-sized allocation behavior.

`struct kmem_cache_args` carries modern cache creation parameters: object alignment, usercopy region, custom free pointer offset, constructor, and optional sheaf capacity. Cache APIs include `__kmem_cache_create_args()`, `kmem_cache_create()`, `kmem_cache_create_usercopy()`, `KMEM_CACHE()`, `KMEM_CACHE_USERCOPY()`, `kmem_cache_destroy()`, `kmem_cache_shrink()`, `kmem_cache_alloc()`, `kmem_cache_alloc_lru()`, `kmem_cache_charge()`, `kmem_cache_free()`, bulk alloc/free functions, NUMA allocation, and sheaf prefill/refill/return helpers.

General allocation APIs include `kmalloc()`, `kmalloc_node()`, `kmalloc_array()`, `krealloc()`, `krealloc_array()`, `kcalloc()`, `kzalloc()`, `kvmalloc()`, `kvzalloc()`, `kvmalloc_array()`, `kvcalloc()`, `kvrealloc()`, `kmalloc_track_caller()`, `kmem_buckets_alloc()`, `kfree()`, `kfree_sensitive()`, `kvfree()`, `kvfree_atomic()`, and `kvfree_sensitive()`. Typed helpers include `kmalloc_obj()`, `kmalloc_objs()`, `kmalloc_flex()`, and zeroed/vmalloc-backed aliases.

## Control Flow
Cache creation routes through `kmem_cache_create()` macro dispatch. `_Generic()` selects either the modern four-argument form with `struct kmem_cache_args`, the default-args wrapper for `NULL`, or the legacy align/flags/ctor form. Allocations from named caches use `kmem_cache_alloc*()` wrappers around non-profiling functions via `alloc_hooks()`.

`kmalloc()` uses a fast inline constant-size path. If the size is compile-time constant and exceeds `KMALLOC_MAX_CACHE_SIZE`, it calls the large page allocator path. Otherwise it maps the size to a bucket index using `kmalloc_index()`, selects a cache type with `kmalloc_type()` based on GFP flags and optional randomization, and calls `__kmalloc_cache_noprof()`. Dynamic sizes fall back to `__kmalloc_noprof()`. Array helpers perform overflow checks with `check_mul_overflow()` before allocating. `kvmalloc()` routes to vmalloc-capable allocation for large or fallback allocations.

## State and Persistence Behavior
Slab caches are persistent in-kernel allocator state until destroyed. Allocated objects persist until freed by the matching free API; zero-sized allocation returns `ZERO_SIZE_PTR`, which is freeable but not dereferenceable. Cache flags influence debugging, memory accounting, reclaim grouping, KASAN/KFENCE behavior, cache merging, DMA zones, and RCU-safe page lifetime. Sheaf settings add per-CPU/per-node object batching for configured caches.

## Dependencies and Integration Points
The header depends on GFP flags, overflow helpers, RCU, workqueues, percpu refcounting, cleanup attributes, hashing, KASAN, allocation tags, NUMA constants, and architecture alignment definitions. It integrates with memcg, KASAN, KFENCE, kmemleak, SLUB debug, fault injection, slab buckets, page allocator large allocation paths, and RCU delayed free barriers.

## Risks and Test Signals
Common risks are integer overflow in object arrays, using `GFP_KERNEL` from atomic context, assuming zero-sized allocations return `NULL`, freeing with the wrong cache, misuse of `SLAB_TYPESAFE_BY_RCU` without independent object validation, incorrect usercopy whitelists, sensitive data not cleared before free, and hidden behavior changes from cache merging or debug flags. Test signals include KASAN/KFENCE/KMSAN reports, memcg charge failures, slabinfo anomalies, kmemleak, fault-injection tests, lockdep around allocation contexts, KUnit slab tests, and targeted tests for overflow-safe allocation helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slimbus.h -->
# sources/distributed-fs/ceph-client/include/linux/slimbus.h

## Purpose
`slimbus.h` declares the Linux SLIMbus client-driver interface. SLIMbus is a low-power multi-drop bus often used for audio codecs and related components. The header defines device identity, driver registration, value/information element transfers, and stream-management APIs.

## Important APIs, Types, and Functions
The main types are `struct slim_eaddr`, `enum slim_device_status`, `struct slim_device`, `struct slim_driver`, `struct slim_val_inf`, and `struct slim_stream_config`. `slim_device` wraps `struct device`, enumeration address, controller pointer, logical address state, status, and a stream list protected by a spinlock. `slim_driver` provides `probe`, `remove`, `shutdown`, `device_status`, driver core metadata, and an id table.

Driver registration uses `slim_driver_register()`, `__slim_driver_register()`, `slim_driver_unregister()`, and `module_slim_driver()`. Device helpers include `slim_get_devicedata()`, `slim_set_devicedata()`, `of_slim_get_device()`, `slim_get_device()`, and `slim_get_logical_addr()`. Messaging APIs include `slim_xfer_msg()`, `slim_readb()`, `slim_writeb()`, `slim_read()`, and `slim_write()`. Stream APIs include `slim_stream_allocate()`, `slim_stream_prepare()`, `slim_stream_enable()`, `slim_stream_disable()`, `slim_stream_unprepare()`, and `slim_stream_free()`.

## Control Flow
The driver model flow is standard bus binding: a controller enumerates devices, assigns logical addresses, and the bus matches `slim_driver` entries by id table. Driver callbacks handle probe/remove and status changes when devices appear, disappear, or lose logical address validity. Element transfer flow builds `slim_val_inf` with offset, buffers, byte count, and optional completion, then submits it with a message code such as request/reply/change information or value. Stream flow allocates a per-device runtime, prepares it with channel/port/rate/format settings, enables data movement, disables it, unprepares, and frees it.

## State and Persistence Behavior
SLIMbus state is in kernel device objects and controller-managed runtime state. `slim_device.status`, `laddr`, and `is_laddr_valid` reflect bus presence and address assignment. Stream state persists in controller-specific `struct slim_stream_runtime` objects and per-device stream lists. No on-disk state exists.

## Dependencies and Integration Points
The header depends on the driver model, modules, completions, device-tree nodes, mod_devicetable IDs, list/spinlock infrastructure, and audio stream conventions (`SNDRV_PCM_STREAM_PLAYBACK`/capture values are referenced by contract). It integrates with SLIMbus controllers, codec/client drivers, device tree lookup, and ASoC-style audio stream setup.

## Risks and Test Signals
Risks include stale logical addresses, racing device status changes with stream operations, invalid channel/port masks, transfers exceeding the 16-byte element message limit, completion lifetime errors for async requests, and mismatched stream prepare/enable/disable/unprepare sequencing. Test signals include bus enumeration tests, device status callback coverage, read/write transaction failures, lockdep around stream list locking, ASoC playback/capture tests, and hotplug or controller reset scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slimbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sm501-regs.h -->
# sources/distributed-fs/ceph-client/include/linux/sm501-regs.h

## Purpose
`sm501-regs.h` is a register map for the Silicon Motion SM501 multifunction graphics/IO controller. It defines offsets and bit fields for system control, GPIO, I2C, UART, USB, display controller, video overlays, hardware cursors, DMA, color-space conversion, and 2D engine blocks.

## Important APIs, Types, and Functions
This file contains preprocessor constants only. Important register base offsets include `SM501_SYS_CONFIG`, `SM501_GPIO`, `SM501_I2C`, `SM501_SSP`, `SM501_UART0`, `SM501_UART1`, `SM501_USB_HOST`, `SM501_USB_GADGET`, `SM501_DC`, `SM501_ZVPORT`, `SM501_AC97`, `SM501_UCONTROLLER`, `SM501_DMA`, `SM501_2D_ENGINE`, and `SM501_2D_ENGINE_DATA`. Important system registers include `SM501_SYSTEM_CONTROL`, `SM501_MISC_CONTROL`, GPIO control/data/DDR/IRQ registers, power gate/clock registers, endian/device-id registers, and programmable PLL control.

Display constants cover panel and CRT control bits, frame-buffer address/offset/width/height registers, timing registers, current line, hardware cursor registers, palette bases, video overlay registers, alpha plane registers, and monitor detect. 2D constants cover source/destination/dimension/control/pitch/color/clip/pattern/window/base/alpha/status registers plus CSC source/destination/pitch/scale/control registers.

## Control Flow
There is no executable control flow. SM501 drivers use these constants to compute MMIO addresses from mapped register bases and to set/clear bit fields. Typical flow is device initialization reading `SM501_DEVICEID`, configuring `SM501_MISC_CONTROL`, enabling unit gates/clocks through power mode registers, setting GPIO/display/USB/UART block registers, and programming display/2D engine registers for framebuffer operations.

## State and Persistence Behavior
The persistent state is hardware register state in the SM501 device, not C state in this header. Register writes persist until reset, suspend/resume restore, firmware/bootloader reconfiguration, or driver changes. Some offsets alias clear/status behavior, such as raw IRQ status/clear and GPIO IRQ status/reset.

## Dependencies and Integration Points
The constants are consumed by SM501 platform, MFD, framebuffer, GPIO, I2C, USB, UART, and acceleration drivers. They pair with `sm501.h` helper APIs for shared register modification and unit power/clock control. Endianness-sensitive accessors are provided in `sm501.h`, not here.

## Risks and Test Signals
Risks are incorrect bit masks, register alias confusion, endian mistakes, programming disabled clock gates, timing values that produce invalid video output, and conflicting writes by multiple child drivers. Test signals include successful device-id detection, framebuffer mode set, GPIO/I2C/UART smoke tests, suspend/resume restore, interrupt clear behavior, 2D engine status transitions, and MMIO tracing around shared registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sm501-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sm501.h -->
# sources/distributed-fs/ceph-client/include/linux/sm501.h

## Purpose
`sm501.h` defines the shared platform interface for Silicon Motion SM501 drivers. It exposes helper functions for power, clocks, and shared register modification, plus platform data structures used by board code and child drivers such as framebuffer and GPIO-I2C support.

## Important APIs, Types, and Functions
Extern helper APIs are `sm501_unit_power()`, `sm501_set_clock()`, `sm501_misc_control()`, and `sm501_modify_reg()`. Platform data types include `struct sm501_platdata_fbsub`, `enum sm501_fb_routing`, `struct sm501_platdata_fb`, `struct sm501_platdata_gpio_i2c`, `struct sm501_reg_init`, `struct sm501_initdata`, `struct sm501_init_gpio`, and `struct sm501_platdata`.

Flag families include framebuffer options (`SM501FB_FLAG_*`), framebuffer platform data flags (`SM501_FBPD_SWAP_FB_ENDIAN`), device-enable bits (`SM501_USE_USB_HOST`, `SM501_USE_UART0`, `SM501_USE_FBACCEL`, `SM501_USE_GPIO`, `SM501_USE_ALL`), and suspend behavior (`SM501_FLAG_SUSPEND_OFF`). Accessors `smc501_readl()` and `smc501_writel()` select big-endian I/O on PPC32 and normal `readl()`/`writel()` elsewhere.

## Control Flow
Board/platform code fills `struct sm501_platdata` with initialization data, GPIO defaults, framebuffer routing/modes, optional power callbacks, and GPIO-I2C bus definitions. The SM501 core driver consumes this during probe to set initial registers and create child devices. Child drivers call the exported helpers to turn units on/off, request clocks, or safely update shared registers with set/clear masks.

## State and Persistence Behavior
State is carried in platform data at probe time and in SM501 hardware registers afterward. `struct sm501_reg_init` pairs masks and set bits for boot-time initialization. Power callbacks and suspend flags define board-specific persistence across low-power transitions. The header itself stores no runtime state.

## Dependencies and Integration Points
The declarations depend on `struct device`, framebuffer mode types, platform device data, and architecture I/O accessors. It integrates with `sm501-regs.h`, SM501 MFD/core code, framebuffer drivers, GPIO and I2C-gpio child devices, USB/UART/SSP/AC97/I2S blocks, and board power-management code.

## Risks and Test Signals
Risks include conflicting child-driver access to shared registers, wrong endian accessor selection, invalid framebuffer routing, missing board power callbacks, and suspend/resume mismatches that leave units powered off or clocks misprogrammed. Test signals include child device probe ordering, register readback after `sm501_modify_reg()`, framebuffer output, GPIO-I2C bus registration, power-cycle/suspend tests, and PPC32 endian-specific coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sm501.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smbdirect.h -->
# sources/distributed-fs/ceph-client/include/linux/smbdirect.h

## Purpose
`smbdirect.h` declares the in-kernel SMB Direct transport interface, mapping SMB over RDMA concepts to socket-like operations. It provides connection setup, negotiated parameter access, send/receive APIs, RDMA read/write memory registration, logging callbacks, and legacy proc diagnostics.

## Important APIs, Types, and Functions
Protocol-facing types are `struct smbdirect_buffer_descriptor_v1`, matching the MS-SMBD buffer descriptor with little-endian offset/token/length, and `struct smbdirect_socket_parameters`, which stores negotiation and transport limits such as timeouts, credits, max send/recv sizes, max RDMA read/write size, FRMR depth, keepalive settings, and port-range flags. Opaque runtime types are `struct smbdirect_socket`, `struct smbdirect_send_batch`, and `struct smbdirect_mr_io`.

Important APIs include RDMA capability helpers `smbdirect_netdev_rdma_capable_node_type()` and `smbdirect_frwr_is_supported()`, socket creation for active and accepted connections, parameter and kernel setting setters/getters, logging setup, connection state/wait helpers, bind/connect/listen/accept/shutdown/release, batched and iterator send functions, receive, send-drain wait, RDMA transmit, memory registration/deregistration, descriptor fill, and debug proc output.

## Control Flow
Active clients create a kernel SMB Direct socket, set initial negotiated parameters and kernel polling/GFP settings, bind if needed, then connect or connect synchronously. Servers create accepting sockets from RDMA CM IDs or listen and accept through the SMB Direct API. Data flow uses send batches or iterator sends for SMB messages, `recvmsg` for receive, and RDMA transmit/register APIs for direct read/write payloads. Memory registration returns an opaque MR object, fills buffer descriptors for the peer, and must be deregistered after use. Logging callbacks let upper layers filter and format events by level and class.

## State and Persistence Behavior
Connection parameters are negotiated at setup and are documented as stable unless explicitly changed. Runtime connection state, credits, pending sends, keepalive timers, registered memory, and RDMA resources live inside opaque socket/MR structures. No disk persistence exists; descriptors are wire-format transient structures.

## Dependencies and Integration Points
The header depends on Linux types, networking namespaces, netdevices, sockets, RDMA CM, InfiniBand attributes, RDMA read/write helpers, scatter/gather iterators, `seq_file`, and proto accept arguments. It integrates with SMB client/server code, RDMA core, network-device capability discovery, and diagnostics/logging paths.

## Risks and Test Signals
Risks include endian/packing mistakes in wire descriptors, negotiated size/credit mismatches, MR lifetime leaks, invalid remote keys, send batching flush errors, blocking waits during teardown, keepalive timeout races, and RDMA capability misdetection. Test signals include SMB Direct negotiation tests, RDMA loopback or soft-RoCE transfers, MR registration/deregistration leak checks, credit exhaustion tests, disconnect/reconnect handling, logging class coverage, and proc debug output consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smbdirect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smc91x.h -->
# sources/distributed-fs/ceph-client/include/linux/smc91x.h

## Purpose
`smc91x.h` defines platform data for the SMC91x Ethernet driver family. It tells the driver which bus access widths and platform quirks are supported and how the device LEDs should be configured.

## Important APIs, Types, and Functions
The file contains flags for access width and behavior: `SMC91X_USE_8BIT`, `SMC91X_USE_16BIT`, `SMC91X_USE_32BIT`, `SMC91X_NOWAIT`, `SMC91X_IO_SHIFT_*`, `SMC91X_IO_SHIFT(x)`, and `SMC91X_USE_DMA`. LED mode constants include `RPC_LED_100_10`, `RPC_LED_RES`, `RPC_LED_10`, `RPC_LED_FD`, `RPC_LED_TX_RX`, `RPC_LED_100`, `RPC_LED_TX`, and `RPC_LED_RX`. `struct smc91x_platdata` carries `flags`, LED A/B modes, and the `pxa_u16_align4` quirk for buggy PXA 16-bit writes at specific alignments.

## Control Flow
There is no executable control flow. Board code supplies `smc91x_platdata` to the Ethernet driver. During probe, the driver interprets flags to choose accessors, I/O address shift, DMA use, and LED configuration. The comments warn that 32-bit support alone is invalid because the driver requires at least 8-bit or 16-bit access.

## State and Persistence Behavior
The only C state is static platform data passed at device registration. Hardware state such as LED mode and bus access behavior is configured by the driver based on this data and persists until device reset or reconfiguration.

## Dependencies and Integration Points
The header depends only on basic C types and `bool`. It integrates with platform-device board files and the SMC91x network driver, especially on embedded systems with nonstandard bus widths or PXA alignment quirks.

## Risks and Test Signals
Risks are invalid access-width combinations, wrong I/O shift, enabling DMA on unsupported boards, and missing the PXA alignment workaround. Test signals include successful probe, register read/write sanity checks at configured widths, packet TX/RX, LED behavior, DMA stress when enabled, and platform-specific alignment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smc91x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp.h -->
# sources/distributed-fs/ceph-client/include/linux/smp.h

## Purpose
`smp.h` is the generic symmetric multiprocessing interface. It declares cross-CPU function call primitives, boot/hotplug setup hooks, CPU stop/panic helpers, reschedule IPIs, current CPU accessors, and UP fallbacks.

## Important APIs, Types, and Functions
Key callback types are `smp_call_func_t` and `smp_cond_func_t`. `struct __call_single_data` and `call_single_data_t` wrap `struct __call_single_node`, callback, and info pointer for single-CPU call queues. `CSD_INIT()` and `INIT_CSD()` initialize callback data. Core APIs include `__smp_call_single_queue()`, `smp_call_function_single()`, `smp_call_function_single_async()`, `smp_call_function()`, `smp_call_function_many()`, `smp_call_function_any()`, `on_each_cpu()`, `on_each_cpu_mask()`, `on_each_cpu_cond()`, and `on_each_cpu_cond_mask()`.

Boot and CPU-management APIs include `smp_prepare_boot_cpu()`, `smp_prepare_cpus()`, `__cpu_up()`, `smp_cpus_done()`, `call_function_init()`, `generic_smp_call_function_single_interrupt()`, `setup_nr_cpu_ids()`, `smp_init()`, `get_boot_cpu_id()`, `arch_disable_smp_support()`, thaw hooks, and `smp_setup_processor_id()`. Runtime helpers include `smp_send_stop()`, `smp_send_reschedule()`, `kick_all_cpus_sync()`, `wake_up_all_idle_cpus()`, `cpus_peek_for_pending_ipi()`, `smp_processor_id()`, `get_cpu()`, `put_cpu()`, and CSD debug hooks.

## Control Flow
Cross-CPU call flow packages a callback and argument in call-single data, enqueues it on a target CPU call queue, and uses architecture IPI delivery to make the target flush its queue. `on_each_cpu*()` variants apply this to online CPU masks and optionally wait for completion. Async single calls require caller-managed `call_single_data_t`. Reschedule flow traces the IPI send and delegates to `arch_smp_send_reschedule()`.

Boot flow is split between generic and architecture code: the boot CPU is prepared, secondary CPUs are prepared and brought up through `__cpu_up()`, and finalization runs after all requested CPUs are online. With `CONFIG_SMP` disabled, many operations collapse to local calls or no-ops while retaining API compatibility.

## State and Persistence Behavior
SMP state includes global CPU counts (`total_cpus`, `setup_max_cpus`, `__boot_cpu_id`), CPU online masks from cpumask infrastructure, per-CPU call queues, and call-single data flags defined in `smp_types.h`. `get_cpu()` temporarily disables preemption so the current CPU id remains stable until `put_cpu()`. No disk persistence exists.

## Dependencies and Integration Points
The header depends on errno/types/list/cpumask/init, `smp_types.h`, preemption, compiler annotations, thread info, architecture `asm/smp.h`, and tracing for IPIs. It integrates with scheduler rescheduling, TLB shootdowns, stop-machine/panic paths, CPU hotplug, irq work-compatible call queue nodes, and architecture-specific CPU bringup.

## Risks and Test Signals
Risks include calling waitable cross-CPU functions from interrupt or preemption-invalid contexts, reusing async CSD before completion, deadlocks when target CPUs are offline or stopped, unstable `smp_processor_id()` use without preemption/IRQ protection, and UP/SMP semantic drift. Test signals include lockdep and `CONFIG_DEBUG_PREEMPT` warnings, CSD lock-wait debug reports, CPU hotplug tests, IPI tracing, scheduler selftests, panic/stop path testing, and SMP/UP build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp_types.h -->
# sources/distributed-fs/ceph-client/include/linux/smp_types.h

## Purpose
`smp_types.h` defines the low-level call-single queue node shared by generic SMP function calls and irq_work-style users. It keeps common flag/type layout separate from the higher-level SMP API.

## Important APIs, Types, and Functions
The anonymous enum defines low bits for `CSD_FLAG_LOCK`, irq-work flags (`IRQ_WORK_PENDING`, `IRQ_WORK_BUSY`, `IRQ_WORK_LAZY`, `IRQ_WORK_HARD_IRQ`, `IRQ_WORK_CLAIMED`), and high-nibble node types (`CSD_TYPE_ASYNC`, `CSD_TYPE_SYNC`, `CSD_TYPE_IRQ_WORK`, `CSD_TYPE_TTWU`, `CSD_FLAG_TYPE_MASK`). `struct __call_single_node` contains an `llist_node`, a union of `u_flags` and `a_flags`, and optional `src`/`dst` CPU fields on 64-bit builds.

## Control Flow
There is no executable flow here. The comments document how `flush_smp_call_function_queue()` first reads the type from `u_flags`, then interprets the memory following the node as either call-single data, irq_work, or TTWU queue data. The shared first-field layout lets heterogeneous work items coexist on the same per-CPU llist queue.

## State and Persistence Behavior
State is transient per queued cross-CPU work item. `u_flags` or `a_flags` records pending/busy/lock/type state until the target CPU consumes the node. Optional `src`/`dst` fields support debugging or tracing on 64-bit systems. There is no persistent storage.

## Dependencies and Integration Points
The header depends on `linux/llist.h` and is consumed by `smp.h`, generic SMP call-function code, irq_work, scheduler wakeup pathways, and any code that embeds `struct __call_single_node` as its queue-compatible prefix.

## Risks and Test Signals
Risks include changing flag values or layout without updating all queue consumers, reading atomic flags through the wrong union member, and misclassifying node type before interpreting the enclosing structure. Test signals include SMP function-call selftests, irq_work tests, scheduler wakeup stress, CSD lock debugging, and build coverage across 32-bit and 64-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smpboot.h -->
# sources/distributed-fs/ceph-client/include/linux/smpboot.h

## Purpose
`smpboot.h` declares the generic framework for per-CPU hotplug threads. It lets subsystems register a descriptor so the kernel can create, park, unpark, run, and clean up one thread per CPU as CPUs come online or offline.

## Important APIs, Types, and Functions
The main type is `struct smp_hotplug_thread`. It contains a per-CPU task pointer store, list linkage for core management, callbacks `thread_should_run`, `thread_fn`, `create`, `setup`, `cleanup`, `park`, and `unpark`, a `selfparking` flag, and `thread_comm` base name. The public APIs are `smpboot_register_percpu_thread()` and `smpboot_unregister_percpu_thread()`.

## Control Flow
A subsystem fills a static `smp_hotplug_thread` descriptor and registers it. The SMP boot/hotplug core creates per-CPU kernel threads, calls optional create/setup callbacks at creation or first operation, repeatedly asks `thread_should_run()` with preemption disabled, and invokes `thread_fn()` for work. CPU offline events park threads and may call `park`; CPU online events unpark them and may call `unpark`. Unregistration stops and cleans up the registered thread family.

## State and Persistence Behavior
State persists in the registered descriptor and the per-CPU `task_struct` pointers referenced by `store`. Threads exist while the descriptor is registered and CPUs are present/online according to hotplug state. Callback-owned subsystem state must handle CPU online/offline transitions. No disk persistence exists.

## Dependencies and Integration Points
The header depends on kernel types and forward-declared `struct task_struct`. It integrates with the CPU hotplug core, scheduler, kthread infrastructure, per-CPU storage, and subsystems that need CPU-local worker threads such as watchdogs, migration helpers, or networking/RCU-adjacent workers.

## Risks and Test Signals
Risks include callback sleep/preemption violations, failing to park or clean up CPU-local resources, stale per-CPU task pointers, unregister races with hotplug, and incorrect `selfparking` behavior. Test signals include CPU hotplug stress, lockdep in callbacks, kthread lifecycle tracing, subsystem-specific online/offline tests, and verifying no per-CPU threads remain after unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smpboot.h -->
