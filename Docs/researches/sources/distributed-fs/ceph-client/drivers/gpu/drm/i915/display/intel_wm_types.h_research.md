# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_wm_types.h

### Purpose
`intel_wm_types.h` defines shared data structures for legacy and SKL-era watermark state, including per-pipe FIFO watermarks, self-refresh watermarks, Valleyview DDL values, and SKL display data buffer entries.

### Important APIs, Types, And Functions
Key types are `enum intel_ddb_partitioning`, `struct ilk_wm_values`, `struct g4x_pipe_wm`, `struct g4x_sr_wm`, `struct vlv_wm_ddl_values`, `struct vlv_wm_values`, `struct g4x_wm_values`, and `struct skl_ddb_entry`. Inline helpers `skl_ddb_entry_size()` and `skl_ddb_entry_equal()` compute DDB block count and equality.

### Control Flow
There is no runtime control flow beyond the inline helpers. Platform watermark code fills these structs during compute/readback and compares/applies them during commit.

### State, Persistence, And Dependencies
Instances of these types are the in-memory representation of hardware watermark and DDB state. The header depends on `intel_display_limits.h` for `I915_MAX_PLANES` and Linux integer types.

### Integration Points
Legacy i9xx/G4x/ILK/VLV watermark backends and SKL watermark code use these structures to stage hardware values. The DDB helpers are shared wherever SKL data-buffer allocations are compared or sized.

### Risks
Array dimensions must match platform pipe/plane limits. `skl_ddb_entry_size()` assumes `end` is exclusive and greater than or equal to `start`; invalid entries can underflow because fields are unsigned. Equality compares only start/end, so callers must compare any associated metadata separately.

### Test Signals
Watermark readback/commit tests, DDB allocation verification, underrun tests under plane changes, and assertions around empty or invalid DDB entries are useful signals.
