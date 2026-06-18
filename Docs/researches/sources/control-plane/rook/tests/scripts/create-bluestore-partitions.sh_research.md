<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-bluestore-partitions.sh -->
# sources/control-plane/rook/tests/scripts/create-bluestore-partitions.sh

Purpose: host-side test helper for wiping a block device and creating BlueStore-related partitions for Rook OSD tests.

Important APIs and control flow: parses `--disk`, optional `--bluestore-type block.db|block.wal`, `--osd-count`, and `--wipe-only`. `wipe_disk` zaps GPT/metadata and optionally exits after printing. `create_partition` creates fixed 2048M partitions named for DB/WAL. `create_block_partition` creates either one largest `block` partition or multiple 6144M OSD partitions and writes udev rules assigning Ceph UID/GID ownership. It finishes with `partprobe`, `udevadm settle`, `lsblk`, and `parted print`.

State, persistence, and integration: destructively modifies the selected disk and host udev rules. Dependencies include `sudo`, `sgdisk`, `dd`, `parted`, `partprobe`, and `udevadm`. Risks are severe if `DISK` is wrong, `OSD_COUNT` is unset, partition naming assumes simple `${DISK}${n}` device names, and udev size matching is hard-coded. Test signals are successful partition table output and later local PV/OSD provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-bluestore-partitions.sh -->
