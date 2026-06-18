<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sisfb.h -->
# sources/distributed-fs/ceph-client/include/video/sisfb.h

## Purpose
This header provides kernel-side SiS framebuffer identifiers and pulls in the UAPI interface for the SiS fb driver.

## Important APIs, Types, And Functions
- Includes `<linux/pci.h>` and `<uapi/video/sisfb.h>` for PCI and userspace-facing definitions.
- `UNKNOWN_VGA`, `SIS_300_VGA`, and `SIS_315_VGA` classify supported SiS VGA families.

## Control Flow
There is no control flow. Driver code uses the family constants after PCI/chip probing to dispatch generation-specific initialization and mode-setting paths.

## State And Persistence
The header declares no state. The family constants influence driver-private runtime state and capability selection.

## Dependencies And Integration Points
It integrates the SiS framebuffer driver with PCI probing and UAPI ioctls/structures in `uapi/video/sisfb.h`.

## Risks And Edge Cases
Misclassifying a chip family can select incompatible register sequences. Because the real UAPI lives elsewhere, changes must preserve compatibility with userspace.

## Test Signals
Probe logs should classify the correct family, expose expected UAPI behavior, and initialize modes on both 300- and 315-series hardware without selecting unknown fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/sisfb.h -->
