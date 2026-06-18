<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Kconfig

## Purpose
This Kconfig fragment declares the common V4L2 test pattern generator library symbol.

## Important APIs, Types, and Functions
It defines `config VIDEO_V4L2_TPG` as a `tristate` symbol with no prompt, making it an internal selectable dependency rather than a direct user-facing option.

## Control Flow
Other media drivers or Kconfig entries select or depend on `VIDEO_V4L2_TPG`; the Makefile then uses the symbol to build the common test pattern generator object.

## State and Persistence Behavior
Kconfig state persists in the kernel build configuration as built-in, module, or disabled. This file has no runtime state.

## Dependencies and Integration Points
The fragment integrates with the kernel media Kconfig tree and the sibling Makefile. It is intentionally minimal because dependencies are managed by selecting users.

## Risks and Test Signals
Because there is no prompt or dependency expression, incorrect external selects can enable the library in unsuitable contexts. Test signals are Kconfig resolution for drivers that use the test pattern generator and correct module/built-in propagation to `v4l2-tpg.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Kconfig -->
