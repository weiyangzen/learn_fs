## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas.h

### Purpose
`vas.h` is the private PowerNV VAS hardware definition header: register offsets/bitfields, state structures, helper enums, inline MMIO accessors, and internal function declarations.

### Important APIs, Types, And Functions
It defines window limits and context sizes, many `VAS_*_OFFSET`/bitmask macros, `VREG()`, enums for notify scope, DMA type, and notify-after-count, FIFO invalid markers, `struct vas_instance`, `struct pnv_vas_window`, `struct vas_winctx`, declarations for instance/debug/fault/window helpers, inline `vas_window_pid()`, `write_uwc_reg()`, `write_hvwc_reg()`, `read_hvwc_reg()`, `encode_pswid()`, and `decode_pswid()`.

### Control Flow
The header itself has no runtime control flow, but its accessors perform big-endian MMIO writes/reads and log nonzero register writes. PSWID helpers encode VAS id and window id for later fault lookup.

### State, Persistence, And Dependencies
The structures define all persistent VAS software state: instance resources, fault FIFO fields, window lookup tables, window mappings, paste address, RX reference counts, and register configuration snapshots. Hardware persistence is in the programmed window context registers.

### Integration Points
All PowerNV VAS implementation files include this header, and public `asm/vas.h` users indirectly depend on these private structures through exported functions.

### Risks
Incorrect bitfield definitions corrupt hardware programming. `windows[VAS_WINDOWS_PER_CHIP]` is large per instance. PSWID encoding comments and shifts must match fault decode expectations.

### Test Signals
Build coverage, register dumps matching hardware documentation, PSWID encode/decode round trips, and VAS open/fault workloads validate the header.
