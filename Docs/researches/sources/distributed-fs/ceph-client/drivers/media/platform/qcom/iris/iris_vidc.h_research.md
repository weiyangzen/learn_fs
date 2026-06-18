# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.h

## Purpose
Declares the generic Iris V4L2 ops initialization and file open/close entry points.

## Important APIs
- `iris_init_ops(struct iris_core *core)` installs static V4L2/vb2 ops into the core.
- `iris_open()` and `iris_close()` are file operations used by video devices.

## Control Flow And Integration Points
`iris_probe.c` calls `iris_init_ops()` and registers video devices whose file ops call `iris_open()` and `iris_close()`.

## State And Persistence Behavior
No header state; implementation creates and destroys per-file instances.

## Dependencies
Requires `struct iris_core` and `struct file` declarations in including code.

## Risks
Open/close prototypes are externally visible through static file ops; signature drift breaks V4L2 integration.

## Test Signals
Compile coverage plus video-device open/close tests.
