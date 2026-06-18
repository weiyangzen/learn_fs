## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw.h

### Purpose
`ivpu_fw.h` defines firmware metadata/state and declares firmware lifecycle and boot-parameter APIs.

### Important APIs, Types, And Functions
`struct ivpu_fw_info` stores the firmware file/name/version, BOs for boot params/version/runtime/SHAVE/logs, firmware-provided addresses and sizes, image offsets, entry points, boot modes, trace config, DVFS mode, preemption buffer sizes, read-only section, scheduler mode, and heartbeat. It declares `ivpu_is_within_range()`, `ivpu_fw_init()`, `ivpu_fw_fini()`, `ivpu_fw_load()`, and `ivpu_fw_boot_params_setup()`. Inline helpers are `ivpu_fw_is_warm_boot()` and `ivpu_fw_preempt_buf_size()`.

### Control Flow
The header itself has only inline checks. Runtime code uses `next_boot_mode` to choose warm versus cold boot and sums primary/secondary preemption buffer sizes for UAPI capability reporting.

### State, Persistence, And Dependencies
Firmware state persists in `vdev->fw` from init to fini and is updated across resets/boots. Dependencies are firmware boot and JSM API definitions plus ivpu BO/device declarations.

### Integration Points
The struct is consumed by driver boot, hardware CPU entry-point programming, debugfs, firmware log/coredump, PM warm boot, and UAPI param handling.

### Risks
All address/size fields are device-visible ABI from firmware; users must validate before allocation/use. Boot mode fields must be updated consistently or warm boot may jump to an invalid entry point.

### Test Signals
Check firmware state after init, after cold boot, after warm boot, after fini, and through debugfs/UAPI paths that read version, scheduler mode, capabilities, and preemption buffer size.
