<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.h

### Purpose
`i915_cmd_parser.h` declares the software command parser API used by i915 engine setup and batch submission paths.

### Important APIs, Types, And Functions
It declares `i915_cmd_parser_get_version()`, `intel_engine_init_cmd_parser()`, `intel_engine_cleanup_cmd_parser()`, and `intel_engine_cmd_parser()`, and defines `I915_CMD_PARSER_TRAMPOLINE_SIZE` as 8.

### Control Flow
Consumers initialize parser state per engine, call the parser for candidate batches with source and shadow VMAs, and clean parser state during engine teardown.

### State, Persistence, And Dependencies
The header owns no state. Parser state is stored in `struct intel_engine_cs`; batch storage is represented by `struct i915_vma`.

### Integration Points
It is included by engine initialization, request submission, and any code needing to report parser version support.

### Risks
Callers must pass aligned offsets and lengths and a shadow VMA large enough for parser/trampoline use. The trampoline size constant is part of the allocation contract.

### Test Signals
Build coverage plus parser submission tests that allocate correct shadow/trampoline sizes are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_cmd_parser.h -->
