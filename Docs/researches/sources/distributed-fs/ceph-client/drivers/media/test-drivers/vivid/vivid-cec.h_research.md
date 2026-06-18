# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-cec.h

## Purpose
`vivid-cec.h` declares VIVID CEC hooks when CEC emulation is enabled.

## Important APIs, types, and functions
Under `CONFIG_VIDEO_VIVID_CEC`, it declares `vivid_cec_alloc_adap()` and `vivid_cec_bus_thread()`. The adapter allocator creates CEC adapters for HDMI capture/output endpoints; the bus thread runs the virtual shared bus.

## Control flow
`vivid-core.c` includes this header, allocates adapters during instance creation, starts the bus thread when CEC endpoints exist, registers adapters during video-node creation, and unregisters/stops them during teardown.

## State and persistence
The header owns no state. CEC state is in `struct vivid_dev`.

## Dependencies and integration points
It depends on `struct vivid_dev` from `vivid-core.h` and the CEC framework types included there. The declarations are unavailable when CEC is not configured, matching conditional call sites.

## Risks and test signals
The primary risk is conditional-build drift. Build tests with `CONFIG_VIDEO_VIVID_CEC=y` and disabled are required, along with runtime adapter registration tests for HDMI-enabled VIVID instances.
