# sources/distributed-fs/ceph-client/include/uapi/linux/loop.h

Purpose: defines the loop block-device userspace ABI for attaching regular files or block devices as loop devices, querying/configuring status, and controlling `/dev/loop-control`.

Important APIs and types: constants include `LO_NAME_SIZE`, `LO_KEY_SIZE`, loop flags `LO_FLAGS_READ_ONLY`, `LO_FLAGS_AUTOCLEAR`, `LO_FLAGS_PARTSCAN`, and `LO_FLAGS_DIRECT_IO`, plus settable/clearable masks. `struct loop_info` is the legacy status format, `struct loop_info64` is the 64-bit status format, and `struct loop_config` supports atomic setup through `LOOP_CONFIGURE`. Ioctls include `LOOP_SET_FD`, `LOOP_CLR_FD`, status get/set, `LOOP_CHANGE_FD`, `LOOP_SET_CAPACITY`, direct I/O, block size, configure, and loop-control add/remove/get-free.

Control flow: userspace opens a loop device, attaches a backing fd, optionally sets offset/size/name/flags/block size, scans partitions, uses the block device, then clears or autoclears it. `LOOP_CONFIGURE` combines setup and configuration to avoid partial state.

State and persistence: runtime state is per loop device: backing file reference, offset, size limit, flags, block size, file/crypt names, and obsolete crypto fields. It is not persistent after detach or reboot unless userspace recreates it.

Dependencies and integration points: depends on `asm/posix_types.h` and `linux/types.h`; integrates block layer, partition scanning, util-linux `losetup`, udev, direct I/O, and legacy loop crypto compatibility.

Risks and test signals: risks include legacy struct width differences, partial configuration races, wrong flag mutability, direct I/O alignment, block size validation, and stale partition tables. Test attach/detach, atomic configure, read-only/autoclear/partscan/direct-io flags, capacity changes, backing fd replacement, 32-bit userspace ABI, and loop-control allocation.
