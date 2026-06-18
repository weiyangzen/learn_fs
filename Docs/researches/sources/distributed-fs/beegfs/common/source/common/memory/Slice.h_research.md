# sources/distributed-fs/beegfs/common/source/common/memory/Slice.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/Slice.h -->
## sources/distributed-fs/beegfs/common/source/common/memory/Slice.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/memory/Slice.h` defines memory/string helper type(s) `Slice` for local non-owning views or malloc-backed ownership. More broadly, it provides allocation-free or malloc-backed memory/string utility types.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('Slice', ''), ('RO_Slice', ''), ('WO_Slice', ''), ('Slice', '')]. Members/functions cover data pointers, byte sizes, reset/drop or offset/limit operations, move-only ownership where applicable, and conversions to Slice/String views. Detected classes are [('Slice', ''), ('RO_Slice', ''), ('WO_Slice', ''), ('Slice', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is local utility behavior with no external I/O. State is pointer plus size/capacity; persistence is heap allocation for Malloc* classes and borrowed memory for Slice/String classes.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `assert.h`, `string.h`. Important local state or payload members include `class Slice`, `return mData`, `return mSize`, `return mData`, `return mSize`, `return mData`, `return mSize`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/memory/Slice.h -->
