# sources/control-plane/mayastor/test/python/v1/pool/test_bdd_lvm.py

Purpose: v1 pytest-bdd coverage for LVM pool feature reporting, LVM pool creation/destruction on loop-backed volume groups, LVS pool creation/destruction, and list output pool type fields.

Important APIs and control flow: fixtures query `mayastor_info`, create a loop-backed `/tmp/ms0-disk0.img`, run `losetup`, `pvcreate`, and `vgcreate`, and create another aio image. Raw `pool_rpc.CreatePool` sends explicit `pooltype` because the high-level handle does not. Steps check `registration_info.features.logicalVolumeManager`, create LVM and LVS pools, destroy them, list pools, and validate capacity, used bytes, online state, and `pooltype`.

State, dependencies, and integration: state includes host loop devices, LVM VG `lvmpool`, aio file `ms0-disk1.img`, and Mayastor pools. Dependencies include `nix-sudo`, LVM tools, loop devices, pool protobufs, and v1 fixtures.

Risks and test signals: duplicate Python function names shadow earlier definitions but pytest-bdd decorators have already registered step handlers. Cleanup detaches loop device before explicit VG removal in this file, which may leave host LVM state if failures occur. Signals cover feature bit and pool listing metadata.
