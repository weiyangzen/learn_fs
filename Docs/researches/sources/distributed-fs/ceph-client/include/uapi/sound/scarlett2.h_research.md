<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/scarlett2.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/scarlett2.h

Purpose: defines the ALSA hwdep protocol ABI for Focusrite Scarlett 2nd/3rd/4th Gen, Clarett USB, and Clarett+ devices, centered on protocol versioning, reboot, flash segment selection, erase, and erase progress.

Important APIs and types: version macros encode major/minor/subminor into `SCARLETT2_HWDEP_VERSION`, with helpers to extract each component. Ioctls are `SCARLETT2_IOCTL_PVERSION`, `REBOOT`, `SELECT_FLASH_SEGMENT`, `ERASE_FLASH_SEGMENT`, and `GET_ERASE_PROGRESS`. `scarlett2_flash_segment_erase_progress` reports erase progress and block count.

Control flow: userspace first reads the protocol version, selects either the settings or firmware flash segment, triggers erase, polls progress until the complete sentinel, and may request device reboot after maintenance.

State and persistence: selected flash segment and erase progress are runtime driver/device state. The target flash contents are persistent on the hardware, making wrong segment selection or interrupted updates externally visible after reboot.

Dependencies and integration points: depends on Linux fixed-size types and ioctl definitions. It integrates with the ALSA Scarlett2 mixer/control driver and firmware/settings update utilities.

Risks and test signals: risks include destructive flash operations exposed through hwdep, version negotiation drift, segment ID validation, and progress sentinel handling. Test with unsupported versions, invalid segment IDs, erase/reboot permission paths, progress polling across disconnect, and ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/scarlett2.h -->
