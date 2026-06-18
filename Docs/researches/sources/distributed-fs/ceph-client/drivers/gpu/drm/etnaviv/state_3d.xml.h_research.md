## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_3d.xml.h

### Purpose
`state_3d.xml.h` is a cut-down generated register header for selected 3D, shader, compute, texture-status, and NTE registers used by the Etnaviv driver.

### Important APIs, Types, And Functions
It defines macro constants for CL compute configuration/workgroup registers, PS/VS shader input/output/uniform/instruction registers, shader config bits, texture-status flush, and NTE descriptor flush fields. It also uses mask/shift/value helper macros such as `VIVS_CL_CONFIG_DIMENSIONS(x)` and `VIVS_PS_INPUT_COUNT_COUNT(x)`.

### Control Flow
There is no executable flow. The macros are compile-time data for command-buffer programming and validation.

### State, Persistence, And Dependencies
The file has no mutable state. Its persistent role is to keep numeric state addresses synchronized with the generated XML register database. It is intentionally smaller than the full upstream generated file.

### Integration Points
3D command emission, cache flush, shader setup, and validation code can use these definitions without including a larger generated header. It complements `state.xml.h` and `state_hi.xml.h`.

### Risks
Because it is cut down, adding code that needs omitted 3D registers requires regenerating or extending the header carefully. Duplicated CL config definitions must stay identical. Wrong shader-state constants can cause hard-to-debug GPU hangs.

### Test Signals
Build coverage, shader command-stream tests, cache-flush tests, compute command tests on supported cores, and comparison with regenerated XML output are the main signals.
