# subset-b-000043 Research

Grouped research for the requested composefs-rs and composefs files. Each section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/splitstream.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/splitstream.rs

Purpose: implements the SplitStream container format: a repository object containing a small fixed header, metadata ranges, compressed inline stream instructions, external object references, named stream references, content type, and total reconstructed stream size. It supports deduplication, zstd compression, fs-verity hash typing, and backward reading of the old bootc <= 1.15.x compiler-reordered header layout.

Important APIs/types/functions: `SplitStreamBuilder`, `SplitStreamWriter`, `SplitStreamReader`, `SplitStreamEntry`, `SplitStreamData`, `SplitStreamStats`, `FileRange`, `SplitstreamHeader`, `SplitstreamInfo`, `UniqueVec`, `new_to_old_format`, `read_exactish` integration, and public reader methods `cat`, `read_exact`, `read_inline_exact`, `iter_named_refs`, `lookup_named_ref`, and `get_object_refs`. `WritableRepo` tokens are carried from construction into repository writes to avoid repeated writable checks.

Control flow: writers buffer adjacent inline bytes, flush them as negative little-endian `i64` instructions, encode external references as non-negative indexes into the object reference table, then write header, info, stream refs, object refs, compressed named refs, and compressed stream into one repository object. The builder variant first awaits background object-storage `JoinHandle`s, then replays resolved entries through the writer. Readers parse either new or old header layout, validate version, algorithm, and 4 KiB fs-verity block size, read section ranges with `pread`, decode named refs, then stream instructions through a zstd decoder.

State/persistence: persistent state is the on-disk SplitStream binary layout plus repository object storage. Deduplication is stable through insertion-ordered `UniqueVec` tables. `total_size`, `content_type`, named refs, object refs, and zstd-compressed stream bytes become durable metadata. Runtime state includes `inline_bytes` while reading and buffers while writing.

Dependencies/integration: integrates with `Repository`, `WritableRepo`, `ObjectStoreMethod`, fs-verity hash algorithms, `zerocopy` layout traits, `zstd`, `rustix` fd I/O, and Tokio blocking/background work. Consumers are repository stream creation/opening paths and higher-level image/container code that needs inline metadata with external content chunks.

Risks/test signals: binary compatibility is high risk because layout offsets and section sizes are part of object identity. The file has compile-time layout assertions and unit tests for inline-only, external-only, mixed content, multiple externals, deduplication, boundary sizes, content type, total size, and old-format header reading. Remaining risks include malformed range handling, hostile oversized sections, named-ref parsing edge cases, and accidental total-size drift when callers use `write_reference` directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/splitstream.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/test.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/test.rs

Purpose: provides reusable test utilities for composefs and internal proptest strategies that generate complex `tree::FileSystem` values across hash algorithms.

Important APIs/types/functions: `tempdir`, crate-test-only `tempfile`, `TestRepo`, `TestRepo::new/path/dir`, and the `proptest_strategies` module with `filename`, `stat`, xattr generators, `LeafContentSpec`, `LeafSpec`, `DirSpec`, `FsSpec`, `UnusualFsSpec`, `filesystem_spec`, `unusual_filesystem_spec`, `build_filesystem`, and `build_unusual_filesystem`.

Control flow: temp directories are allocated under `$CFS_TEST_TMPDIR` or `~/.var/tmp` to avoid tmpfs/overlayfs fs-verity limitations. `TestRepo::new` initializes an insecure repository for tests. Proptest strategies generate Linux-valid filenames, xattr namespaces, symlink targets, regular inline/external files, devices, sockets, fifos, whiteouts, directories, and hardlinks, then builders convert specs into concrete composefs trees.

State/persistence: temp repo paths are retained by `TempDir` lifetimes and cleaned on drop. Generated filesystem specs are in-memory only, but they deliberately model persistent metadata such as uid/gid/mode, mtimes, xattrs, external object hashes/sizes, and hardlink identity via shared `LeafId`s.

Dependencies/integration: depends on `once_cell`, `tempfile`, `rustix::fs::CWD`, `proptest`, `hex`, and composefs tree/fsverity/repository modules. It is used by crate unit tests and downstream crate tests needing stable test repos or generated trees.

Risks/test signals: the generators intentionally stress EROFS/composefs boundaries: 255-byte names, xattr prefix indexes, overlay xattr escaping, ACL bits, V1 lustre fallback behavior, large directories, 30 GB external sizes, whiteouts, and hardlinks. Risks are mainly generator drift from production invariants and environmental failures if the selected temp filesystem cannot support required operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/tree.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/tree.rs

Purpose: specializes the generic filesystem tree model for composefs regular-file storage, where small files are inline and larger files are external fs-verity-addressed objects.

Important APIs/types/functions: `RegularFile<ObjectID>` with `Inline(Box<[u8]>)` and `External(ObjectID, u64)`, plus type aliases `LeafContent`, `Leaf`, `Directory`, `Inode`, `FileSystem`, and `DirectoryRef`. It re-exports `generic_tree`, `ImageError`, and `Stat`.

Control flow: this file mostly defines types; behavior is inherited from `generic_tree`. Tests create directories/leaves, insert entries into `BTreeMap`-backed directories, and validate lookup helpers for leaf IDs, regular file retrieval, and subdirectory retrieval.

State/persistence: persistent semantics are the tree metadata and leaf content strategy. External regular files persist only as an object hash plus declared size; inline regular files persist raw bytes in the image metadata.

Dependencies/integration: integrates fs-verity hash values into the generic tree and is used by dumpfile parsing, EROFS image writers, repository code, mkfs tests, and proptest tree generation.

Risks/test signals: correctness depends on external object size/hash consistency and on `generic_tree` preserving hardlink/shared-leaf semantics. Local tests cover basic insertion and typed lookup; broader coverage comes from mkfs and property tests that serialize this tree to EROFS.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/util.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/src/util.rs

Purpose: central utility module for digest I/O adaptation, file-descriptor helpers, exact-ish reads, SHA-256 parsing, errno filtering, temporary-name generation, and atomic symlink replacement.

Important APIs/types/functions: `DigestWrite<D>`, `DigestWrite::finalize`, `proc_self_fd`, `reopen_tmpfile_ro`, `create_tmpfile_in`, `read_exactish`, `read_exactish_async`, `Sha256Digest`, `parse_sha256`, `ErrnoFilter`, `generate_tmpname`, and `replace_symlinkat`.

Control flow: `read_exactish` loops until a buffer is full, distinguishes clean EOF from partial EOF, and retries `Interrupted`; the async form mirrors this with Tokio. `replace_symlinkat` first tries direct creation, then no-ops if an existing symlink already points to the target, otherwise creates a randomized temporary symlink and atomically renames it into place.

State/persistence: `create_tmpfile_in` creates anonymous `O_TMPFILE` state and `reopen_tmpfile_ro` transitions it for fs-verity. `replace_symlinkat` persists symlink targets atomically in a directory fd. Random temporary names are process-local and not persisted except during replacement.

Dependencies/integration: uses `rustix` for fd-relative filesystem operations, `sha2` for digest types, `tokio` for async reads, `rand` for temp names, and Unix path byte access. It supports repository object writes, splitstream parsing, fs-verity enablement, and link replacement.

Risks/test signals: tests cover clean EOF, partial EOF, broken readers, async behavior, and SHA-256 parsing including case and length errors. Remaining risks include 16-attempt temporary-name collision exhaustion, fd/path assumptions through `/proc/self/fd`, and callers misusing `parse_sha256` for non-SHA256 algorithms.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/tests/mkfs.rs -->
# sources/cloud-native/composefs-rs/crates/composefs/tests/mkfs.rs

Purpose: integration-style Rust tests for EROFS image generation, byte stability, fsck compatibility, and equivalence with the C `mkcomposefs` tool.

Important APIs/types/functions: `default_stat`, `debug_fs`, `empty`, `add_leaf`, `simple`, `foreach_case`, `dump_image`, tests `test_empty`, `test_simple`, `test_fsck`, `test_vs_mkcomposefs`, `test_erofs_digest_stability`, `test_erofs_v1_digest_stability`, and `test_vs_mkcomposefs_min_version_1`.

Control flow: canonical in-memory trees are generated, rendered through `mkfs_erofs` or `mkfs_erofs_versioned`, optionally passed to `fsck.erofs`, compared byte-for-byte to C `mkcomposefs` output from dumpfile input, and checked against pinned fs-verity digests.

State/persistence: temporary image files are created for external tools. Pinned digest constants are persistent compatibility contracts, especially for bootc sealed UKI trust chains where image bytes must stay stable.

Dependencies/integration: integrates composefs dumpfile, EROFS writer/debug code, fs-verity hashing, `insta` snapshots, `similar_asserts`, `test_with` executable gates, `fsck.erofs`, and C `mkcomposefs`.

Risks/test signals: high-value tests catch layout drift and C compatibility regressions. Tests gated on external executables may silently skip in constrained environments, so CI needs those tools for full coverage. Intentional format changes require updating snapshots and pinned digests with care.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/tests/mkfs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/tests/test.sh -->
# sources/cloud-native/composefs-rs/crates/composefs/tests/test.sh

Purpose: shell integration test for `composefs-setup-root`, emulating initramfs/sysroot layout and verifying the root pivot creates read-only root plus writable `/etc` and `/var` overlays.

Important APIs/types/functions: helper functions `mkd` and `assert_fail`; invokes `composefs-setup-root --config --cmdline --root-fs --sysroot`.

Control flow: requires root/unshare context, creates a fake block-device tree with composefs repo/state/deployment directories, bind-mounts a fake read-only root, bind-mounts the block tree as `/sysroot`, runs setup with a fixed image id, validates mount effects, writes into `/etc` and `/var`, unmounts recursively, and checks no test mounts remain.

State/persistence: creates persistent test directories under the provided top directory and expects writes to land in deployment upper/state paths. Mount namespace state is mutated and then reversed with `umount -R`.

Dependencies/integration: depends on Linux mount, user/mount namespaces, `composefs-setup-root`, `/proc/mounts`, and overlay/writeable sysroot semantics.

Risks/test signals: catches pivot/mount regressions and persistence placement bugs. Risks include requiring root privileges, bind-mount support, and fake EROFS content that cannot fully validate real kernel EROFS behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/crates/composefs/tests/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/Containerfile -->
# sources/cloud-native/composefs-rs/examples/bls/Containerfile

Purpose: builds a Fedora BLS-style composefs boot image base with kernel, composefs tools, SSH, systemd, and example workarounds.

Important APIs/types/functions: Containerfile stages are single-stage `fedora:43`; commands install packages, copy `cfsctl`, copy `extra/`, copy Fedora workarounds, run `kernel-install add-all`, enable `systemd-networkd`, clear root password, and create `/sysroot`.

Control flow: dependency installation is kept above the cache boundary, then project artifacts and boot configuration are copied in and kernel-install generates boot loader entries.

State/persistence: image state includes installed RPMs, copied initramfs/kernel-install/systemd snippets, enabled networkd unit, password state, and `/sysroot` mountpoint.

Dependencies/integration: integrates Fedora dnf, composefs RPM, kernel-install BLS layout, dracut/initramfs snippets, systemd-networkd, and test workarounds.

Risks/test signals: package names and Fedora version are time-sensitive, and root password deletion is test-only. Its behavior is validated indirectly by example build/run tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/etc/dracut.conf.d/no-xattr.conf -->
# sources/cloud-native/composefs-rs/examples/bls/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables xattr preservation in dracut for the BLS example by exporting `DRACUT_NO_XATTR=1`.

Important APIs/types/functions: one dracut environment assignment.

Control flow: read by dracut configuration loading before initramfs generation.

State/persistence: persists as a config file inside the image and affects generated initramfs content.

Dependencies/integration: integrates with dracut and the example image build.

Risks/test signals: minimal logic; risk is loss of required xattrs in future images. Covered only indirectly by boot tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/etc/dracut.conf.d/no-xattr.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/etc/mkinitcpio.conf -->
# sources/cloud-native/composefs-rs/examples/bls/extra/etc/mkinitcpio.conf

Purpose: mkinitcpio configuration for the BLS example, selecting modules, binaries, and hooks needed for composefs boot.

Important APIs/types/functions: `MODULES=(overlay erofs)`, `BINARIES=(strace)`, and `HOOKS=(base udev composefs autodetect microcode modconf kms keyboard keymap block filesystems)`.

Control flow: mkinitcpio consumes these arrays when building an initramfs, including the custom composefs hook before normal filesystem handling.

State/persistence: persists kernel image generation policy in the image.

Dependencies/integration: depends on mkinitcpio, overlay, EROFS, strace, and the installed composefs hook/install scripts.

Risks/test signals: hook ordering is sensitive; missing modules prevent root setup. Boot tests are the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/etc/mkinitcpio.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: dracut configuration for BLS images to force a non-hostonly initramfs and include drivers needed under virtualization.

Important APIs/types/functions: `hostonly=no` and `force_drivers+=" virtio_net vfat "`.

Control flow: dracut reads it during initramfs creation, making the image less tied to the build host and including network/VFAT support.

State/persistence: persists in the image and changes generated initramfs contents.

Dependencies/integration: integrates with dracut, virtio, VFAT ESP handling, and composefs boot examples.

Risks/test signals: over-inclusion increases initramfs size; under-inclusion breaks boot on virtual hardware. Tested via example VM boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: initramfs systemd unit that runs `composefs-setup-root` during BLS boot when the kernel command line contains `composefs`.

Important APIs/types/functions: `[Unit]` with `ConditionKernelCommandLine=composefs`, `After/Requires=sysroot.mount`, `Before=initrd-root-fs.target` and `initrd-switch-root.target`; `[Service]` one-shot `ExecStart=/usr/bin/composefs-setup-root`.

Control flow: systemd in the initramfs starts this after `/sysroot` is mounted and before switch-root, isolating to emergency target on failure.

State/persistence: the unit itself is packaged into initramfs; runtime mount/sysroot state is modified by the setup binary.

Dependencies/integration: depends on systemd initrd, dracut module installation, `composefs-setup-root`, and kernel cmdline.

Risks/test signals: ordering is critical; running too early or too late can leave an unusable root. VM boot and `test.sh` exercise the behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: dracut module installer for composefs setup in the BLS example.

Important APIs/types/functions: dracut callbacks `check`, `depends`, and `install`; installs `strace`, `composefs-setup-root`, the systemd service, and adds a wants link from `initrd-root-fs.target`.

Control flow: dracut calls `check` and `depends`, then `install` copies files into the initramfs and registers the service.

State/persistence: persists binaries and unit wants inside the generated initramfs.

Dependencies/integration: depends on dracut helper functions `inst`, `$SYSTEMCTL`, `${moddir}`, `${initdir}`, and `${systemdsystemunitdir}`.

Risks/test signals: path mismatches or missing helpers break initramfs generation. BLS copy includes `strace`, unlike UKI/unified variants, which may affect debugging and size.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/hooks/composefs -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/hooks/composefs

Purpose: mkinitcpio late hook that runs composefs root setup when `composefs` is present on the kernel command line.

Important APIs/types/functions: `run_latehook`, `getarg composefs`, and `/usr/bin/composefs-setup-root --sysroot /new_root`.

Control flow: the late hook exits silently without the cmdline flag; otherwise it invokes setup against mkinitcpio's `/new_root`.

State/persistence: no persistent state itself; mutates the initramfs mount tree at boot.

Dependencies/integration: depends on mkinitcpio ash runtime, `getarg`, and installed `composefs-setup-root`.

Risks/test signals: assumes `/new_root` semantics and command availability. Boot tests for mkinitcpio/Arch-like paths are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/hooks/composefs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/install/composefs -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/install/composefs

Purpose: mkinitcpio install script for adding composefs setup support.

Important APIs/types/functions: `build`, `add_binary`, and `add_runscript`.

Control flow: copies the dracut module's `composefs-setup-root` helper to `/usr/bin/composefs-setup-root` in the initramfs and registers the hook script.

State/persistence: affects generated initramfs contents.

Dependencies/integration: depends on mkinitcpio install API and the composefs setup helper path.

Risks/test signals: path coupling to dracut module layout is fragile. Boot tests reveal missing helper or hook registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/initcpio/install/composefs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: selects BLS layout for kernel-install in the BLS example.

Important APIs/types/functions: `layout = bls`.

Control flow: kernel-install reads this and emits Boot Loader Specification entries instead of UKIs.

State/persistence: persists kernel installation policy in the image.

Dependencies/integration: integrates with `kernel-install add-all` from the BLS Containerfile.

Risks/test signals: wrong layout would produce unbootable or wrong artifact type. Validated by example image boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->
# sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: overrides `systemd-growfs-root.service` to grow `/sysroot` instead of the composed read-only `/` in BLS composefs systems.

Important APIs/types/functions: systemd drop-in clears `ExecStart=` and replaces it with `/usr/lib/systemd/systemd-growfs /sysroot`.

Control flow: systemd merges the drop-in when starting growfs, redirecting the grow operation to the backing writable sysroot partition.

State/persistence: persistent service override in the image; runtime effect changes filesystem growth target.

Dependencies/integration: depends on systemd unit override semantics and `/sysroot` being the backing filesystem.

Risks/test signals: if `/sysroot` is absent or renamed, growfs fails or grows the wrong filesystem. VM boot and persistence tests are indirect signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/notify-multiuser.py -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/notify-multiuser.py

Purpose: RHEL9 workaround script that notifies the host VM harness when the guest reaches `multi-user.target`.

Important APIs/types/functions: reads `$CREDENTIALS_DIRECTORY/vmm.notify_socket`, parses `vsock:cid:port`, creates an `AF_VSOCK` `SOCK_SEQPACKET` socket, and sends `X_SYSTEMD_UNIT_ACTIVE=multi-user.target`.

Control flow: run by a systemd service after multi-user target; connects to host-provided vsock notification endpoint and sends one sd-notify-like line.

State/persistence: no persistent state; consumes systemd credentials at runtime.

Dependencies/integration: integrates with `testthing.VirtualMachine` sd-notify server and systemd credential injection.

Risks/test signals: assumes credential format and vsock support. Failure can make VM tests time out even if guest booted.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/notify-multiuser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/multi-user.target.wants/notify-multiuser.service -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/multi-user.target.wants/notify-multiuser.service

Purpose: enables the `notify-multiuser.service` workaround by placing the unit in `multi-user.target.wants`.

Important APIs/types/functions: unit content matches `notify-multiuser.service`: `After/Wants=multi-user.target`, `LoadCredential=vmm.notify_socket`, `ExecStart=/etc/notify-multiuser.py`, `Type=exec`, `RemainAfterExit=yes`.

Control flow: systemd treats this path as an enablement symlink/copy and starts the notifier after multi-user target.

State/persistence: persistent unit enablement in the workaround tree.

Dependencies/integration: depends on systemd unit loading and the Python notifier script.

Risks/test signals: duplicated full unit instead of symlink can drift from the canonical service file. VM harness readiness depends on it.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/multi-user.target.wants/notify-multiuser.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/notify-multiuser.service -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/notify-multiuser.service

Purpose: systemd unit that runs the RHEL9 host-notification script at multi-user target.

Important APIs/types/functions: `LoadCredential=vmm.notify_socket`, `ExecStart=/etc/notify-multiuser.py`, `Type=exec`, and `RemainAfterExit=yes`.

Control flow: after/wants multi-user target, starts the script once and remains active.

State/persistence: persistent service definition in the guest image workaround tree.

Dependencies/integration: depends on systemd credentials and `notify-multiuser.py`; integrates with `testthing` startup readiness.

Risks/test signals: if credentials are unavailable or service ordering changes, tests wait for SSH readiness incorrectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/notify-multiuser.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sockets.target.wants/sshd-vsock.socket -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sockets.target.wants/sshd-vsock.socket

Purpose: enables the RHEL9 SSH-via-vsock socket for VM tests.

Important APIs/types/functions: socket unit content `ListenStream=vsock::22`, `Accept=yes`, `Wants=ssh-access.target`, `Before=ssh-access.target`.

Control flow: systemd socket activation listens on guest vsock port 22 and starts an instance service per connection.

State/persistence: persistent socket enablement in `sockets.target.wants`.

Dependencies/integration: depends on systemd socket units, AF_VSOCK, and `sshd-vsock@.service`.

Risks/test signals: duplicated unit can drift from canonical socket file. Without it, the host cannot connect over the expected vsock path.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sockets.target.wants/sshd-vsock.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock.socket -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock.socket

Purpose: systemd socket definition for accepting OpenSSH connections over AF_VSOCK.

Important APIs/types/functions: `[Socket] ListenStream=vsock::22` and `Accept=yes`, with ordering around `ssh-access.target`.

Control flow: when a host connection arrives on vsock port 22, systemd activates `sshd-vsock@.service`.

State/persistence: persistent guest service configuration; runtime state is the listening socket.

Dependencies/integration: integrates with OpenSSH, systemd socket activation, and the `testthing` ProxyCommand.

Risks/test signals: depends on guest kernel/systemd vsock support. VM tests will fail to connect if socket activation breaks.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock@.service -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock@.service

Purpose: per-connection OpenSSH service for vsock socket activation on RHEL9 test images.

Important APIs/types/functions: `ExecStart=-/usr/sbin/sshd -i $OPTIONS -o "AuthorizedKeysFile ${CREDENTIALS_DIRECTORY}/ssh.ephemeral-authorized_keys-all .ssh/authorized_keys"`, `StandardInput=socket`, `LoadCredential=ssh.ephemeral-authorized_keys-all`, and optional `/etc/sysconfig/sshd`.

Control flow: spawned for each accepted socket connection, runs sshd in inetd mode, and uses systemd credentials for ephemeral host-generated SSH keys.

State/persistence: persistent service definition; runtime credentials and socket fd are provided per activation.

Dependencies/integration: depends on OpenSSH, systemd credentials, socket activation, and the host VM harness.

Risks/test signals: credential path syntax and sshd options are distro-sensitive. Connection failure is caught by VM startup and test command execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/sshd-vsock@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/systemd-ssh-proxy -->
# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/systemd-ssh-proxy

Purpose: Python polyfill for `systemd-ssh-proxy`, forwarding an already-open stdout socket to a vsock connection via fd passing.

Important APIs/types/functions: argparse parser for `vsock/<cid>` and port, `socket.AF_VSOCK`, and `socket.send_fds`.

Control flow: parses address, wraps stdout as a socket, connects a new vsock stream to the guest, sends that fd through stdout, and closes the local vsock socket.

State/persistence: no persistent state; operates per ProxyCommand invocation.

Dependencies/integration: depends on Python fd-passing support and AF_VSOCK. Used where systemd's proxy binary is unavailable.

Risks/test signals: assumes stdout is a socket suitable for fd passing. SSH connection tests reveal breakage.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/systemd-ssh-proxy -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/check-config -->
# sources/cloud-native/composefs-rs/examples/common/check-config

Purpose: preflight script validating host tools and fs-verity support needed to build composefs example disk images.

Important APIs/types/functions: checks for `fsverity`, `mkfs.erofs`, `mkfs.ext4`, `mkfs.vfat`, `mtools`, `skopeo`, `systemd-repart`; functions `check_measure` and `check_metadata`; env `FS_VERITY_MODE`.

Control flow: verifies the working directory supports fs-verity measurement, optionally exits early for `FS_VERITY_MODE=fix|none`, checks `systemd-repart` and `mkfs.ext4` binary strings for fs-verity support, and checks metadata dump ioctl support.

State/persistence: no persistent state; exits non-zero with diagnostic messages when host setup is inadequate.

Dependencies/integration: integrates with example build scripts, `install-patched-tools`, and `fix-verity` fallback mode.

Risks/test signals: binary string probing is heuristic and version-sensitive. It protects against known broken image generation paths, especially `/var/tmp` or filesystems without metadata ioctl support.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/check-config -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/fix-verity/Containerfile -->
# sources/cloud-native/composefs-rs/examples/common/fix-verity/Containerfile

Purpose: builds a small Fedora-based UEFI/dracut image that can boot against a disk image and enable fs-verity after systemd-repart created files without it.

Important APIs/types/functions: installs `kernel`, `binutils`, `systemd-boot-unsigned`, `btrfs-progs`, and `fsverity-utils`; runs `dracut --uefi --no-hostonly --install 'sync fsverity' --include /dracut-hook.sh ... /fix-verity.efi`.

Control flow: container build emits `/fix-verity.efi` containing the hook in pre-pivot.

State/persistence: generated EFI binary is later extracted by `fix-verity`.

Dependencies/integration: integrates with dracut, Fedora kernel packaging, fsverity-utils, and the QEMU fixup script.

Risks/test signals: Fedora version/kernel package availability can drift. Failure manifests when `FS_VERITY_MODE=fix` image post-processing cannot produce or run the EFI.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/fix-verity/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/fix-verity/dracut-hook.sh -->
# sources/cloud-native/composefs-rs/examples/common/fix-verity/dracut-hook.sh

Purpose: initramfs hook run by the fix-verity EFI to enable fs-verity on composefs objects and `meta.json` inside `/sysroot/composefs`.

Important APIs/types/functions: `mount -o remount,rw /sysroot`, loop over `objects/*/*`, `fsverity enable`, `umount /sysroot`, `sync`, and `poweroff -ff`.

Control flow: remounts the target sysroot writable, enables verity on all composefs object files and metadata, unmounts, syncs, and powers off the VM.

State/persistence: mutates the disk image by enabling fs-verity metadata on files.

Dependencies/integration: depends on fsverity tool, mounted root partition, composefs repository layout, and QEMU boot from `fix-verity`.

Risks/test signals: glob misses or layout changes could leave unsealed files. Abrupt poweroff is intentional after sync but still sensitive to storage flushing.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/fix-verity/dracut-hook.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/fix-verity/fix-verity -->
# sources/cloud-native/composefs-rs/examples/common/fix-verity/fix-verity

Purpose: host script that builds/extracts `fix-verity.efi` if needed and boots QEMU to apply fs-verity fixups to a raw disk image.

Important APIs/types/functions: builds `quay.io/lis/fix-verity`, extracts `/fix-verity.efi`, locates OVMF CODE/VARS, copies VARS to a temp file, and invokes `qemu-system-x86_64` with virtio disk plus `-kernel fix-verity.efi`.

Control flow: lazily builds the helper image, prepares firmware arguments when available, then runs a headless QEMU instance against the supplied raw disk.

State/persistence: creates cached `fix-verity.efi`, temporary OVMF VARS copy, and mutates the disk image.

Dependencies/integration: depends on podman, QEMU/KVM, OVMF paths, dracut-built EFI, and the hook.

Risks/test signals: host firmware path detection is distro-specific; failure leaves images without fs-verity. The script is selected by `run-repart` when `FS_VERITY_MODE=fix`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/fix-verity/fix-verity -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/install-patched-tools -->
# sources/cloud-native/composefs-rs/examples/common/install-patched-tools

Purpose: builds patched/newer `systemd-repart` and `mkfs.ext4` into a caller-provided install path for fs-verity-capable image creation.

Important APIs/types/functions: clones `systemd` at `v258`, builds `systemd-repart`; clones `e2fsprogs` at `v1.47.3`, builds `mke2fs`, and copies it as `mkfs.ext4`.

Control flow: sequentially clones, checks out tags, configures/builds, creates install directories, and copies binaries/shared objects.

State/persistence: writes built tools under `$install_path` and leaves source/build trees in the current directory.

Dependencies/integration: depends on git, meson, ninja, configure/make, network access, and build dependencies.

Risks/test signals: destructive in current working directory if `systemd` or `e2fsprogs` already exist; pinned versions can age. `check-config` suggests this path when system tools lack fs-verity support.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/install-patched-tools -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/install-systemd-boot -->
# sources/cloud-native/composefs-rs/examples/common/install-systemd-boot

Purpose: prepares an EFI System Partition tree with systemd-boot for example images.

Important APIs/types/functions: creates `tmp/efi/loader`, writes `loader.conf`, creates `EFI/BOOT` and `EFI/systemd`, and copies `systemd-bootx64.efi` to both vendor and fallback paths.

Control flow: straight-line shell script that populates the temporary ESP before repartitioning.

State/persistence: writes files under `tmp/efi`.

Dependencies/integration: depends on systemd-boot binary path and is consumed by `run-repart` partition definitions.

Risks/test signals: x86_64-specific paths and binary name; missing package breaks image build.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/install-systemd-boot -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/make-image -->
# sources/cloud-native/composefs-rs/examples/common/make-image

Purpose: final image assembly helper that checks composefs EROFS images, runs repart under fakeroot, converts raw disk to qcow2, and removes the raw intermediate.

Important APIs/types/functions: iterates `tmp/sysroot/composefs/images/*` through `fsck.erofs`, runs `fakeroot run-repart tmp/image.raw`, and runs `qemu-img convert`.

Control flow: validate images first, create raw disk image, convert to requested output, delete raw image.

State/persistence: writes final qcow2 at caller path and temporary raw image under `tmp`.

Dependencies/integration: depends on `fsck.erofs`, `fakeroot`, `systemd-repart` via `run-repart`, and `qemu-img`.

Risks/test signals: fails early on invalid EROFS; assumes image glob exists. Conversion failures leave partial artifacts.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/make-image -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/run-repart -->
# sources/cloud-native/composefs-rs/examples/common/run-repart

Purpose: creates a raw disk image with ESP and sysroot partitions, applying ownership/SELinux labels and optional fs-verity copy/fix behavior.

Important APIs/types/functions: `chown`, `chcon`, repart definitions `01-esp.conf` and `02-sysroot.conf`, env `SYSTEMD_REPART_MKFS_OPTIONS_EXT4=-O verity`, `FS_VERITY_MODE`, `FS_FORMAT`, `COPY_FILES_FLAG`, and `systemd-repart`.

Control flow: normalizes ownership and labels, writes partition definition files, sets `CopyFiles` to include `fsverity=copy` in repart mode, runs `systemd-repart` offline with `TMPDIR=$PWD/tmp`, then optionally runs fix-verity.

State/persistence: writes `tmp/repart.d`, mutates `tmp/sysroot` metadata, and produces the raw image path supplied as `$1`.

Dependencies/integration: depends on SELinux tools, systemd-repart fs-verity support, `install-systemd-boot` output under `tmp/efi`, and optional `fix-verity`.

Risks/test signals: label patterns are example-specific and may fail on non-SELinux hosts. CopyFiles fs-verity support is version-sensitive; `check-config` protects this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/common/run-repart -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/pyproject.toml -->
# sources/cloud-native/composefs-rs/examples/pyproject.toml

Purpose: pytest configuration for example VM tests.

Important APIs/types/functions: `[tool.pytest.ini_options]` with strict markers, verbose output, automatic asyncio mode, `pythonpath = "."`, and `testpaths = ["test"]`.

Control flow: pytest reads this when invoked from examples, enabling async tests without explicit decorators and discovering only the `test` directory.

State/persistence: repository configuration only.

Dependencies/integration: integrates with `pytest`, `pytest-asyncio`, `testthing.py`, and `examples/test/run`.

Risks/test signals: broad `pythonpath="."` relies on running from examples root. Misconfiguration prevents async VM tests from running.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/s3-uploader.py -->
# sources/cloud-native/composefs-rs/examples/s3-uploader.py

Purpose: uploads files from a directory to S3-compatible object storage, with MIME detection, optional zstd compression, symlink-target handling, and parallel processing.

Important APIs/types/functions: `MimeDB`, `MimeDB.getdb/content_type_for_data`, `ensure_file`, `find_not_type_d`, and `main`.

Control flow: opens the source directory as an fd, walks files with `os.fwalk`, sorts paths, creates a boto3 bucket resource, and maps files through a `ThreadPoolExecutor`. Each file is skipped if S3 `HEAD` succeeds, otherwise read with `O_NOFOLLOW`; symlinks are uploaded as their target text with content type `text/x-symlink-target`; payloads are compressed with zstd level 19 only if ratio exceeds 1.1.

State/persistence: remote S3 objects are persisted with `ContentEncoding` and `ContentType`; local state is read-only except environment variable `AWS_REQUEST_CHECKSUM_CALCULATION`.

Dependencies/integration: depends on boto3/botocore, libmagic Python bindings, zstd module, S3 endpoint credentials, and Unix fd-relative I/O.

Risks/test signals: no explicit tests in this subset. Race risk exists between HEAD skip and PUT; symlink handling encodes target with surrogateescape; path traversal is constrained by dirfd and `O_NOFOLLOW`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/s3-uploader.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/test/run -->
# sources/cloud-native/composefs-rs/examples/test/run

Purpose: wrapper to build one example image for a given OS and run the pytest VM tests against it.

Important APIs/types/functions: positional `EXAMPLE` and `OS`; invokes `"${EXAMPLE}/build" "${OS}"`; sets `TEST_IMAGE="${EXAMPLE}/${OS}-${EXAMPLE}-efi.qcow2"` and runs `pytest test`.

Control flow: changes to examples root, builds image, then launches tests with the image path in the environment.

State/persistence: produces example qcow2 images via the build script and consumes them in tests.

Dependencies/integration: depends on example-specific `build` scripts, pytest configuration, and `test_basic.py`.

Risks/test signals: naming convention must match each build script output. Failure to build stops tests due to `set -eux`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/test/run -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/test/test_basic.py -->
# sources/cloud-native/composefs-rs/examples/test/test_basic.py

Purpose: async pytest smoke test for composefs booted example images.

Important APIs/types/functions: `machine` async fixture, `test_basic`, `testthing.IpcDirectory`, and `testthing.VirtualMachine`.

Control flow: fixture requires `TEST_IMAGE`, starts a VM with verbose logging, and yields it. Test verifies root is read-only, `/sysroot` contains expected entries, writes to `/etc` and `/var`, reboots, checks both persisted, and removes them.

State/persistence: tests persistence of mutable deployment state across reboot while using VM snapshot mode by default.

Dependencies/integration: depends on QEMU/OVMF/vsock/SSH harness, example image bootability, and filesystem layout.

Risks/test signals: strong end-to-end signal for root immutability and `/etc`/`/var` overlays. It is expensive and host-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/test/test_basic.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/testthing.py -->
# sources/cloud-native/composefs-rs/examples/testthing.py

Purpose: standalone async VM harness used by pytest and manually to boot qcow2 images, wait for guest readiness over vsock, and execute commands over SSH.

Important APIs/types/functions: `IpcDirectory`, `_vsock_listen`, `_find_qemu`, `_find_ovmf`, `_qmp_command`, `_ssh_direct_args`, `GuestPath`, `VirtualMachine`, `SubprocessError`, `cleanup_on_signal`, and `_main`.

Control flow: allocates `/run/user/$uid/test.thing/tt.n`, generates an ephemeral SSH key, starts a vsock sd-notify server, launches QEMU with OVMF, QMP, virtio disk, vhost-vsock, credentials, and console logging, waits for guest `multi-user.target` notification, establishes an SSH control socket, then exposes `execute`, `write`, `reboot`, port-forwarding, and QMP operations. Shutdown cancels background tasks and quits or powers down the VM depending on snapshot mode.

State/persistence: IPC directories, SSH keys, control sockets, QMP socket, console logs, and copied OVMF VARS are host-side transient state. Guest disk writes are transient when `snapshot=True` and persistent with `--maintain`.

Dependencies/integration: depends on Python asyncio, QEMU/KVM, OVMF, OpenSSH, AF_VSOCK, systemd credentials, guest notifier units, and pytest fixtures. It integrates tightly with the workaround files in this subset.

Risks/test signals: startup timeout reports console logs, giving good diagnostics. Risks include distro-specific QEMU/OVMF paths, vsock CID assignment by chosen port, SSH ProxyCommand availability, snapshot semantics, and a formatting bug in one timeout string literal that lacks an `f` prefix.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/testthing.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/Containerfile -->
# sources/cloud-native/composefs-rs/examples/uki/Containerfile

Purpose: multi-stage Fedora Containerfile for composefs-enabled UKI images where the base stage contains the root filesystem and later stages add kernel/boot artifacts.

Important APIs/types/functions: `base`, `kernel`, and `bootable` stages; `ARG COMPOSEFS_FSVERITY`; installs composefs, kernel, systemd-boot, ukify, SELinux tools, SSH, skopeo, btrfs/dosfstools; writes `/etc/kernel/cmdline` with `composefs=${COMPOSEFS_FSVERITY} rw`; runs `kernel-install add-all`.

Control flow: base image is prepared without final `/boot`; kernel stage receives the composefs fs-verity digest as a build arg and bakes it into the kernel command line before kernel-install; bootable stage copies `/boot` from kernel onto base.

State/persistence: image stores SELinux workaround module, enabled networkd, cleared root password, `/sysroot`, and generated UKI/boot files.

Dependencies/integration: integrates with `cfsctl` build flow that supplies `COMPOSEFS_FSVERITY`, systemd ukify, kernel-install, dracut/mkinitcpio snippets, and VM tests.

Risks/test signals: digest must match exact base filesystem; any post-digest mutation invalidates the trust chain. Package/version availability and SELinux policy compilation are host/distro-sensitive.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/etc/dracut.conf.d/no-xattr.conf -->
# sources/cloud-native/composefs-rs/examples/uki/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables dracut xattr handling for UKI example initramfs generation.

Important APIs/types/functions: `export DRACUT_NO_XATTR=1`.

Control flow: consumed by dracut at build time.

State/persistence: persists in image config and affects generated UKI initramfs.

Dependencies/integration: dracut and UKI Containerfile.

Risks/test signals: same as BLS copy; future xattr-dependent boot content could be omitted.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/etc/dracut.conf.d/no-xattr.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/etc/mkinitcpio.conf -->
# sources/cloud-native/composefs-rs/examples/uki/extra/etc/mkinitcpio.conf

Purpose: mkinitcpio composefs boot configuration for UKI example variants.

Important APIs/types/functions: `MODULES=(overlay erofs)`, `BINARIES=(strace)`, and hook order with `composefs` before filesystem discovery.

Control flow: used by mkinitcpio when building initramfs content.

State/persistence: persistent initramfs generation config.

Dependencies/integration: mkinitcpio hooks/install scripts and composefs setup binary.

Risks/test signals: hook order and module inclusion are boot-critical.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/etc/mkinitcpio.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: makes UKI dracut output non-hostonly for portable example boot.

Important APIs/types/functions: `hostonly=no`.

Control flow: dracut includes generic drivers/modules rather than tailoring to build host.

State/persistence: affects generated UKI/initramfs.

Dependencies/integration: dracut and kernel-install/ukify.

Risks/test signals: broad inclusion increases size; insufficient inclusion breaks VM boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: UKI copy of the initramfs systemd service that runs `composefs-setup-root`.

Important APIs/types/functions: same unit contract as BLS: `ConditionKernelCommandLine=composefs`, requires `sysroot.mount`, runs before initrd root/switch-root targets, and executes `/usr/bin/composefs-setup-root`.

Control flow: starts only when composefs cmdline is present during initrd boot.

State/persistence: packed into the UKI initramfs.

Dependencies/integration: dracut module install, systemd initrd, and composefs setup binary.

Risks/test signals: ordering and failure isolation are boot-critical; tested by VM boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: UKI dracut module installer for composefs setup.

Important APIs/types/functions: `check`, `depends`, `install`; copies composefs setup binary and service, and adds service to `initrd-root-fs.target`.

Control flow: dracut invokes installer during initramfs creation.

State/persistence: generated initramfs includes binary, unit, and wants link.

Dependencies/integration: dracut module variables and `$SYSTEMCTL`.

Risks/test signals: unlike BLS version, it does not install `strace`, so debug expectations differ. Boot tests catch missing files.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/hooks/composefs -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/hooks/composefs

Purpose: UKI mkinitcpio late hook for composefs root setup.

Important APIs/types/functions: `run_latehook`, `getarg composefs`, `/usr/bin/composefs-setup-root --sysroot /new_root`.

Control flow: no-ops without composefs cmdline; otherwise sets up root late in initcpio.

State/persistence: runtime mount mutation only.

Dependencies/integration: mkinitcpio runtime and setup binary.

Risks/test signals: boot-critical path for mkinitcpio-based UKI examples.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/hooks/composefs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/install/composefs -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/install/composefs

Purpose: UKI mkinitcpio install script for composefs setup support.

Important APIs/types/functions: `build`, `add_binary`, and `add_runscript`.

Control flow: copies helper binary into initramfs and registers hook script.

State/persistence: generated initramfs content.

Dependencies/integration: mkinitcpio API and dracut module helper path.

Risks/test signals: path coupling and missing binary risk; VM boot reveals failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/initcpio/install/composefs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: selects UKI generation through `ukify` for the UKI example.

Important APIs/types/functions: `layout = uki` and `uki_generator = ukify`.

Control flow: kernel-install uses ukify rather than BLS entries.

State/persistence: persistent kernel-install policy.

Dependencies/integration: systemd kernel-install and systemd-ukify package.

Risks/test signals: wrong generator/layout would prevent UKI boot artifacts. Validated by example build/boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->
# sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: UKI copy of the growfs override that targets `/sysroot`.

Important APIs/types/functions: clears `ExecStart` and sets `/usr/lib/systemd/systemd-growfs /sysroot`.

Control flow: systemd drop-in redirects root growfs.

State/persistence: persistent unit override in the image.

Dependencies/integration: systemd and composefs backing sysroot layout.

Risks/test signals: incorrect target breaks disk growth or mutates the composed root.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/uki/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/Containerfile -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/Containerfile

Purpose: Fedora multi-stage Containerfile for a unified composefs UKI image with Secure Boot signing support.

Important APIs/types/functions: base/kernel/bootable stages; installs `mokutil`, `sbsigntools`, `systemd-ukify`, composefs, SELinux tools, SSH; computes `COMPOSEFS_FSVERITY` with `cfsctl compute-id --bootable /mnt/base`; writes `/etc/kernel/cmdline`; runs `kernel-install add-all` with BuildKit secrets `key` and `cert`.

Control flow: base root is prepared, kernel stage binds base to compute its digest, writes composefs cmdline, then signs/generated UKIs using configured secrets and `uki.conf`; final bootable stage copies `/boot`.

State/persistence: generated signed UKI artifacts and Secure Boot policy references are persisted in `/boot`; secrets are build-time only.

Dependencies/integration: depends on cfsctl, systemd ukify, sbsign, BuildKit secrets, dracut snippets, and Secure Boot test runner.

Risks/test signals: strongest risk is digest/signing mismatch if base changes after compute-id or secrets are unavailable. Secure Boot runtime coverage comes from `run`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/dracut.conf.d/no-xattr.conf -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables dracut xattr preservation for unified-secureboot example.

Important APIs/types/functions: `export DRACUT_NO_XATTR=1`.

Control flow: read by dracut during initramfs/UKI generation.

State/persistence: persistent config affecting generated UKI.

Dependencies/integration: dracut and secureboot Containerfile.

Risks/test signals: xattr suppression may hide future metadata requirements.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/dracut.conf.d/no-xattr.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/kernel/uki.conf -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/kernel/uki.conf

Purpose: ukify Secure Boot signing configuration for the unified-secureboot example.

Important APIs/types/functions: `[UKI]`, `SecureBootSigningTool=sbsign`, `SecureBootPrivateKey=/run/secrets/key`, and `SecureBootCertificate=/run/secrets/cert`.

Control flow: kernel-install/ukify reads this during UKI generation and signs using BuildKit-mounted secrets.

State/persistence: config persists in image; private key/cert paths are ephemeral build secrets.

Dependencies/integration: depends on systemd-ukify, sbsign, and `Containerfile` secret mounts.

Risks/test signals: missing or mismatched secrets fail UKI signing. Runtime validation is through Secure Boot QEMU run.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/etc/kernel/uki.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: non-hostonly dracut config for unified-secureboot composefs images.

Important APIs/types/functions: `hostonly=no`.

Control flow: read during UKI generation to avoid host-specific initramfs.

State/persistence: affects generated signed UKI.

Dependencies/integration: dracut and ukify.

Risks/test signals: size vs portability tradeoff; boot test validates inclusion.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: initramfs service for running composefs setup in unified-secureboot UKIs.

Important APIs/types/functions: systemd initrd unit with composefs cmdline condition, sysroot dependency, initrd target ordering, emergency failure isolation, and one-shot setup execution.

Control flow: activated in signed UKI initramfs before switch-root.

State/persistence: embedded in generated signed UKI.

Dependencies/integration: dracut module installer and composefs setup binary.

Risks/test signals: failure can break Secure Boot boot chain; `run` exercises boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: dracut installer for composefs setup in unified-secureboot images.

Important APIs/types/functions: `check`, `depends`, `install`, `inst`, and `$SYSTEMCTL add-wants`.

Control flow: installs setup binary/service and registers service with `initrd-root-fs.target`.

State/persistence: generated initramfs/UKI content.

Dependencies/integration: dracut and systemd initrd.

Risks/test signals: signing can make post-build fixes impossible, so missing content must be caught during build/boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: tells kernel-install to generate ukify UKIs for unified-secureboot.

Important APIs/types/functions: `layout = uki`, `uki_generator = ukify`.

Control flow: kernel-install chooses UKI generation and consults `uki.conf` for signing.

State/persistence: persistent kernel-install policy in image.

Dependencies/integration: ukify, sbsign config, kernel-install.

Risks/test signals: incorrect generator bypasses Secure Boot signing path.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: growfs override for unified-secureboot images, targeting `/sysroot`.

Important APIs/types/functions: resets `ExecStart` then runs `systemd-growfs /sysroot`.

Control flow: systemd applies it when starting root growfs.

State/persistence: persistent unit drop-in.

Dependencies/integration: systemd and composefs sysroot layout.

Risks/test signals: backing partition must be mounted at `/sysroot`; VM boot validates.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/run -->
# sources/cloud-native/composefs-rs/examples/unified-secureboot/run

Purpose: manual QEMU runner for unified-secureboot images, optionally enabling Secure Boot using generated/custom OVMF variable templates.

Important APIs/types/functions: detects `secureboot/`, invokes `virt-fw-vars` with PK/KEK/db certs, prepares `qemu_args`, and runs `qemu-system-x86_64` with virtio disk and optional secure pflash.

Control flow: if secureboot directory exists, builds or reuses a VARS template, copies it for a fresh run, and enables SMM/secure pflash; otherwise uses plain OVMF BIOS path. Then launches QEMU headless with `fedora-unified-secureboot-efi.qcow2`.

State/persistence: writes `VARS_CUSTOM.secboot.fd.template` and per-run `VARS_CUSTOM.secboot.fd`.

Dependencies/integration: depends on QEMU/KVM, edk2 OVMF secureboot paths, `virt-fw-vars`, and generated qcow2 image.

Risks/test signals: firmware paths and QEMU machine version are host-specific. This is the direct manual signal that signed UKIs boot under Secure Boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified-secureboot/run -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/Containerfile -->
# sources/cloud-native/composefs-rs/examples/unified/Containerfile

Purpose: Fedora multi-stage Containerfile for unified composefs UKI images without Secure Boot signing.

Important APIs/types/functions: base/kernel/bootable stages; installs composefs, kernel, systemd-boot, ukify, SELinux tools, SSH; computes fs-verity digest from bound base via `cfsctl`; writes kernel cmdline; runs `kernel-install add-all`.

Control flow: base root is prepared, kernel stage computes digest over base and generates `/boot`, bootable stage combines base with generated boot files.

State/persistence: resulting image includes `/boot` UKIs, command line with composefs digest, SELinux workaround module, and `/sysroot`.

Dependencies/integration: cfsctl, kernel-install, ukify, dracut module files, and VM tests.

Risks/test signals: digest must match base content exactly; removing random seed improves reproducibility. Example tests validate boot and persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/Containerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/etc/dracut.conf.d/no-xattr.conf -->
# sources/cloud-native/composefs-rs/examples/unified/extra/etc/dracut.conf.d/no-xattr.conf

Purpose: disables dracut xattr preservation for unified example images.

Important APIs/types/functions: `export DRACUT_NO_XATTR=1`.

Control flow: dracut reads during UKI initramfs generation.

State/persistence: persistent build config.

Dependencies/integration: dracut and unified Containerfile.

Risks/test signals: can hide future xattr requirements; boot tests are indirect signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/etc/dracut.conf.d/no-xattr.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf

Purpose: makes unified example dracut output non-hostonly.

Important APIs/types/functions: `hostonly=no`.

Control flow: applied during initramfs/UKI build.

State/persistence: affects generated boot artifacts.

Dependencies/integration: dracut and kernel-install.

Risks/test signals: portability/size tradeoff; validated by VM boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/dracut.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->
# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service

Purpose: initramfs service for composefs root setup in unified UKIs.

Important APIs/types/functions: composefs cmdline condition, `sysroot.mount` dependency, ordering before initrd root/switch-root targets, one-shot `ExecStart=/usr/bin/composefs-setup-root`.

Control flow: systemd initrd starts it when composefs boot is requested.

State/persistence: embedded in generated UKI.

Dependencies/integration: dracut, systemd, and setup binary.

Risks/test signals: unit ordering controls root pivot correctness; VM tests validate.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/composefs-setup-root.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->
# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh

Purpose: dracut module installer for unified composefs setup.

Important APIs/types/functions: `check`, `depends`, `install`, `inst`, and `$SYSTEMCTL add-wants`.

Control flow: installs setup binary/service and links service into initrd target.

State/persistence: generated UKI/initramfs content.

Dependencies/integration: dracut and systemd initrd.

Risks/test signals: path and unit registration errors break boot.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/dracut/modules.d/37composefs/module-setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->
# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/kernel/install.conf.d/37composefs.conf

Purpose: selects ukify UKI generation for unified images.

Important APIs/types/functions: `layout = uki`, `uki_generator = ukify`.

Control flow: consumed by kernel-install during `add-all`.

State/persistence: kernel-install policy file.

Dependencies/integration: systemd ukify package.

Risks/test signals: wrong layout breaks expected image boot path.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/kernel/install.conf.d/37composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->
# sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf

Purpose: growfs root service override for unified composefs images.

Important APIs/types/functions: replaces default `ExecStart` with `systemd-growfs /sysroot`.

Control flow: applied when systemd starts growfs service.

State/persistence: persistent systemd drop-in.

Dependencies/integration: composefs sysroot layout.

Risks/test signals: wrong target can fail disk growth or mutate incorrect filesystem.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/examples/unified/extra/usr/lib/systemd/system/systemd-growfs-root.service.d/37-composefs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs-rs/renovate.json -->
# sources/cloud-native/composefs-rs/renovate.json

Purpose: configures Renovate for composefs-rs by extending a shared bootc-dev infrastructure preset.

Important APIs/types/functions: JSON schema URL and `extends: ["local>bootc-dev/infra:renovate-shared-config.json"]`.

Control flow: Renovate loads the shared local preset to determine dependency update behavior.

State/persistence: repository automation configuration only.

Dependencies/integration: depends on Renovate and the referenced shared config repository/preset.

Risks/test signals: if the local preset is unavailable or renamed, dependency automation fails. No runtime tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs-rs/renovate.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.devcontainer/debian/devcontainer.json -->
# sources/cloud-native/composefs/.devcontainer/debian/devcontainer.json

Purpose: Debian devcontainer definition for the C composefs repository.

Important APIs/types/functions: image `ghcr.io/bootc-dev/devenv-debian`, VS Code extensions `rust-lang.rust-analyzer` and `golang.Go`, `devaipod.nestedContainers=true`, `privileged=true`, post-create `sudo /usr/local/bin/devenv-init.sh`, and PATH extension for cargo.

Control flow: devcontainer tooling pulls the image, starts a privileged/nested-container-capable environment, runs init, and sets remote environment.

State/persistence: development environment config; no project runtime state.

Dependencies/integration: integrates with VS Code Dev Containers/Codespaces and bootc devenv image.

Risks/test signals: privileged mode is broad; image tags are external. Same content as root devcontainer, so drift should be avoided.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.devcontainer/debian/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.devcontainer/devcontainer.json -->
# sources/cloud-native/composefs/.devcontainer/devcontainer.json

Purpose: default devcontainer definition, currently matching the Debian variant.

Important APIs/types/functions: bootc Debian devenv image, rust/go extensions, nested container customization, privileged fallback, devenv init, and cargo PATH.

Control flow: used when no distro subfolder is selected.

State/persistence: development-only configuration.

Dependencies/integration: VS Code/devcontainer CLI, devaipod, and bootc-dev image.

Risks/test signals: duplicated config can diverge from Debian file; privileged default may be undesirable outside controlled dev environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.devcontainer/ubuntu/devcontainer.json -->
# sources/cloud-native/composefs/.devcontainer/ubuntu/devcontainer.json

Purpose: Ubuntu devcontainer definition for the C composefs repository.

Important APIs/types/functions: image `ghcr.io/bootc-dev/devenv-ubuntu`, same VS Code/devaipod/privileged/init/PATH settings as Debian variants.

Control flow: starts an Ubuntu-based development container and runs the standard init script.

State/persistence: development-only configuration.

Dependencies/integration: VS Code/devcontainer tooling and bootc Ubuntu devenv image.

Risks/test signals: distro image differences can hide dependency assumptions; config has no direct CI test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.devcontainer/ubuntu/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.gemini/config.yaml -->
# sources/cloud-native/composefs/.gemini/config.yaml

Purpose: Gemini code-review automation configuration, maintained from bootc-dev infra common config.

Important APIs/types/functions: `have_fun`, `code_review.disable=false`, severity threshold `MEDIUM`, unlimited max review comments, PR-opened help/summary disabled, code review enabled, and empty ignore patterns.

Control flow: Gemini reads this during PR review to decide comment behavior.

State/persistence: automation configuration only.

Dependencies/integration: depends on Gemini review tooling and shared infra maintenance.

Risks/test signals: comment volume can be high with unlimited comments; "DO NOT EDIT" means local changes may be overwritten.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.gemini/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.github/workflows/builds.yaml -->
# sources/cloud-native/composefs/.github/workflows/builds.yaml

Purpose: GitHub Actions workflow that builds binary composefs artifacts across several distro container bases on every push.

Important APIs/types/functions: matrix over Ubuntu 24.04/22.04, Fedora 41, CentOS Stream 9; bootstrap git, checkout, install deps, set `SOURCE_DATE_EPOCH`, Meson configure/build/install, reproducible tar creation, artifact upload, and log upload.

Control flow: each matrix job runs in its container, installs dependencies with `hacking/installdeps.sh`, builds with FUSE disabled, captures install root as a normalized tarball, and uploads results.

State/persistence: CI artifacts `composefs-<basename>.tar` and logs.

Dependencies/integration: GitHub Actions, distro package managers, Meson, tar reproducibility options, and upload-artifact.

Risks/test signals: push-only workflow may not protect PRs; log artifact name is static `testlog-asan.txt` despite no tests. Distro image/package drift can break builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.github/workflows/builds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.github/workflows/ci-bootc.yml -->
# sources/cloud-native/composefs/.github/workflows/ci-bootc.yml

Purpose: reverse-dependency CI that validates composefs changes against bootc install flow.

Important APIs/types/functions: workflow triggers on main push, PR, and manual dispatch; concurrency cancellation; job builds `ci/Containerfile.c9s-bootc`; runs privileged `bootc install to-filesystem --replace=alongside`.

Control flow: checkout, build local test image with podman, then run it privileged against host `/target` and container storage mounts.

State/persistence: mutates the CI runner filesystem target during bootc install, within ephemeral runner lifetime.

Dependencies/integration: GitHub Actions Ubuntu runner, podman, bootc, privileged container execution, and composefs package integration in bootc.

Risks/test signals: high-privilege CI step and host mount coupling. Provides valuable revdep signal but can be brittle on runner environment changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.github/workflows/ci-bootc.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/.github/workflows/test.yaml -->
# sources/cloud-native/composefs/.github/workflows/test.yaml

Purpose: primary CI workflow for C composefs builds, formatting, sanitizer tests, baseline builds, integration tests, distcheck, and required-check aggregation.

Important APIs/types/functions: jobs `clang-format`, `build` with ASAN/UBSAN and unit tests, `build-noasan`, `build-baseline` on Ubuntu Focal, `build-latest-clang`, `integration`, `distcheck`, and `required-checks`.

Control flow: builds install dependencies, configures Meson with `--werror` and optional sanitizers, compiles/tests, uploads artifacts/logs, runs integration tests after installing kernel modules/fsverity and extracted artifacts, then required-checks inspects `needs` JSON for failures.

State/persistence: CI artifacts, Meson logs, installed composefs tar in integration runner, and ephemeral build directories.

Dependencies/integration: GitHub Actions, Meson/Ninja, apt, erofs-utils, go-md2man, Linux modules, fsverity, jq, and repository integration scripts.

Risks/test signals: broad and valuable signal set; risks include sanitizer package names (`libasan6`) and baseline dependency allowances drifting. Required-checks sentinel allows skipped jobs but fails failed/cancelled jobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/.github/workflows/test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/composefs.pc.in -->
# sources/cloud-native/composefs/composefs.pc.in

Purpose: pkg-config template for libcomposefs consumers.

Important APIs/types/functions: variables `prefix`, `exec_prefix`, `libdir`, `includedir`; fields `Name`, `Description`, `Version`, `Requires`, `Requires.private`, `Libs`, `Libs.private`, and `Cflags`.

Control flow: Meson/configure substitutes placeholders and installs the `.pc` file for downstream builds.

State/persistence: installed metadata under pkgconfig directory.

Dependencies/integration: integrates with package builds, RPM spec, and downstream C consumers linking `-lcomposefs`.

Risks/test signals: incorrect public/private dependency placement can overlink or underlink consumers. Build/install CI validates template substitution.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/composefs.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/composefs.spec.in -->
# sources/cloud-native/composefs/composefs.spec.in

Purpose: RPM spec template for packaging composefs tools, library, and development files.

Important APIs/types/functions: package metadata, `%bcond man`, `BuildRequires`, runtime `Requires`, subpackages `devel` and `libs`, `%meson` configure with FUSE/man options, `%meson_build`, `%meson_install`, static library removal, and `%files` lists.

Control flow: RPM build expands `@VERSION@`, downloads source tarball, sets up sources, builds shared library/tools, installs, splits files into packages, and generates changelog via `%autochangelog`.

State/persistence: installed RPM package contents and dependency metadata.

Dependencies/integration: Fedora/RPM ecosystem, Meson macros, OpenSSL, fuse3, go-md2man on Go arches, and composefs release tarballs.

Risks/test signals: package file lists must track installed outputs; license expressions must match source. CI build does not necessarily exercise RPM build, so distro packaging is a separate validation lane.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/composefs.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/deny.toml -->
# sources/cloud-native/composefs/deny.toml

Purpose: cargo-deny policy for Rust dependency license/source hygiene in the composefs repository.

Important APIs/types/functions: denies unlicensed crates, allows Apache/MIT/BSD/Unicode licenses, denies unknown registries and unknown git sources, and allows no git sources.

Control flow: cargo-deny reads this to evaluate dependency graph compliance.

State/persistence: policy file only.

Dependencies/integration: cargo-deny and any Rust components in the repo.

Risks/test signals: allowlist may need updates for new transitive licenses. No bans are configured, so duplicate/vulnerable crate policy may be elsewhere or absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/deny.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/hacking/installdeps.sh -->
# sources/cloud-native/composefs/hacking/installdeps.sh

Purpose: distro-aware dependency installer for composefs development and CI builds.

Important APIs/types/functions: Fedora/RHEL path using dnf, CRB enablement for RHEL-like systems, `dnf builddep composefs`; Debian path with `DEBIAN_FRONTEND=noninteractive`, package list, and `ALLOW_MISSING` split into required vs optional packages.

Control flow: if `/usr/bin/dnf` exists, installs dnf-utils/tar/git/meson and builddeps then exits. Otherwise installs required apt packages and optionally attempts ignored-missing packages.

State/persistence: mutates host/container package database.

Dependencies/integration: CI workflows call it with sudo; build containers rely on it for Meson/C dependencies.

Risks/test signals: package names and `dnf builddep composefs` depend on distro repos. Optional package handling supports old Ubuntu Focal missing `libfsverity-dev`.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/hacking/installdeps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/bitrotate.h -->
# sources/cloud-native/composefs/libcomposefs/bitrotate.h

Purpose: vendored/gnulib-style inline helpers for rotating unsigned integer bits of multiple widths.

Important APIs/types/functions: macros `_GL_INLINE`, `_GL_ATTRIBUTE_CONST`, `BITROTATE_INLINE`; functions `rotl64`, `rotr64`, `rotl32`, `rotr32`, `rotl_sz`, `rotr_sz`, `rotl16`, `rotr16`, `rotl8`, and `rotr8`.

Control flow: pure inline arithmetic using shifts and masks; no runtime state.

State/persistence: header-only compile-time utility.

Dependencies/integration: depends on standard integer limits/types and is likely used by hashing/filter code such as EROFS xattr filters or CRC-related helpers.

Risks/test signals: callers must respect documented shift ranges for 32/64/size_t helpers to avoid undefined behavior at zero/full-width shifts. Compile coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/bitrotate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/erofs_fs.h -->
# sources/cloud-native/composefs/libcomposefs/erofs_fs.h

Purpose: canonical EROFS on-disk format definitions used by libcomposefs to create or inspect EROFS-compatible images.

Important APIs/types/functions: feature flags, `erofs_super_block`, inode layouts, chunk info, xattr headers/entries, long xattr prefixes, device slots, dirents, compression config/map structs, chunk indexes, xattr sizing helpers, `erofs_inode_is_data_compressed`, and `erofs_check_ondisk_layout_definitions`.

Control flow: mostly declarative packed/LE structs and macros. Inline helpers compute xattr ibody/entry sizes and validate compile-time struct sizes with `BUILD_BUG_ON`.

State/persistence: defines persistent disk ABI for superblocks, inodes, xattrs, directory entries, chunks, compression maps, and device tables. Any field/layout change affects image compatibility.

Dependencies/integration: included through `erofs_fs_wrapper.h`, depends on wrapper-provided Linux integer/endian macros and compile-time assertions. Used by C composefs image writer/reader code.

Risks/test signals: extremely high compatibility risk; definitions must match Linux EROFS. Compile-time layout checks catch size drift, while integration tests/fsck catch semantic drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/erofs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/erofs_fs_wrapper.h -->
# sources/cloud-native/composefs/libcomposefs/erofs_fs_wrapper.h

Purpose: userspace compatibility wrapper around Linux EROFS format definitions, providing endian helpers, alignment/bit macros, block constants, CRC32C, file type enum, and `ilog2` before including `erofs_fs.h`.

Important APIs/types/functions: `__packed`, `u8`, `cpu_to_le16/32/64`, `le16/32/64_to_cpu`, `round_up`, `round_down`, `ALIGN_TO`, `BIT`, `BUILD_BUG_ON`, `DIV_ROUND_UP`, `EROFS_BLKSIZ`, `erofs_crc32c`, EROFS file-type enum, and macro `ilog2`.

Control flow: inline endian conversion delegates to host byte-order functions; CRC32C iterates bytes/bits with the little-endian polynomial; `ilog2` is a long constant-expression ternary chain.

State/persistence: no runtime state, but constants and conversions define how persistent EROFS bytes are encoded.

Dependencies/integration: depends on `<linux/types.h>`, `<stdbool.h>`, host endian functions, and includes `erofs_fs.h`. It lets libcomposefs reuse kernel-style headers in userspace.

Risks/test signals: missing includes for endian functions must be supplied by translation units or platform headers. CRC32C implementation is simple but slow; correctness is validated indirectly by image checksums/fsck.
<!-- END_FILE_RESEARCH: sources/cloud-native/composefs/libcomposefs/erofs_fs_wrapper.h -->
