<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Makefile

## Purpose
Defines the object composition for the Qualcomm Iris V4L2 decoder driver module.

## Important APIs, Types, And Functions
- Builds `qcom-iris.o` when `CONFIG_VIDEO_QCOM_IRIS` is enabled.
- Aggregates Iris source objects for buffer management, core/platform setup, firmware, HFI command/packet/response handling, instance state, control handling, power management, V4L2 file/ioctl paths, VB2 integration, and VPU buffer handling.
- Adds `iris_platform_gen1.o` only when `CONFIG_VIDEO_QCOM_VENUS` is unset.

## Control Flow
Kbuild expands `qcom-iris-objs` into the ordered object list for the composite `qcom-iris.o` target. The final object is linked built-in or as a module according to the Kconfig tristate.

## State And Persistence
No runtime state is stored in the Makefile. Build outputs are generated under the kernel build tree and are not source persistence.

## Dependencies And Integration Points
Depends on the matching Kconfig symbol and the listed Iris C files. It integrates the Iris driver into the kernel media platform Qualcomm build directory.

## Risks And Edge Cases
Missing an object can produce unresolved symbols or silently omit functionality. Stale object names break builds when source files are renamed. Object ordering can matter for initcall/linker-section behavior, though normal C symbol resolution is order-insensitive within this composite object.

## Test Signals
`make M=drivers/media/platform/qcom/iris` or full kernel builds with `CONFIG_VIDEO_QCOM_IRIS=m/y` should produce `qcom-iris.o` without missing object or unresolved symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Makefile -->
