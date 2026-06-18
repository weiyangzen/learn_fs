## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.c

### Purpose
`ivpu_fw.c` requests, validates, loads, and describes Intel NPU firmware. It parses firmware headers, chooses scheduler mode, allocates firmware/runtime/log/shave BOs, applies firmware-version-dependent workarounds, copies the image, and populates boot parameters for cold and warm boots.

### Important APIs, Types, And Functions
Public APIs are `ivpu_is_within_range()`, `ivpu_fw_init()`, `ivpu_fw_fini()`, `ivpu_fw_load()`, and `ivpu_fw_boot_params_setup()`. Key internal helpers include firmware request/name selection, API compatibility checks, scheduler selection, preemption-buffer parsing, firmware header parsing, workaround init, firmware BO allocation/free, and boot-parameter debug printing.

### Control Flow
Initialization requests a debug-override firmware or the first matching production firmware for the hardware IP generation. Parsing validates file size, header version, boot-parameter/version/runtime/image/read-only address ranges, entry point, SHAVE NN size, API major versions, scheduler mode, trace defaults, and preemption buffer sizes. Memory init creates runtime BOs at firmware-provided addresses, sets read-only pages in the global context, allocates critical/verbose log buffers, and optionally allocates SHAVE NN firmware memory. Loading zeros the image-load prefix, copies the firmware image, optionally clears the rest of runtime memory, and issues a write memory barrier. Boot-param setup either updates warm-boot variable fields or fills the full cold-boot structure.

### State, Persistence, And Dependencies
Persistent state is stored in `struct ivpu_fw_info`, firmware BOs mapped in the global MMU context, firmware log BOs, scheduler/trace/preemption/DVFS fields, entry points, and cached firmware version/name. Dependencies include Linux firmware loading, ivpu GEM/runtime BOs, hardware ranges/frequencies/telemetry, MMU context page protections, IPC buffer addresses, PM timestamps, boot/JSM API headers, and module parameters.

### Integration Points
`ivpu_dev_init()` calls firmware init before IPC boot. `ivpu_boot()` calls boot-param setup and hardware boot. Debugfs reads and updates trace/DVFS fields. Coredump/log paths consume firmware logs. JSM/HWS setup depends on selected scheduler mode and preemption buffer sizes.

### Risks
Firmware header validation is the security boundary for device-visible runtime addresses. `runtime_size = fw_hdr->runtime_size - boot_params_size - fw_version_size` relies on unsigned arithmetic and must be guarded by range checks. Trace and scheduler mode choices depend on API version. BO allocation unwind must free partially allocated resources. Warm-boot setup updates only variable fields, so stale cold-boot fields must remain valid.

### Test Signals
Use valid and malformed firmware images: small file, bad header version, invalid ranges, oversized image/SHAVE NN, incompatible API, old/new JSM versions, HW/OS scheduler selection, preemption buffer limits, read-only section validation, cold and warm boot parameter contents, and log buffer allocation sizes for each log level.
