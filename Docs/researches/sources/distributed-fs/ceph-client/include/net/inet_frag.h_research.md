# sources/distributed-fs/ceph-client/include/net/inet_frag.h

Purpose: declares common IPv4/IPv6 fragment queue infrastructure. It provides per-netns fragment directories, fragment queue objects, fragment family operations, memory accounting, ECN combination support, insertion return codes, and reassembly helpers.

Important APIs/types: `struct fqdir` stores thresholds, timeout, max distance, dead flag, rhashtable, atomic memory use, destroy work, and free list. `struct inet_frag_queue` stores v4/v6 keys, timer, lock, refcount, rb-tree fragments, tail/run pointers, timestamp, length/meat, flags, max size, directory, and RCU. `struct inet_frags` defines constructor/destructor/expire callbacks, cache, rhashtable params, refcount, and completion. APIs initialize/finalize families and directories, find/kill/destroy queues, flush queues, insert fragments, prepare/finish reassembly, and pull the head skb.

Control flow and state: receive paths find or create a queue, insert fragments by offset into an rb-tree, track meat/len/flags and memory, then reassemble when complete or flush/expire on timeout/memory pressure. State persists in per-netns rhashtables until complete/expired.

Dependencies and integration: depends on rhashtable, timers, rbtrees, refcounts, completion, and drop reasons. It integrates with IPv4/IPv6 defrag, conntrack, bridge, AF_PACKET, and virtual-server users.

Risks: overlap handling, memory accounting, queue refcounts, and expiration races are high-risk. Tests should cover duplicate/overlap returns, ECN table combinations, high/low threshold pruning, namespace exit, timer expiry, reassembly coalescing, and drop reasons.
