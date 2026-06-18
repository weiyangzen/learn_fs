## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_reg_io.h

### Purpose
`ivpu_hw_reg_io.h` provides register read/write/poll helpers and field manipulation macros for ivpu BAR register access with debug tracing and optional fault injection.

### Important APIs, Types, And Functions
Macros `REGB_*` and `REGV_*` wrap reads/writes against buttress and IP BARs. Field macros include `REG_FLD`, `REG_FLD_NUM`, `REG_GET_FLD`, `REG_CLR_FLD`, `REG_SET_FLD`, `REG_SET_FLD_NUM`, and tests. Poll macros call `ivpu_hw_reg_poll_fld()`. Inline functions implement 32/64-bit reads/writes, indexed writes, and polling.

### Control Flow
Callers invoke register macros with a local `vdev`. Polling logs start, uses `read_poll_timeout()` until `(value & mask) == expected`, optionally forces timeout through fault injection, logs completion, and returns status.

### State, Persistence, And Dependencies
State is hardware register state. The helper also depends on global fault attribute `ivpu_hw_failure` when fault injection is enabled. It requires mapped `vdev->regb`/`regv` and register/mask macro naming conventions.

### Integration Points
All hardware buttress and IP files use this header for register I/O, making it the common tracing and fault-injection point for hardware tests.

### Risks
Macros assume the caller has a variable named `vdev`; misuse can produce confusing compile errors. `REG_IO_ERROR` is `0xffffffff`, which can also be a valid raw register value for some registers, so callers should use it only where documented. Poll sleep/timeout values affect boot/recovery latency.

### Test Signals
Enable register debug mask and verify read/write traces, inject `ivpu_hw_failure` to force poll timeouts, test field set/get macros with known masks, and validate indexed doorbell writes produce expected offsets.
