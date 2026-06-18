<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.c

### Purpose
`i915_cmd_parser.c` implements the i915 software batch-buffer command parser. It audits user batch buffers for privileged commands, restricted register access, and privileged memory access patterns, then produces a validated shadow batch or trampoline sequence for hardware execution.

### Important APIs, Types, And Functions
Public APIs are `intel_engine_init_cmd_parser()`, `intel_engine_cleanup_cmd_parser()`, `intel_engine_cmd_parser()`, and `i915_cmd_parser_get_version()`. Core types include `struct drm_i915_cmd_descriptor`, `struct drm_i915_cmd_table`, `struct drm_i915_reg_descriptor`, `struct drm_i915_reg_table`, and `struct cmd_node`. Important helpers include command length decoders for gen7/gen9 engines, sorted-table validators, `init_hash_table()`, `find_cmd()`, `find_reg()`, `copy_batch()`, `check_cmd()`, `check_bbstart()`, and `alloc_whitelist()`.

### Control Flow
Engine initialization selects command and register tables based on graphics generation and engine class: gen7 render/video/blitter/VEBOX and gen9 blitter are supported, with gen9 BCS marked as requiring the parser. It validates sorted tables, builds a hash table keyed by opcode, records register whitelist tables, and sets engine flags. Parsing copies the source batch into a shadow GEM object, allocates a bitmap of already executed command indices for recursive BB_START validation when not using a trampoline, canonicalizes original and shadow addresses, and then walks commands until `MI_BATCH_BUFFER_END`.

For each command, the parser finds an explicit or default descriptor, derives length, bounds-checks it against the batch, rejects forbidden commands, validates whitelisted registers and mask/value constraints, validates command bitmask constraints, and rewrites legal `MI_BATCH_BUFFER_START` targets to the equivalent shadow address only if the jump stays inside the batch and targets a previously executed command. In trampoline mode the shadow contains a privileged first execution and a second non-privileged chain; unsafe but hardware-valid batches are redirected to the original non-secure batch.

### State, Persistence, And Dependencies
Persistent per-engine state includes `cmd_hash`, `reg_tables`, `reg_table_count`, `get_cmd_length_mask`, and parser flags. The parser uses temporary shadow object mappings, optional jump whitelist bitmaps, cache flush flags, and register/command static tables. Dependencies include i915 engine metadata, GEM object read/write mapping helpers, DRM cache flush helpers, command/register definitions, WC memcpy optimization, and VMA offsets.

### Integration Points
Request submission code invokes `intel_engine_cmd_parser()` for engines using or requiring parser support. UAPI reports parser availability through `i915_cmd_parser_get_version()`. Cleanup runs during engine teardown. The parser complements hardware parsing by enabling safe secure execution for selected operations and falling back to hardware validation when needed.

### Risks
This is a security boundary. Missing a privileged command, register, GGTT bit, or recursive jump case can grant userspace unauthorized GPU access. Length decoding errors can overrun the batch or skip checks. Register whitelist ordering is required for binary search. `copy_batch()` must handle cache-coherent and WC mappings correctly. The jump whitelist intentionally constrains BB_START recursion and must stay synchronized with command offsets.

### Test Signals
High-value tests include parser init on IVB/HSW/gen9 BCS, sorted-table validation failures, rejected privileged commands, register whitelist accepts/rejects including masked registers, GGTT bit rejection, short-command rejection, batches without BBE, recursive BB_START to current/previous/future/out-of-range commands, trampoline fallback behavior, cache flush/map failure injection, and UAPI version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.c -->
