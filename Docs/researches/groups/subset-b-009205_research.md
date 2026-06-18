# subset-b-009205 research

Grouped research report for blktests meta/NBD/NVMe/RNBD/SCSI/SRP/throtl/ublk/zbd files and CrashMonkey Makefile. Each section preserves the exact source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/021 -->
# sources/test-tools/blktests/tests/meta/021

Purpose: blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. This specific test is declared as: "exit with non-zero status from test_device_array()".

Important APIs/types/functions: sourced libraries `tests/meta/rc`; top-level variables `DESCRIPTION=exit with non-zero status from test_device_array()`; functions `test_device_array()` lines 11-15; external commands `echo`.

Control flow: `test_device_array()` uses commands `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `tests/meta/rc`; runtime command surface includes `echo`.

Risks and test signals: primary risk is build or harness drift; signal is make/shell exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/022 -->
# sources/test-tools/blktests/tests/meta/022

Purpose: blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. This specific test is declared as: "skip test_device_array() in device_requries()".

Important APIs/types/functions: sourced libraries `tests/meta/rc`; top-level variables `DESCRIPTION=skip test_device_array() in device_requries()`; functions `device_requires()` lines 11-13, `test_device_array()` lines 15-17; external commands `echo`.

Control flow: `device_requires()` is present and carries the file-specific action body. `test_device_array()` uses commands `echo`.

State and persistence behavior: records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `tests/meta/rc`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/023 -->
# sources/test-tools/blktests/tests/meta/023

Purpose: blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. This specific test is declared as: "skip test_device_array() in requires()".

Important APIs/types/functions: sourced libraries `tests/meta/rc`; top-level variables `DESCRIPTION=skip test_device_array() in requires()`; functions `requires()` lines 11-13, `test_device_array()` lines 15-17; external commands `echo`.

Control flow: `requires()` is present and carries the file-specific action body. `test_device_array()` uses commands `echo`.

State and persistence behavior: records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `tests/meta/rc`; runtime command surface includes `echo`.

Risks and test signals: unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/024 -->
# sources/test-tools/blktests/tests/meta/024

Purpose: blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. This specific test is declared as: "skip in test_device_array()".

Important APIs/types/functions: sourced libraries `tests/meta/rc`; top-level variables `DESCRIPTION=skip in test_device_array()`; functions `test_device_array()` lines 11-13.

Control flow: `test_device_array()` is present and carries the file-specific action body.

State and persistence behavior: records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `tests/meta/rc`.

Risks and test signals: unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/024 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/rc -->
# sources/test-tools/blktests/tests/meta/rc

Purpose: shared `tests/meta/rc` support for blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. It defines 3 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`; functions `group_requires()` lines 9-13, `group_device_requires()` lines 15-19, `fake_bug_on()` lines 21-59; external commands `cat`, `echo`.

Control flow: `group_requires()` is present and carries the file-specific action body. `group_device_requires()` is present and carries the file-specific action body.

State and persistence behavior: touches state paths such as `/dev/kmsg`, `$TMPDIR/dmesg` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `common/rc`; runtime command surface includes `cat`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/001 -->
# sources/test-tools/blktests/tests/nbd/001

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "resize a connected nbd device".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=resize a connected nbd device`, `QUICK=1`; functions `requires()` lines 13-17, `test()` lines 19-37; external commands `parted`, `echo`, `nbd-client`, `grep`.

Control flow: `requires()` uses commands `parted`; gates `_have_nbd`, `_have_program parted`, `_have_src_program nbdsetsize`. `test()` uses commands `echo`, `nbd-client`, `parted`, `grep`.

State and persistence behavior: touches state paths such as `/dev/nbd0`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_nbd`, `_have_program parted`, `_have_src_program nbdsetsize`; runtime command surface includes `parted`, `echo`, `nbd-client`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/002 -->
# sources/test-tools/blktests/tests/nbd/002

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "tests on partition handling for an nbd device".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=tests on partition handling for an nbd device`, `QUICK=1`; functions `requires()` lines 19-22, `test()` lines 24-134; external commands `parted`, `echo`, `nbd-client`, `sleep`.

Control flow: `requires()` uses commands `parted`; gates `_have_nbd_netlink`, `_have_program parted`. `test()` uses commands `echo`, `nbd-client`, `parted`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/nbd0`, `/dev/nbd0p1`, `/dev/null`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_nbd_netlink`, `_have_program parted`; runtime command surface includes `parted`, `echo`, `nbd-client`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/003 -->
# sources/test-tools/blktests/tests/nbd/003

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "mount/unmount concurrently with NBD_CLEAR_SOCK".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=mount/unmount concurrently with NBD_CLEAR_SOCK`, `QUICK=1`; functions `requires()` lines 13-16, `test()` lines 18-31; external commands `echo`, `nbd-client`, `mkfs.ext4`, `umount`.

Control flow: `requires()` uses gates `_have_nbd`, `_have_src_program mount_clear_sock`. `test()` uses commands `echo`, `nbd-client`, `mkfs.ext4`, `umount`.

State and persistence behavior: touches state paths such as `/dev/nbd0`, `/dev/null`, `$FULL` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_nbd`, `_have_src_program mount_clear_sock`; runtime command surface includes `echo`, `nbd-client`, `mkfs.ext4`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/004 -->
# sources/test-tools/blktests/tests/nbd/004

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "module load/unload concurrently with connect/disconnect".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=module load/unload concurrently with connect/disconnect`, `QUICK=1`; functions `requires()` lines 13-15, `module_load_and_unload()` lines 17-22, `connect_and_disconnect()` lines 24-29, `test()` lines 31-71; external commands `modprobe`, `echo`, `sleep`, `grep`, `nbd-client`.

Control flow: `requires()` uses gates `_have_module nbd`. `test()` uses local helpers `module_load_and_unload`, `connect_and_disconnect`; commands `echo`, `sleep`, `grep`, `nbd-client`.

State and persistence behavior: touches state paths such as `/dev/null`, `$((i + 1)` loads or unloads kernel modules, so host module parameters and device lifetimes are part of the test state.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_module nbd`; runtime command surface includes `modprobe`, `echo`, `sleep`, `grep`, `nbd-client`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/rc -->
# sources/test-tools/blktests/tests/nbd/rc

Purpose: shared `tests/nbd/rc` support for Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. It defines 11 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`; functions `group_requires()` lines 9-11, `_have_nbd()` lines 13-28, `_have_nbd_netlink()` lines 30-42, `_wait_for_nbd_connect()` lines 44-53, `_wait_for_nbd_disconnect()` lines 55-63, `_start_nbd_server()` lines 65-84, `_stop_nbd_server()` lines 86-90, `_start_nbd_server_netlink()` lines 92-95, `_stop_nbd_server_netlink()` lines 97-100, `_netlink_connect()` lines 102-104, `_netlink_disconnect()` lines 106-108; external commands `nbd-client`, `grep`, `sleep`, `cat`.

Control flow: `group_requires()` uses local helpers `_have_nbd`; gates `_have_root`, `_have_nbd`.

State and persistence behavior: touches state paths such as `/sys/kernel/debug/nbd/nbd0/tasks`, `/dev/nbd0`, `/dev/null`, `$FULL`, `$(lsblk --raw --noheadings -o SIZE /dev/nbd0)`, `$(cat "${TMPDIR}/nbd.pid")` writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `common/rc`; requirement gates include `_have_root`, `_have_nbd`, `_have_driver nbd`, `_have_program nbd-server`, `_have_program nbd-client`, `_have_nbd_netlink`, `_have_program genl-ctrl-list`; runtime command surface includes `nbd-client`, `grep`, `sleep`, `cat`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/002 -->
# sources/test-tools/blktests/tests/nvme/002

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create many subsystems and test discovery".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create many subsystems and test discovery`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-53; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_loop`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `$(_create_nvmet_port)`, `$(losetup -f)`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_loop`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/003 -->
# sources/test-tools/blktests/tests/nvme/003

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test if we're sending keep-alives to a discovery controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test if we're sending keep-alives to a discovery controller`, `QUICK=1`; functions `requires()` lines 13-18, `set_conditions()` lines 20-22, `test()` lines 24-50; external commands `echo`, `sleep`, `grep`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_have_writeable_kmsg`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`, `grep`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_have_writeable_kmsg`; runtime command surface includes `echo`, `sleep`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/004 -->
# sources/test-tools/blktests/tests/nvme/004

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme and nvmet UUID NS descriptors".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme and nvmet UUID NS descriptors`, `QUICK=1`; functions `requires()` lines 14-18, `set_conditions()` lines 20-22, `test()` lines 24-42; external commands `nvme`, `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_find_nvme_dev "${def_subsysnqn}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `nvme`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/005 -->
# sources/test-tools/blktests/tests/nvme/005

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "reset local loopback target".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=reset local loopback target`, `QUICK=1`; functions `requires()` lines 13-18, `set_conditions()` lines 20-22, `test()` lines 24-44; external commands `multipath`, `echo`.

Control flow: `requires()` uses commands `multipath`; gates `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/sys/class/nvme/${nvmedev}/reset_controller`, `$(_find_nvme_dev "${def_subsysnqn}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `multipath`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/006 -->
# sources/test-tools/blktests/tests/nvme/006

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create an NVMeOF target".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create an NVMeOF target`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-32; external commands `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/008 -->
# sources/test-tools/blktests/tests/nvme/008

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create an NVMeOF host".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create an NVMeOF host`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-41; external commands `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_find_nvme_dev "${def_subsysnqn}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/010 -->
# sources/test-tools/blktests/tests/nvme/010

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run data verification fio job".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=run data verification fio job`, `TIMED=1`; functions `requires()` lines 12-17, `set_conditions()` lines 19-21, `test()` lines 23-44; external commands `fio`, `echo`.

Control flow: `requires()` uses gates `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$(_find_nvme_ns "${def_subsys_uuid}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/012 -->
# sources/test-tools/blktests/tests/nvme/012

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run mkfs and data verification fio".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=run mkfs and data verification fio`, `TIMED=1`; functions `requires()` lines 13-20, `set_conditions()` lines 22-24, `test()` lines 26-48; external commands `mkfs`, `fio`, `echo`.

Control flow: `requires()` uses gates `_have_xfs`, `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_test_img_size 350m`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `fio`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$(_find_nvme_ns "${def_subsys_uuid}")` creates filesystems or mountpoints and must unwind them during cleanup.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_xfs`, `_have_fio`, `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_test_img_size 350m`; runtime command surface includes `mkfs`, `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/014 -->
# sources/test-tools/blktests/tests/nvme/014

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "flush a command from host".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=flush a command from host`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-52; external commands `echo`, `blockdev`, `dd`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `blockdev`, `dd`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/urandom`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(blockdev --getsize64 "/dev/${ns}")`, `$(blockdev --getbsz "/dev/${ns}")`, `$((size / bs)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `blockdev`, `dd`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/016 -->
# sources/test-tools/blktests/tests/nvme/016

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create/delete many NVMeOF block device-backed ns and test discovery".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create/delete many NVMeOF block device-backed ns and test discovery`; functions `requires()` lines 11-14, `set_conditions()` lines 16-18, `test()` lines 20-53; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_require_nvme_trtype_is_loop`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(losetup -f)`, `$((def_nsid + i - 1)`, `$(_create_nvmet_port)`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_nvme_trtype_is_loop`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/017 -->
# sources/test-tools/blktests/tests/nvme/017

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create/delete many file-ns and test discovery".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create/delete many file-ns and test discovery`; functions `requires()` lines 11-14, `set_conditions()` lines 16-18, `test()` lines 20-55; external commands `echo`.

Control flow: `requires()` uses gates `_require_nvme_trtype_is_loop`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(_nvme_def_file_path)`, `$((def_nsid + i - 1)`, `$(_create_nvmet_port)`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_nvme_trtype_is_loop`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/017 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/018 -->
# sources/test-tools/blktests/tests/nvme/018

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "unit test NVMe-oF out of range access on a file backend".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=unit test NVMe-oF out of range access on a file backend`, `QUICK=1`; functions `requires()` lines 13-17, `set_conditions()` lines 19-21, `test()` lines 23-50; external commands `echo`, `blockdev`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `blockdev`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(blockdev --getsz "/dev/${ns}")`, `$(blockdev --getbsz "/dev/${ns}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `blockdev`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/018 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/019 -->
# sources/test-tools/blktests/tests/nvme/019

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe DSM Discard command".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe DSM Discard command`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-44; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$(_find_nvme_ns "${def_subsys_uuid}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/019 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/021 -->
# sources/test-tools/blktests/tests/nvme/021

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe list command".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe list command`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-44; external commands `echo`, `nvme`, `grep`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`, `grep`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/021 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/022 -->
# sources/test-tools/blktests/tests/nvme/022

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe reset command".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe reset command`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-45; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${nvmedev}`, `$FULL`, `$(_find_nvme_dev "${def_subsysnqn}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/022 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/023 -->
# sources/test-tools/blktests/tests/nvme/023

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe smart-log command".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe smart-log command`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-44; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/023 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/025 -->
# sources/test-tools/blktests/tests/nvme/025

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe effects-log".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe effects-log`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-44; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${nvmedev}`, `$FULL`, `$(_find_nvme_dev "${def_subsysnqn}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/025 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/026 -->
# sources/test-tools/blktests/tests/nvme/026

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe ns-descs".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe ns-descs`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-44; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/026 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/027 -->
# sources/test-tools/blktests/tests/nvme/027

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe ns-rescan command".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe ns-rescan command`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-45; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${nvmedev}`, `$FULL`, `$(_find_nvme_dev "${def_subsysnqn}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/027 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/028 -->
# sources/test-tools/blktests/tests/nvme/028

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe list-subsys".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe list-subsys`, `QUICK=1`; functions `requires()` lines 12-16, `set_conditions()` lines 18-20, `test()` lines 22-40; external commands `echo`, `nvme`, `grep`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`, `grep`.

State and persistence behavior: touches state paths such as `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `nvme`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/028 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/029 -->
# sources/test-tools/blktests/tests/nvme/029

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test userspace IO via nvme-cli read/write interface".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test userspace IO via nvme-cli read/write interface`, `QUICK=1`; functions `requires()` lines 13-17, `set_conditions()` lines 19-21, `test()` lines 55-93; external commands `blockdev`, `dd`, `nvme`, `diff`, `echo`, `cat`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/vm/nr_hugepages`, `/dev/urandom`, `/dev/$`, `/proc/sys/vm/nr_hugepages`, `$FULL`, `$(blockdev --getss "$disk")`, `$((cnt * bs)`, `$(mktemp /tmp/blk_img_XXXXXX)`, `$(cat /proc/sys/vm/nr_hugepages)`, `$(_find_nvme_ns "${def_subsys_uuid}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `blockdev`, `dd`, `nvme`, `diff`, `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/029 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/030 -->
# sources/test-tools/blktests/tests/nvme/030

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "ensure the discovery generation counter is updated appropriately".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=ensure the discovery generation counter is updated appropriately`, `QUICK=1`; functions `requires()` lines 12-17, `set_conditions()` lines 19-21, `test()` lines 23-69; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_kernel_nvme_target`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `$(_create_nvmet_port)`, `$(losetup -f)`, `$(_discovery_genctr "$port")`, `$(_check_genctr "${genctr}" "$port" \
			       "adding a subsystem to a port")`, `$(_check_genctr "${genctr}" "$port" "adding host to allow_hosts")`, `$(_check_genctr "${genctr}" "$port" \
			       "removing host from allow_hosts")`, `$(_check_genctr "${genctr}" "$port" \
			       "removing a subsystem from a port")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`, `_require_kernel_nvme_target`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/030 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/031 -->
# sources/test-tools/blktests/tests/nvme/031

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test deletion of NVMeOF controllers immediately after setup".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test deletion of NVMeOF controllers immediately after setup`, `QUICK=1`; functions `requires()` lines 20-24, `set_conditions()` lines 26-28, `test()` lines 30-62; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `$(_nvme_def_file_path)`, `$(losetup -f --show "$(_nvme_def_file_path)`, `$(_create_nvmet_port)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/031 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/032 -->
# sources/test-tools/blktests/tests/nvme/032

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme pci adapter rescan/reset/remove during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `nvme_trtype=pci`, `DESCRIPTION=test nvme pci adapter rescan/reset/remove during I/O`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 21-24, `device_requires()` lines 26-28, `test_device()` lines 30-74; external commands `nvme`, `echo`, `sleep`.

Control flow: `requires()` uses gates `_have_fio`. `device_requires()` uses gates `_require_test_dev_is_nvme_pci`. `test_device()` uses commands `echo`, `sleep`, `nvme`.

State and persistence behavior: touches state paths such as `/sys/bus/pci/devices/${pdev}`, `/sys/bus/pci/rescan`, `/dev/null`, `$(_get_pci_dev_from_blkdev)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_require_test_dev_is_nvme_pci`; runtime command surface includes `nvme`, `echo`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/032 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/033 -->
# sources/test-tools/blktests/tests/nvme/033

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "create and connect to an NVMeOF target with a passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=create and connect to an NVMeOF target with a passthru controller`, `QUICK=1`; functions `requires()` lines 11-14, `device_requires()` lines 16-18, `set_conditions()` lines 20-22, `nvme_info()` lines 24-29, `compare_dev_info()` lines 31-53, `test_device()` lines 55-75; external commands `nvme`, `grep`, `cat`, `diff`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses local helpers `compare_dev_info`; commands `echo`.

State and persistence behavior: touches state paths such as `$(nvme_info "${TEST_DEV}")`, `$(nvme_info "${passthru_dev}")`, `$(_nvmet_passthru_target_connect)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `nvme`, `grep`, `cat`, `diff`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/033 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/034 -->
# sources/test-tools/blktests/tests/nvme/034

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run data verification fio job on an NVMeOF passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=run data verification fio job on an NVMeOF passthru controller`, `TIMED=1`; functions `requires()` lines 11-15, `device_requires()` lines 17-20, `set_conditions()` lines 22-24, `test_device()` lines 26-45; external commands `fio`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_fio`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_nvmet_passthru_target_connect)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_fio`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/034 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/035 -->
# sources/test-tools/blktests/tests/nvme/035

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "run mkfs and data verification fio job on an NVMeOF passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=run mkfs and data verification fio job on an NVMeOF passthru controller`, `TIMED=1`; functions `requires()` lines 12-17, `device_requires()` lines 19-24, `set_conditions()` lines 26-28, `test_device()` lines 30-49; external commands `mkfs`, `fio`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_xfs`, `_have_fio`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`, `_require_test_dev_size`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`, `fio`.

State and persistence behavior: touches state paths such as `$(_nvmet_passthru_target_connect)` creates filesystems or mountpoints and must unwind them during cleanup.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_have_xfs`, `_have_fio`, `_require_test_dev_is_not_nvme_multipath`, `_require_test_dev_size`; runtime command surface includes `mkfs`, `fio`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/035 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/036 -->
# sources/test-tools/blktests/tests/nvme/036

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test NVMe reset command on an NVMeOF target with a passthru controller".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test NVMe reset command on an NVMeOF target with a passthru controller`, `QUICK=1`; functions `requires()` lines 11-14, `device_requires()` lines 16-18, `set_conditions()` lines 20-22, `test_device()` lines 24-49; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/${ctrldev}`, `$FULL`, `$(_nvmet_passthru_target_connect)`, `$(_find_nvme_dev "${def_subsysnqn}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/036 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/037 -->
# sources/test-tools/blktests/tests/nvme/037

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test deletion of NVMeOF passthru controllers immediately after setup".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test deletion of NVMeOF passthru controllers immediately after setup`; functions `requires()` lines 10-13, `device_requires()` lines 15-17, `set_conditions()` lines 19-21, `test_device()` lines 23-48; external commands `echo`.

Control flow: `requires()` uses gates `_have_kernel_option NVME_TARGET_PASSTHRU`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `set_conditions()` is present and carries the file-specific action body. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_nvmet_passthru_target_connect \
				--subsysnqn "${subsys}${i}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option NVME_TARGET_PASSTHRU`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/037 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/038 -->
# sources/test-tools/blktests/tests/nvme/038

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test deletion of NVMeOF subsystem without enabling".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test deletion of NVMeOF subsystem without enabling`, `QUICK=1`; functions `requires()` lines 17-19, `set_conditions()` lines 21-23, `test()` lines 25-40; external commands `echo`.

Control flow: `requires()` is present and carries the file-specific action body. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_create_nvmet_port)` uses configfs/sysfs to create or tear down kernel target configuration.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/038 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/039 -->
# sources/test-tools/blktests/tests/nvme/039

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test error logging".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test error logging`, `QUICK=1`; functions `requires()` lines 15-18, `device_requires()` lines 20-22, `test_device()` lines 182-232; external commands `nvme`, `grep`, `dd`, `echo`, `blockdev`, `sleep`.

Control flow: `requires()` uses commands `nvme`; gates `_have_program nvme`, `_have_kernel_options FAULT_INJECTION FAULT_INJECTION_DEBUG_FS`. `device_requires()` uses gates `_require_test_dev_is_not_nvme_multipath`. `test_device()` uses commands `echo`, `blockdev`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/null`, `/dev/zero`, `$(echo "$1" |  cut -d "n" -f3)`, `$(blockdev --getss "${TEST_DEV}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_program nvme`, `_have_kernel_options FAULT_INJECTION FAULT_INJECTION_DEBUG_FS`, `_require_test_dev_is_not_nvme_multipath`; runtime command surface includes `nvme`, `grep`, `dd`, `echo`, `blockdev`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/039 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/040 -->
# sources/test-tools/blktests/tests/nvme/040

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme fabrics controller reset/disconnect operation during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme fabrics controller reset/disconnect operation during I/O`; functions `requires()` lines 12-17, `set_conditions()` lines 19-21, `test()` lines 23-58; external commands `nvme`, `echo`, `fio`, `sleep`.

Control flow: `requires()` uses gates `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `fio`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/null`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(_find_nvme_ns "${def_subsys_uuid}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `nvme`, `echo`, `fio`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/040 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/041 -->
# sources/test-tools/blktests/tests/nvme/041

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Create authenticated connections".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Create authenticated connections`, `QUICK=1`; functions `requires()` lines 12-19, `set_conditions()` lines 21-23, `test()` lines 25-56; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-dhchap-key -n "${def_subsysnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/041 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/042 -->
# sources/test-tools/blktests/tests/nvme/042

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test dhchap key types for authenticated connections".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test dhchap key types for authenticated connections`, `QUICK=1`; functions `requires()` lines 12-19, `set_conditions()` lines 21-23, `test()` lines 25-68; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-dhchap-key --hmac=${hmac} -n "${def_subsysnqn}" 2> /dev/null)`, `$(nvme gen-dhchap-key --key-length=${key_len} -n "${def_subsysnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/042 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/043 -->
# sources/test-tools/blktests/tests/nvme/043

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test hash and DH group variations for authenticated connections".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test hash and DH group variations for authenticated connections`, `QUICK=1`; functions `requires()` lines 12-20, `set_conditions()` lines 22-24, `test()` lines 26-69; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-dhchap-key -n "${def_hostnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/043 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/044 -->
# sources/test-tools/blktests/tests/nvme/044

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test bi-directional authentication".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test bi-directional authentication`, `QUICK=1`; functions `requires()` lines 12-20, `set_conditions()` lines 22-24, `test()` lines 26-88; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-dhchap-key -n "${def_subsysnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/044 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/045 -->
# sources/test-tools/blktests/tests/nvme/045

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test re-authentication".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test re-authentication`, `QUICK=1`; functions `requires()` lines 12-21, `set_conditions()` lines 23-25, `test()` lines 27-115; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_fio`, `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/sys/class/nvme/${ctrldev}/dhchap_secret`, `/sys/class/nvme/${ctrldev}/dhchap_ctrl_secret`, `/dev/null`, `/dev/${ns}`, `$(nvme gen-dhchap-key -n "${def_subsysnqn}" 2> /dev/null)`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(nvme gen-dhchap-key --nqn "${def_subsysnqn}" 2> /dev/null)`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_nvme_calc_rand_io_size 4m)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TARGET_AUTH`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_nvme_trtype_is_fabrics`, `_require_nvme_cli_auth`, `_have_crypto_algorithm dh-generic`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/045 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/046 -->
# sources/test-tools/blktests/tests/nvme/046

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "basic test for unprivileged passthrough on /dev/ngX".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=basic test for unprivileged passthrough on /dev/ngX`, `QUICK=1`; functions `requires()` lines 11-15, `test_device()` lines 17-53; external commands `echo`, `chmod`, `nvme`.

Control flow: `requires()` uses gates `_require_normal_user`, `_have_kver 6 2`. `test_device()` uses commands `echo`, `chmod`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/ngX`, `$(stat -c "%a" "$ngdev")`, `$(_test_dev_nvme_nsid)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_normal_user`, `_have_kver 6 2`; runtime command surface includes `echo`, `chmod`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/046 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/047 -->
# sources/test-tools/blktests/tests/nvme/047

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test different queue types for fabric transports".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=test different queue types for fabric transports`; functions `requires()` lines 12-18, `set_conditions()` lines 20-22, `test()` lines 24-52; external commands `rdma`, `echo`.

Control flow: `requires()` uses commands `rdma`; gates `_have_xfs`, `_have_fio`, `_require_nvme_trtype tcp rdma`, `_have_kver 4 21`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `$FULL`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_nvme_calc_rand_io_size 4M)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_xfs`, `_have_fio`, `_require_nvme_trtype tcp rdma`, `_have_kver 4 21`; runtime command surface includes `rdma`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/047 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/048 -->
# sources/test-tools/blktests/tests/nvme/048

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test queue count changes on reconnect".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test queue count changes on reconnect`; functions `requires()` lines 11-16, `set_conditions()` lines 18-20, `nvmf_check_queue_count()` lines 22-47, `set_nvmet_attr_qid_max()` lines 49-55, `set_qid_max()` lines 57-66, `test()` lines 68-102; external commands `rdma`, `cat`, `echo`, `sleep`.

Control flow: `requires()` uses commands `rdma`; gates `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_require_min_cpus 2`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `set_qid_max`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/class/nvme-fabrics/ctl/`, `$(_find_nvme_dev "${subsys_name}")`, `$((queue_count + 1)`, `$(cat /sys/class/nvme-fabrics/ctl/"${nvmedev}"/queue_count)`, `$((retries - 1)` uses configfs/sysfs to create or tear down kernel target configuration records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_require_min_cpus 2`; runtime command surface includes `rdma`, `cat`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/048 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/049 -->
# sources/test-tools/blktests/tests/nvme/049

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "basic test for uring-passthrough I/O on /dev/ngX".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=basic test for uring-passthrough I/O on /dev/ngX`, `QUICK=1`; functions `requires()` lines 11-16, `metadata_bytes_per_4k_io()` lines 18-25, `test_device()` lines 27-76; external commands `echo`, `fio`, `grep`.

Control flow: `requires()` uses gates `_have_kernel_option IO_URING`, `_have_kver 6 1`, `_have_fio_ver 3 33`. `test_device()` uses local helpers `metadata_bytes_per_4k_io`; commands `echo`, `fio`, `grep`.

State and persistence behavior: touches state paths such as `/dev/ngX`, `$(<"${TEST_DEV_SYSFS}"/queue/physical_block_size)`, `$(<"${TEST_DEV_SYSFS}"/metadata_bytes)`, `$((4096 * md_bytes / phys_bs)`, `$(_min_io "$ngdev")`, `$(metadata_bytes_per_4k_io)`, `$(fio --name=check --bs="$test_dev_bs" --size="$target_size" --filename="$ngdev" \
			    --rw=read --ioengine=io_uring_cmd 2>&1)` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option IO_URING`, `_have_kver 6 1`, `_have_fio_ver 3 33`; runtime command surface includes `echo`, `fio`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/049 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/050 -->
# sources/test-tools/blktests/tests/nvme/050

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme-pci timeout with fio jobs".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme-pci timeout with fio jobs`, `CAN_BE_ZONED=1`, `nvme_trtype=pci`; functions `requires()` lines 16-20, `test_device()` lines 22-61; external commands `timeout`, `fio`, `echo`, `grep`, `sleep`.

Control flow: `requires()` uses gates `_have_fio`, `_have_kernel_options FAIL_IO_TIMEOUT FAULT_INJECTION_DEBUG_FS`. `test_device()` uses commands `echo`, `fio`, `grep`, `sleep`.

State and persistence behavior: touches state paths such as `/sys/block/`, `/sys/kernel/debug/fail_io_timeout/probability`, `/sys/kernel/debug/fail_io_timeout/interval`, `/sys/kernel/debug/fail_io_timeout/times`, `/sys/kernel/debug/fail_io_timeout/space`, `/sys/kernel/debug/fail_io_timeout/verbose`, `/sys/bus/pci/devices/${pdev}/remove`, `/sys/bus/pci/rescan`, `$FULL`, `$(_get_pci_dev_from_blkdev)`, `$(basename "${TEST_DEV}")`, `$(nproc)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_fio`, `_have_kernel_options FAIL_IO_TIMEOUT FAULT_INJECTION_DEBUG_FS`; runtime command surface includes `timeout`, `fio`, `echo`, `grep`, `sleep`.

Risks and test signals: declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/050 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/051 -->
# sources/test-tools/blktests/tests/nvme/051

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvmet concurrent ns enable/disable".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvmet concurrent ns enable/disable`, `QUICK=1`; functions `requires()` lines 13-16, `set_conditions()` lines 18-20, `ns_enable_disable_loop()` lines 22-28, `test()` lines 30-47; external commands `echo`.

Control flow: `requires()` uses gates `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `ns_enable_disable_loop`; commands `echo`.

State and persistence behavior: uses configfs/sysfs to create or tear down kernel target configuration.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/051 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/052 -->
# sources/test-tools/blktests/tests/nvme/052

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test file-ns creation/deletion under one subsystem".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test file-ns creation/deletion under one subsystem`; functions `requires()` lines 13-17, `set_conditions()` lines 19-21, `test()` lines 23-65; external commands `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_loop`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$((def_nsid + i - 1)`, `$(_nvme_def_file_path)`, `$(_create_nvmet_ns --blkdev "$filepath" --nsid "${nsid}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_loop`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/052 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/053 -->
# sources/test-tools/blktests/tests/nvme/053

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test controller rescan under I/O load".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test controller rescan under I/O load`, `TIMED=1`; functions `get_sleep_time()` lines 15-19, `rescan_controller()` lines 21-37, `test_device()` lines 39-70; external commands `echo`, `sleep`.

Control flow: `test_device()` uses local helpers `rescan_controller`; commands `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$FULL`, `$((RANDOM % 50 + 1)`, `$((duration / 10)`, `$((duration % 10)`, `$(($(date +%s)`, `$(date +%s)`, `$(get_sleep_time)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; runtime command surface includes `echo`, `sleep`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/053 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/054 -->
# sources/test-tools/blktests/tests/nvme/054

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test the NVMe reservation feature".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test the NVMe reservation feature`, `QUICK=1`; functions `requires()` lines 13-16, `set_conditions()` lines 18-20, `resv_report()` lines 22-28, `test_resv()` lines 30-69, `test()` lines 71-104; external commands `nvme`, `grep`, `echo`.

Control flow: `requires()` uses gates `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `test_resv`; commands `echo`, `grep`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/null`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(echo "${ns}" | grep -oE '[0-9]+' | sed -n '2p')` uses configfs/sysfs to create or tear down kernel target configuration records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_nvme_trtype_is_fabrics`; runtime command surface includes `nvme`, `grep`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/054 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/055 -->
# sources/test-tools/blktests/tests/nvme/055

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test nvme write to a loop target ns just after ns is disabled".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test nvme write to a loop target ns just after ns is disabled`, `QUICK=1`; functions `requires()` lines 19-24, `set_conditions()` lines 26-28, `nvmf_disable_ns_change_aen()` lines 30-70, `test()` lines 72-119; external commands `nvme`, `sleep`, `timeout`, `echo`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_loop`, `_have_kernel_option DEBUG_ATOMIC_SLEEP`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `nvmf_disable_ns_change_aen`; commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/$`, `/dev/urandom`, `$FULL`, `$(nvme get-feature "$disk" --feature-id=0xB | cut -d':' -f3)`, `$(( aen_conf & 0xFEFF )`, `$(date +%s)`, `$(nvme get-feature "$disk" \
			--feature-id=0xB | cut -d':' -f3)`, `$(_find_nvme_ns "${def_subsys_uuid}")` uses configfs/sysfs to create or tear down kernel target configuration writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_loop`, `_have_kernel_option DEBUG_ATOMIC_SLEEP`; runtime command surface includes `nvme`, `sleep`, `timeout`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/055 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/056 -->
# sources/test-tools/blktests/tests/nvme/056

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "enable zero copy offload and run rw traffic".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=enable zero copy offload and run rw traffic`, `TIMED=1`; functions `requires()` lines 23-37, `have_netlink_cli()` lines 39-57, `have_iface()` lines 59-65, `set_conditions()` lines 67-69, `netlink_cli()` lines 71-75, `eth_stat()` lines 77-79, `ddp_stat()` lines 81-84, `ddp_caps()` lines 86-90, `configure_ddp()` lines 92-107, `connect_run_disconnect()` lines 109-208, `test()` lines 210-277; external commands `ip`, `ethtool`, `python3`, `echo`, `modprobe`, `cat`.

Control flow: `requires()` uses local helpers `have_netlink_cli`, `have_iface`; commands `ip`, `ethtool`, `python3`; gates `_require_remote_nvme_target`, `_require_nvme_trtype tcp`, `_have_kernel_option ULP_DDP`, `_have_module nvme_tcp`, `_have_module_param nvme_tcp ddp_offload`, `_have_fio`, `_have_program ip`, `_have_program ethtool`, `_have_kernel_source`, `_have_program python3`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `ddp_caps`, `configure_ddp`, `connect_run_disconnect`; commands `echo`, `ip`, `cat`.

State and persistence behavior: touches state paths such as `/sys/module/nvme_tcp/parameters/ddp_offload`, `/dev/null`, `/dev/$`, `$FULL`, `$(netlink_cli --do caps-get --json "{\"ifindex\": $iface_idx}")`, `$(ddp_stat rx-nvme-tcp-sk-add)`, `$(ddp_stat rx-nvme-tcp-sk-add-fail)`, `$(ddp_stat rx-nvme-tcp-sk-del)`, `$(ddp_stat rx-nvme-tcp-setup-fail)`, `$(ddp_stat rx-nvme-tcp-drop)`, `$(ddp_stat rx-nvme-tcp-resync)`, `$(ddp_stat rx-nvme-tcp-packets)` loads or unloads kernel modules, so host module parameters and device lifetimes are part of the test state writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_require_remote_nvme_target`, `_require_nvme_trtype tcp`, `_have_kernel_option ULP_DDP`, `_have_module nvme_tcp`, `_have_module_param nvme_tcp ddp_offload`, `_have_fio`, `_have_program ip`, `_have_program ethtool`, `_have_kernel_source`, `_have_program python3`; runtime command surface includes `ip`, `ethtool`, `python3`, `echo`, `modprobe`, `cat`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/056 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/057 -->
# sources/test-tools/blktests/tests/nvme/057

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme fabrics controller ANA failover during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme fabrics controller ANA failover during I/O`; functions `requires()` lines 11-16, `set_conditions()` lines 18-20, `failback()` lines 22-35, `failover()` lines 37-50, `test()` lines 52-97; external commands `nvme`, `echo`, `sleep`.

Control flow: `requires()` uses gates `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `failback`, `failover`; commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/${ns}`, `/dev/null`, `$FULL`, `$(( portno + 1 )`, `$(( portno + 1)`, `$(_find_nvme_ns "$def_subsys_uuid")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_fio`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `nvme`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/057 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/058 -->
# sources/test-tools/blktests/tests/nvme/058

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test rapid namespace remapping".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test rapid namespace remapping`; functions `requires()` lines 11-15, `set_conditions()` lines 17-19, `_setup_ana()` lines 21-52, `test()` lines 54-112; external commands `echo`, `losetup`.

Control flow: `requires()` uses gates `_have_loop`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `_setup_ana`; commands `echo`, `losetup`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(( portno + 1 )`, `$(losetup -f --show "${file_path}")`, `$(uuidgen)`, `$(( (i % 3)`, `$(seq 1 "${num_namespaces}" | shuf)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `losetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/058 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/059 -->
# sources/test-tools/blktests/tests/nvme/059

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test atomic writes".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=test atomic writes`, `QUICK=1`; functions `requires()` lines 13-17, `device_requires()` lines 19-21, `test_device()` lines 23-146; external commands `nvme`, `echo`, `cat`, `grep`.

Control flow: `requires()` uses commands `nvme`; gates `_have_program nvme`, `_have_xfs_io_atomic_write`. `device_requires()` uses gates `_require_device_support_atomic_writes`. `test_device()` uses commands `echo`, `cat`, `nvme`, `grep`.

State and persistence behavior: touches state paths such as `$(cat "$queue_path"/logical_block_size)`, `$(cat "$queue_path"/max_hw_sectors_kb)`, `$(( "$sysfs_max_hw_sectors_kb" * 1024 )`, `$(cat "$queue_path"/atomic_write_max_bytes)`, `$(cat "$queue_path"/atomic_write_unit_max_bytes)`, `$(cat "$queue_path"/atomic_write_unit_min_bytes)`, `$(nvme id-ns /dev/"${ns_dev}" | grep nsfeat | awk '{ print $3}')`, `$((("$nvme_nsfeat" & 0x2)`, `$(nvme id-ns /dev/"$ns_dev" | grep nawupf | awk '{ print $3}')`, `$(( ("$nvme_awupf" + 1)`, `$(nvme id-ctrl /dev/"${ctrl_dev}" | grep awupf | awk '{ print $3}')`, `$(run_xfs_io_xstat /dev/"$ns_dev" "stat.atomic_write_unit_max")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_program nvme`, `_have_xfs_io_atomic_write`, `_require_device_support_atomic_writes`; runtime command surface includes `nvme`, `echo`, `cat`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/059 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/060 -->
# sources/test-tools/blktests/tests/nvme/060

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test nvme fabrics target reset".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test nvme fabrics target reset`; functions `requires()` lines 11-16, `set_conditions()` lines 18-20, `nvmet_debug_trigger_reset()` lines 22-27, `nvmet_reset_loop()` lines 29-34, `test()` lines 36-64; external commands `nvme`, `rdma`, `echo`, `sleep`.

Control flow: `requires()` uses commands `rdma`; gates `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_have_kernel_option NVME_TARGET_DEBUGFS`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `nvmet_reset_loop`; commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/null`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_require_nvme_trtype tcp rdma fc`, `_have_kernel_option NVME_TARGET_DEBUGFS`; runtime command surface includes `nvme`, `rdma`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/060 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/061 -->
# sources/test-tools/blktests/tests/nvme/061

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test fabric target teardown and setup during I/O".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=test fabric target teardown and setup during I/O`, `TIMED=1`; functions `requires()` lines 13-18, `set_conditions()` lines 20-22, `test()` lines 24-66; external commands `rdma`, `echo`, `sleep`, `cat`.

Control flow: `requires()` uses commands `rdma`; gates `_have_loop`, `_have_fio`, `_require_nvme_trtype tcp rdma fc`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`, `cat`.

State and persistence behavior: touches state paths such as `/sys/class/nvme-fabrics/ctl/${nvmedev}/state`, `/dev/${ns}`, `/dev/null`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(cat "${state_file}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_fio`, `_require_nvme_trtype tcp rdma fc`; runtime command surface includes `rdma`, `echo`, `sleep`, `cat`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/061 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/062 -->
# sources/test-tools/blktests/tests/nvme/062

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Create TLS-encrypted connections".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Create TLS-encrypted connections`, `QUICK=1`; functions `requires()` lines 12-21, `set_conditions()` lines 23-25, `test()` lines 27-94; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_TCP_TLS NVME_TARGET_TCP_TLS`, `_require_kernel_nvme_fabrics_feature tls`, `_require_nvme_trtype tcp`, `_require_nvme_cli_tls`, `_have_libnvme_ver 1 11`, `_have_systemd_tlshd_service`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(nvme gen-tls-key -n "${def_hostnqn}" -c "${def_subsysnqn}" -m 1 -I 1 -i 2> /dev/null)`, `$(_find_nvme_dev "${def_subsysnqn}")`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_TCP_TLS NVME_TARGET_TCP_TLS`, `_require_kernel_nvme_fabrics_feature tls`, `_require_nvme_trtype tcp`, `_require_nvme_cli_tls`, `_have_libnvme_ver 1 11`, `_have_systemd_tlshd_service`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/062 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/063 -->
# sources/test-tools/blktests/tests/nvme/063

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Create authenticated TCP connections with secure concatenation".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Create authenticated TCP connections with secure concatenation`, `QUICK=1`; functions `requires()` lines 12-22, `set_conditions()` lines 24-26, `test()` lines 28-107; external commands `echo`, `nvme`.

Control flow: `requires()` uses gates `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TCP_TLS NVME_TARGET_AUTH \`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_kernel_nvme_fabrics_feature concat`, `_require_nvme_trtype tcp`, `_require_nvme_cli_auth`, `_have_systemd_tlshd_service`. `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `nvme`.

State and persistence behavior: touches state paths such as `/dev/null`, `/dev/${ctrl}`, `$(nvme gen-dhchap-key -m 1 -n "${def_hostnqn}" 2> /dev/null)`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(_nvme_ctrl_tls_key "$ctrl" || true)`, `$(nvme gen-dhchap-key -m 2 -n "${def_hostnqn}" 2> /dev/null)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_loop`, `_have_kernel_options NVME_AUTH NVME_TCP_TLS NVME_TARGET_AUTH \`, `_require_kernel_nvme_fabrics_feature dhchap_ctrl_secret`, `_require_kernel_nvme_fabrics_feature concat`, `_require_nvme_trtype tcp`, `_require_nvme_cli_auth`, `_have_systemd_tlshd_service`; runtime command surface includes `echo`, `nvme`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/063 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/064 -->
# sources/test-tools/blktests/tests/nvme/064

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "exercise the nvme metadata usage with passthrough commands".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=exercise the nvme metadata usage with passthrough commands`, `QUICK=1`; functions `requires()` lines 14-16, `device_requires()` lines 18-21, `test_device()` lines 26-34; external commands `nvme`, `echo`.

Control flow: `requires()` is present and carries the file-specific action body. `device_requires()` is present and carries the file-specific action body. `test_device()` uses commands `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; runtime command surface includes `nvme`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/064 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/065 -->
# sources/test-tools/blktests/tests/nvme/065

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "test unmap write zeroes sysfs interface with nvmet devices".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test unmap write zeroes sysfs interface with nvmet devices`, `QUICK=1`, `nvmet_blkdev_type=device`; functions `requires()` lines 16-20, `set_conditions()` lines 22-24, `setup_test_device()` lines 26-46, `cleanup_test_device()` lines 48-52, `test()` lines 54-97; external commands `echo`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `setup_test_device`, `cleanup_test_device`; commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `/sys/block/$dname/queue/write_zeroes_unmap_max_hw_bytes`, `/sys/block/$dname/queue/write_zeroes_unmap_max_bytes`, `/sys/block/$dname/queue/write_zeroes_max_bytes`, `/dev/${SCSI_DEBUG_DEVICES`, `$(_create_nvmet_port)`, `$(setup_test_device lbprz=0)`, `$(cat "/sys/block/$dname/queue/write_zeroes_unmap_max_hw_bytes")`, `$(cat "/sys/block/$dname/queue/write_zeroes_unmap_max_bytes")`, `$(setup_test_device lbprz=1 lbpws=1)`, `$(cat "/sys/block/$dname/queue/write_zeroes_max_bytes")` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/065 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/066 -->
# sources/test-tools/blktests/tests/nvme/066

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "Test NVMe host driver code for NVME SED operations".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=Test NVMe host driver code for NVME SED operations`, `QUICK=1`, `SED_PASSWORD=password`, `SED_NEW_PASSWORD=PASSWORD`; functions `requires()` lines 18-24, `device_requires()` lines 26-29, `nvme_sed_discover()` lines 31-35, `nvme_sed_init()` lines 37-48, `nvme_sed_lock()` lines 50-54, `nvme_sed_unlock()` lines 56-60, `nvme_sed_change_password()` lines 62-75, `nvme_sed_revert()` lines 77-86, `nvme_sed_revert_destructive()` lines 88-101, `test_device()` lines 103-173; external commands `nvme`, `echo`, `grep`.

Control flow: `requires()` uses commands `nvme`; gates `_have_kernel_option BLK_SED_OPAL`, `_have_program expect`, `_have_program nvme`, `_require_nvme_cli_sed`. `device_requires()` uses gates `_require_test_dev_is_nvme`, `_require_test_dev_support_sed`. `test_device()` uses local helpers `nvme_sed_discover`, `nvme_sed_init`, `nvme_sed_lock`, `nvme_sed_unlock`, `nvme_sed_change_password`, `nvme_sed_revert`, `nvme_sed_revert_destructive`; commands `echo`, `grep`.

State and persistence behavior: touches state paths such as `/dev/null`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option BLK_SED_OPAL`, `_have_program expect`, `_have_program nvme`, `_require_nvme_cli_sed`, `_require_test_dev_is_nvme`, `_require_test_dev_support_sed`; runtime command surface includes `nvme`, `echo`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/066 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/067 -->
# sources/test-tools/blktests/tests/nvme/067

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "exercise the nvme admin commands usage with io uring passthrough interfaces".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`; top-level variables `DESCRIPTION=exercise the nvme admin commands usage with io uring passthrough interfaces`, `QUICK=1`; functions `requires()` lines 8-11, `test_device()` lines 16-36; external commands `nvme`, `echo`.

Control flow: `requires()` uses gates `_have_kernel_option IO_URING`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/}`, `/dev/${devname`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`; requirement gates include `_have_kernel_option IO_URING`; runtime command surface includes `nvme`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/067 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/068 -->
# sources/test-tools/blktests/tests/nvme/068

Purpose: NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. This specific test is declared as: "NVMe multipath delayed removal test".

Important APIs/types/functions: sourced libraries `tests/nvme/rc`, `common/xfs`; top-level variables `DESCRIPTION=NVMe multipath delayed removal test`; functions `requires()` lines 14-19, `set_conditions()` lines 21-23, `_delayed_nvme_reconnect_ctrl()` lines 25-28, `test()` lines 30-113; external commands `multipath`, `sleep`, `echo`.

Control flow: `requires()` uses commands `multipath`; gates `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `_delayed_nvme_reconnect_ctrl`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/block/${ns}/delayed_removal_secs`, `$(_find_nvme_dev "${def_subsysnqn}")`, `$(_find_nvme_ns "${def_subsys_uuid}")`, `$(_module_use_count nvme_core)`, `$(run_xfs_io_pwritev2 /dev/"$ns" 4096)`.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `tests/nvme/rc`, `common/xfs`; requirement gates include `_have_loop`, `_have_module_param_value nvme_core multipath Y`, `_require_nvme_trtype_is_fabrics`; runtime command surface includes `multipath`, `sleep`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/068 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/rc -->
# sources/test-tools/blktests/tests/nvme/rc

Purpose: shared `tests/nvme/rc` support for NVMe and NVMe-over-Fabrics coverage, including loop/rdma/tcp/fc targets, passthrough controllers, authentication, TLS, ANA, queue management, reset, discovery, and admin commands. It defines 43 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/nvme`, `common/multipath-over-rdma`; functions `_NVMET_TRTYPES_is_valid()` lines 11-25, `_set_nvme_trtype()` lines 27-40, `_set_nvmet_blkdev_type()` lines 42-55, `group_setup()` lines 57-62, `group_requires()` lines 64-68, `group_device_requires()` lines 70-72, `_require_test_dev_is_nvme_pci()` lines 74-80, `_require_test_dev_is_not_nvme_multipath()` lines 82-88, `_require_test_dev_support_sed()` lines 90-100, `_require_nvme_cli_auth()` lines 102-108, `_require_nvme_cli_tls()` lines 110-116, `_require_nvme_cli_sed()` lines 118-124, `_require_kernel_nvme_fabrics_feature()` lines 126-140, `_require_kernel_nvme_target()` lines 142-148, `_require_remote_nvme_target()` lines 150-156, `_test_dev_nvme_ctrl()` lines 158-160, `_test_dev_nvme_nsid()` lines 162-164, `_nvme_get_ctrl_list()` lines 166-182, `_nvme_calc_rand_io_size()` lines 184-192, `_nvme_discover()` lines 194-210, `_remove_nvmet_allow_hosts()` lines 212-218, `_create_nvmet_passthru()` lines 220-233, `_remove_nvmet_passhtru()` lines 235-243, `_set_nvmet_hostkey()` lines 245-251, `_set_nvmet_ctrlkey()` lines 253-259, `_set_nvmet_hash()` lines 261-267, `_set_nvmet_dhgroup()` lines 269-275, `_enable_nvmet_ns()` lines 277-285, plus 15 more helpers; external commands `nvme`, `rdma`, `echo`, `multipath`, `grep`, `cat`, `sleep`, `timeout`.

Control flow: `group_setup()` is present and carries the file-specific action body. `group_requires()` uses local helpers `_NVMET_TRTYPES_is_valid`; gates `_have_root`, `_have_nvme_cli_with_json_support`. `group_device_requires()` uses gates `_require_test_dev_is_nvme`.

State and persistence behavior: touches state paths such as `/sys/block/${nvmedev}n`, `/sys/class/nvme/`, `/sys/kernel/debug/`, `/dev/null`, `/dev/nvme-fabrics`, `/dev/char/$`, `/dev/${dev}n${nsid}`, `$(${nvme_target_control} config --show-trtype)`, `$(${nvme_target_control} config --show-blkdev-type)`, `$(readlink -f "$TEST_DEV_SYSFS/device")`, `$(cat "${TEST_DEV_SYSFS}/device/dev")`, `$(readlink  "${TEST_DEV_SYSFS}/device/subsystem")` uses configfs/sysfs to create or tear down kernel target configuration records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nvme` suite and the shared harness; through `common/rc`, `common/nvme`, `common/multipath-over-rdma`; requirement gates include `_have_root`, `_have_nvme_cli_with_json_support`, `_require_test_dev_is_nvme`, `_require_test_dev_is_nvme_pci`, `_require_test_dev_is_not_nvme_multipath`, `_require_test_dev_support_sed`, `_require_nvme_cli_auth`, `_require_nvme_cli_tls`, `_require_nvme_cli_sed`, `_require_kernel_nvme_fabrics_feature`, `_have_driver nvme-fabrics`, `_require_kernel_nvme_target`, `_require_remote_nvme_target`, `_have_tlshd_ver`, `_have_program tlshd`, `_have_systemd_tlshd_service`, `_have_tlshd_ver 1 0 0`, `_have_systemctl_unit tlshd`; runtime command surface includes `nvme`, `rdma`, `echo`, `multipath`, `grep`, `cat`, `sleep`, `timeout`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nvme/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/001 -->
# sources/test-tools/blktests/tests/rnbd/001

Purpose: RNBD client/server smoke and stress coverage for remote block-device mapping over loopback RDMA. This specific test is declared as: "Start Stop RNBD".

Important APIs/types/functions: sourced libraries `tests/rnbd/rc`; top-level variables `DESCRIPTION=Start Stop RNBD`, `CHECK_DMESG=1`, `QUICK=1`; functions `requires()` lines 13-16, `test()` lines 35-39; external commands `losetup`, `sleep`, `echo`.

Control flow: `requires()` uses gates `_have_rnbd`, `_have_loop`. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(losetup -f)`.

Dependencies and integration points: integrates with the blktests `rnbd` suite and the shared harness; through `tests/rnbd/rc`; requirement gates include `_have_rnbd`, `_have_loop`; runtime command surface includes `losetup`, `sleep`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/002 -->
# sources/test-tools/blktests/tests/rnbd/002

Purpose: RNBD client/server smoke and stress coverage for remote block-device mapping over loopback RDMA. This specific test is declared as: "Start Stop RNBD repeatedly".

Important APIs/types/functions: sourced libraries `tests/rnbd/rc`; top-level variables `DESCRIPTION=Start Stop RNBD repeatedly`, `CHECK_DMESG=1`, `QUICK=1`; functions `requires()` lines 19-22, `test()` lines 43-47; external commands `losetup`, `echo`.

Control flow: `requires()` uses gates `_have_rnbd`, `_have_loop`. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$(losetup -f)`.

Dependencies and integration points: integrates with the blktests `rnbd` suite and the shared harness; through `tests/rnbd/rc`; requirement gates include `_have_rnbd`, `_have_loop`; runtime command surface includes `losetup`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/rc -->
# sources/test-tools/blktests/tests/rnbd/rc

Purpose: shared `tests/rnbd/rc` support for RNBD client/server smoke and stress coverage for remote block-device mapping over loopback RDMA. It defines 4 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/multipath-over-rdma`; functions `_have_rnbd()` lines 10-17, `_setup_rnbd()` lines 19-29, `_stop_rnbd_client()` lines 36-44, `_start_rnbd_client()` lines 46-52; external commands `grep`, `echo`.

Control flow: `_have_rnbd()` uses gates `_have_driver rdma_rxe`, `_have_driver rnbd_server`, `_have_driver rnbd_client`.

State and persistence behavior: touches state paths such as `/sys/block/rnbd`, `/sys/devices/virtual/rnbd-client/ctl/map_device`, `/dev/null`, `$(rdma_network_interfaces)`, `$(get_ipv4_addr "$i")`, `$(ls -d /sys/block/rnbd* 2>/dev/null)` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `rnbd` suite and the shared harness; through `common/rc`, `common/multipath-over-rdma`; requirement gates include `_have_rnbd`, `_have_driver rdma_rxe`, `_have_driver rnbd_server`, `_have_driver rnbd_client`; runtime command surface includes `grep`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/001 -->
# sources/test-tools/blktests/tests/scsi/001

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "try triggering a kernel GPF with 0 byte SG reads".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`; top-level variables `DESCRIPTION=try triggering a kernel GPF with 0 byte SG reads`, `QUICK=1`; functions `requires()` lines 13-16, `test_device()` lines 18-26; external commands `echo`, `timeout`.

Control flow: `requires()` uses gates `_have_scsi_generic`, `_have_src_program sg/syzkaller1`. `test_device()` uses commands `echo`, `timeout`.

State and persistence behavior: touches state paths such as `/dev/$`, `$(_get_test_dev_sg)`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`; requirement gates include `_have_scsi_generic`, `_have_src_program sg/syzkaller1`; runtime command surface includes `echo`, `timeout`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/002 -->
# sources/test-tools/blktests/tests/scsi/002

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "perform a SG_DXFER_FROM_DEV from the /dev/sg read-write interface".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`; top-level variables `DESCRIPTION=perform a SG_DXFER_FROM_DEV from the /dev/sg read-write interface`, `QUICK=1`; functions `requires()` lines 13-16, `test_device()` lines 18-25; external commands `echo`.

Control flow: `requires()` uses gates `_have_scsi_generic`, `_have_src_program sg/dxfer-from-dev`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/dev/sg`, `/dev/$`, `$(_get_test_dev_sg)`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`; requirement gates include `_have_scsi_generic`, `_have_src_program sg/dxfer-from-dev`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/004 -->
# sources/test-tools/blktests/tests/scsi/004

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "ensure repeated TASK SET FULL results in EIO on timing out command".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=ensure repeated TASK SET FULL results in EIO on timing out command`, `CAN_BE_ZONED=1`; functions `requires()` lines 20-22, `test()` lines 24-49; external commands `echo`, `timeout`, `dd`, `grep`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`. `test()` uses commands `echo`, `timeout`, `dd`, `grep`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `/sys/bus/pseudo/drivers/scsi_debug/opts`, `/sys/bus/pseudo/drivers/scsi_debug/ndelay`, `/sys/bus/pseudo/drivers/scsi_debug/add_host`, `/dev/${SCSI_DEBUG_DEVICES`, `/dev/null`, `$(cat /sys/bus/pseudo/drivers/scsi_debug/add_host)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`; runtime command surface includes `echo`, `timeout`, `dd`, `grep`, `cat`.

Risks and test signals: declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/005 -->
# sources/test-tools/blktests/tests/scsi/005

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test SCSI device blacklisting".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test SCSI device blacklisting`, `QUICK=1`; functions `requires()` lines 13-16, `test()` lines 18-48; external commands `echo`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`, `_have_module_param scsi_debug inq_vendor`. `test()` uses commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/device/vendor")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/device/model")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/device/blacklist")`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`, `_have_module_param scsi_debug inq_vendor`; runtime command surface includes `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/006 -->
# sources/test-tools/blktests/tests/scsi/006

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "toggle SCSI cache type".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`; top-level variables `DESCRIPTION=toggle SCSI cache type`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `device_requires()` lines 15-17, `test_device()` lines 19-52; external commands `echo`, `cat`, `grep`.

Control flow: `device_requires()` uses gates `_require_test_dev_is_scsi_disk`. `test_device()` uses commands `echo`, `cat`, `grep`.

State and persistence behavior: touches state paths such as `$(cat "$cache_type_path")`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`; requirement gates include `_require_test_dev_is_scsi_disk`; runtime command surface includes `echo`, `cat`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/007 -->
# sources/test-tools/blktests/tests/scsi/007

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "Trigger the SCSI error handler".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=Trigger the SCSI error handler`, `QUICK=1`; functions `requires()` lines 14-16, `start_tracing()` lines 18-37, `stop_tracing()` lines 39-51, `run_test()` lines 53-92, `test()` lines 94-111; external commands `echo`, `cat`, `grep`, `timeout`, `dd`.

Control flow: `requires()` uses gates `_have_loadable_scsi_debug`. `test()` uses local helpers `run_test`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/kernel/tracing/tracing_on`, `/sys/kernel/tracing`, `/sys/module/scsi_mod/parameters/scsi_logging_level`, `/sys/class/block/$dev/queue/io_timeout`, `/sys/module/scsi_debug/parameters/delay`, `/dev/$dev`, `/dev/null`, `$FULL`, `$(<"/sys/class/block/$dev/queue/io_timeout")`, `$(_get_kernel_option HZ)`, `$((delay_s * "${freq}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_loadable_scsi_debug`; runtime command surface includes `echo`, `cat`, `grep`, `timeout`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/008 -->
# sources/test-tools/blktests/tests/scsi/008

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test block data lifetime support".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test block data lifetime support`, `QUICK=1`; functions `requires()` lines 11-17, `submit_io()` lines 19-56, `test()` lines 58-88; external commands `echo`, `fio`, `grep`.

Control flow: `requires()` uses gates `_have_scsi_debug_group_number_stats`, `_have_fio_ver 3 37`. `test()` uses local helpers `submit_io`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/bus/pseudo/drivers/scsi_debug/group_number_stats`, `/sys/vm/drop_caches`, `/dev/${SCSI_DEBUG_DEVICES`, `/proc/sys/vm/drop_caches`, `$((1 - direct_io)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug_group_number_stats`, `_have_fio_ver 3 37`; runtime command surface includes `echo`, `fio`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/009 -->
# sources/test-tools/blktests/tests/scsi/009

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test scsi atomic writes".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`, `common/xfs`; top-level variables `DESCRIPTION=test scsi atomic writes`, `QUICK=1`; functions `requires()` lines 14-17, `device_requires()` lines 19-21, `fallback_device()` lines 23-32, `cleanup_fallback_device()` lines 34-36, `test_device()` lines 38-183; external commands `echo`.

Control flow: `requires()` uses gates `_have_scsi_debug`, `_have_xfs_io_atomic_write`. `device_requires()` uses gates `_require_device_support_atomic_writes`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `/sys/module/scsi_debug/parameters/atomic_wr_max_length`, `/sys/module/scsi_debug/parameters/atomic_wr_gran`, `/dev/${SCSI_DEBUG_DEVICES`, `$(< "${TEST_DEV_SYSFS}"/queue/logical_block_size)`, `$(< "${TEST_DEV_SYSFS}"/queue/max_hw_sectors_kb)`, `$(( "$sysfs_max_hw_sectors_kb" * 1024 )`, `$(< "${TEST_DEV_SYSFS}"/queue/atomic_write_max_bytes)`, `$(< "${TEST_DEV_SYSFS}"/queue/atomic_write_unit_max_bytes)`, `$(< "${TEST_DEV_SYSFS}"/queue/atomic_write_unit_min_bytes)`, `$(< /sys/module/scsi_debug/parameters/atomic_wr_max_length)`, `$(< /sys/module/scsi_debug/parameters/atomic_wr_gran)`, `$(( "$scsi_debug_atomic_wr_max_length" * "$sysfs_logical_block_size" )`.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`, `common/xfs`; requirement gates include `_have_scsi_debug`, `_have_xfs_io_atomic_write`, `_require_device_support_atomic_writes`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/010 -->
# sources/test-tools/blktests/tests/scsi/010

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test unmap write zeroes sysfs interface with scsi devices".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test unmap write zeroes sysfs interface with scsi devices`, `QUICK=1`; functions `requires()` lines 14-16, `setup_test_device()` lines 18-28, `test()` lines 30-84; external commands `echo`, `cat`.

Control flow: `requires()` uses gates `_have_scsi_debug`. `test()` uses local helpers `setup_test_device`; commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/${SCSI_DEBUG_DEVICES`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/queue/write_zeroes_unmap_max_hw_bytes")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/queue/write_zeroes_unmap_max_bytes")`, `$(cat "/sys/block/${SCSI_DEBUG_DEVICES[0]}/queue/write_zeroes_max_bytes")` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/scsi_debug`; requirement gates include `_have_scsi_debug`; runtime command surface includes `echo`, `cat`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/011 -->
# sources/test-tools/blktests/tests/scsi/011

Purpose: SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. This specific test is declared as: "test data lifetime propagation".

Important APIs/types/functions: sourced libraries `tests/scsi/rc`, `common/null_blk`, `common/scsi_debug`; top-level variables `DESCRIPTION=test data lifetime propagation`, `QUICK=1`; functions `requires()` lines 12-21, `run_test()` lines 23-47, `test()` lines 49-74; external commands `mkfs.f2fs`, `mount`, `echo`, `umount`.

Control flow: `requires()` uses commands `mkfs.f2fs`; gates `_have_fio`, `_have_driver f2fs`, `_have_kver 6 10`, `_have_program mkfs.f2fs`, `_have_scsi_debug_group_number_stats`. `test()` uses local helpers `run_test`; commands `echo`, `umount`.

State and persistence behavior: touches state paths such as `/sys/bus/pseudo/drivers/scsi_debug/group_number_stats`, `/dev/${SCSI_DEBUG_DEVICES`, `$TMPDIR/mnt` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `tests/scsi/rc`, `common/null_blk`, `common/scsi_debug`; requirement gates include `_have_fio`, `_have_driver f2fs`, `_have_kver 6 10`, `_have_program mkfs.f2fs`, `_have_scsi_debug_group_number_stats`; runtime command surface includes `mkfs.f2fs`, `mount`, `echo`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/rc -->
# sources/test-tools/blktests/tests/scsi/rc

Purpose: shared `tests/scsi/rc` support for SCSI and sg/blk queue coverage using scsi_debug, sg devices, unmap/write-zeroes, data-lifetime, cache, atomic-write, and error-handler paths. It defines 7 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`; functions `group_requires()` lines 9-11, `group_device_requires()` lines 13-15, `_have_scsi_generic()` lines 17-19, `_require_test_dev_is_scsi()` lines 21-27, `_require_test_dev_is_scsi_disk()` lines 29-35, `_get_test_dev_sg()` lines 37-39, `_test_dev_is_sata()` lines 41-43; external commands `echo`, `grep`.

Control flow: `group_requires()` uses gates `_have_root`. `group_device_requires()` uses local helpers `_require_test_dev_is_scsi`; gates `_require_test_dev_is_scsi`.

State and persistence behavior: touches state paths such as `$(<"${TEST_DEV_SYSFS}"/device/vendor)` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `scsi` suite and the shared harness; through `common/rc`; requirement gates include `_have_root`, `_require_test_dev_is_scsi`, `_have_scsi_generic`, `_have_driver sg`, `_require_test_dev_is_scsi_disk`; runtime command surface includes `echo`, `grep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/scsi/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/001 -->
# sources/test-tools/blktests/tests/srp/001

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Create and remove LUNs".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Create and remove LUNs`, `QUICK=1`; functions `count_luns()` lines 11-23, `wait_for_luns()` lines 25-37, `test()` lines 39-42; external commands `echo`, `sleep`, `trap`.

Control flow: `test()` uses local helpers `wait_for_luns`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `/sys/class/srp_remote_ports/`, `/sys/class/scsi_device/${h}`, `$FULL`, `$(count_luns)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `echo`, `sleep`, `trap`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/002 -->
# sources/test-tools/blktests/tests/srp/002

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "File I/O on top of multipath concurrently with logout and login (mq)".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=File I/O on top of multipath concurrently with logout and login (mq)`, `TIMED=1`; functions `test_disconnect_repeatedly()` lines 10-31, `test()` lines 33-37; external commands `multipath`, `trap`, `echo`.

Control flow: `test()` uses local helpers `test_disconnect_repeatedly`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$(mountpoint 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `multipath`, `trap`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/003 -->
# sources/test-tools/blktests/tests/srp/003

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "File I/O on top of multipath concurrently with logout and login (sq)".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=File I/O on top of multipath concurrently with logout and login (sq)`, `TIMED=1`; functions `requires()` lines 10-12, `test_disconnect_repeatedly()` lines 14-35, `test()` lines 37-41; external commands `multipath`, `trap`, `echo`.

Control flow: `requires()` uses gates `_have_legacy_dm`. `test()` uses local helpers `test_disconnect_repeatedly`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$(mountpoint 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; requirement gates include `_have_legacy_dm`; runtime command surface includes `multipath`, `trap`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/004 -->
# sources/test-tools/blktests/tests/srp/004

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "File I/O on top of multipath concurrently with logout and login (sq-on-mq)".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=File I/O on top of multipath concurrently with logout and login (sq-on-mq)`, `TIMED=1`; functions `requires()` lines 10-12, `test_disconnect_repeatedly()` lines 14-35, `test()` lines 37-41; external commands `multipath`, `trap`, `echo`.

Control flow: `requires()` uses gates `_have_legacy_dm`. `test()` uses local helpers `test_disconnect_repeatedly`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$(mountpoint 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; requirement gates include `_have_legacy_dm`; runtime command surface includes `multipath`, `trap`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/005 -->
# sources/test-tools/blktests/tests/srp/005

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O with large transfer sizes, cmd_sg_entries=255 and bs=4M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O with large transfer sizes, cmd_sg_entries=255 and bs=4M`, `QUICK=1`; functions `test_large_transfer_size()` lines 10-22, `test()` lines 24-27; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_large_transfer_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$((1<<17)`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/006 -->
# sources/test-tools/blktests/tests/srp/006

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O with large transfer sizes, cmd_sg_entries=255 and bs=8M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O with large transfer sizes, cmd_sg_entries=255 and bs=8M`, `QUICK=1`; functions `test_large_transfer_size()` lines 10-22, `test()` lines 24-27; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_large_transfer_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$((1<<17)`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/007 -->
# sources/test-tools/blktests/tests/srp/007

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O with large transfer sizes, cmd_sg_entries=1 and bs=4M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O with large transfer sizes, cmd_sg_entries=1 and bs=4M`, `QUICK=1`; functions `test_low_sg_size()` lines 10-22, `test()` lines 24-27; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_low_sg_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/008 -->
# sources/test-tools/blktests/tests/srp/008

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O with large transfer sizes, cmd_sg_entries=1 and bs=8M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O with large transfer sizes, cmd_sg_entries=1 and bs=8M`, `QUICK=1`; functions `test_low_sg_size()` lines 10-21, `test()` lines 23-26; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_low_sg_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/009 -->
# sources/test-tools/blktests/tests/srp/009

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Buffered I/O with large transfer sizes, cmd_sg_entries=255 and bs=4M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Buffered I/O with large transfer sizes, cmd_sg_entries=255 and bs=4M`, `QUICK=1`; functions `test_large_transfer_size()` lines 10-22, `test()` lines 24-27; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_large_transfer_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$((1<<17)`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/010 -->
# sources/test-tools/blktests/tests/srp/010

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Buffered I/O with large transfer sizes, cmd_sg_entries=255 and bs=8M".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Buffered I/O with large transfer sizes, cmd_sg_entries=255 and bs=8M`, `QUICK=1`; functions `test_large_transfer_size()` lines 10-22, `test()` lines 24-27; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_large_transfer_size`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$((1<<17)`, `$(get_bdev 0)`, `$((10**6)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/011 -->
# sources/test-tools/blktests/tests/srp/011

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Block I/O on top of multipath concurrently with logout and login".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Block I/O on top of multipath concurrently with logout and login`, `TIMED=1`; functions `test_disconnect_repeatedly()` lines 10-31, `test()` lines 33-37; external commands `multipath`, `trap`, `echo`.

Control flow: `test()` uses local helpers `test_disconnect_repeatedly`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `multipath`, `trap`, `echo`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/012 -->
# sources/test-tools/blktests/tests/srp/012

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "dm-mpath on top of multiple I/O schedulers".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=dm-mpath on top of multiple I/O schedulers`, `QUICK=1`; functions `test_io_schedulers()` lines 10-41, `test()` lines 43-46; external commands `modprobe`, `echo`, `trap`.

Control flow: `test()` uses local helpers `test_io_schedulers`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `/dev/null`, `$FULL`, `$(uname -r)`, `$(basename "$m")`, `$(get_bdev 0)`, `$(basename "$(readlink -f "${dev}")`, `$(_io_schedulers "$dm")` loads or unloads kernel modules, so host module parameters and device lifetimes are part of the test state writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; requirement gates include `_have_legacy_dm`; runtime command surface includes `modprobe`, `echo`, `trap`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/013 -->
# sources/test-tools/blktests/tests/srp/013

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Direct I/O using a discontiguous buffer".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Direct I/O using a discontiguous buffer`, `QUICK=1`; functions `discontiguous_io()` lines 10-35, `test()` lines 37-40; external commands `echo`, `dd`, `trap`.

Control flow: `test()` uses local helpers `discontiguous_io`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(get_bdev 0)`, `$(printf "%x" $((byte ^ 0xa5)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `echo`, `dd`, `trap`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/014 -->
# sources/test-tools/blktests/tests/srp/014

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "Run sg_reset while I/O is ongoing".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=Run sg_reset while I/O is ongoing`, `TIMED=1`; functions `make_running()` lines 15-35, `make_all_running()` lines 39-51, `set_running_loop()` lines 54-63, `sg_reset_loop()` lines 66-79, `test_sg_reset()` lines 81-101, `test()` lines 103-107; external commands `sg_reset`, `echo`, `sleep`, `trap`.

Control flow: `test()` uses local helpers `test_sg_reset`; commands `trap`, `echo`.

State and persistence behavior: touches state paths such as `/sys/class/scsi_device/`, `/sys/class/block/`, `/dev/disk/by-id/dm-uuid-mpath-360014056e756c6c62300000000000000`, `/dev/}`, `/dev/null`, `$FULL`, `$(dirname "$(dirname "$sp")`, `$(<"$sp")`, `$(realpath "$dev")`, `$(basename "$(dirname "$(dirname "$h")`, `$(($(_uptime_s)`, `$(get_bdev 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `sg_reset`, `echo`, `sleep`, `trap`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/016 -->
# sources/test-tools/blktests/tests/srp/016

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This specific test is declared as: "RDMA hot-unplug".

Important APIs/types/functions: sourced libraries `tests/srp/rc`; top-level variables `DESCRIPTION=RDMA hot-unplug`, `QUICK=1`; functions `test_hot_unplug()` lines 10-15, `test()` lines 17-20; external commands `trap`, `echo`.

Control flow: `test()` uses local helpers `test_hot_unplug`; commands `trap`, `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `tests/srp/rc`; runtime command surface includes `trap`, `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/016 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/multipath.conf -->
# sources/test-tools/blktests/tests/srp/multipath.conf

Purpose: SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. This source has no `DESCRIPTION` assignment, so its purpose is inferred from its entry points and command surface.

Important APIs/types/functions: .

Control flow: The file contributes data/configuration consumed by the surrounding test harness.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness.

Risks and test signals: primary risk is build or harness drift; signal is make/shell exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/multipath.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/rc -->
# sources/test-tools/blktests/tests/srp/rc

Purpose: shared `tests/srp/rc` support for SCSI RDMA Protocol coverage using LIO, null_blk, scsi_debug, multipath, ib_srp/srpt, and RDMA/CM or IB/CM login/logout cycles. It defines 28 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/scsi_debug`, `common/multipath-over-rdma`; top-level variables `elevator=none`, `srp_rdma_cm_port=5555`; functions `is_lio_configured()` lines 17-28, `group_requires()` lines 30-91, `use_blk_mq()` lines 96-125, `srp_single_login()` lines 128-133, `do_ib_cm_login()` lines 138-151, `rdma_dev_to_net_dev()` lines 153-155, `do_rdma_cm_login()` lines 160-193, `show_srp_connections()` lines 195-220, `log_in()` lines 224-256, `log_out()` lines 259-268, `simulate_network_failure_loop()` lines 271-291, `remove_mpath_devs()` lines 295-324, `start_srp_ini()` lines 327-330, `stop_srp_ini()` lines 333-347, `configure_lio_vdev()` lines 350-375, `lio_scsi_mpath_id()` lines 379-393, `scsi_mpath_id()` lines 395-397, `get_bdev_path()` lines 401-407, `get_bdev()` lines 410-412, `configure_target_ports()` lines 417-466, `start_lio_srpt()` lines 469-538, `stop_lio_srpt()` lines 541-569, `start_srpt()` lines 572-583, `stop_srpt()` lines 586-589, `start_target()` lines 591-593, `stop_target()` lines 595-597, `shutdown_client()` lines 599-603, `setup()` lines 606-608; external commands `mkfs.ext4`, `mkfs.xfs`, `multipath`, `multipathd`, `pidof`, `rdma`, `sg_reset`, `fio`, `diff`, `echo`, `sleep`, `modprobe`, `grep`, `dd`.

Control flow: `group_requires()` uses local helpers `is_lio_configured`; commands `mkfs.ext4`, `mkfs.xfs`, `multipath`, `multipathd`, `pidof`, `rdma`, `sg_reset`, `fio`, `diff`; gates `_have_configfs`, `_have_driver sd_mod`, `_have_driver sg`, `_have_driver scsi_dh_alua`, `_have_driver scsi_dh_emc`, `_have_driver scsi_dh_rdac`, `_have_module dm_multipath`, `_have_module dm_queue_length`, `_have_module dm_service_time`, `_have_module ib_ipoib`.

State and persistence behavior: touches state paths such as `/sys/kernel/config/target`, `/sys/module/dm_mod/parameters`, `/sys/module/scsi_mod/parameters`, `/sys/class/infiniband/$ibdev/ports/$port/gids/0`, `/sys/class/infiniband_srp/srp-${2}-`, `/sys/class/net/$d/ifindex`, `/sys/class/scsi_host/`, `/sys/class/scsi_host/host}`, `/sys/class/scsi_device/${h}`, `/sys/module/ib_srpt/parameters/srpt_service_guid`, `/sys/class/infiniband/`, `/sys/class/srp_remote_ports` loads or unloads kernel modules, so host module parameters and device lifetimes are part of the test state uses configfs/sysfs to create or tear down kernel target configuration creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `srp` suite and the shared harness; through `common/rc`, `common/scsi_debug`, `common/multipath-over-rdma`; requirement gates include `_have_configfs`, `_have_driver sd_mod`, `_have_driver sg`, `_have_driver scsi_dh_alua`, `_have_driver scsi_dh_emc`, `_have_driver scsi_dh_rdac`, `_have_module dm_multipath`, `_have_module dm_queue_length`, `_have_module dm_service_time`, `_have_module ib_ipoib`, `_have_module ib_srp`, `_have_module ib_srpt`, `_have_module ib_umad`, `_have_module ib_uverbs`, `_have_module null_blk`, `_have_module rdma_cm`, `_have_module rdma_rxe`, `_have_module siw`; runtime command surface includes `mkfs.ext4`, `mkfs.xfs`, `multipath`, `multipathd`, `pidof`, `rdma`, `sg_reset`, `fio`, `diff`, `echo`, `sleep`, `modprobe`, `grep`, `dd`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/srp/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/001 -->
# sources/test-tools/blktests/tests/throtl/001

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "basic functionality".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=basic functionality`, `QUICK=1`; functions `set_conditions()` lines 12-14, `test()` lines 16-43; external commands `echo`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$((1024 * 1024)`.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/002 -->
# sources/test-tools/blktests/tests/throtl/002

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "iops limit over IO split".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=iops limit over IO split`, `QUICK=1`; functions `set_conditions()` lines 13-15, `test()` lines 17-46; external commands `echo`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_get_page_size)`, `$(($(_throtl_get_max_io_size)`, `$((page_size / 1024)`, `$((iops * page_size)`.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/003 -->
# sources/test-tools/blktests/tests/throtl/003

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "bps limit over IO split".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=bps limit over IO split`, `QUICK=1`; functions `set_conditions()` lines 13-15, `test()` lines 17-39; external commands `echo`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_get_page_size)`, `$((1024 * 1024)`.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/004 -->
# sources/test-tools/blktests/tests/throtl/004

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "delete disk while IO is throttled".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=delete disk while IO is throttled`, `QUICK=1`; functions `set_conditions()` lines 14-16, `test()` lines 18-40; external commands `echo`, `sleep`, `grep`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`, `grep`.

State and persistence behavior: touches state paths such as `$FULL`, `$((1024 * 1024)` persists transient cgroup controller limits while IO is running writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`, `sleep`, `grep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/005 -->
# sources/test-tools/blktests/tests/throtl/005

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "change config with throttled IO".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=change config with throttled IO`, `QUICK=1`; functions `set_conditions()` lines 13-15, `test()` lines 17-38; external commands `echo`, `sleep`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `$((512 * 1024)`, `$((256 * 1024)` persists transient cgroup controller limits while IO is running.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`, `sleep`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/006 -->
# sources/test-tools/blktests/tests/throtl/006

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "test if meta IO has higher priority than data IO".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=test if meta IO has higher priority than data IO`, `QUICK=1`; functions `requires()` lines 13-16, `set_conditions()` lines 18-20, `test_meta_io()` lines 22-36, `test()` lines 38-68; external commands `mkfs.ext4`, `echo`, `mount`, `sleep`, `umount`.

Control flow: `requires()` uses commands `mkfs.ext4`; gates `_have_program mkfs.ext4`, `_have_driver ext4`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `test`, `test_meta_io`; commands `echo`, `mkfs.ext4`, `mount`, `sleep`, `umount`.

State and persistence behavior: touches state paths such as `/dev/${THROTL_DEV}`, `$FULL`, `$(date +%s.%N)`, `$(echo "$end_time - $start_time" | bc)`, `$((1024 * 1024)`, `$(ps -eo pid,comm | pgrep -f "jbd2/${THROTL_DEV}" | awk '{print $1}')` creates filesystems or mountpoints and must unwind them during cleanup persists transient cgroup controller limits while IO is running writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; requirement gates include `_have_program mkfs.ext4`, `_have_driver ext4`; runtime command surface includes `mkfs.ext4`, `echo`, `mount`, `sleep`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/007 -->
# sources/test-tools/blktests/tests/throtl/007

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "bps limit with iops limit over io split".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`; top-level variables `DESCRIPTION=bps limit with iops limit over io split`, `QUICK=1`; functions `set_conditions()` lines 14-16, `test()` lines 18-48; external commands `echo`.

Control flow: `set_conditions()` is present and carries the file-specific action body. `test()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$(_get_page_size)`, `$((1024 * 1024)`.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/008 -->
# sources/test-tools/blktests/tests/throtl/008

Purpose: block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. This specific test is declared as: "test cgroup iocost controller limits".

Important APIs/types/functions: sourced libraries `tests/throtl/rc`, `common/fio`; top-level variables `DESCRIPTION=test cgroup iocost controller limits`; functions `requires()` lines 12-15, `set_conditions()` lines 17-19, `run_test()` lines 21-79, `test()` lines 81-107; external commands `fio`, `echo`, `cat`.

Control flow: `requires()` uses gates `_have_fio`, `_have_kernel_option BLK_CGROUP_IOCOST`. `set_conditions()` is present and carries the file-specific action body. `test()` uses local helpers `run_test`; commands `echo`.

State and persistence behavior: touches state paths such as `/sys/block/${THROTL_DEV}/dev`, `/dev/${THROTL_DEV}`, `$TMPDIR/fio_perf`, `$FULL`, `$(<"/sys/block/${THROTL_DEV}/dev")`, `$(_cgroup2_base_dir)`, `$(echo "$read_iops < 90 || $read_iops > 110" | bc -l)`, `$(echo "$write_iops < 8 || $write_iops > 12" | bc -l)` persists transient cgroup controller limits while IO is running writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `tests/throtl/rc`, `common/fio`; requirement gates include `_have_fio`, `_have_kernel_option BLK_CGROUP_IOCOST`; runtime command surface includes `fio`, `echo`, `cat`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/rc -->
# sources/test-tools/blktests/tests/throtl/rc

Purpose: shared `tests/throtl/rc` support for block cgroup throttling coverage for cgroup v1/v2 limits, IO split accounting, delete-during-throttle, config changes, metadata priority, and iocost. It defines 14 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/null_blk`, `common/scsi_debug`, `common/cgroup`; top-level variables `THROTL_DIR=$(echo $TEST_NAME | tr / _)`, `THROTL_BLKDEV_TYPES=${THROTL_BLKDEV_TYPES:-nullb sdebug}`, `THROTL_NULL_DEV=dev_nullb`; functions `group_requires()` lines 20-27, `_set_throtl_blkdev_type()` lines 29-42, `_configure_throtl_blkdev()` lines 45-88, `_delete_throtl_blkdev()` lines 90-101, `_exit_throtl_blkdev()` lines 103-113, `_set_up_throtl()` lines 116-140, `_clean_up_throtl()` lines 142-153, `_throtl_set_limits()` lines 155-158, `_throtl_remove_limits()` lines 160-163, `_throtl_get_max_io_size()` lines 165-167, `_throtl_set_max_io_size()` lines 169-171, `_throtl_issue_fs_io()` lines 173-190, `_throtl_issue_io()` lines 192-208, `_throtl_test_io()` lines 213-225; external commands `echo`, `grep`, `cat`, `dd`.

Control flow: `group_requires()` uses gates `_have_root`, `_have_null_blk`, `_have_scsi_debug`, `_have_kernel_option BLK_DEV_THROTTLING`, `_have_cgroup2_controller io`, `_have_program bc`.

State and persistence behavior: touches state paths such as `/sys/kernel/config/nullb/$THROTL_DEV/power`, `/sys/block/$THROTL_DEV/device/delete`, `/sys/block/`, `/sys/block/$THROTL_DEV/queue/max_sectors_kb`, `/dev/null`, `/dev/zero`, `$(echo "$TEST_NAME" | tr '/' '_')`, `$((sector_size / 512)`, `$(_cgroup2_base_dir)`, `$(cat /sys/block/"$THROTL_DEV"/dev)`, `$(date +%s.%N)`, `$(echo "$end_time - $start_time" | bc)` uses configfs/sysfs to create or tear down kernel target configuration persists transient cgroup controller limits while IO is running.

Dependencies and integration points: integrates with the blktests `throtl` suite and the shared harness; through `common/rc`, `common/null_blk`, `common/scsi_debug`, `common/cgroup`; requirement gates include `_have_root`, `_have_null_blk`, `_have_scsi_debug`, `_have_kernel_option BLK_DEV_THROTTLING`, `_have_cgroup2_controller io`, `_have_program bc`; runtime command surface includes `echo`, `grep`, `cat`, `dd`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/throtl/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/001 -->
# sources/test-tools/blktests/tests/ublk/001

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk delete".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk delete`; functions `_run()` lines 11-31, `test()` lines 33-47; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/002 -->
# sources/test-tools/blktests/tests/ublk/002

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk crash with delete after dead confirmation".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk crash with delete after dead confirmation`; functions `_run()` lines 11-46, `test()` lines 48-62; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL`, `$(_get_ublk_daemon_pid 0)`, `$(_get_ublk_dev_state 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/003 -->
# sources/test-tools/blktests/tests/ublk/003

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test mounting block device exported by ublk".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test mounting block device exported by ublk`; functions `requires()` lines 11-13, `test()` lines 15-50; external commands `ublk`, `mkfs.ext4`, `echo`, `mount`, `umount`.

Control flow: `requires()` uses commands `mkfs.ext4`; gates `_have_program mkfs.ext4`. `test()` uses commands `echo`, `mount`, `umount`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `/dev/null`, `$TMPDIR/mnt`, `$TMPDIR/img`, `$FULL`, `$(findmnt -l -o FSTYPE -n "$mnt")` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; requirement gates include `_have_program mkfs.ext4`; runtime command surface includes `ublk`, `mkfs.ext4`, `echo`, `mount`, `umount`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/004 -->
# sources/test-tools/blktests/tests/ublk/004

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk crash with delete just after daemon kill".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk crash with delete just after daemon kill`; functions `_run()` lines 11-33, `test()` lines 35-49; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL`, `$(_get_ublk_daemon_pid 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/005 -->
# sources/test-tools/blktests/tests/ublk/005

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk recovery with one time daemon kill".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk recovery with one time daemon kill`; functions `_run()` lines 13-61, `test()` lines 63-77; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL`, `$(_get_ublk_daemon_pid 0)`, `$(_get_ublk_dev_state 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/006 -->
# sources/test-tools/blktests/tests/ublk/006

Purpose: ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. This specific test is declared as: "test ublk recovery with two times daemon kill".

Important APIs/types/functions: sourced libraries `tests/ublk/rc`; top-level variables `DESCRIPTION=test ublk recovery with two times daemon kill`; functions `_run()` lines 13-64, `test()` lines 66-80; external commands `ublk`, `echo`, `sleep`.

Control flow: `test()` uses local helpers `_run`; commands `echo`. `_run()` uses commands `echo`, `sleep`.

State and persistence behavior: touches state paths such as `/dev/ublkb0`, `$TMPDIR/img`, `$FULL`, `$(_get_ublk_daemon_pid 0)`, `$(_get_ublk_dev_state 0)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `tests/ublk/rc`; runtime command surface includes `ublk`, `echo`, `sleep`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/rc -->
# sources/test-tools/blktests/tests/ublk/rc

Purpose: shared `tests/ublk/rc` support for ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. It defines 1 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/ublk`; functions `group_requires()` lines 10-14; external commands `ublk`.

Control flow: `group_requires()` uses gates `_have_root`, `_have_ublk`, `_have_fio`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `common/rc`, `common/ublk`; requirement gates include `_have_root`, `_have_ublk`, `_have_fio`; runtime command surface includes `ublk`.

Risks and test signals: exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/001 -->
# sources/test-tools/blktests/tests/zbd/001

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "sysfs and ioctl".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=sysfs and ioctl`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 14-16, `fallback_device()` lines 18-20, `cleanup_fallback_device()` lines 22-24, `test_device()` lines 26-74; external commands `echo`.

Control flow: `requires()` uses gates `_have_src_program zbdioctl`. `test_device()` uses commands `echo`.

State and persistence behavior: touches state paths such as `$FULL`, `$(( (capacity - 1)`, `$(src/zbdioctl -s "${TEST_DEV}")`, `$(src/zbdioctl -n "${TEST_DEV}")` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_src_program zbdioctl`; runtime command surface includes `echo`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/001 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/002 -->
# sources/test-tools/blktests/tests/zbd/002

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "report zone".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=report zone`, `CAN_BE_ZONED=1`; functions `fallback_device()` lines 12-14, `cleanup_fallback_device()` lines 16-18, `_check_blkzone_report()` lines 20-109, `test_device()` lines 111-121; external commands `echo`.

Control flow: `test_device()` uses local helpers `_check_blkzone_report`; commands `echo`.

State and persistence behavior: touches state paths such as `$((REPORTED_COUNT - 1)`, `$((ZONE_STARTS[max_idx] + ZONE_LENGTHS[max_idx])`, `$((idx+1)`, `$((cur_start+len)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; runtime command surface includes `echo`.

Risks and test signals: declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/002 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/003 -->
# sources/test-tools/blktests/tests/zbd/003

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "reset sequential required zones".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=reset sequential required zones`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 14-16, `fallback_device()` lines 18-20, `cleanup_fallback_device()` lines 22-24, `test_device()` lines 26-87; external commands `blkzone`, `echo`, `dd`.

Control flow: `requires()` uses commands `blkzone`; gates `_have_program blkzone`. `test_device()` uses commands `echo`, `blkzone`, `dd`.

State and persistence behavior: touches state paths such as `/dev/zero`, `$FULL`, `$(_test_dev_max_open_active_zones)`, `$(_find_two_contiguous_seq_zones)`, `$((zone_idx + 1)`, `$(( 4096 / bs )`, `$((ZONE_STARTS[i] * 512 / bs)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_program blkzone`; runtime command surface includes `blkzone`, `echo`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/003 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/004 -->
# sources/test-tools/blktests/tests/zbd/004

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "write split across sequential zones".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=write split across sequential zones`, `QUICK=1`, `CAN_BE_ZONED=1`; functions `fallback_device()` lines 15-17, `cleanup_fallback_device()` lines 19-21, `_check_zone_cond()` lines 23-32, `test_device()` lines 34-109; external commands `echo`, `dd`.

Control flow: `test_device()` uses local helpers `_check_zone_cond`; commands `echo`, `dd`.

State and persistence behavior: touches state paths such as `/dev/zero`, `$FULL`, `$(_find_two_contiguous_seq_zones cap_eq_len)`, `$((idx+1)`, `$(((ZONE_LENGTHS[idx] - phys_blk_sectors)`, `$((ZONE_STARTS[idx] * 512 / phys_blk_size)`, `$((ZONE_STARTS[idx+1] - phys_blk_sectors)`, `$((phys_blk_size * 2)`, `$((start_sector * 512)` writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; runtime command surface includes `echo`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/004 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/005 -->
# sources/test-tools/blktests/tests/zbd/005

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "write command ordering".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=write command ordering`, `TIMED=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 16-18, `fallback_device()` lines 20-22, `cleanup_fallback_device()` lines 24-26, `test_device()` lines 28-62; external commands `echo`, `blkzone`.

Control flow: `requires()` uses gates `_have_fio_zbd_zonemode`. `test_device()` uses commands `echo`, `blkzone`.

State and persistence behavior: touches state paths such as `$(_find_first_sequential_zone)`, `$((ZONE_STARTS[zone_idx] * 512)`, `$(_test_dev_max_open_active_zones)`.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_fio_zbd_zonemode`; runtime command surface includes `echo`, `blkzone`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/005 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/006 -->
# sources/test-tools/blktests/tests/zbd/006

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "revalidate".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=revalidate`, `TIMED=1`, `CAN_BE_ZONED=1`; functions `requires()` lines 14-16, `fallback_device()` lines 18-20, `cleanup_fallback_device()` lines 22-24, `test_device()` lines 26-53; external commands `echo`, `blkzone`.

Control flow: `requires()` uses gates `_have_fio_zbd_zonemode`. `test_device()` uses commands `echo`, `blkzone`.

State and persistence behavior: touches state paths such as `$(_find_first_sequential_zone)`, `$((ZONE_STARTS[zone_idx] * 512)`, `$((ZONE_LENGTHS[zone_idx] * 512)`.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_fio_zbd_zonemode`; runtime command surface includes `echo`, `blkzone`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/006 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/007 -->
# sources/test-tools/blktests/tests/zbd/007

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "zone mapping between logical and container devices".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=zone mapping between logical and container devices`, `CAN_BE_ZONED=1`, `QUICK=1`; functions `requires()` lines 16-18, `device_requires()` lines 20-22, `select_zones()` lines 27-41, `test_device()` lines 43-120; external commands `dmsetup`, `echo`, `blkzone`, `grep`, `dd`.

Control flow: `requires()` uses commands `dmsetup`; gates `_have_program dmsetup`. `device_requires()` uses gates `_require_test_dev_is_logical`. `test_device()` uses local helpers `select_zones`; commands `echo`, `blkzone`, `grep`, `dd`.

State and persistence behavior: touches state paths such as `/dev/zero`, `$FULL`, `$(_find_first_sequential_zone)`, `$(_find_last_sequential_zone)`, `$(_find_sequential_zone_in_middle \
				      "${zones[0]}" "${zones[1]}")`, `$((4096 * (i + 1)`, `$((container_start * 512 / bs)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_program dmsetup`, `_require_test_dev_is_logical`; runtime command surface includes `dmsetup`, `echo`, `blkzone`, `grep`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates declares `CAN_BE_ZONED=1`, so zoned-device behavior is part of the valid matrix contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/007 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/008 -->
# sources/test-tools/blktests/tests/zbd/008

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "check no stale page cache after BLKZONERESET and data read race".

Important APIs/types/functions: sourced libraries `tests/block/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=check no stale page cache after BLKZONERESET and data read race`, `TIMED=1`; functions `requires()` lines 15-19, `test()` lines 21-55; external commands `echo`, `blkzone`, `dd`.

Control flow: `requires()` uses gates `_have_loadable_scsi_debug`, `_have_module_param scsi_debug zbc`, `_have_program xfs_io`. `test()` uses commands `echo`, `blkzone`, `dd`.

State and persistence behavior: touches state paths such as `/dev/${SCSI_DEBUG_DEVICES`, `/dev/null`, `$FULL`, `$(dd if="$dev" bs=4k 2>> "$FULL" | hexdump -e '"%x"')` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/block/rc`, `common/scsi_debug`; requirement gates include `_have_loadable_scsi_debug`, `_have_module_param scsi_debug zbc`, `_have_program xfs_io`; runtime command surface includes `echo`, `blkzone`, `dd`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/008 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/009 -->
# sources/test-tools/blktests/tests/zbd/009

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test gap zone support with BTRFS".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test gap zone support with BTRFS`, `QUICK=1`; functions `ver_a_is_before_b()` lines 12-18, `have_good_mkfs_btrfs()` lines 21-32, `requires()` lines 34-40, `test()` lines 42-82; external commands `mkfs.btrfs`, `echo`, `mount`, `umount`.

Control flow: `requires()` uses local helpers `have_good_mkfs_btrfs`; commands `mkfs.btrfs`; gates `_have_fio`, `_have_driver btrfs`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.btrfs`, `_have_loadable_scsi_debug`. `test()` uses commands `echo`, `mkfs.btrfs`, `mount`, `umount`.

State and persistence behavior: touches state paths such as `/dev/${SCSI_DEBUG_DEVICES`, `$TMPDIR/mnt`, `$(mkfs.btrfs -V | sed 's/[^[:digit:]]*//')` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/scsi_debug`; requirement gates include `_have_fio`, `_have_driver btrfs`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.btrfs`, `_have_loadable_scsi_debug`; runtime command surface includes `mkfs.btrfs`, `echo`, `mount`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/009 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/010 -->
# sources/test-tools/blktests/tests/zbd/010

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test gap zone support with F2FS".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/null_blk`, `common/scsi_debug`; top-level variables `DESCRIPTION=test gap zone support with F2FS`, `QUICK=1`; functions `requires()` lines 12-20, `test()` lines 22-73; external commands `mkfs.f2fs`, `echo`, `mount`, `umount`.

Control flow: `requires()` uses commands `mkfs.f2fs`; gates `_have_fio`, `_have_driver f2fs`, `_have_module null_blk`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.f2fs`, `_have_loadable_scsi_debug`. `test()` uses commands `echo`, `mkfs.f2fs`, `mount`, `umount`.

State and persistence behavior: touches state paths such as `/dev/nullb0`, `/dev/${SCSI_DEBUG_DEVICES`, `$TMPDIR/mnt` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/null_blk`, `common/scsi_debug`; requirement gates include `_have_fio`, `_have_driver f2fs`, `_have_module null_blk`, `_have_module_param scsi_debug zone_cap_mb`, `_have_program mkfs.f2fs`, `_have_loadable_scsi_debug`; runtime command surface includes `mkfs.f2fs`, `echo`, `mount`, `umount`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/010 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/011 -->
# sources/test-tools/blktests/tests/zbd/011

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "DM zone resource limits stacking".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`; top-level variables `DESCRIPTION=DM zone resource limits stacking`, `QUICK=1`; functions `requires()` lines 24-30, `setup_dm()` lines 35-76, `setup_concat()` lines 81-132, `check_limits()` lines 137-173, `test()` lines 284-309; external commands `dmsetup`, `echo`, `dd`.

Control flow: `requires()` uses commands `dmsetup`; gates `_have_kver 6 11`, `_have_driver dm-mod`, `_have_driver dm-crypt`, `_have_program dmsetup`, `_have_program cryptsetup`. `test()` uses local helpers `check_limits`; commands `echo`, `dmsetup`.

State and persistence behavior: touches state paths such as `/sys/block/${dname}/queue/nr_zones`, `/sys/block/${dname}/queue/chunk_sectors`, `/sys/block/${dname0}/queue/nr_zones`, `/sys/block/${dname1}/queue/nr_zones`, `/sys/block/${dname0}/queue/chunk_sectors`, `/sys/block/${devpath`, `/dev/random`, `/dev/null`, `/dev/${dname0}`, `/dev/${dname1}`, `/dev/nullb_zbd_011_1`, `/dev/nullb_zbd_011_2`.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`; requirement gates include `_have_kver 6 11`, `_have_driver dm-mod`, `_have_driver dm-crypt`, `_have_program dmsetup`, `_have_program cryptsetup`; runtime command surface includes `dmsetup`, `echo`, `dd`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/011 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/012 -->
# sources/test-tools/blktests/tests/zbd/012

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test requeuing of zoned writes and queue freezing".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/scsi_debug`; top-level variables `DESCRIPTION=test requeuing of zoned writes and queue freezing`, `TIMED=1`; functions `requires()` lines 14-17, `toggle_iosched()` lines 19-28, `test()` lines 30-91; external commands `echo`, `sleep`, `fio`.

Control flow: `requires()` uses gates `_have_fio_zbd_zonemode`, `_have_loadable_scsi_debug`. `test()` uses local helpers `toggle_iosched`; commands `echo`, `fio`.

State and persistence behavior: touches state paths such as `/sys/class/block/$`, `/dev/${SCSI_DEBUG_DEVICES`, `$(basename "$zdev")`, `$((2 * qd)`, `$((${TIMEOUT:-30}/5)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/scsi_debug`; requirement gates include `_have_fio_zbd_zonemode`, `_have_loadable_scsi_debug`; runtime command surface includes `echo`, `sleep`, `fio`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/012 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/013 -->
# sources/test-tools/blktests/tests/zbd/013

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test stacked drivers and queue freezing".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/null_blk`; top-level variables `DESCRIPTION=test stacked drivers and queue freezing`, `TIMED=1`; functions `requires()` lines 15-20, `queue_freeze_loop()` lines 25-32, `run_test()` lines 34-90, `test()` lines 92-118; external commands `echo`, `sleep`, `cat`.

Control flow: `requires()` uses gates `_have_driver dm-crypt`, `_have_driver null_blk`, `_have_fio`, `_have_program cryptsetup`. `test()` uses local helpers `run_test`; commands `echo`, `cat`.

State and persistence behavior: touches state paths such as `/sys/block/`, `/dev/nullb1`, `/dev/${zdev_basename}`, `/dev/mapper/${luks_vol_name}`, `/dev/${dmdev}`, `/dev/null`, `$(((1 << 32)`, `$(basename "$(readlink "${luksdev}")`, `$(<"${max_sectors_zdev}")`, `$(cat "${loop_pid_filename}" 2>/dev/null)` writes diagnostic command output to the blktests `$FULL` log.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/null_blk`; requirement gates include `_have_driver dm-crypt`, `_have_driver null_blk`, `_have_fio`, `_have_program cryptsetup`; runtime command surface includes `echo`, `sleep`, `cat`.

Risks and test signals: marked `TIMED=1`, so runtime and timing jitter are expected test concerns contains loops or background/concurrent work, making cleanup and race timing important.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/013 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/014 -->
# sources/test-tools/blktests/tests/zbd/014

Purpose: zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. This specific test is declared as: "test inline encryption and bio splitting".

Important APIs/types/functions: sourced libraries `tests/zbd/rc`, `common/null_blk`; top-level variables `DESCRIPTION=test inline encryption and bio splitting`; functions `requires()` lines 22-35, `trace_block_io()` lines 38-65, `wait_until_tracing_started()` lines 68-74, `stop_tracing()` lines 77-87, `report_stats()` lines 91-100, `devno()` lines 103-107, `run_test()` lines 109-197, `test()` lines 199-225; external commands `mkfs.f2fs`, `echo`, `grep`, `cat`, `sleep`, `umount`, `mount`, `dd`.

Control flow: `requires()` uses commands `mkfs.f2fs`; gates `_have_driver f2fs`, `_have_driver null_blk`, `_have_program fscrypt`, `_have_program mkfs.f2fs`. `test()` uses local helpers `run_test`, `stop_tracing`; commands `echo`, `umount`, `cat`.

State and persistence behavior: touches state paths such as `/sys/kernel/tracing/tracing_on`, `/sys/kernel/tracing`, `/sys/class/block/.../stat.`, `/sys/class/block/$`, `/sys/class/block/$zdev_basename/queue`, `/sys/class/block/${zdev_basename}/stat`, `/dev/nullb1`, `/dev/${zdev_basename}`, `/dev/null`, `/dev/zero`, `/etc/fscrypt.conf`, `$TMPDIR/keyfile` creates filesystems or mountpoints and must unwind them during cleanup writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `tests/zbd/rc`, `common/null_blk`; requirement gates include `_have_driver f2fs`, `_have_driver null_blk`, `_have_program fscrypt`, `_have_program mkfs.f2fs`; runtime command surface includes `mkfs.f2fs`, `echo`, `grep`, `cat`, `sleep`, `umount`, `mount`, `dd`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/014 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/rc -->
# sources/test-tools/blktests/tests/zbd/rc

Purpose: shared `tests/zbd/rc` support for zoned block device coverage using blkzone, null_blk, dm, filesystems, reset/report/ioctl/sysfs, zone mapping, queue freezing, cache races, and inline encryption. It defines 15 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/null_blk`, `common/dm`; functions `group_requires()` lines 15-19, `group_device_requires()` lines 21-26, `_fallback_null_blk_zoned()` lines 28-34, `_get_sysfs_variable()` lines 80-101, `_put_sysfs_variable()` lines 103-105, `_get_blkzone_report()` lines 109-188, `_put_blkzone_report()` lines 190-199, `_reset_zones()` lines 203-213, `_find_first_sequential_zone()` lines 215-226, `_find_last_sequential_zone()` lines 228-238, `_find_sequential_zone_in_middle()` lines 241-269, `_find_two_contiguous_seq_zones()` lines 277-294, `_require_test_dev_is_logical()` lines 296-302, `_test_dev_has_dm_map()` lines 304-316, `_get_dev_container_and_sector()` lines 320-375; external commands `blkzone`, `dd`, `echo`, `grep`, `dmsetup`.

Control flow: `group_requires()` uses commands `blkzone`, `dd`; gates `_have_root`, `_have_program blkzone`, `_have_program dd`, `_have_kernel_option BLK_DEV_ZONED`, `_have_null_blk`, `_have_module_param null_blk zoned`. `group_device_requires()` is present and carries the file-specific action body.

State and persistence behavior: touches state paths such as `/dev/nullb1`, `$FULL`, `$(<"${TEST_DEV_PART_SYSFS}"/size)`, `$(<"${_dir}"/size)`, `$(<"${_dir}"/queue/chunk_sectors)`, `$(<"${_dir}"/queue/physical_block_size)`, `$((SYSFS_VARS[SV_PHYS_BLK_SIZE] / 512)`, `$(<"${_dir}"/queue/nr_zones)`, `$(( (SYSFS_VARS[SV_CAPACITY] - 1)`, `$((_tokens[1])`, `$((_tokens[3])`, `$((_tokens[cap_idx])` writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `zbd` suite and the shared harness; through `common/rc`, `common/null_blk`, `common/dm`; requirement gates include `_have_root`, `_have_program blkzone`, `_have_program dd`, `_have_kernel_option BLK_DEV_ZONED`, `_have_null_blk`, `_have_module_param null_blk zoned`, `_require_test_dev_is_logical`; runtime command surface includes `blkzone`, `dd`, `echo`, `grep`, `dmsetup`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/zbd/rc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/Makefile -->
# sources/test-tools/crashmonkey/Makefile

Purpose: builds CrashMonkey from local C++ sources, selecting compiler/linker flags, object layout, and clean targets for the crash-consistency test tool.

Important APIs/types/functions: make variables `CODEDIR=code`, `SUBDIRS=$(CODEDIR)`, `SUBDIRS_CLEAN=$(addsuffix .clean, $(SUBDIRS))`, `BUILD_DIR=build`; targets `.PHONY`, `all`, `tests`, `seq1`, `gentests`, `permuters`, `clean`; command surface `make`, `rm` through recipes.

Control flow: The default target compiles CrashMonkey C++ objects and links the final binary; `clean` removes generated objects and executables. Build behavior is driven by make dependencies rather than a shell test entry point.

State and persistence behavior: touches state paths such as `$(CODEDIR)`, `$(addsuffix .clean, $(SUBDIRS)`, `$(SUBDIRS)`, `$(SUBDIRS_CLEAN)`, `$(MAKE)`, `$(subst .clean, , $@)`.

Dependencies and integration points: integrates with the blktests `crashmonkey` suite and the shared harness.

Risks and test signals: primary risk is build or harness drift; signal is make/shell exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/Makefile -->
