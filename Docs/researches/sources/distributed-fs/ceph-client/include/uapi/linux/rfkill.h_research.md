<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rfkill.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rfkill.h

Purpose: defines the `/dev/rfkill` userspace event/control ABI for radio kill switches and wireless device block state.

Important APIs and types: state constants distinguish soft-blocked, unblocked, and hard-blocked. `enum rfkill_type` lists WLAN, Bluetooth, UWB, WiMAX, WWAN, GPS, FM, NFC, and all-types requests. `enum rfkill_operation` identifies add/delete/change/change-all. `enum rfkill_hard_block_reasons` identifies hardware signal and host-ownership reasons. `struct rfkill_event` is the legacy packed event, and `struct rfkill_event_ext` adds hard-block reasons. Ioctls disable rfkill-input and opt into a maximum event size.

Control flow: userspace reads events from `/dev/rfkill`, writes change requests, and can request extended event size. The kernel emits add/delete/change records and applies soft-block changes, while hard-block state follows hardware/firmware ownership.

State and persistence: rfkill state is runtime per device plus default state for hotplugged devices after change-all. Soft block may be policy-managed by userspace; hard block is hardware/firmware state.

Dependencies and integration points: depends on Linux types. Integrates with wireless, Bluetooth, platform hotkey drivers, NetworkManager/systemd/BlueZ, and input rfkill handling.

Risks and test signals: risks include event struct extensibility breakage, short read/write handling, default state surprises, hard-block reason opt-in, and policy races among managers. Test legacy and extended event sizes, add/change/delete events, change-all defaults, hard block reasons, `RFKILL_IOCTL_MAX_SIZE`, and old userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rfkill.h -->
