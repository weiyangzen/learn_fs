<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.h

## Purpose
`solo6x10-tw28.h` declares TW28xx decoder constants and the control/status API shared between decoder setup, V4L2 capture/encoder code, and ALSA audio code.

## Important APIs, Types, and Functions
The header defines chip addressing (`TW_NUM_CHIP`, `TW_BASE_ADDR`, `TW_CHIP_OFFSET_ADDR()`), status and control register address macros for TW2815 and TW286x families, and prototypes for `solo_tw28_init()`, video control get/set, sharpness capability, audio gain get/set, and video status.

## Control Flow
There is no runtime control flow. Callers include the header to select proper register offsets and call the TW28 helper functions implemented in `solo6x10-tw28.c`.

## State and Persistence
The header does not store state. It describes accessors for volatile decoder hardware state tracked through `struct solo_dev`.

## Dependencies and Integration Points
It includes `solo6x10.h`, so it inherits the full device structure and V4L2 type context. It is consumed by ALSA G.723, live V4L2 display, V4L2 encoder, and TW28 implementation code.

## Risks and Edge Cases
Macros encode different address layouts for TW2815 and TW286x chips. Passing chip numbers where channel numbers are expected, or vice versa, can address the wrong register. Because the header includes the main driver header, include cycles must remain controlled by include guards.

## Test Signals
Compile all users with both `CONFIG_GPIOLIB` states, exercise picture and audio controls on TW2815 and TW286x boards, and confirm video status reads use the correct family-specific status register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.h -->
