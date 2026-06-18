## sources/distributed-fs/ceph-client/drivers/accel/ivpu/Makefile

### Purpose
The `ivpu` Makefile defines the `intel_vpu` composite object and conditionally includes debugfs and coredump support.

### Important APIs, Types, And Functions
`intel_vpu-y` lists core objects for driver entry, firmware, logs, GEM, userptr, hardware, IPC, jobs, JSM, MMU, PM, sysfs, and tracing. `intel_vpu-$(CONFIG_DEBUG_FS)` adds `ivpu_debugfs.o`; `intel_vpu-$(CONFIG_DEV_COREDUMP)` adds `ivpu_coredump.o`; `obj-$(CONFIG_DRM_ACCEL_IVPU)` builds the module. Debug builds add `-DDEBUG`, and `ivpu_trace_points.o` gets an include path.

### Control Flow
There is no runtime flow. Kbuild uses the object list to link `intel_vpu.o` with optional instrumentation objects based on configuration.

### State, Persistence, And Dependencies
Build output state is the generated module or built-in object. The file depends on the object list matching source files and Kconfig symbols.

### Integration Points
It ties the Kconfig option to the ivpu driver implementation and ensures tracing, PM, MMU, job scheduling, sysfs, debugfs, and coredump objects are linked.

### Risks
Omitting an object causes unresolved symbols or missing runtime features. Conditional objects must match the stub headers, so debugfs/coredump disabled builds still compile through inline fallbacks.

### Test Signals
Build all relevant configs: `CONFIG_DRM_ACCEL_IVPU=m/y`, with and without `CONFIG_DEBUG_FS`, `CONFIG_DEV_COREDUMP`, and `CONFIG_DRM_ACCEL_IVPU_DEBUG`.
