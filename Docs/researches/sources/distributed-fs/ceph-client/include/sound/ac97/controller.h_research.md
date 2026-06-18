# sources/distributed-fs/ceph-client/include/sound/ac97/controller.h

## Purpose
`controller.h` defines the newer AC97 bus controller abstraction used by low-level AC-Link controller drivers. It models an AC97 controller, the adapter device registered for it, its available codec slots, platform data per codec, and the mandatory register access operations that the AC97 bus can invoke.

## Important APIs, Types, and Functions
Key constants are `AC97_BUS_MAX_CODECS` and `AC97_SLOTS_AVAILABLE_ALL`. `struct ac97_controller` stores the operation table, global controller list node, adapter `struct device`, numeric adapter id, slot mask, parent device, discovered codec devices, and per-codec platform data. `struct ac97_controller_ops` supplies reset, warm reset, read, and write callbacks. `snd_ac97_controller_register()` and `snd_ac97_controller_unregister()` are real APIs only when `CONFIG_AC97_BUS_NEW` is enabled; otherwise registration returns `ERR_PTR(-ENODEV)`.

## Control Flow
Controller drivers register an ops table and slot mask. The AC97 bus scans slots, creates codec devices, and routes codec register reads and writes through `ops->read` and `ops->write`; reset and warm-reset hooks bracket discovery or recovery.

## State and Persistence Behavior
State is in the registered `struct ac97_controller` and child codec device pointers. It is kernel runtime state only; platform data is retained through device lifetime but no file-backed persistence exists.

## Dependencies and Integration Points
The header depends on Linux device and list APIs and forward-declared AC97 codec devices. It integrates controller drivers with the AC97 bus core and indirectly with codec drivers that bind to discovered codec devices.

## Risks and Test Signals
Risks are invalid slot masks, missing callbacks, read/write error propagation, and lifetime mismatches between controller unregister and codec devices. Test signals include build coverage with and without `CONFIG_AC97_BUS_NEW`, registration failure paths, reset ordering, and multi-codec slot discovery.
