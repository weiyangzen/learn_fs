<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.h

## Purpose
Declares the SELinux extensible bitmap representation and iteration helpers. Ebitmaps provide sparse sets for policy symbols and MLS categories without a fixed maximum bit count in the in-memory API.

## Important APIs, Types, and Functions
Types are `struct ebitmap_node` and `struct ebitmap`. Constants derive node size from word size, including `EBITMAP_NODE_SIZE`, `EBITMAP_UNIT_NUMS`, `EBITMAP_UNIT_SIZE`, and `EBITMAP_SIZE`. Inline helpers cover initialization, first/next positive bit iteration, node bit get/set/clear, and `ebitmap_for_each_positive_bit()`. Function declarations cover copy, intersection, containment, bit access, serialization, hashing, destruction, and optional NetLabel conversion.

## Control Flow
Callers initialize an empty bitmap, mutate bits, iterate positive bits using the macro, serialize/deserialize through policy files, and explicitly destroy nodes. Iteration skips empty maps and stops at `highbit`.

## State and Persistence
Each bitmap stores a linked list of nodes and a `highbit` boundary. Node `startbit` anchors the fixed-size map array. Persistence is implemented in `ebitmap.c` but shaped by this header's layout.

## Dependencies and Integration Points
Depends on NetLabel declarations for optional category conversion and Linux bit helpers through implementation users. Used by MLS ranges, constraint name sets, role/type sets, and policy hashing.

## Risks
Macro arithmetic such as `EBITMAP_SHIFT_UNIT_SIZE()` and node index/offset calculations must remain portable across 32-bit and 64-bit builds. Callers must not use node bit helpers on bits outside the node range. Missing `ebitmap_destroy()` leaks slab nodes.

## Test Signals
Build/test on 32-bit and 64-bit configurations, iterate empty and sparse bitmaps, test boundary bits at node edges, validate NetLabel disabled stubs, and run policy load/unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/ebitmap.h -->
