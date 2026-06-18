<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_boot_api.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_boot_api.h

### Purpose
`vpu_boot_api.h` defines the packed host/firmware boot ABI for Intel VPU firmware images, boot parameters, tracing buffers, scheduling mode, power profile, DVFS, D0i3, and DCT configuration.

### Important APIs, Types, And Functions
The header exports version macros `VPU_BOOT_API_VER_*`, firmware header constants, `struct vpu_firmware_header`, boot type and scheduling mode macros, cache/ECC/governor enums, trace destination and processor bit definitions, `struct vpu_boot_params`, tracing buffer canary/format constants, and `struct vpu_tracing_buffer_header`. There are no functions.

### Control Flow
No code executes here. The driver reads firmware image headers, fills boot parameters, and firmware later reads/writes the shared boot parameter block. Warm boot flow depends on `save_restore_ret_address`, while trace and power-management code depend on boot-time fields and firmware-updated telemetry fields.

### State, Persistence, And Dependencies
The structures are packed to 4-byte alignment and are binary ABI. Fields persist in firmware image headers or shared boot-parameter memory. The boot params include IPC region addresses, global PIO base, IRQ numbers, device identity, trace buffers, DVFS settings, D0i3 residency and timestamps, system time, power-state timestamps, scheduling mode, focus timer, ECC signal mode, power profile, and DCT active/inactive periods.

### Integration Points
`ivpu_fw` and `ivpu_pm` use this ABI for cold/warm boot and suspend/resume. `ivpu_job.c` uses scheduling mode constants, and tracing/firmware-log code uses trace buffer definitions. Firmware packaging tools use the version table and firmware header layout.

### Risks
This is a strict ABI: changing packing, field order, sizes, version macros, or reserved spacing can break firmware compatibility. Many fields are hardware-generation sensitive. The boot parameter struct is large and offset-oriented, so inserted fields outside reserved areas would corrupt subsequent firmware reads. Host and firmware must agree on scheduling mode, IPC memory, IRQ routing, and trace buffer layout.

### Test Signals
Verify firmware header parsing and API version negotiation, cold boot and warm boot paths, D0i3 suspend/resume, trace buffer canary and wrap handling, scheduling mode selection, DVFS parameter programming, power-state timestamps, and firmware compatibility tests across supported VPU generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_boot_api.h -->
