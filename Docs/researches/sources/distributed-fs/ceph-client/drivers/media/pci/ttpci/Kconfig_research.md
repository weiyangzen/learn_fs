<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Kconfig

## Purpose
`ttpci/Kconfig` defines build-time configuration options for SAA7146-based "budget" DVB PCI cards, including base support, simple cards, CI cards, and analog-input cards.

## Important APIs, Types, and Functions
The symbols are `DVB_BUDGET_CORE`, `DVB_BUDGET`, `DVB_BUDGET_CI`, and `DVB_BUDGET_AV`. They express dependencies on `DVB_CORE`, `PCI`, `I2C`, `RC_CORE`, and `VIDEO_DEV`, and select SAA7146, EEPROM, frontend, tuner, LNB, and V4L2 helper modules when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control Flow
There is no runtime flow. The configuration graph ensures common core support is built before variant modules and that optional demod/tuner dependencies are selected for known cards.

## State and Persistence
Kconfig selections persist in the kernel `.config`, controlling which modules or built-in objects are produced. No runtime state is owned by this file.

## Dependencies and Integration Points
The file integrates the TTPci budget drivers with the kernel media build system, DVB frontend/tuner libraries, SAA7146 core support, remote-control core, and video-device support for analog capture cards.

## Risks and Edge Cases
Autoselect only pulls known subdrivers when `MEDIA_SUBDRV_AUTOSELECT` is set; otherwise users must enable matching frontends manually. `DVB_BUDGET_CI` depends on `RC_CORE`, so CI cards with IR support cannot be built without remote-control core. `DVB_BUDGET_AV` depends on `VIDEO_DEV` via SAA7146 VV support.

## Test Signals
Check all four symbols build as modules and built-ins, dependency resolution with and without `MEDIA_SUBDRV_AUTOSELECT`, module names matching help text, and successful compilation of selected frontend combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Kconfig -->
