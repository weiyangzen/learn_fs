# sources/control-plane/mayastor/io-engine/tests/mount_fs.rs

Purpose: end-to-end filesystem tests for a mirrored nexus shared over NVMf, validating mount/write/read consistency, repeated mount cycles, and fio verify.

Important APIs/types/functions: `prepare_storage` creates two 400 MiB AIO files. `create_connected_nvmf_nexus` creates/shares a two-child nexus and connects with `libnvme_rs::NvmeTarget`. `mount_test` formats, mounts, writes a file, records md5, destroys the mirror, creates single-child nexuses for each disk, mounts each separately, and verifies md5. Tests call `common::mkfs`, `mount_and_write_file`, `mount_and_get_md5`, `mount_umount`, and `fio_run_verify`.

Control flow: `mount_fs_mirror` runs the md5 split verification for xfs and ext4. `mount_fs_multiple` mount/unmounts the NVMf device ten times. `mount_fn_fio` runs fio verification. Cleanup disconnects target, unshares, and destroys nexuses.

State and persistence: real temp disk files persist filesystem data across destroying the mirror and re-exporting each child individually.

Dependencies and integration points: filesystem tools, mount privileges, libnvme-rs, NVMf target/initiator, nexus mirroring, AIO bdevs, fio.

Risks and edge cases: requires root-like mount permissions and filesystem tools. Fixed `/tmp/disk1.img`/`disk2.img`. Data consistency check assumes both mirrored children contain identical filesystem contents.

Test signals: high-value data-integrity signal across NVMf, nexus mirroring, filesystem, and fio workloads.
