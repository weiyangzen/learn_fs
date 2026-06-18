# Research: subset-b-009557

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/801 -->
# sources/test-tools/xfstests/tests/xfs/801

Purpose: stress XFS online repair while tmpfs transparent huge pages and large folios are forced on, validating that the xfile staging code handles folio-sized page cache entries.

Important APIs, types, and functions: uses `_require_xfs_stress_online_repair`, `_scratch_xfs_stress_online_repair -S '-k'`, `sysfs-dump`, and sysfs THP knobs under `/sys/kernel/mm/transparent_hugepage`. The associative array `oldvalues` records original knob values.

Control flow: the test snapshots THP settings, enables every supported `hugepages-*kB/enabled` knob to inherit, forces `shmem_enabled`, formats and mounts scratch XFS, then runs fsstress plus online repair.

State and persistence behavior: persistent system state is limited to THP sysfs knobs, restored by `_cleanup`. Filesystem state is temporary scratch data and xfile repair staging.

Dependencies and integration points: depends on writable THP sysfs controls, xfstests fuzzy/inject/xfs helpers, scratch XFS, and kernel behavior fixed by commit `099d90642a711`.

Risks and test signals: failure risks include unavailable THP controls, global THP setting side effects, online repair crashes, livelocks, or corruption. The expected output is `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/801 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/802 -->
# sources/test-tools/xfstests/tests/xfs/802

Purpose: end-to-end systemd service coverage for XFS online fsck background scans. It checks per-filesystem `xfs_scrub@` and global `xfs_scrub_all` services and verifies post-scan health reporting.

Important APIs, types, and functions: uses `_require_systemd_is_running`, `_systemd_unit_path`, `_systemd_runtime_dir`, `_xfs_scrub_svcname`, `_scratch_populate_cached`, `xfs_spaceman health`, `attr -R -s xfs:autofsck`, and a local `run_scrub_service` wait loop.

Control flow: the script populates scratch, marks the mount for autofsck, starts the specific scrub service, clones and edits the runtime `xfs_scrub_all.service` to avoid the host media-scan stamp, cycles the mount, and starts the modified global service.

State and persistence behavior: it creates a temporary runtime systemd unit and temporary stamp directory, both cleaned up. Scratch health state and xattrs are changed only for the test filesystem.

Dependencies and integration points: integrates with systemd, python3-dbus for `xfs_scrub_all`, xfs_scrub, xfs_spaceman health, populate helpers, and attr support.

Risks and test signals: marked unreliable in parallel because global scrub scans mounted filesystems. Test signals are successful service completion and `health` output ending in `ok` for scratch.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/802 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/803 -->
# sources/test-tools/xfstests/tests/xfs/803

Purpose: functional coverage for low-level XFS filesystem property manipulation through `xfs_io` online commands and `xfs_db` offline attribute commands.

Important APIs, types, and functions: exercises `getfsprops`, `setfsprops`, `removefsprops`, `listfsprops`, `attr_get -Z`, `attr_set -Z`, `attr_remove -Z`, and `attr_list -Z`. It uses `filter_inum` to hide variable inode numbers.

Control flow: the online phase performs empty get/remove/list, set/list/get, child file and directory rejection, removal, long-name/value failures, and permission checks as `fsgqa`. The offline phase unmounts and repeats comparable xfs_db operations on root.

State and persistence behavior: the test writes and removes the fake root filesystem property `fakeproperty`, creates temporary child entries, and cleans the property with `attr -R -r`.

Dependencies and integration points: depends on test filesystem, xattrs, `xfs_io` fsprops support, `xfs_db attr_list`, and the xfstests attr helper.

Risks and test signals: coverage is sensitive to root-only semantics and maximum name/value sizes. Output verifies correct rejection, visibility through xattrs, and no leftover property state.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/803 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/804 -->
# sources/test-tools/xfstests/tests/xfs/804

Purpose: functional testing for the `xfs_property` wrapper across offline device mode and online mounted-directory mode.

Important APIs, types, and functions: uses `$XFS_PROPERTY_PROG` subcommands `get`, `set`, `list`, and `remove`, plus `attr -R -l` to observe backing filesystem property xattrs. Long property names and values are generated with perl.

Control flow: the script unmounts the test filesystem for offline device tests, then mounts it and repeats the same operation sequence online against `$TEST_DIR`.

State and persistence behavior: it creates and removes `fakeproperty`, temporary child paths, and no durable data beyond the filesystem property under test. Cleanup removes the property from `$TEST_DEV`.

Dependencies and integration points: depends on `xfs_property`, xattrs, test XFS, and `xfs_io listfsprops` as a feature probe.

Risks and test signals: risks include wrapper/device path divergence and incomplete cleanup. Signals are correct empty get/remove behavior, set/list/get visibility, and expected long input failures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/804 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/805 -->
# sources/test-tools/xfstests/tests/xfs/805

Purpose: verifies that `mkfs.xfs -m autofsck` encodes the requested automatic fsck directive as a filesystem property.

Important APIs, types, and functions: `testme` builds `mkfs.xfs -f -m autofsck[=value]` arguments for empty, named, and numeric values, then inspects root metadata with `xfs_db -x -c 'path /' -c 'attr_get -Z autofsck'`.

Control flow: the test creates a 10 GiB sparse image in `$TEST_DIR`, formats it repeatedly with different autofsck values, and prints the stored root property through xfs_db.

State and persistence behavior: all state is in the temporary sparse file and mount directory, removed during cleanup. No mounted filesystem is required for the assertions.

Dependencies and integration points: depends on `mkfs.xfs`, xfs_db attr_get support, and `xfs_io listfsprops` as the fs property feature probe.

Risks and test signals: unsupported mkfs options cause `_notrun`. The test signal is the exact property value stored by mkfs for each accepted spelling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/805 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/806 -->
# sources/test-tools/xfstests/tests/xfs/806

Purpose: checks that `mkfs.xfs` autofsck filesystem properties are visible to `xfs_scrub -o autofsck` and influence the scrub tool's reported directive.

Important APIs, types, and functions: uses `testme`, `mkfs.xfs -m <autofsck option>`, loop mounting, `XFS_SCRUB_PHASE=7`, and `$XFS_SCRUB_PROG -d -o autofsck`.

Control flow: a temporary 10 GiB image is reformatted for each autofsck value, mounted via loop, queried with xfs_scrub, filtered to directive output, and unmounted.

State and persistence behavior: state is confined to the sparse image and temporary mount directory. Each iteration rewrites the filesystem image.

Dependencies and integration points: depends on xfs_scrub, xfs_db attr_get support, loop mounts, fs property support, and xfstests fuzzy filtering.

Risks and test signals: absence of an autofsck directive is not tested because defaults vary with mkfs features. The signal is scrub reporting the expected directive text without path noise.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/806 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/807 -->
# sources/test-tools/xfstests/tests/xfs/807

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory root inode at `path -m /`. It populates a scratch filesystem, corrupts every selected field, and uses online repair through xfs_scrub/ioctl paths.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `online`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/807 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/808 -->
# sources/test-tools/xfstests/tests/xfs/808

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory root inode at `path -m /`. It populates a scratch filesystem, corrupts every selected field, and uses offline repair through xfs_repair.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `offline`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/808 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/809 -->
# sources/test-tools/xfstests/tests/xfs/809

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory root inode at `path -m /`. It populates a scratch filesystem, corrupts every selected field, and uses no repair, leaving verifier behavior as the signal.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `none`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/809 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/810 -->
# sources/test-tools/xfstests/tests/xfs/810

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory root inode at `path -m /`. It populates a scratch filesystem, corrupts every selected field, and uses online repair followed by offline repair if needed.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `both`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/810 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/811 -->
# sources/test-tools/xfstests/tests/xfs/811

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory `/rtgroups` subdirectory inode. It populates a scratch filesystem, corrupts every selected field, and uses online repair through xfs_scrub/ioctl paths.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `online`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/811 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/812 -->
# sources/test-tools/xfstests/tests/xfs/812

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory `/rtgroups` subdirectory inode. It populates a scratch filesystem, corrupts every selected field, and uses offline repair through xfs_repair.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `offline`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/812 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/813 -->
# sources/test-tools/xfstests/tests/xfs/813

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory `/rtgroups` subdirectory inode. It populates a scratch filesystem, corrupts every selected field, and uses no repair, leaving verifier behavior as the signal.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `none`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/813 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/814 -->
# sources/test-tools/xfstests/tests/xfs/814

Purpose: dangerous XFS metadata fuzzer coverage for the metadata-directory `/rtgroups` subdirectory inode. It populates a scratch filesystem, corrupts every selected field, and uses online repair followed by offline repair if needed.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `all fields` and the repair mode argument is `both`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_xfs_scratch_metadir and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/814 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/815 -->
# sources/test-tools/xfstests/tests/xfs/815

Purpose: races fsstress against metadata-directory path scrub operations to catch crashes, livelocks, or metapath lookup corruption under load.

Important APIs, types, and functions: probes `xfs_io -x -c 'scrub metapath ...'` through `try_verb`, discovers supported verbs (`quotadir`, quota roots, `rtdir`, `rtbitmap`, `rtsummary`, `rtrmapbt`, `rtrefcbt`), and runs `_scratch_xfs_stress_scrub`.

Control flow: after mkfs and mount, the script sources mkfs geometry from filtered output, builds a list of supported metapath scrub commands including realtime group numbers, and feeds them to the stress scrub helper.

State and persistence behavior: scratch filesystem contents mutate under fsstress. The discovered verb list is logged to `$seqres.full`; cleanup stops the stress scrub worker.

Dependencies and integration points: depends on xfs_io metapath scrub support, scratch XFS, realtime-group geometry when available, and xfstests inject/fuzzy/xfs helpers.

Risks and test signals: skips if no metapath verbs are accepted. Success is a quiet stress run ending in `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/815 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/816 -->
# sources/test-tools/xfstests/tests/xfs/816

Purpose: races fsstress against online metapath repair operations to validate metadata-directory path repair under concurrent filesystem activity.

Important APIs, types, and functions: probes `xfs_io -x -c 'repair metapath ...'`, filters benign `did not need repair` output, builds repair commands for quota, realtime directory, and realtime group metadata paths, then calls `_scratch_xfs_stress_online_repair`.

Control flow: the script formats and mounts scratch, discovers all supported repair metapath verbs, logs the verb list, converts each into a `repair metapath` stress command, and runs the online repair stress harness.

State and persistence behavior: state is transient scratch filesystem activity and repair attempts. Cleanup stops stress scrub/repair background jobs.

Dependencies and integration points: depends on online repair support, xfs_io metapath commands, realtime group count from mkfs output, and xfstests stress helpers.

Risks and test signals: no discovered verbs causes `_notrun`. Signals are no crash, no livelock, and quiet completion with `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/816 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/817 -->
# sources/test-tools/xfstests/tests/xfs/817

Purpose: functional test for repairing missing or corrupt XFS metadata-directory paths, especially `/rtgroups/0.rmap`, using raw online repair ioctls, `xfs_scrub`, and `xfs_repair`.

Important APIs, types, and functions: `prepare_fs` formats scratch, requires rmapbt/realtime/metadir/parent, records inode/generation pairs, and corrupts a parent pointer with xfs_db. `simple_online_repair` sequences directory, parent, metapath, and nlinks scrub/repair commands.

Control flow: the test runs three parts: direct xfs_io scrub/repair commands, full xfs_scrub, and offline xfs_repair. Each part prepares a fresh corrupted filesystem and validates with `_check_scratch_fs`.

State and persistence behavior: intentionally corrupts metadata parent pointers and directory links in the scratch filesystem, then verifies repair restoration before unmount.

Dependencies and integration points: depends on xfs_db link/unlink support, online repair, parent pointers, metadir, realtime, rmapbt, and scrub/repair tools.

Risks and test signals: destroying metadir paths can prevent mounts, so the online sequence is carefully ordered. Success is all three repair paths returning a consistent filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/817 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/818 -->
# sources/test-tools/xfstests/tests/xfs/818

Purpose: validates that `xfs_protofile` can describe a populated XFS tree, that mkfs can recreate it with `-p`, and that file metadata and content match.

Important APIs, types, and functions: defines `make_md5`, `cmp_md5`, `make_stat`, and `cmp_stat`; uses `_scratch_populate_cached`, `_run_fsstress`, `$XFS_PROTOFILE_PROG`, `_try_mkfs_dev -p`, and standard `find`, `stat`, `md5sum`, and `diff`.

Control flow: populate scratch, add fsstress-created files, record stats and hashes, generate a protofile, create a same-sized image, format it from the protofile, mount it, and compare stat and md5 data.

State and persistence behavior: creates a temporary image, protofile, and mount directory under `$TEST_DIR/$seq`; cleanup unmounts and removes them.

Dependencies and integration points: depends on xfs_protofile, mkfs protofile population, scrub/populate commands, and non-realtime compatibility.

Risks and test signals: known `_notrun` cases include too many xattr names, insufficient space from lost reflink sharing, and unsupported realtime files. Signals are clean stat diff and md5 verification.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/818 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/819 -->
# sources/test-tools/xfstests/tests/xfs/819

Purpose: mkfs protofile regression test for creating filesystems with xattrs, special files, symlinks, setuid/setgid modes, and large file content.

Important APIs, types, and functions: constructs a protofile manually, writes source files with `xfs_io` and `devzero`, sets root/security/user/big xattrs with `attr`, formats with `_scratch_mkfs_xfs -p`, and validates using `lstat64`, `diff`, and attr listing.

Control flow: the test builds source files and a protofile tree, then `_verify_fs 2` unmounts, formats, checks, mounts, confirms xattr support, lists and filters metadata, compares file and symlink content, lists xattrs, and unmounts.

State and persistence behavior: temporary protofile and source files live under `$tmp` and `$TEST_DIR`; scratch filesystem is rebuilt from the protofile.

Dependencies and integration points: depends on attr tooling, mkfs protofile support, xfs scratch, lstat64/devzero helper programs, and no `rtinherit` mkfs option.

Risks and test signals: skips when protofile xattrs are unsupported. Signals are matching file tree metadata, valid bigfile content, and preserved xattrs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/819 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/820 -->
# sources/test-tools/xfstests/tests/xfs/820

Purpose: tests persistent quota accounting and enforcement flags when XFS metadata directories are enabled.

Important APIs, types, and functions: uses `_require_xfs_scratch_metadir`, `_require_xfs_quota`, `qerase_mkfs_options`, `confirm`, `_qmount_option`, `xfs_quota state -ugp`, `_scratch_xfs_repair`, and shutdown recovery helpers.

Control flow: the script removes quota mkfs options from the environment, formats with different persistent quota flag combinations, mounts with and without quota options, checks state, runs repair, tests odd option combinations, and validates recovery after forced shutdown and quotaoff.

State and persistence behavior: quota flag state is persisted in metadir-backed quota metadata across repair, shutdown recovery, and remounts.

Dependencies and integration points: depends on mkfs support for `uquota`, xfs_quota, metadata directories, scratch mount option manipulation, and filesystem checking.

Risks and test signals: mount options can mask persistent settings, so the helper blanks them deliberately. Signals are stable filtered quota state and clean scratch checks after recovery.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/820 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/821 -->
# sources/test-tools/xfstests/tests/xfs/821

Purpose: functional testing for realtime quota accounting and enforcement, including ownership transfers, hard limits, soft-limit timers, warnings, and bmbt block quota interactions.

Important APIs, types, and functions: uses `_scratch_supports_rtquota`, `_xfs_force_bdev realtime`, `report_rtusage`, xfs_quota `limit`, `timer`, `quota -u -r`, `xfs_io pwrite`, `_su` as the qa user, and `punch-alternating`.

Control flow: after mounting with user quota, it records realtime geometry, writes realtime extents as root and numeric users, changes ownership to move usage, tests hard and soft realtime block enforcement, extends grace periods, and checks bmbt quota during extent map punching.

State and persistence behavior: creates realtime files and quota records on scratch. Quota usage and timers persist until scratch cleanup.

Dependencies and integration points: depends on realtime support, user quota, qa user, punch-alternating helper, and xfs_quota realtime reporting.

Risks and test signals: delayed allocation affects when enforcement begins, so writes are synced. Signals are filtered quota reports, expected EDQUOT behavior, and final quota/bmap details.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/821 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/822 -->
# sources/test-tools/xfstests/tests/xfs/822

Purpose: races fsstress against realtime reverse-map btree scrub to detect crashes, livelocks, or rtrmapbt scrub races.

Important APIs, types, and functions: uses `_require_realtime`, `_require_xfs_stress_scrub`, `_require_xfs_has_feature realtime/rmapbt`, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_scrub -s 'scrub rtrmapbt %rgno%'`.

Control flow: format scratch, mount, require realtime and rmapbt, force new files to realtime storage, and run scrub stress for each realtime group placeholder.

State and persistence behavior: scratch contents are mutated under fsstress while rtrmapbt scrub reads metadata.

Dependencies and integration points: integrates with realtime XFS geometry, xfs_io scrub command templates, and xfstests stress cleanup.

Risks and test signals: skips without realtime/rmapbt. Success is no kernel crash, no livelock, and `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/822 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/823 -->
# sources/test-tools/xfstests/tests/xfs/823

Purpose: races fsstress against realtime bitmap online repair and covers command syntax differences across rtgroups and older scrub implementations.

Important APIs, types, and functions: uses `_scratch_xfs_stress_online_repair`, `_xfs_has_feature rtgroups`, `xfs_io -c 'help scrub'`, and repair templates `repair rtbitmap %rgno%`, `repair rtbitmap 0`, or `repair rtbitmap`.

Control flow: format/mount scratch, require realtime, force realtime allocation, choose the appropriate repair command form, then run online repair stress.

State and persistence behavior: scratch realtime bitmap state changes under fsstress and online repair. Cleanup stops background work.

Dependencies and integration points: depends on realtime XFS, online repair, xfs_io scrub help output, and xfstests xfs/inject/fuzzy helpers.

Risks and test signals: version-dependent command syntax is a key risk. Success is quiet stress completion without crash or livelock.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/823 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/824 -->
# sources/test-tools/xfstests/tests/xfs/824

Purpose: races fsstress against online repair of realtime reverse-map btrees.

Important APIs, types, and functions: uses `_require_realtime`, `_require_xfs_stress_online_repair`, realtime/rmapbt feature probes, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_online_repair -s 'repair rtrmapbt %rgno%'`.

Control flow: the script formats and mounts scratch, verifies realtime and rmapbt support, forces realtime allocation, and launches the online repair stress command template.

State and persistence behavior: all mutations occur in the scratch realtime volume and repair metadata state, removed by test cleanup.

Dependencies and integration points: integrates with xfs_io online repair command templates and the fsstress_online_repair harness.

Risks and test signals: skips without realtime/rmapbt or online repair support. Signals are no crash, no livelock, and `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/824 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/825 -->
# sources/test-tools/xfstests/tests/xfs/825

Purpose: dangerous XFS metadata fuzzer coverage for realtime reverse-map btree record fields. It populates a scratch filesystem, corrupts every selected field, and uses online repair followed by offline repair if needed.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `record fields below a two-level rtrmapbt` and the repair mode argument is `both`. It narrows record fuzzing with `addr u${inode_ver}.rtrmapbt.ptrs[1]`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_xfs_scratch_rmapbt, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/825 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/826 -->
# sources/test-tools/xfstests/tests/xfs/826

Purpose: dangerous XFS metadata fuzzer coverage for realtime reverse-map btree key/pointer fields. It populates a scratch filesystem, corrupts every selected field, and uses offline repair through xfs_repair.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `(rtrmapbt)` and the repair mode argument is `offline`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_xfs_scratch_rmapbt, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.

Note: the header and test groups describe the usual both-repair pattern, but the actual `_scratch_xfs_fuzz_metadata` mode is `offline`, so xfs_repair is the repair signal for this file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/826 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/827 -->
# sources/test-tools/xfstests/tests/xfs/827

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree record fields. It populates a scratch filesystem, corrupts every selected field, and uses online repair through xfs_scrub/ioctl paths.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `record fields below a two-level rtrefcountbt` and the repair mode argument is `online`. It narrows record fuzzing with `addr u${inode_ver}.rtrefcbt.ptrs[1]`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/827 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/828 -->
# sources/test-tools/xfstests/tests/xfs/828

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree record fields. It populates a scratch filesystem, corrupts every selected field, and uses offline repair through xfs_repair.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `record fields below a two-level rtrefcountbt` and the repair mode argument is `offline`. It narrows record fuzzing with `addr u${inode_ver}.rtrefcbt.ptrs[1]`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/828 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/829 -->
# sources/test-tools/xfstests/tests/xfs/829

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree record fields. It populates a scratch filesystem, corrupts every selected field, and uses no repair, leaving verifier behavior as the signal.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `record fields below a two-level rtrefcountbt` and the repair mode argument is `none`. It narrows record fuzzing with `addr u${inode_ver}.rtrefcbt.ptrs[1]`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/829 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/830 -->
# sources/test-tools/xfstests/tests/xfs/830

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree record fields. It populates a scratch filesystem, corrupts every selected field, and uses online repair followed by offline repair if needed.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `record fields below a two-level rtrefcountbt` and the repair mode argument is `both`. It narrows record fuzzing with `addr u${inode_ver}.rtrefcbt.ptrs[1]`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/830 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/831 -->
# sources/test-tools/xfstests/tests/xfs/831

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree key/pointer fields. It populates a scratch filesystem, corrupts every selected field, and uses online repair through xfs_scrub/ioctl paths.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `(rtrefcbt)` and the repair mode argument is `online`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/831 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/832 -->
# sources/test-tools/xfstests/tests/xfs/832

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree key/pointer fields. It populates a scratch filesystem, corrupts every selected field, and uses offline repair through xfs_repair.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `(rtrefcbt)` and the repair mode argument is `offline`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/832 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/833 -->
# sources/test-tools/xfstests/tests/xfs/833

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree key/pointer fields. It populates a scratch filesystem, corrupts every selected field, and uses no repair, leaving verifier behavior as the signal.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `(rtrefcbt)` and the repair mode argument is `none`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/833 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/834 -->
# sources/test-tools/xfstests/tests/xfs/834

Purpose: dangerous XFS metadata fuzzer coverage for realtime refcount btree key/pointer fields. It populates a scratch filesystem, corrupts every selected field, and uses online repair followed by offline repair if needed.

Important APIs, types, and functions: this shell test uses `_begin_fstest`, `_scratch_populate_cached`, `_scratch_xfs_get_metadata_field`, and `_scratch_xfs_fuzz_metadata`. The fuzz selector is `(rtrefcbt)` and the repair mode argument is `both`.

Control flow: the script imports the common xfstests preamble, filter, populate, and fuzzy helpers, registers `_cleanup`, requires `_require_realtime, _require_scratch_reflink, and _require_scratch_xfs_fuzz_fields`, disables dmesg checking for intentional corruption, populates the scratch filesystem, finds the target metadata path, then invokes `_scratch_xfs_fuzz_metadata` and records detail in `$seqres.full`.

State and persistence behavior: all state lives in the scratch XFS image and temporary xfstests files. The test intentionally persists corrupted metadata long enough for scrub, repair, or verifiers to inspect it, then relies on framework cleanup.

Dependencies and integration points: integrates with xfs_db metadata addressing, xfs_scrub/xfs_repair repair modes, realtime or reflink feature gates where required, and the xfstests dangerous fuzzer groups.

Risks and test signals: the test is destructive by design and skips without the required feature set or fuzz-field support. Success is a completed fuzz run without crashes, livelocks, unexpected repair failure, or verifier misses.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/834 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/835 -->
# sources/test-tools/xfstests/tests/xfs/835

Purpose: stress-tests scrub of realtime reference count btrees while fsstress mutates a realtime reflink filesystem.

Important APIs, types, and functions: requires realtime, scratch, `_require_xfs_stress_scrub`, realtime and reflink feature probes, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_scrub -s 'scrub rtrefcountbt %rgno%'`.

Control flow: mkfs, mount, verify realtime and reflink, force realtime allocation, then run scrub stress against the realtime refcount btree per realtime group.

State and persistence behavior: scratch realtime refcount metadata changes under fsstress and scrub observation.

Dependencies and integration points: depends on realtime reflink XFS and the scrub stress harness.

Risks and test signals: intended to catch crashes and livelocks. Success emits `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/835 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/836 -->
# sources/test-tools/xfstests/tests/xfs/836

Purpose: stress-tests online repair of realtime reference count btrees while fsstress mutates a realtime reflink filesystem.

Important APIs, types, and functions: requires realtime, scratch, `_require_xfs_stress_online_repair`, realtime and reflink feature probes, `_xfs_force_bdev realtime`, and `_scratch_xfs_stress_online_repair -s 'repair rtrefcountbt %rgno%'`.

Control flow: the test formats and mounts scratch, verifies realtime and reflink features, forces realtime allocation, and runs the online repair stress template.

State and persistence behavior: state is transient scratch filesystem metadata plus online repair activity, with cleanup stopping stress workers.

Dependencies and integration points: integrates with realtime refcountbt online repair and xfstests fsstress_online_repair.

Risks and test signals: target failures are kernel crashes, repair races, and livelocks. Expected output is `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/836 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/837 -->
# sources/test-tools/xfstests/tests/xfs/837

Purpose: verifies mount, remount, write rejection, and unmount behavior when an external XFS realtime device is marked read-only.

Important APIs, types, and functions: uses `blockdev --setro/--setrw`, `_scratch_mkfs '-d rtinherit'`, `_try_scratch_mount`, `_scratch_remount rw`, `_scratch_unmount`, and filtering helpers for read-only mount messages.

Control flow: require realtime and external local scratch rtdev, register cleanup to restore read-write, format with rtinherit, select an output variant for old quota behavior, mark the rt device read-only, try mounting, attempt a direct write, try remounting rw, and unmount.

State and persistence behavior: changes the block device readonly flag and restores it in cleanup. Scratch filesystem data is temporary.

Dependencies and integration points: depends on external `$SCRATCH_RTDEV`, blockdev, XFS realtime support, and kernel behavior fixed by commit `bfecc4091e07`.

Risks and test signals: quota mount options on non-metadir filesystems can cause expected EPERM, captured via `837.cfg`. Signals are filtered mount/write/remount outcomes and final `*** done`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/837 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/837.cfg -->
# sources/test-tools/xfstests/tests/xfs/837.cfg

Purpose: xfstests output configuration for test `xfs/837`.

Important APIs, types, and functions: defines one output variant mapping, `oldquota: oldquota`, for `_link_out_file` selection in the test script.

Control flow: the harness uses this cfg file when `xfs/837` detects old quota behavior on a non-metadir filesystem with quota mount options.

State and persistence behavior: no runtime state; it is static metadata for expected output selection.

Dependencies and integration points: integrated by the xfstests group/output comparison machinery and the `xfs/837` script.

Risks and test signals: an incorrect variant name would make otherwise valid oldquota output compare against the wrong golden file.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/837.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/838 -->
# sources/test-tools/xfstests/tests/xfs/838

Purpose: validates multi-fsblock realtime atomic write support, including advertised size bounds, direct I/O requirements, and unaligned direct I/O rejection.

Important APIs, types, and functions: uses `statx -r -m $STATX_WRITE_ATOMIC`, `_get_atomic_write_unit_min/max`, `_simple_atomic_write`, `_test_atomic_file_writes`, realtime forcing, and xfs_io fallocate/fsync.

Control flow: query rt device atomic properties, mkfs/mount scratch, force realtime allocation, query file atomic properties, preallocate space, test sizes below and above advertised bounds, test every supported power-of-two size, then check buffered and unaligned direct I/O failures.

State and persistence behavior: writes to one scratch realtime file and logs statx data to `$seqres.full`.

Dependencies and integration points: depends on realtime, scratch atomic multi-fsblock support, atomicwrites common helpers, and xfs_io statx.

Risks and test signals: device capability discovery controls skips. Signals are expected EINVAL/EOPNOTSUPP lines and silent success for supported sizes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/838 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/839 -->
# sources/test-tools/xfstests/tests/xfs/839

Purpose: checks that software atomic-write recovery completes correctly after an injected crash during a fragmented-file atomic write.

Important APIs, types, and functions: uses `punch-alternating`, `_scratch_inject_error free_extent`, `_simple_atomic_write`, `statx` atomic write queries, `cmp`, `md5sum`, and cycle mount recovery.

Control flow: create fragmented data and a check file, write expected post-atomic content to the check file, sync, inject `free_extent`, perform a direct atomic write that shuts down the filesystem, verify a later touch fails, remount for recovery, and compare final contents.

State and persistence behavior: scratch journal/recovery state is intentionally exercised across shutdown and remount.

Dependencies and integration points: depends on atomicwrites helpers, xfs_io error injection, punch-alternating helper, and multi-fsblock atomic write support.

Risks and test signals: skips if maximum atomic unit is too small. Failure signals include stray post-shutdown file creation or content mismatch after recovery.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/839 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/840 -->
# sources/test-tools/xfstests/tests/xfs/840

Purpose: hardware large atomic write error-injection test for reflinked files, validating shutdown and log replay behavior.

Important APIs, types, and functions: uses `_scratch_inject_error bmap_finish_one`, `_require_scratch_write_atomic`, xfs_io `pwrite -A -D -V1`, reflink copy, `_scratch_remount_dump_log`, and md5sum comparisons.

Control flow: mkfs/mount scratch, create two reflinked files, record checksums, inject bmap finishing error, attempt a 4 KiB atomic direct write to one file, confirm the filesystem shuts down, remount to replay the log, recheck checksums, and confirm the filesystem is usable.

State and persistence behavior: writes reflinked scratch data and exercises journal recovery across a forced shutdown.

Dependencies and integration points: depends on reflink, hardware atomic write support, xfs_io atomic pwrite, and inject helpers.

Risks and test signals: skips if 4 KiB atomic writes are unavailable. Signals are expected shutdown, stable checksums, and successful post-replay touch.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/840 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/841 -->
# sources/test-tools/xfstests/tests/xfs/841

Purpose: verifies bit-for-bit reproducible XFS image creation when `mkfs.xfs` is supplied fixed reproducibility inputs.

Important APIs, types, and functions: checks `-m uuid=`, `-p` population, `SOURCE_DATE_EPOCH`, and `DETERMINISTIC_SEED`; creates a proto directory with fsstress plus fifo, socket, block, and character device entries; hashes images with sha256sum.

Control flow: build a prototype tree, create three fresh 512 MiB images with fixed UUID and epoch, mount each image to compare the tree, collect hashes, and require all hashes to match.

State and persistence behavior: temporary prototype, mount directory, and image file live under `$TEST_DIR` and are removed by cleanup.

Dependencies and integration points: depends on mkfs reproducibility support, fsstress, af_unix helper, mount/unmount helpers, and root privileges for special device nodes when available.

Risks and test signals: special files may be skipped if creation fails, but reproducibility still depends on deterministic metadata. The main signal is `All filesystem images are identical.`
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/841 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/Makefile -->
# sources/test-tools/xfstests/tests/xfs/Makefile

Purpose: build and install rules for the xfstests `xfs` test directory.

Important APIs, types, and functions: includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`, sets `XFS_DIR`, `TARGET_DIR`, and `DIRT = group.list`, and defines `install`.

Control flow: the default target builds generated dirt such as `group.list`. `install` creates the target xfs test directory and installs executable `$(TESTS)`, `group.list`, and output files with the expected modes.

State and persistence behavior: generated state is limited to `group.list`; installed files are copied into `$(PKG_LIB_DIR)/$(TESTS_DIR)/xfs`.

Dependencies and integration points: integrates with the top-level xfstests make infrastructure and packaging install paths.

Risks and test signals: incorrect modes would break test execution or output comparison. The empty `install-dev install-lib` targets intentionally do nothing.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/buffer.go -->
# sources/user-network-fs/bazil-fuse/buffer.go

Purpose: internal byte buffer builder for low-level FUSE protocol messages.

Important APIs, types, and functions: defines `type buffer []byte`, `(*buffer).alloc`, `(*buffer).reset`, and `newBuffer`. `alloc` returns an `unsafe.Pointer` to newly extended storage, and `newBuffer` reserves space for `outHeader`.

Control flow: callers create a buffer with header capacity, append fixed-size segments through `alloc`, and reuse it with `reset`.

State and persistence behavior: state is only in-memory byte slices. `reset` zeroes the entire capacity before shortening to avoid stale protocol data reuse.

Dependencies and integration points: depends on `unsafe` and the package's FUSE wire header definitions.

Risks and test signals: pointer safety depends on callers not retaining pointers across reallocations. Tests should cover message encoding sizes and reuse zeroing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz

Purpose: helper shell script for running go-fuzz against the `mountinfo` parser.

Important APIs, types, and functions: runs `go-fuzz-build` and then `go-fuzz -workdir=testdata/fuzz` via `go run github.com/dvyukov/go-fuzz/...`.

Control flow: `set -e` stops on build errors; successful build immediately execs the fuzzing loop.

State and persistence behavior: fuzz corpus, crashers, and generated artifacts live under `testdata/fuzz`.

Dependencies and integration points: depends on the go-fuzz tooling and the build-tagged `fuzz.go` entrypoint.

Risks and test signals: external tool availability and corpus quality drive coverage. Crashes become regression tests through the corpus files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz.go

Purpose: go-fuzz entrypoint for the Linux mountinfo parser.

Important APIs, types, and functions: under the `gofuzz` build tag, `Fuzz(data []byte) int` calls the package-private `parse` function and returns 1 for valid parsed lines and 0 for rejected inputs.

Control flow: fuzzing feeds arbitrary bytes directly to `parse`; parse errors are non-interesting, successful parses are kept as useful corpus inputs.

State and persistence behavior: no state beyond fuzzer-managed corpus data.

Dependencies and integration points: integrates with `go-fuzz-build` and the `mountinfo` package parser.

Risks and test signals: the useful signal is absence of panics on malformed mountinfo and growth of valid corpus entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo.go

Purpose: parser and streaming reader for Linux `/proc/self/mountinfo`, extracting the fields needed by `fuse-abort`.

Important APIs, types, and functions: exports `DefaultPath`, `Open`, `Reader`, `Reader.Next`, `Reader.Close`, and `Mount`. Internal `unescape` decodes backslash-prefixed octal sequences; `parse` extracts major, minor, mountpoint, and filesystem type.

Control flow: `Open` wraps an `os.File` in a scanner. `Next` scans one line, calls `parse`, returns `io.EOF` at end, and propagates parse errors. `parse` splits fields, validates major:minor, skips optional fields until `-`, and unescapes mountpoint/fstype.

State and persistence behavior: state is the open file and scanner cursor only.

Dependencies and integration points: used by `cmd/fuse-abort/main.go`; depends on Linux mountinfo format, `bufio.Scanner`, and octal escaping rules.

Risks and test signals: scanner token limits and strict space splitting can reject unusual lines. Tests and fuzzing cover real entries, escapes, and crashers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo_test.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo_test.go

Purpose: regression tests for the mountinfo reader/parser.

Important APIs, types, and functions: covers `Open`, `Reader.Next`, `Reader.Close`, EOF handling, escaped fields, and malformed fuzzer crashers.

Control flow: `TestOpenError` checks not-exist behavior. `TestReal` scans a corpus file until a known FUSE mount is found and verifies major/minor/fstype. `TestEscape` validates octal unescaping. `TestCrashers` iterates a crasher corpus and ignores parse errors as long as there is no panic.

State and persistence behavior: reads static corpus files only.

Dependencies and integration points: depends on `testdata/fuzz/corpus` and the public mountinfo API.

Risks and test signals: coverage is limited to corpus examples, but fuzz crashers guard parser robustness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/mountinfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/tools.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/tools.go

Purpose: records fuzzing tools as Go module tool dependencies without building them normally.

Important APIs, types, and functions: under the `tools` build tag, blank-imports `github.com/dvyukov/go-fuzz/go-fuzz` and `go-fuzz-build`.

Control flow: no runtime control flow; the file exists for dependency retention.

State and persistence behavior: no program state.

Dependencies and integration points: integrates with Go modules and the local `fuzz` script.

Risks and test signals: if tool module paths change, fuzz setup breaks; normal builds ignore this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/internal/mountinfo/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/main.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/main.go

Purpose: Linux command-line utility to forcibly abort and unmount hung FUSE mountpoints by writing to `/sys/fs/fuse/connections/<id>/abort`.

Important APIs, types, and functions: `findFUSEMounts`, `abort`, `pruneEmptyDir`, `run`, `usage`, and `main`. It uses `mountinfo.Open`, `fuse.Unmount`, `filepath.Abs`, and `syscall.Rmdir`.

Control flow: command-line parsing requires mountpoints and optional `-p`. `run` builds a mountpoint-to-connection map, processes arguments in order, validates each is a FUSE mount, writes `1` to sysfs abort, unmounts, and optionally prunes empty directories.

State and persistence behavior: modifies kernel FUSE connection state and mount state. Optional pruning removes only empty directories.

Dependencies and integration points: Linux-only build; depends on proc mountinfo, sysfs FUSE connection layout, and bazil fuse unmount logic.

Risks and test signals: races with unmount are treated as success for missing abort files. Risks include wrong mountpoint path resolution and privilege errors. Tests should mock mountinfo/sysfs or run in controlled namespaces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/debug.go -->
# sources/user-network-fs/bazil-fuse/debug.go

Purpose: package-level debug hook for FUSE protocol and server trace messages.

Important APIs, types, and functions: `stack` captures the current goroutine stack, `nop` discards messages, and exported variable `Debug func(msg interface{})` defaults to `nop`.

Control flow: other package code calls `fuse.Debug` with JSON-safe, human-readable values; callers may replace it before serving.

State and persistence behavior: global process state is the `Debug` function pointer; no persistent storage.

Dependencies and integration points: used by the FUSE connection and `fs.Server` debug plumbing; test utilities can redirect it to logs.

Risks and test signals: implementations must not retain `msg`. Racy global replacement can affect concurrent connections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_freebsd.go -->
# sources/user-network-fs/bazil-fuse/error_freebsd.go

Purpose: FreeBSD-specific mapping for the platform error meaning missing extended attribute.

Important APIs, types, and functions: defines `ENOATTR = Errno(syscall.ENOATTR)`, sets `errNoXattr`, and registers the errno name in `errnoNames`.

Control flow: package init installs the display name for `ErrNoXattr`.

State and persistence behavior: process-global errno name map is updated at init.

Dependencies and integration points: paired with `error_std.go` to expose platform-independent `ErrNoXattr`.

Risks and test signals: build tags select this on FreeBSD; tests should verify Getxattr missing-attribute responses use ENOATTR.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_linux.go -->
# sources/user-network-fs/bazil-fuse/error_linux.go

Purpose: Linux-specific mapping for the platform error meaning missing extended attribute.

Important APIs, types, and functions: defines `ENODATA = Errno(syscall.ENODATA)`, assigns `errNoXattr`, and registers `ENODATA` in `errnoNames`.

Control flow: init updates the errno display table.

State and persistence behavior: only process-global errno name state changes.

Dependencies and integration points: consumed by `error_std.go` and xattr request handlers.

Risks and test signals: Linux syscall behavior must use ENODATA for absent xattrs; tests should assert `fuse.ErrNoXattr` encodes that value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_std.go -->
# sources/user-network-fs/bazil-fuse/error_std.go

Purpose: common, platform-independent exported missing-xattr error.

Important APIs, types, and functions: exposes `const ErrNoXattr = errNoXattr` and compile-time interface assertions for `error`, `Errno`, and `ErrorNumber`.

Control flow: no runtime control flow; platform files provide `errNoXattr`.

State and persistence behavior: no mutable state.

Dependencies and integration points: used by filesystem implementations responding to Getxattr/Listxattr/Removexattr and backed by Linux or FreeBSD errno constants.

Risks and test signals: incorrect platform mapping causes wrong kernel errno for absent xattrs. Build matrix tests are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_std.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/clockfs/clockfs.go -->
# sources/user-network-fs/bazil-fuse/examples/clockfs/clockfs.go

Purpose: example FUSE filesystem exposing a `clock` file whose content changes every second and invalidates kernel cache data.

Important APIs, types, and functions: defines `FS`, `Dir`, and `File`; uses `fuse.Mount`, `fs.New`, `Server.InvalidateNodeData`, `atomic.Value`, `OpenKeepCache`, and `fuseutil.HandleRead`.

Control flow: `run` mounts, creates a server and persistent clock node, ticks once, starts an update goroutine, and serves. Directory lookup returns the clock file; file open allows read-only access and read returns current content.

State and persistence behavior: file content and update count are in memory only. Kernel cache state is invalidated on every tick.

Dependencies and integration points: demonstrates bazil/fuse fs interfaces, mount options, and notification APIs.

Risks and test signals: update goroutine never exits in the example. Cache invalidation may return `ErrNotCached`, which is ignored; visible signal is changing file content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/clockfs/clockfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/hellofs/hello.go -->
# sources/user-network-fs/bazil-fuse/examples/hellofs/hello.go

Purpose: minimal hello-world FUSE filesystem exposing a single read-only `hello` file.

Important APIs, types, and functions: implements `FS.Root`, `Dir.Attr`, `Dir.Lookup`, `Dir.ReadDirAll`, `File.Attr`, and `File.ReadAll`; uses `fuse.Mount` and `fs.Serve`.

Control flow: `main` parses one mountpoint, mounts with FS name/subtype, serves `FS{}`, and defers connection close. The root directory returns the fixed file for name `hello` and ENOENT otherwise.

State and persistence behavior: no mutable or persistent state; `greeting` is a constant.

Dependencies and integration points: demonstrates the core `fs.Node`, lookup, directory listing, and read-all interfaces.

Risks and test signals: read-only behavior depends on mode bits and lack of write handlers. Signal is successful mount and `cat hello` returning `hello, world`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/hellofs/hello.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_create_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/bench_create_test.go

Purpose: benchmark FUSE create throughput with a subprocess performing many `os.Create` calls against a minimal filesystem.

Important APIs, types, and functions: `benchCreateDir.Create` returns a dummy file as both node and handle; `benchCreateHelp` exposes `/init` and `/bench` through `httpjson.ServePOST`; `BenchmarkCreate` mounts with `fstestutil.MountedT`.

Control flow: benchmark prepares deterministic filenames in the helper, resets the timer, then asks the helper subprocess to create `b.N` files under the FUSE mount.

State and persistence behavior: helper stores filename list under mutex; scratch mount contents are temporary.

Dependencies and integration points: uses fstestutil mounting, spawntest helper subprocesses, HTTP JSON control, and Go benchmark framework.

Risks and test signals: helper uses `log.Fatalf`, killing the subprocess on errors. Benchmark signal is create operations per second with reduced in-process overhead.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_lookup_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/bench_lookup_test.go

Purpose: benchmark negative lookup/stat performance through a FUSE directory that always returns ENOENT.

Important APIs, types, and functions: `benchLookupDir.Lookup` implements `fs.NodeRequestLookuper`; `doBenchLookup` runs repeated `os.Stat`; `benchLookupHelper` exposes it through HTTP JSON.

Control flow: benchmark mounts the filesystem, spawns the helper, builds a non-existent path, resets the timer, and asks the helper to stat it `b.N` times.

State and persistence behavior: no filesystem state beyond the mounted directory; all lookups are negative.

Dependencies and integration points: integrates fs lookup interfaces, fstestutil, spawntest, and HTTP JSON.

Risks and test signals: kernel negative dentry caching can affect results depending on FUSE entry validity behavior. Signal is stable benchmark timing and expected `os.IsNotExist` errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_lookup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_readwrite_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/bench_readwrite_test.go

Purpose: benchmarks FUSE read, write, and write+sync paths for page-cache and direct-I/O modes at several transfer sizes.

Important APIs, types, and functions: defines `benchFS`, `benchDir`, `benchFile`, `benchConfig`, `benchmark`, `benchmarkSizes`, helper functions `doBenchWrite`, `doBenchWriteSync`, and `doBenchRead`. File handlers implement `Open`, `Read`, `Write`, and `Fsync`.

Control flow: each benchmark mounts the test FS with large readahead, async read, and writeback cache, spawns a helper, then the helper performs the requested I/O loop.

State and persistence behavior: file content is synthetic; reads fill response capacity, writes acknowledge byte counts, and no durable backing store exists.

Dependencies and integration points: uses FUSE open flags `OpenDirectIO` and `OpenKeepCache`, fstestutil, spawntest, and Go benchmark subtests.

Risks and test signals: `doBenchRead` opens with `os.Create`, so benchmark semantics rely on FUSE read behavior for the resulting descriptor. Timing is sensitive to kernel cache options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_readwrite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/doc.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/doc.go

Purpose: package documentation for the `fs/bench` benchmark package.

Important APIs, types, and functions: declares package `bench` and explains that benchmarks live separately from debug-heavy tests.

Control flow: no runtime control flow.

State and persistence behavior: no state.

Dependencies and integration points: affects Go documentation and package separation.

Risks and test signals: package split avoids benchmark contamination by normal test debug defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/helpers_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/helpers_test.go

Purpose: benchmark package `TestMain` wiring for spawntest helper subprocesses.

Important APIs, types, and functions: declares global `helpers spawntest.Registry`; `TestMain` adds helper flags, parses flags, runs helper mode if selected, and then runs tests/benchmarks.

Control flow: helper subprocesses enter `helpers.RunIfNeeded` and do not return; normal benchmark processes call `m.Run`.

State and persistence behavior: process-wide command-line flags and helper registry state only.

Dependencies and integration points: required by benchmark helpers registered in other files.

Risks and test signals: missing `TestMain` would make helper spawning fail due to unknown flags or inactive helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/checkdir.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/checkdir.go

Purpose: directory content assertion helper for tests.

Important APIs, types, and functions: defines `FileInfoCheck`, `checkDirError`, and `CheckDir`.

Control flow: `CheckDir` reads a directory, builds a missing set from expected names, stats each entry, applies an exact-name or wildcard `""` checker, records unexpected entries, and returns detailed errors for missing/extra items.

State and persistence behavior: reads filesystem state only; no mutation.

Dependencies and integration points: uses `os.ReadDir` and `os.FileInfo`, intended for FUSE integration tests.

Risks and test signals: `Buffer.Bytes`-style aliasing is not present, but returned errors expose map ordering nondeterminism. Tests should cover missing, extra, wildcard, and checker failure cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/checkdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/debug.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/debug.go

Purpose: command-line debug flag integration for FUSE tests.

Important APIs, types, and functions: defines `flagDebug`, global `debug`, `Set`, `String`, `IsBoolFlag`, `logMsg`, `DebugByDefault`, and registers `-fuse.debug` in init.

Control flow: setting the flag true assigns `fuse.Debug = logMsg`; setting false restores a no-op. `MountedFuncT` later uses `debug` to wire test logging.

State and persistence behavior: process-global flag value and `fuse.Debug` function pointer are mutated.

Dependencies and integration points: integrates Go flags, log package, fuse debug hook, and fstestutil mount helpers.

Risks and test signals: global debug state can leak across tests. Signals are visible FUSE logs when `-fuse.debug` or `DebugByDefault` is active.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/doc.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/doc.go

Purpose: package declaration and import-path documentation for `bazil.org/fuse/fs/fstestutil`.

Important APIs, types, and functions: declares package `fstestutil` with canonical import path.

Control flow: no runtime behavior.

State and persistence behavior: no state.

Dependencies and integration points: supports Go package documentation and import path checking.

Risks and test signals: build tooling verifies the import comment remains consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mounted.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mounted.go

Purpose: test helper for mounting a FUSE filesystem in a temporary directory and serving it in a goroutine.

Important APIs, types, and functions: defines `Mount`, `Close`, `MountedFunc`, `Mounted`, `MountedFuncT`, and `MountedT`.

Control flow: `MountedFunc` creates a temp dir, mounts FUSE, constructs an `fs.Server`, starts `server.Serve` in a goroutine, and returns a `Mount`. `Close` retries unmount, waits for serve completion, closes the connection, and removes the directory.

State and persistence behavior: owns temporary mount directory, FUSE connection, server, error channel, and closed flag.

Dependencies and integration points: used by tests and benchmarks; integrates `fuse.Mount`, `fuse.Unmount`, `fs.New`, and optional testing debug logs.

Risks and test signals: unmount can be busy and is retried up to 1000 times. Tests rely on proper cleanup to avoid leaked mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mounted.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo.go

Purpose: small cross-platform API for querying mount information relevant to tests.

Important APIs, types, and functions: defines `MountInfo` with `FSName` and `Type`, and exported `GetMountInfo` delegating to platform-specific `getMountInfo`.

Control flow: one wrapper call routes to the selected OS implementation.

State and persistence behavior: read-only query helper; no persistent state.

Dependencies and integration points: used by tests needing to assert FUSE mount type/name.

Risks and test signals: platform support differs; FreeBSD returns a fixed error while Linux parses `/proc/mounts`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_freebsd.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_freebsd.go

Purpose: FreeBSD implementation stub for test mount information.

Important APIs, types, and functions: `getMountInfo` returns an error stating FreeBSD has no useful mount information.

Control flow: all calls fail immediately.

State and persistence behavior: no state.

Dependencies and integration points: selected by Go build constraints on FreeBSD.

Risks and test signals: tests requiring mount info must skip or handle this error on FreeBSD.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_linux.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_linux.go

Purpose: Linux implementation of `GetMountInfo` by parsing `/proc/mounts`.

Important APIs, types, and functions: defines `fstabUnescape`, `errNotFound`, and `getMountInfo`.

Control flow: sleeps briefly to reduce a known race, reads `/proc/mounts`, splits lines into fields, unescapes fsname/dir/type, and returns the entry matching the mount directory.

State and persistence behavior: read-only snapshot of procfs mount state.

Dependencies and integration points: depends on Linux `/proc/mounts` fstab-style escaping and is used by test assertions.

Risks and test signals: the fixed sleep hints at mount visibility races. Tests should cover escaped paths and not-found behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/buffer.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/record/buffer.go

Purpose: concurrency-safe bytes buffer for recording test data from FUSE handlers.

Important APIs, types, and functions: `Buffer` wraps `bytes.Buffer` with a mutex and implements `io.Writer`; methods are `Write` and `Bytes`.

Control flow: `Write` locks and appends; `Bytes` locks and returns the underlying byte slice.

State and persistence behavior: in-memory buffer only.

Dependencies and integration points: used by `record.Writes` to capture write request data.

Risks and test signals: `Bytes` returns an alias to internal storage after unlocking, so callers must not mutate it concurrently. Tests should cover concurrent writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/record.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/record/record.go

Purpose: suite of recorder helper types for tests to capture FUSE requests and handler calls.

Important APIs, types, and functions: includes `Writes`, `Counter`, `MarkRecorder`, `Flushes`, `Recorder`, `RequestRecorder`, and request-specific recorders for setattr, fsync, mkdir, symlink, link, mknod, open, xattr operations, and create.

Control flow: handler methods copy request structs, sanitize hard-to-reproduce headers through `RecordRequest`, sometimes deep-copy byte slices, store values under locks, and generally return simple errors or success suitable for test assertions.

State and persistence behavior: state is in-memory counters, buffers, and last-recorded requests. No disk persistence.

Dependencies and integration points: implements many `fs.Node*` and `fs.Handle*` interfaces and uses `fuse.ErrNoXattr` and syscall errors.

Risks and test signals: shallow copies can be unsafe for reused buffers, so `Setxattr` deep-copies xattr data. Tests use recorded zero values to detect missing calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/record.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/wait.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/record/wait.go

Purpose: recorder for asynchronous FUSE `Release` calls with optional timeout waiting.

Important APIs, types, and functions: `ReleaseWaiter` implements `fs.HandleReleaser` with `Release` and exposes `WaitForRelease`.

Control flow: lazy `init` creates a buffered channel once. `Release` copies and sanitizes the request, sends it, and closes the channel. `WaitForRelease` blocks forever or until a timeout.

State and persistence behavior: in-memory once/channel state only.

Dependencies and integration points: used by tests where release is not synchronous with client close.

Risks and test signals: repeated Release calls after channel close would panic, matching the assumption of one release per handle. Timeout behavior avoids relying on global test timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/record/wait.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/example_test.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/example_test.go

Purpose: documentation-style example for using spawntest helpers with HTTP JSON control.

Important APIs, types, and functions: defines a registry, `addRequest`, `addResult`, `add`, `addHelper`, example test/main functions, and `Example`.

Control flow: the disabled-by-name test spawns a helper subprocess, sends JSON to `/`, and checks the addition result. The disabled `TestMain` shows flag and helper dispatch setup.

State and persistence behavior: no persistent state; helper process lifetime is controlled by `Control.Close`.

Dependencies and integration points: demonstrates `spawntest.Registry`, `Helper.Spawn`, and `httpjson.ServePOST`.

Risks and test signals: functions are prefixed `name_me_` to keep them illustrative rather than active; underscore assignments quiet linters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/client.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/client.go

Purpose: client helper for calling JSON-over-HTTP resources in tests.

Important APIs, types, and functions: exports `JSON`, `Resource`, and `(*Resource).Call`.

Control flow: `Call` marshals non-nil data as POST JSON or uses GET for nil data, sets JSON headers, executes the request with context, checks for HTTP 200, decodes JSON with unknown fields disallowed, and rejects trailing data via `mustEOF`.

State and persistence behavior: `Resource` stores an HTTP client and base URL only.

Dependencies and integration points: used by spawntest `Control.JSON` and benchmark helpers.

Risks and test signals: strict decoding can break clients if helpers add fields. Non-200 bodies are surfaced in error messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/doc.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/doc.go

Purpose: package documentation for JSON-over-HTTP test transport helpers.

Important APIs, types, and functions: declares package `httpjson` and describes possible future extraction.

Control flow: no runtime behavior.

State and persistence behavior: no state.

Dependencies and integration points: documents the client/server helpers used by spawntest.

Risks and test signals: documentation-only file; build confirms package consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/musteof.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/musteof.go

Purpose: shared strict JSON decoder helper that rejects trailing tokens after a top-level value.

Important APIs, types, and functions: defines `TrailingDataError` and `mustEOF`.

Control flow: `mustEOF` asks the decoder for another token; `io.EOF` is success, a token becomes `TrailingDataError`, and other errors propagate.

State and persistence behavior: no persistent state.

Dependencies and integration points: used by both HTTP JSON client and server to enforce exact one-message bodies.

Risks and test signals: error wording mimics JSON syntax errors. Tests should cover trailing whitespace, trailing objects, and malformed data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/musteof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/server.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/server.go

Purpose: reflection-based adapter from typed Go functions to POST-only JSON HTTP handlers.

Important APIs, types, and functions: exports `ServePOST`; internal `jsonPOST` implements `http.Handler`.

Control flow: `ServePOST` validates function shape `func(context.Context, T) (R, error)`. `ServeHTTP` rejects non-POST, decodes one JSON request with unknown fields disallowed, calls the function with request context, maps returned errors to HTTP 500, marshals the result, and writes JSON.

State and persistence behavior: handler stores reflection values and types only.

Dependencies and integration points: used by spawntest helpers and benchmark control endpoints.

Risks and test signals: reflection panics on bad registration shape; all function errors become 500, so bad-request granularity is absent. Strict JSON is a useful test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/spawntest.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/spawntest.go

Purpose: subprocess helper framework for tests that need client operations outside the main test process.

Important APIs, types, and functions: defines `Registry`, `Register`, `AddFlag`, `RunIfNeeded`, `Helper`, `Helper.Spawn`, `Control`, `Close`, `Signal`, `HTTP`, and `JSON`.

Control flow: tests register named HTTP handlers, add the internal helper flag in `TestMain`, and spawn the same test binary with an inherited Unix listener on fd 3. Helper mode serves HTTP on that listener; parent mode controls it with an httpunix client.

State and persistence behavior: registry maps names to handlers; each spawned helper owns a temp dir, Unix socket, process, and HTTP client until `Close`.

Dependencies and integration points: uses `net`, `os/exec`, `testing.TB`, `github.com/tv42/httpunix`, and `httpjson`.

Risks and test signals: process cleanup depends on `Close`; startup errors call `t.Fatalf`. Duplicate helper names panic, catching test setup mistakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/spawntest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/testfs.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/testfs.go

Purpose: simple reusable filesystem node implementations for tests.

Important APIs, types, and functions: defines `SimpleFS`, embeddable `File`, embeddable `Dir`, and map-backed `ChildMap`.

Control flow: `SimpleFS.Root` returns its configured node. `File.Attr` sets a regular writable mode, `Dir.Attr` sets directory mode, and `ChildMap.Lookup` returns a child or ENOENT.

State and persistence behavior: `ChildMap` stores in-memory child nodes; no backing persistence.

Dependencies and integration points: implements bazil/fuse `fs.FS`, `fs.Node`, and `fs.NodeStringLookuper` interfaces for tests and benchmarks.

Risks and test signals: default permissive modes may not match specific permission tests; child nodes must be stable map-key-capable values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/testfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/helpers_test.go -->
# sources/user-network-fs/bazil-fuse/fs/helpers_test.go

Purpose: top-level fs package test `TestMain` for spawntest helpers.

Important APIs, types, and functions: adds helper flags to `flag.CommandLine`, parses flags, dispatches helper mode with `helpers.RunIfNeeded`, and exits with `m.Run`.

Control flow: helper subprocesses do not run the normal test suite; normal processes continue to tests.

State and persistence behavior: process-wide flags and helper registry only.

Dependencies and integration points: supports fs package tests that register helpers such as lock helpers.

Risks and test signals: missing this setup would make helper subprocess tests fail on unknown flags or no HTTP server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve.go -->
# sources/user-network-fs/bazil-fuse/fs/serve.go

Purpose: core high-level FUSE service loop that maps kernel FUSE requests onto Go `FS`, `Node`, and `Handle` interfaces and exposes cache/notification helpers.

Important APIs, types, and functions: defines `FS`, `Node`, many optional `Node*` interfaces, `Handle` and optional `Handle*` interfaces, `Config`, `Server`, `New`, `Serve`, `DataHandle`, and `GenerateDynamicInode`. Internal state types include `serveNode`, `serveHandle`, and `serveRequest`.

Control flow: `Server.Serve` obtains the root node, registers it as NodeID 1, reads requests from `fuse.Conn`, and handles each in a goroutine. `serve` sets up context cancellation, request tracking, panic/Goexit protection, debug logging, and delegates to `handleRequest`. `handleRequest` switches over concrete request types for statfs, attrs, lookup, create, open, read/write, flush/release, forget, xattrs, locks, poll, fallocate, interrupts, destroy, and notify replies.

State and persistence behavior: server state is in-memory maps/slices for node IDs, handles, reference counts, pending requests, free lists, and notify wait channels, protected by mutexes. Filesystem persistence is delegated to user implementations. Kernel cache state is manipulated through invalidation and notify methods.

Dependencies and integration points: integrates the low-level `bazil.org/fuse` protocol package, `fuseutil.HandleRead`, `golang.org/x/sys/unix` lock constants, user filesystem implementations, and kernel notification APIs.

Risks and test signals: key risks are NodeID/refcount mismatches, stale handle access, duplicate request IDs, handler panics, context cancellation semantics, notify sequence exhaustion, and dynamic inode collisions. Tests should exercise every optional interface path, forget/batch-forget, interrupts, locks, cache invalidation, notify retrieve/store/delete, and panic/error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_freebsd_test.go -->
# sources/user-network-fs/bazil-fuse/fs/serve_freebsd_test.go

Purpose: FreeBSD-specific adapters for fs package tests comparing stat and statfs results.

Important APIs, types, and functions: defines `platformStatfs` and `platformStat` for `syscall.Statfs_t` and `os.FileInfo`.

Control flow: functions translate platform fields into common `statfsResult` and `statResult` structs used by cross-platform tests.

State and persistence behavior: read-only conversion of syscall data.

Dependencies and integration points: selected on FreeBSD and consumed by shared serve tests.

Risks and test signals: field width and naming differences are the main risk; tests compare normalized results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_freebsd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_linux_test.go -->
# sources/user-network-fs/bazil-fuse/fs/serve_linux_test.go

Purpose: Linux-specific adapters and OFD lock helper registration for fs package tests.

Important APIs, types, and functions: defines `platformStatfs`, `platformStat`, and registers `lock-ofd` with `lockHelp` using `unix.FcntlFlock` and OFD lock commands.

Control flow: stat helpers normalize Linux syscall structs. The init function assigns `lockOFDHelper` so shared lock tests can spawn a subprocess that sets, waits on, unlocks, and queries OFD locks.

State and persistence behavior: read-only stat conversion plus subprocess-driven kernel lock state during tests.

Dependencies and integration points: depends on Linux `golang.org/x/sys/unix`, shared fs tests, and spawntest helper infrastructure.

Risks and test signals: OFD locks are Linux-specific and require correct command selection for wait vs non-wait paths. Tests should observe lock conflicts and unlock behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_linux_test.go -->
