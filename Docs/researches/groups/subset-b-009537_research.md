# subset-b-009537 research

Grouped research report for subset-b-009537. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-TestVM.yaml -->
# sources/test-tools/xfstests-bld/run-fstests/roles-TestVM.yaml

- Purpose: GCE IAM custom role for individual test VMs; it declares the permissions that launched test VMs receive for metadata, disks, logging, storage, and limited Compute API interactions. The file is 185 lines/5215 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/roles-TestVM.yaml`.
- Important APIs/types/functions: YAML custom-role fields `stage`, `title`, `description`, and `includedPermissions`; permissions include compute.addresses.get, compute.addresses.list, compute.addresses.use, compute.addresses.useInternal, compute.diskTypes.get, compute.diskTypes.list, compute.disks.create, compute.disks.createSnapshot and 172 more entries.
- Control flow: declarative only; `gce-do-setup` passes it to `gcloud iam roles update --file` for the project-scoped role `forTestVM`.
- State and persistence: persists in GCP IAM, not in the repository at runtime; changes affect future launched test VMs after setup reruns.
- Dependencies/integration: consumed by setup scripts, GCE service accounts, metadata/storage/logging APIs, and Compute Engine disk/image operations used by test VMs.
- Risks and test signals: overly broad permissions increase blast radius, missing permissions break finalization/result upload; validate by rerunning setup and launching a smoke GCE test VM.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/roles-TestVM.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-copy-image -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-copy-image

- Purpose: GCE image copy helper; it copies a source Compute Engine image or image-family image into a destination project by creating a temporary disk and then an image, preserving labels and description. The file is 207 lines/4134 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-copy-image`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, DIR, SRC_FAMILY, DEST_FAMILY, SRC_IMAGE, DEST_IMAGE, TEMP_DISK, DESCRIPTION, NO_ACTION; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-copy-image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-do-setup -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-do-setup

- Purpose: one-time gce-xfstests project bootstrap; it enables required Google APIs, creates IAM custom roles and service accounts, grants storage access, validates configured bucket/project/zone/image settings, and provisions certificates/passwords. The file is 297 lines/9147 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-do-setup`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR; functions include gce_gen_cert, gce_gen_ltm_pass, SetupRole, SetupServiceAccount, SetupServiceAccountCloudBuild.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-do-setup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-export-image -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-export-image

- Purpose: GCE image export launcher; it uploads a templated startup script to GCS and starts a Debian VM that exports an image or disk into a tarball in Cloud Storage. The file is 167 lines/4113 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-export-image`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, DIR, GS_RW, GS_RO, LOG_WR, COMPUTE_RW, DATECODE, SCOPES, EXP_INST, EXP_DISK, IMG_DISK, TMP_DISK, DEB_IMAGE_FAMILY, DEB_IMAGE_PROJECT, NOACTION, GS_SCRIPT; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-export-image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-export.sh -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-export.sh

- Purpose: startup script used by image export VM; it runs inside the exporter VM, creates or attaches disks from the requested image source, optionally clears UUIDs, archives the disk, uploads it to GCS, and deletes the exporter instance. The file is 78 lines/2516 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-export.sh`.
- Important APIs/types/functions: shell variables include BUCKET, GS_TAR, GCE_ZONE, GCE_IMAGE_PROJECT, GCE_PROJECT, IMAGE_FLAG, ROOT_FS, SKIP_UUID, IMG_DISK, EXP_INST; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-export.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-import-image -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-import-image

- Purpose: GCE image import helper; it imports a tarball image from GCS into a Compute Engine image with configured family/description metadata. The file is 82 lines/1654 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-import-image`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, DIR, DESC, SRC_URI, NO_ACTION; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-import-image -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-dashboard -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-dashboard

- Purpose: Cloud Run dashboard launcher; it deploys the gce-xfstests dashboard container with configured project, bucket, and service account settings. The file is 70 lines/1339 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-dashboard`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, DASHBOARD_CONTAINER_URI; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-dashboard -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-kcs -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-kcs

- Purpose: Kernel Compile Server launcher; it creates the persistent KCS GCE VM, records its endpoint and password locally, and passes metadata that starts the server in the appliance. The file is 219 lines/5586 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-kcs`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, INSTANCE, NO_ACTION, DESCRIBE, GS_RW, LOG_WR, COMPUTE_RW, SCOPES, PREEMPTIBLE, ARG, LAUNCH_KCS_EXIT_STATUS; functions include wait_for_command.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-kcs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-ltm -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-ltm

- Purpose: Long Term Manager launcher; it creates the persistent LTM GCE VM, records its endpoint and password locally, and passes metadata that starts batch test management services. The file is 219 lines/5466 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-ltm`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, INSTANCE, NO_ACTION, GS_RW, LOG_WR, COMPUTE_RW, SCOPES, PREEMPTIBLE, ARG, LAUNCH_LTM_EXIT_STATUS; functions include wait_for_command.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-launch-ltm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-setup-cert -->
# sources/test-tools/xfstests-bld/run-fstests/util/gce-setup-cert

- Purpose: local certificate synchronizer; it fetches, renews, or regenerates the self-signed LTM/KCS certificate material stored in GCS and local cache files. The file is 85 lines/2052 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/gce-setup-cert`.
- Important APIs/types/functions: shell variables include XFSTESTS_FLAVOR, FORCE_REGEN, FORCE_RENEW, UPDATE_COMBINED, EXPIRE_DAYS, CHECKENDSECS; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/gce-setup-cert -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/kvm-do-setup -->
# sources/test-tools/xfstests-bld/run-fstests/util/kvm-do-setup

- Purpose: KVM setup checker; it verifies local dependencies and directs users to KVM configuration setup for local xfstests execution. The file is 40 lines/945 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/kvm-do-setup`.
- Important APIs/types/functions: shell variables include DIR; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/kvm-do-setup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/parse_cli -->
# sources/test-tools/xfstests-bld/run-fstests/util/parse_cli

- Purpose: shared command-line parser for xfstests frontends; it normalizes CLI options into VM/appliance metadata including filesystem configs, test sets, kernel/build parameters, storage flags, GCE/KVM tuning, and LTM/KCS requests. The file is 1448 lines/30533 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/parse_cli`.
- Important APIs/types/functions: shell variables include FSTESTCFG, SNAPSHOT, DO_AEX, API, ORIG_CMDLINE, ORIG_CMDLINE_B64, TESTRUNID, SKIP_KERNEL_ARCH_PROBE, FSTESTOPT, ARG; functions include _cleanup, supported_flavors, print_help, validate_test_name, validate_config_name, validate_commit_name, validate_branch_name, set_git_repo, get_default_repo_branch, get_default_repo_commit.
- Control flow: initializes defaults/traps, validates options with `getopt`, resolves test names/configs/repos/kernels, performs compatibility checks for GCE/KVM/LTM/KCS modes, and builds the metadata argument string consumed by VM launchers and appliance boot scripts.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/parse_cli -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifdown -->
# sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifdown

- Purpose: QEMU tap teardown hook; it brings a QEMU network interface down when a KVM guest exits. The file is 4 lines/34 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifdown`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifdown -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifup -->
# sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifup

- Purpose: QEMU tap setup hook; it configures a host-side QEMU interface and NAT forwarding through the default route interface. The file is 15 lines/514 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifup`.
- Important APIs/types/functions: shell variables include INTER_NET; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/qemu-ifup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/zerofree.c -->
# sources/test-tools/xfstests-bld/run-fstests/util/zerofree.c

- Purpose: ext filesystem free-block zeroing utility; it opens an ext2-family filesystem image/device and writes zeros to unused blocks so sparse/compressed appliance images shrink better. The file is 165 lines/3531 bytes and is researched as source path `sources/test-tools/xfstests-bld/run-fstests/util/zerofree.c`.
- Important APIs/types/functions: C program using ext2fs library calls, block bitmap iteration, file/device open/write paths, and command-line arguments for target filesystem/device handling.
- Control flow: opens the ext filesystem, walks free block metadata, writes zero-filled buffers to free blocks, reports progress/errors, and closes filesystem resources.
- State and persistence: mutates the underlying filesystem image/device by zeroing unused blocks; intended state change is data-neutral for allocated files but affects raw free-space contents and image compressibility.
- Dependencies/integration: depends on libext2fs/e2fsprogs headers and is useful during appliance image preparation before export/compression.
- Risks and test signals: unsafe on mounted or unsupported filesystems and dangerous on wrong devices; validate on disposable ext images with fsck before/after and image-size comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/run-fstests/util/zerofree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/appliance -->
# sources/test-tools/xfstests-bld/selftests/appliance

- Purpose: selftest appliance orchestration script; it builds architecture-specific appliances, optionally launches KVM/GCE smoke runs, and verifies artifacts for amd64/i386/arm64 paths. The file is 206 lines/4493 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/appliance`.
- Important APIs/types/functions: shell variables include ALL_LIST, DATECODE, LIST, SKIP_BUILD, SKIP_TEST, SKIP_ARM_QEMU_TEST, KSRC, KSRC_EXPLICIT, NO_ACTION, SKIP_GCE, SKIP_QEMU, GCE_TEST_VMS, GCE_XFSTESTS; functions include build_appliance.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/appliance -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/build-kernel -->
# sources/test-tools/xfstests-bld/selftests/build-kernel

- Purpose: selftest kernel build driver; it builds test kernels for selected architectures to validate kbuild integration used by appliance and KCS flows. The file is 81 lines/1579 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/build-kernel`.
- Important APIs/types/functions: shell variables include ALL_LIST, LIST; functions include build_kernel.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/build-kernel -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/config -->
# sources/test-tools/xfstests-bld/selftests/config

- Purpose: selftest default configuration; it sets baseline primary filesystem, kernel source path, and distribution knobs for the selftest scripts. The file is 21 lines/436 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/config`.
- Important APIs/types/functions: shell variables include PRIMARY_FSTYPE, KSRC, DISTRO; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/ltm-auto-resume -->
# sources/test-tools/xfstests-bld/selftests/ltm-auto-resume

- Purpose: LTM auto-resume selftest; it launches LTM workflows, interrupts or cancels runs, and validates that queued jobs resume and report expected results. The file is 205 lines/5147 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/ltm-auto-resume`.
- Important APIs/types/functions: shell variables include GCE_XFSTESTS, DEBUG_OUTPUT, ARCH, KERNEL_DEB, NO_RELAUNCH; functions include cleanup, cancel.
- Control flow: sources selftest helpers, launches or contacts LTM/KCS services, submits work, polls GCS/server state, and tears down or verifies artifacts according to the scenario.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/ltm-auto-resume -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/ltm-kcs -->
# sources/test-tools/xfstests-bld/selftests/ltm-kcs

- Purpose: LTM/KCS integration selftest; it starts LTM/KCS infrastructure, submits a kernel build/test request, and checks GCS/result artifacts. The file is 132 lines/2975 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/ltm-kcs`.
- Important APIs/types/functions: shell variables include NO_ACTION, GCE_XFSTESTS, DATECODE, GCE_TEST_VMS, LTM_TEST_FILE, GS_BUCKET, GS_PREFIX; functions include top-level script logic.
- Control flow: sources selftest helpers, launches or contacts LTM/KCS services, submits work, polls GCS/server state, and tears down or verifies artifacts according to the scenario.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/ltm-kcs -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/check_results.py -->
# sources/test-tools/xfstests-bld/selftests/util/check_results.py

- Purpose: selftest result checker; it parses JUnit XML and compares observed test counts, failures, skips, and errors against expected assertions. The file is 38 lines/1754 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/util/check_results.py`.
- Important APIs/types/functions: Python imports sys, argparse, junitparser, get_stats; definitions include top-level CLI logic.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/check_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/ltm -->
# sources/test-tools/xfstests-bld/selftests/util/ltm

- Purpose: selftest LTM helper library; it waits for LTM readiness, queries management state, shuts down or relaunches LTM, and detects whether it is managing tests. The file is 133 lines/2835 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/util/ltm`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include wait_ltm_online, get_ltm_info, ltm_managing_tests, shutdown_ltm, relaunch_ltm.
- Control flow: sources selftest helpers, launches or contacts LTM/KCS services, submits work, polls GCS/server state, and tears down or verifies artifacts according to the scenario.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/ltm -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/results -->
# sources/test-tools/xfstests-bld/selftests/util/results

- Purpose: selftest results helper library; it downloads, unpacks, and compares archived test results using the appliance Python result tooling. The file is 82 lines/1883 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/util/results`.
- Important APIs/types/functions: shell variables include PYTHONPATH; functions include check_debug_results, unpack_results.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/results -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/setup -->
# sources/test-tools/xfstests-bld/selftests/util/setup

- Purpose: selftest cloud/storage helper library; it wraps gcloud storage commands, debug logging, and kernel artifact lookup for selftests. The file is 75 lines/1059 bytes and is researched as source path `sources/test-tools/xfstests-bld/selftests/util/setup`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include log_debug, gcs_cp, gcs_rm, gcs_ls, gcs_cat, gcs_rsync, gcs_exists, get_gs_kernel.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/selftests/util/setup -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/setup-buildchroot -->
# sources/test-tools/xfstests-bld/setup-buildchroot

- Purpose: Debian build chroot creator; it creates native or foreign schroot environments for building xfstests tarballs and appliance images, including package selection, binfmt/QEMU validation, fstab setup, and optional tar export. The file is 879 lines/21509 bytes and is researched as source path `sources/test-tools/xfstests-bld/setup-buildchroot`.
- Important APIs/types/functions: shell variables include SCRIPTNAME, SCRIPTDIR, INTERACTIVE, DEBIAN_RELEASE, DEBIAN_RELEASE_DEFAULT, DEBIAN_PORTS_RELEASE_DEFAULT, DEBIAN_KEYRING, DEBIAN_KEYRING_DEFAULT, DEBIAN_PORTS_KEYRING_DEFAULT, DEBIAN_ARCH, DEBIAN_PORTS_ARCH_DEFAULT, DEBIAN_MIRROR, DEBIAN_MIRROR_DEFAULT, DEBIAN_PORTS_MIRROR_DEFAULT, CHROOT_NAME, CHROOT_DIR; functions include select_packages, die, log, run_cmd, usage, check_prerequisites, prompt_for_param, select_debian_release, select_debian_arch, select_debian_mirror, select_debian_keyring, add_fstab_bind, select_chroot_name, select_chroot_user, select_ccache, select_proxy, parse_options, is_native_chroot.
- Control flow: parses options or prompts, checks root/prerequisites, selects Debian release/arch/mirror/keyring, validates foreign-arch binfmt/QEMU, creates debootstrap chroot, adds schroot/fstab config, installs build dependencies, configures ccache, and optionally emits a compressed tar chroot.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/setup-buildchroot -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/android-setup-partitions -->
# sources/test-tools/xfstests-bld/test-appliance/android-setup-partitions

- Purpose: Android transient partition setup script; it shrinks userdata filesystem view and creates temporary kernel partition mappings for xfstests block devices without changing the on-disk partition table. The file is 407 lines/13075 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/android-setup-partitions`.
- Important APIs/types/functions: shell variables include RESULT_FILE, PARTITION_NAMES, PARTITION_SIZES, PARTITION_REQUIRED, BYTES_PER_GIB, START_PARTITION_NUMBER, USERDATA_SHRUNKEN_SIZE, USERDATA_RAW_DEV, DISK_DEV, USERDATA_FS_DEV, USERDATA_FS_TYPE; functions include finished, die, pprint_bytes, get_partition_number, get_partition_disk_size, get_partition_size, get_partition_start, find_userdata_partition, find_dm_device_by_name, validate_dm_device, all_partitions_present, extract_binval, get_fs_size, shrink_userdata_partition, delete_xfstests_partitions, create_xfstests_partitions.
- Control flow: detects userdata/raw/dm devices, validates encryption/device-mapper layout, shrinks userdata filesystem view, deletes stale transient partition mappings, creates required xfstests partitions starting at number 100, and writes symlinks/result status.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/android-setup-partitions -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/create-local-mirror -->
# sources/test-tools/xfstests-bld/test-appliance/create-local-mirror

- Purpose: local Debian mirror creator; it uses apt-mirror/debootstrap inputs to build a local package mirror prefix for appliance construction. The file is 25 lines/555 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/create-local-mirror`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/create-local-mirror -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/docker-entrypoint -->
# sources/test-tools/xfstests-bld/test-appliance/docker-entrypoint

- Purpose: container test appliance entrypoint; it sets local/default xfstests metadata and runs the appliance test script inside a Docker environment. The file is 12 lines/199 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/docker-entrypoint`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/docker-entrypoint -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/acpi/powerbtn-acpi-support.sh -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/acpi/powerbtn-acpi-support.sh

- Purpose: ACPI power button handler; it logs ACPI power button events and initiates shutdown behavior in the appliance. The file is 19 lines/454 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/acpi/powerbtn-acpi-support.sh`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/acpi/powerbtn-acpi-support.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/ld.so.conf.d/xfstests.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/ld.so.conf.d/xfstests.conf

- Purpose: dynamic linker path drop-in; it adds /root/xfstests/lib to ld.so search paths so bundled xfstests libraries are resolvable. The file is 2 lines/19 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/ld.so.conf.d/xfstests.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements XML or single-purpose config entries; key lines include top-level XML settings.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/ld.so.conf.d/xfstests.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/lighttpd/ltm.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/lighttpd/ltm.conf

- Purpose: lighttpd LTM web configuration; it sets the LTM web document root, CGI support, and index handling for the management UI. The file is 11 lines/303 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/lighttpd/ltm.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements XML or single-purpose config entries; key lines include server.document-root        = "/var/www", index-file.names            := ( "index.shtml", "index.html" ), mimetype.assign = (, ".htm" => "text/html",, ".html" => "text/html",, ".shtml" => "text/html",, "" => "text/plain" ), static-file.exclude-extensions += ( ".shtml" ).
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/lighttpd/ltm.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/nfs.conf.d/version2.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/nfs.conf.d/version2.conf

- Purpose: NFS daemon compatibility config; it enables UDP and NFSv2 service options for legacy xfstests coverage. The file is 4 lines/21 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/nfs.conf.d/version2.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements nfsd; key lines include udp=y, vers2=y.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/nfs.conf.d/version2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/phoronix-test-suite.xml -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/phoronix-test-suite.xml

- Purpose: Phoronix Test Suite user config; it preseeds PTS preferences and result settings used when the appliance runs phoronix workloads. The file is 85 lines/3667 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/phoronix-test-suite.xml`.
- Important APIs/types/functions: declarative configuration with sections/elements XML or single-purpose config entries; key lines include <?xml version="1.0"?>, <?xml-stylesheet type="text/xsl" href="xsl/pts-user-config-viewer.xsl"?>.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/phoronix-test-suite.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/journald.conf.d/99-gce-xfstests.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/journald.conf.d/99-gce-xfstests.conf

- Purpose: journald noise-control drop-in; it disables journal forwarding to console, wall, and kmsg on GCE test appliances. The file is 5 lines/73 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/journald.conf.d/99-gce-xfstests.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements Journal; key lines include ForwardToConsole=no, ForwardToWall=no, ForwardToKmsg=no.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/journald.conf.d/99-gce-xfstests.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/logind.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/logind.conf

- Purpose: systemd logind appliance policy; it sets login/power-key/session behavior so VM shutdown and console handling suit automated tests. The file is 35 lines/963 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/logind.conf`.
- Important APIs/types/functions: declarative configuration with sections/elements Login; key lines include HandlePowerKey=ignore.
- Control flow: read by the owning daemon/library at startup rather than executed directly; behavior changes when the appliance image installs this file into `/etc`.
- State and persistence: persists as appliance configuration under `/etc`; state is held by the consuming daemon or library.
- Dependencies/integration: integrates with lighttpd, nfsd, systemd-journald/logind, phoronix-test-suite, or ld.so depending on destination path.
- Risks and test signals: syntax errors or incompatible daemon versions can silently disable intended behavior; validate with daemon config checks, boot logs, and target workload execution.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/logind.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-fetch-gs-files.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-fetch-gs-files.service

- Purpose: systemd unit for GCS bootstrap files; it runs gce-fetch-gs-files after networking to fetch certificates/configuration before server units need them. The file is 17 lines/584 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-fetch-gs-files.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=GCE self-signed cert fetch from GCS; After=local-fs.target network-online.target network.target; After=rsyslog.service google-network-setup.service google-accounts-daemon.service; Wants=local-fs.target network-online.target network.target; Wants=google-network-setup.service google-accounts-daemon.service; Type=oneshot; ExecStart=/usr/local/lib/gce-fetch-gs-files; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gce-fetch-gs-files; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-fetch-gs-files.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize-wait.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize-wait.service

- Purpose: systemd unit for finalization wait marker; it starts a wait loop that keeps finalization coordination visible until shutdown or cleanup clears it. The file is 14 lines/228 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize-wait.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=GCE finalization waiter job; After=local-fs.target; Wants=local-fs.target; Type=oneshot; ExecStart=/usr/local/lib/gce-finalize-wait; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gce-finalize-wait; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize-wait.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.service

- Purpose: systemd finalization timeout service; it runs the timeout helper that records a timeout shutdown reason and powers off the VM. The file is 9 lines/137 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service` with directives Description=GCE finalization; Type=simple; ExecStart=/usr/local/lib/gce-finalize-timeout.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gce-finalize-timeout; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.timer -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.timer

- Purpose: systemd finalization timer; it schedules the timeout finalizer near the 24-hour VM lifetime guard. The file is 10 lines/129 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.timer`.
- Important APIs/types/functions: systemd unit sections `Unit, Timer, Install` with directives Description=GCE finalization timer; OnBootSec=23h 45m; WantedBy=timers.target.
- Control flow: systemd evaluates ordering/conditions, then runs the configured unit action; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-finalize.timer -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-kcs.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-kcs.service

- Purpose: systemd KCS server unit; it starts /usr/local/lib/bin/kcs when present so a launched appliance becomes a kernel compile server. The file is 16 lines/269 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-kcs.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=GCE KCS server; ConditionPathExists=/usr/local/lib/bin/kcs; After=network-online.target; Type=simple; WorkingDirectory=/usr/local/lib/bin; ExecStart=/usr/local/lib/bin/kcs; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/bin/kcs; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-kcs.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm-batch-watcher.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm-batch-watcher.service

- Purpose: systemd LTM batch watcher unit; it starts the batch watcher that monitors GCS batch control files for LTM. The file is 16 lines/301 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm-batch-watcher.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=ltm-batch watcherk; ConditionPathExists=/usr/local/lib/gce-ltm-batch-watcher; After=network-online.target; Type=simple; WorkingDirectory=/usr/local/lib/bin; ExecStart=/usr/local/lib/gce-ltm-batch-watcher; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gce-ltm-batch-watcher; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm-batch-watcher.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm.service

- Purpose: systemd LTM server unit; it starts /usr/local/lib/bin/ltm when present so a launched appliance becomes the long-term manager. The file is 16 lines/269 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=GCE LTM server; ConditionPathExists=/usr/local/lib/bin/ltm; After=network-online.target; Type=simple; WorkingDirectory=/usr/local/lib/bin; ExecStart=/usr/local/lib/bin/ltm; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/bin/ltm; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-ltm.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.service

- Purpose: systemd KCS repository cleanup unit; it runs periodic repository cleanup for cached KCS kernel source trees. The file is 9 lines/139 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service` with directives Description=KCS repository cleanup; Type=simple; ExecStart=/usr/local/lib/gce-repo-cleanup.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gce-repo-cleanup; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.timer -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.timer

- Purpose: systemd KCS cleanup timer; it runs repository cleanup after boot and then at recurring intervals. The file is 12 lines/180 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.timer`.
- Important APIs/types/functions: systemd unit sections `Unit, Timer, Install` with directives Description=KCS repository cleanup timer; OnBootSec=15m; WantedBy=timers.target.
- Control flow: systemd evaluates ordering/conditions, then runs the configured unit action; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gce-repo-cleanup.timer -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gen-ssh-keys.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gen-ssh-keys.service

- Purpose: systemd SSH key generation unit; it generates appliance SSH keys before multi-user services need them. The file is 14 lines/227 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gen-ssh-keys.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=Generate ssh keys for GCE; After=local-fs.target; Wants=local-fs.target; Type=oneshot; ExecStart=/usr/local/lib/gen-ssh-keys; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/gen-ssh-keys; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/gen-ssh-keys.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/kvm-xfstests.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/kvm-xfstests.service

- Purpose: systemd KVM appliance boot unit; it runs /root/kvm-xfstests.boot once local filesystems, networking, and logging are ready. The file is 17 lines/340 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/kvm-xfstests.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service, Install` with directives Description=KVM-xfstests; After=local-fs.target network-online.target network.target; After=rsyslog.service; Wants=local-fs.target network-online.target network.target; Type=oneshot; ExecStart=/root/kvm-xfstests.boot; TimeoutStartSec=0; WantedBy=multi-user.target.
- Control flow: systemd evaluates ordering/conditions, then runs /root/kvm-xfstests.boot; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/kvm-xfstests.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/stress.service -->
# sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/stress.service

- Purpose: systemd stress workload unit; it starts the configured stress workload helper as a simple service. The file is 8 lines/111 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/stress.service`.
- Important APIs/types/functions: systemd unit sections `Unit, Service` with directives Description=Stress Workload; Type=simple; ExecStart=/usr/local/lib/start-stress.
- Control flow: systemd evaluates ordering/conditions, then runs /usr/local/lib/start-stress; install targets connect it to boot or timer activation.
- State and persistence: unit state is managed by systemd; side effects come from the invoked helper scripts, marker files, timers, and service logs rather than this declarative file.
- Dependencies/integration: integrates with appliance boot, network-online/local-fs targets, GCE metadata/bootstrap files, LTM/KCS binaries, cleanup timers, or KVM one-shot startup depending on the unit.
- Risks and test signals: ordering mistakes can race network, local filesystems, or fetched certificates; validate with `systemctl status`, boot logs, and whether expected result/shutdown/server artifacts appear.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/etc/systemd/system/stress.service -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/9p/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/9p/config

- Purpose: 9p filesystem test configuration; it 9p shared filesystem config using mount-oriented operations instead of block formatting.. The file is 51 lines/653 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/9p/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", export PLAN9_MOUNT_OPTIONS="-o trans=virtio,version=9p2000.L,posixacl", export PLAN9_MOUNT_OPTIONS="$PLAN9_MOUNT_OPTIONS,$MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `9p` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/9p/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/btrfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/btrfs/config

- Purpose: btrfs filesystem test configuration; it btrfs config using btrfs check/mkfs and optional multi-device scratch pool behavior.. The file is 65 lines/925 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/btrfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mount_opts, show_mkfs_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `btrfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/btrfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/exfat/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/exfat/config

- Purpose: exfat filesystem test configuration; it exfat config using fsck.exfat/mkfs.exfat and vfat-like mount option plumbing.. The file is 65 lines/947 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/exfat/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `exfat` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/exfat/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext2/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext2/config

- Purpose: ext2 filesystem test configuration; it ext2 config using e2fsck/mke2fs defaults and ext-family aliases.. The file is 67 lines/1040 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext2/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MKFS_OPTIONS="-q $EXT_MKFS_OPTIONS", export EXT_MOUNT_OPTIONS="$EXT_MOUNT_OPTIONS,$MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `ext2` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext2/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext3/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext3/config

- Purpose: ext3 filesystem test configuration; it ext3 config using e2fsck/mke2fs with journaling-compatible ext-family settings.. The file is 65 lines/954 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext3/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export EXT_MOUNT_OPTIONS="$EXT_MOUNT_OPTIONS,$MNTOPTS", export EXT_MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `ext3` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext3/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/config

- Purpose: ext4 filesystem test configuration; it ext4 config using e2fsck/mke2fs, config aliases, and mkfs option handling including feature variants.. The file is 98 lines/2099 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="-b 4096", export MKE2FS_CONFIG="$MKFS_CONFIG_FILE", local dev="$1", logdev_opt="-j $TEST_LOGDEV", ret="$?", local dev="$1", local opts="$2", logdev_opt="-O journal_dev $TEST_LOGDEV".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `ext4` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/mkfs_cfg/prod-dc.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/mkfs_cfg/prod-dc.conf

- Purpose: ext4 mkfs profile prod-dc.conf; it defines named mkfs defaults consumed by the ext4 config when runtests.sh is invoked with mkfs_config=prod-dc. The file is 13 lines/305 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/mkfs_cfg/prod-dc.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `defaults, fs_types` with options blocksize = 4096, inode_size = 128, inode_ratio = 20480, reserved_ratio = 1.0, lazy_itable_init = false, ext4 = {, features = ^ext_attr,^resize_inode,^has_journal,extents,huge_file,flex_bg,uninit_bg,dir_nlink,sparse_super, hash_alg = half_md4.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/mkfs_cfg/prod-dc.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/f2fs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/f2fs/config

- Purpose: f2fs filesystem test configuration; it f2fs config using fsck.f2fs/mkfs.f2fs plus required mount and feature handling.. The file is 76 lines/1459 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/f2fs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", opts+=" -f", F2FS_MOUNT_OPTIONS+="${F2FS_MOUNT_OPTIONS:+,}$MNTOPTS", local mode='\x00\x00\x00\x00'.
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `f2fs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/f2fs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/hfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/hfs/config

- Purpose: hfs filesystem test configuration; it hfs config using fsck.hfs/mkfs.hfs and block-device test wiring.. The file is 65 lines/931 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/hfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `hfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/hfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/jfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/jfs/config

- Purpose: jfs filesystem test configuration; it jfs config using fsck.jfs/mkfs.jfs with standard xfstests variable reset hooks.. The file is 65 lines/935 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/jfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `jfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/jfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/local/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/local/config

- Purpose: local filesystem test configuration; it local pseudo-filesystem config that points tests at local directories without destructive block formatting.. The file is 47 lines/379 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/local/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `local` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/local/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/msdos/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/msdos/config

- Purpose: msdos filesystem test configuration; it msdos FAT config using dosfsck/mkfs.msdos and FAT mount option reporting.. The file is 65 lines/947 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/msdos/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `msdos` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/msdos/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/nfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/nfs/config

- Purpose: nfs filesystem test configuration; it NFS config that provisions server/export backed testing and wraps fsck/mkfs as no-op or backing-device operations.. The file is 115 lines/1809 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/nfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks __fsck, check_filesystem, __mkfs, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", local dev="$1", mkfs.xfs -f -m rmapbt=1,reflink=1 "$dev", export NFS_MOUNT_OPTIONS="-o rw,relatime", export NFS_MOUNT_OPTIONS="NFS_MOUNT_OPTIONS,$MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `nfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/nfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs/config

- Purpose: ntfs filesystem test configuration; it NTFS config using ntfsfix/mkntfs style tooling for legacy ntfs coverage.. The file is 65 lines/960 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export NTFS_MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export NTFS_MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `ntfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs3/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs3/config

- Purpose: ntfs3 filesystem test configuration; it ntfs3 kernel driver config using NTFS mkfs/check tooling but mounting as ntfs3.. The file is 65 lines/970 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs3/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export NTFS3_MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export NTFS3_MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `ntfs3` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ntfs3/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/overlay/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/overlay/config

- Purpose: overlay filesystem test configuration; it overlayfs config that composes upper/lower/work directories over a backing filesystem and customizes check/format delegation.. The file is 140 lines/2369 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/overlay/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks __fsck, __check_filesystem, check_filesystem, __mkfs, __format_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", local tst_dev="$1", local tst_mnt="$2", local scr_dev="$3", local scr_mnt="$4", ret="$?", ret2="$?".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `overlay` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/overlay/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/reiserfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/reiserfs/config

- Purpose: reiserfs filesystem test configuration; it reiserfs config using reiserfsck/mkreiserfs tooling and standard config hooks.. The file is 65 lines/1020 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/reiserfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export REISERFS_MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export REISERFS_MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `reiserfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/reiserfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/tmpfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/tmpfs/config

- Purpose: tmpfs filesystem test configuration; it tmpfs config that mounts memory-backed test/scratch directories and avoids block-device formatting.. The file is 53 lines/653 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/tmpfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", export TMPFS_MOUNT_OPTIONS="$TMPFS_MOUNT_OPTIONS,$MNTOPTS", export TMPFS_MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `tmpfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/tmpfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ubifs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ubifs/config

- Purpose: ubifs filesystem test configuration; it UBIFS config that allocates MTD/UBI devices, creates volumes, formats with mkfs.ubifs, and maps block devices to UBI volumes.. The file is 181 lines/4332 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ubifs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, __mtd_find, __mtd_find_or_create, __ubi_find, __ubi_find_or_create, __blkdev_to_ubi_volume, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local blkdev=$1 mtd_dir, local blkdev=$1 mtd, echo 1>&2 "Error: CONFIG_MTD_BLOCK2MTD=y is required to emulate flash device for ubifs!", mtd=$(__mtd_find $blkdev), mtd=$(__mtd_find $blkdev), local mtd_num="${1#/dev/mtd}" ubi_dir, local mtd="$1" ubi.
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `ubifs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ubifs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/udf/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/udf/config

- Purpose: udf filesystem test configuration; it UDF config using fsck/mkudffs tooling for optical-style filesystem coverage.. The file is 63 lines/998 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/udf/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS", export DISABLE_UDF_TEST=1.
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `udf` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/udf/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/vfat/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/vfat/config

- Purpose: vfat filesystem test configuration; it vfat config using dosfsck/mkfs.vfat and FAT mount option reporting.. The file is 65 lines/939 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/vfat/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="", local dev="$1", ret="$?", local dev="$1", local opts="$2", ret="$?", export MOUNT_OPTIONS="$MOUNT_OPTIONS,$MNTOPTS", export MOUNT_OPTIONS="-o $MNTOPTS".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `vfat` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/vfat/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/virtiofs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/virtiofs/config

- Purpose: virtiofs filesystem test configuration; it virtiofs shared filesystem config using mount-only behavior against virtiofs exports.. The file is 46 lines/396 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/virtiofs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mkfs_opts, show_mount_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `virtiofs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/virtiofs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/config -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/config

- Purpose: xfs filesystem test configuration; it XFS config using xfs_repair/mkfs.xfs, optional LTS mkfs profiles, and combine-xfs-mkfs-opts to avoid duplicate option failures.. The file is 111 lines/2227 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/config`.
- Important APIs/types/functions: sourced shell config exports `DEFAULT_MKFS_OPTIONS` and implements hooks check_filesystem, xfs_adjust_mkfs_opts, format_filesystem, setup_mount_opts, get_mkfs_opts, show_mount_opts, show_mkfs_opts, test_name_alias, reset_vars; assignments include DEFAULT_MKFS_OPTIONS="-bsize=4096", local dev="$1", logdev_opt="-l $TEST_LOGDEV", rt_opt="-r $TEST_RTDEV", ret="$?", export XFS_MKFS_OPTIONS=$(xfs_combine_output_opts), adjust_mkfs_options=xfs_adjust_mkfs_opts, local dev="$1".
- Control flow: `runtests.sh` sources this via `get_fs_config`, calls `reset_vars`, derives aliases with `test_name_alias`, formats/checks devices through `format_filesystem`/`check_filesystem`, and records mkfs/mount options for each `xfs` test config.
- State and persistence: changes mounted test/scratch filesystems, loop/UBI/export directories where applicable, and per-config result metadata; variables are reset between configs to avoid cross-test leakage.
- Dependencies/integration: integrates with `/root/runtests.sh`, xfstests `local.config`, mkfs/fsck/mount tools for the target filesystem, exclude/config lists, and optional GCE/KVM device inventories.
- Risks and test signals: wrong mkfs/check commands can destroy the wrong device or skip valid tests; validate with smoke config selection, generated config files, fsck output, and xUnit result creation for this filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/config -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_4.19.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_4.19.conf

- Purpose: xfs mkfs profile lts_4.19.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_4.19. The file is 20 lines/255 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_4.19.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=0, crc=1, finobt=1, inobtcount=0, reflink=0, rmapbt=0, autofsck=0, sparse=1, nrext64=0, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_4.19.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.10.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.10.conf

- Purpose: xfs mkfs profile lts_5.10.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_5.10. The file is 20 lines/255 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.10.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=0, crc=1, finobt=1, inobtcount=0, reflink=1, rmapbt=0, autofsck=0, sparse=1, nrext64=0, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.10.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.15.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.15.conf

- Purpose: xfs mkfs profile lts_5.15.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_5.15. The file is 20 lines/255 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.15.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=1, crc=1, finobt=1, inobtcount=1, reflink=1, rmapbt=0, autofsck=0, sparse=1, nrext64=0, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.15.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.4.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.4.conf

- Purpose: xfs mkfs profile lts_5.4.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_5.4. The file is 20 lines/254 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.4.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=0, crc=1, finobt=1, inobtcount=0, reflink=1, rmapbt=0, autofsck=0, sparse=1, nrext64=0, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_5.4.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.1.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.1.conf

- Purpose: xfs mkfs profile lts_6.1.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_6.1. The file is 20 lines/254 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.1.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=1, crc=1, finobt=1, inobtcount=1, reflink=1, rmapbt=0, autofsck=0, sparse=1, nrext64=0, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.12.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.12.conf

- Purpose: xfs mkfs profile lts_6.12.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_6.12. The file is 20 lines/255 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.12.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=1, crc=1, finobt=1, inobtcount=1, reflink=1, rmapbt=1, autofsck=0, sparse=1, nrext64=1, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.12.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.6.conf -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.6.conf

- Purpose: xfs mkfs profile lts_6.6.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_6.6. The file is 20 lines/254 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.6.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=1, crc=1, finobt=1, inobtcount=1, reflink=1, rmapbt=1, autofsck=0, sparse=1, nrext64=1, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_6.6.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/runblktests.sh -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/runblktests.sh

- Purpose: blktests appliance runner; it sets up appliance context, runs blktests suites with repeat support, and writes result/exit status artifacts. The file is 87 lines/1502 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/runblktests.sh`.
- Important APIs/types/functions: shell variables include API_MAJOR, API_MINOR, RPT_COUNT; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/runblktests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/runltptests.sh -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/runltptests.sh

- Purpose: LTP appliance runner; it sets up appliance context, runs Linux Test Project workloads, and writes summary/result artifacts. The file is 89 lines/1392 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/runltptests.sh`.
- Important APIs/types/functions: shell variables include API_MAJOR, API_MINOR, RESULTS, RUNSTATS, RPT_COUNT; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/runltptests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/runtests.sh -->
# sources/test-tools/xfstests-bld/test-appliance/files/root/runtests.sh

- Purpose: main xfstests appliance runner; it consumes /root/test-config metadata, resolves filesystem configs/devices, formats and checks filesystems, runs xfstests check loops, merges xUnit results, truncates bulky logs, and writes exit status. The file is 582 lines/16186 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/runtests.sh`.
- Important APIs/types/functions: shell variables include API_MAJOR, API_MINOR, RPT_COUNT, FAIL_LOOP_COUNT, NO_TRUNCATE, NEW_COUNT; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/root/runtests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/cgi-bin/print_proc -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/cgi-bin/print_proc

- Purpose: CGI proc-file printer; it maps the script basename to /proc/<name> and prints it for dashboard diagnostics. The file is 11 lines/112 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/cgi-bin/print_proc`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/cgi-bin/print_proc -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/diff_stats.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/diff_stats.py

- Purpose: JUnit statistics differ; it compares two JUnit result sets and reports changed failures/errors/skips for selftests and result analysis. The file is 106 lines/4208 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/diff_stats.py`.
- Important APIs/types/functions: Python imports argparse, sys, gen_results_summary, xml.etree.ElementTree, junitparser; definitions include def diff_stats, def read_stats, def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/diff_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/gen_results_summary.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/gen_results_summary.py

- Purpose: results summary library; it walks results.xml files, aggregates JUnit statistics, handles LTM ordering/properties, writes human summaries, and optionally merges xUnit XML. The file is 434 lines/13866 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/gen_results_summary.py`.
- Important APIs/types/functions: Python imports copy, os, sys, time, datetime, junitparser; definitions include class TestStats, class wrapped_print, def get_results, def parse_timestamp, def failed_tests, def get_property, def get_properties, def remove_properties, def print_tests, def total_tests, def sum_testsuites, def get_testsuite_stats, def testsuite_failed, def print_summary, def print_property_line, def print_properties, def print_header, def print_trailer.
- Control flow: walks result trees for `results.xml`, loads JUnit XML, adjusts LTM properties/order when `ltm-run-stats` exists, prints per-suite summaries, optionally marks hard failures and writes merged XML atomically via `.new`/rename.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/gen_results_summary.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/get_stats.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/get_stats.py

- Purpose: JUnit statistics extractor; it reads result directories and emits compact stats used by diff/merge/check helper scripts. The file is 69 lines/2317 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/get_stats.py`.
- Important APIs/types/functions: Python imports argparse, sys, gen_results_summary, junitparser; definitions include def get_stats_from_dir, def write_stats, def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/get_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__init__.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__init__.py

- Purpose: junitparser package export module; it re-exports the local JUnit XML classes and helpers for appliance result scripts. The file is 19 lines/240 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__init__.py`.
- Important APIs/types/functions: Python imports .junitparser; definitions include top-level CLI logic.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__main__.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__main__.py

- Purpose: junitparser module entrypoint; it dispatches python -m junitparser to the CLI main function. The file is 6 lines/73 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__main__.py`.
- Important APIs/types/functions: Python imports sys, .cli; definitions include top-level CLI logic.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/__main__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/cli.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/cli.py

- Purpose: junitparser command-line interface; it implements merge-oriented CLI handling over globbed JUnit XML input files. The file is 58 lines/1595 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/cli.py`.
- Important APIs/types/functions: Python imports argparse, glob, itertools, .; definitions include def merge, def _parser, def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/junitparser.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/junitparser.py

- Purpose: vendored JUnit/xUnit XML object model; it defines Element, JUnitXml, TestSuite, TestCase, result nodes, attributes, parsing, merging, and statistics update behavior. The file is 753 lines/21094 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/junitparser.py`.
- Important APIs/types/functions: Python imports copy, builtins, io, locale; definitions include def write_xml, class JUnitXmlError, class Attr, class IntAttr, class FloatAttr, def attributed, class junitxml, class Element, class JUnitXml, class TestSuite, class Properties, class Property, class Result, class Skipped, class Failure, class Error, class TestCase, class System.
- Control flow: XML is parsed into wrapper objects (`JUnitXml`, `TestSuite`, `TestCase`, `Property`, result nodes); merge/add operations append suites or cases and `update_statistics()` recomputes tests, failures, errors, skipped, and runtime before writing XML.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/junitparser/junitparser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/merge_stats.py -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/merge_stats.py

- Purpose: JUnit stats merger; it combines baseline/current stats XML so result comparison state can be carried forward. The file is 46 lines/1488 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/merge_stats.py`.
- Important APIs/types/functions: Python imports argparse, sys, xml.etree.ElementTree, get_stats, diff_stats, gen_results_summary, junitparser; definitions include def merge_stats, def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/lib/python3/dist-packages/merge_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/add_error_xunit -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/add_error_xunit

- Purpose: xUnit error injector; it adds an error testcase to an existing or new JUnit suite to represent infrastructure failures. The file is 49 lines/1264 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/add_error_xunit`.
- Important APIs/types/functions: Python imports argparse, os, sys, junitparser; definitions include def get_test_suite.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/add_error_xunit -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/combine_xunit -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/combine_xunit

- Purpose: xUnit combiner; it loads multiple JUnit XML files and writes a combined testsuites document. The file is 28 lines/830 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/combine_xunit`.
- Important APIs/types/functions: Python imports junitparser, argparse; definitions include def combine_xunit.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/combine_xunit -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/gen_results_summary -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/gen_results_summary

- Purpose: CLI wrapper for summary generation; it parses command-line options and calls gen_results_summary.gen_results_summary. The file is 35 lines/1349 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/gen_results_summary`.
- Important APIs/types/functions: Python imports argparse, sys, gen_results_summary; definitions include def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/gen_results_summary -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/get_error_count -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/get_error_count

- Purpose: xUnit error counter; it returns aggregate error/failure counts from a JUnit XML document for runner exit decisions. The file is 26 lines/594 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/get_error_count`.
- Important APIs/types/functions: Python imports argparse, os, sys, junitparser; definitions include def get_test_suite.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/get_error_count -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/merge_xunit -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/merge_xunit

- Purpose: xUnit merge utility; it merges one JUnit XML file into another while preserving suite/test statistics. The file is 33 lines/865 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/merge_xunit`.
- Important APIs/types/functions: Python imports argparse, os, sys, junitparser; definitions include def get_test_suite.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/merge_xunit -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/results_no_reboots -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/results_no_reboots

- Purpose: result reboot detector; it reports whether result summaries indicate VM reboots/preemptions or other restart signals. The file is 20 lines/391 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/results_no_reboots`.
- Important APIs/types/functions: Python imports argparse, sys, gen_results_summary; definitions include def main.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/results_no_reboots -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/run-syz -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/run-syz

- Purpose: syzkaller repro runner; it runs syzkaller repro tests under the xfstests syz harness inside the appliance. The file is 75 lines/1174 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/run-syz`.
- Important APIs/types/functions: shell variables include DIR; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/run-syz -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/truncate-test-files -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/truncate-test-files

- Purpose: result artifact trimmer; it truncates large .full and .fsxlog files for passing tests while preserving failure evidence. The file is 56 lines/1073 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/truncate-test-files`.
- Important APIs/types/functions: shell variables include DIR; functions include top-level script logic.
- Control flow: sources appliance config/utilities, prepares result directories and runner options, invokes the target test harness, copies/merges xUnit output, summarizes results, and writes `/tmp/retdir/exit_code`.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/truncate-test-files -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/update_properties_xunit -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/update_properties_xunit

- Purpose: xUnit property updater; it adds, replaces, or removes JUnit suite properties used by result metadata pipelines. The file is 47 lines/1129 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/update_properties_xunit`.
- Important APIs/types/functions: Python imports argparse, os, sys, junitparser; definitions include def get_test_suite, def clean_test_suite.
- Control flow: parses CLI arguments, loads one or more JUnit XML/stat files through the local `junitparser`/summary modules, mutates or compares suite data, then writes XML/text output and exits with status useful to shell runners.
- State and persistence: reads and writes result XML/stat/report files; no daemon state, but output files are consumed by `runtests.sh`, selftests, and result publication.
- Dependencies/integration: depends on the vendored `junitparser` package plus standard Python modules; wrappers under `/usr/local/bin` are called by test runners and selftest helpers.
- Risks and test signals: malformed XML, missing properties, duplicate suite identity, or locale-sensitive float parsing can skew counts; test with representative passing/failing/skipped/preempted xUnit samples and CLI exit status checks.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/bin/update_properties_xunit -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/combine-xfs-mkfs-opts -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/combine-xfs-mkfs-opts

- Purpose: XFS mkfs option combiner library; it parses xfsprogs sectioned mkfs options/config files and emits a de-duplicated command line. The file is 141 lines/2750 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/combine-xfs-mkfs-opts`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include xfs_combine_reset, xfs_combine_sect_map, xfs_combine_keys, xfs_combine_opt_string, xfs_combine_config_file, xfs_combine_output_opts.
- Control flow: executes top-level shell logic in order, using environment variables/positional arguments to select external commands and produce appliance/cloud side effects.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/combine-xfs-mkfs-opts -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-add-metadata -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-add-metadata

- Purpose: GCE metadata xattr helper; it adds GCE metadata to result artifacts using xattrs under a lock when metadata is available. The file is 11 lines/231 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-add-metadata`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-add-metadata -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-build-upload-kernel -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-build-upload-kernel

- Purpose: KCS kernel build/upload worker; it checks out requested repo/commit, builds or installs kconfig, packages kernel/modules, and uploads artifacts to GCS. The file is 90 lines/2394 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-build-upload-kernel`.
- Important APIs/types/functions: shell variables include KBUILD_OPTS, KERNEL_PATH, DPKG_FLAGS; functions include install_kconfig.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-build-upload-kernel -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-delete-scratch-disk -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-delete-scratch-disk

- Purpose: GCE scratch disk cleanup helper; it uses metadata/test config to delete attached scratch disks after tests finish. The file is 11 lines/310 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-delete-scratch-disk`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-delete-scratch-disk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-fetch-gs-files -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-fetch-gs-files

- Purpose: GCS bootstrap fetcher; it downloads certificates, config, and optional files from the configured bucket into appliance locations. The file is 44 lines/1815 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-fetch-gs-files`.
- Important APIs/types/functions: shell variables include DIR; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-fetch-gs-files -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize

- Purpose: GCE finalization trigger; it stops the wait loop and launches final shutdown/finalize handling. The file is 11 lines/197 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-timeout -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-timeout

- Purpose: GCE timeout finalizer; it records timeout as shutdown reason and initiates shutdown when the VM lifetime timer expires. The file is 6 lines/89 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-timeout`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-timeout -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-wait -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-wait

- Purpose: GCE finalization wait loop; it creates /run/gce-finalize-wait and sleeps until finalization clears it. The file is 10 lines/133 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-wait`.
- Important APIs/types/functions: shell variables include mostly positional/environment inputs; functions include top-level script logic.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-finalize-wait -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-funcs -->
# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-funcs

- Purpose: GCE appliance helper library; it retrieves metadata with retries, persists zone/id/instance/bucket state, runs hook directories, and wraps gcloud storage operations. The file is 200 lines/4458 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-funcs`.
- Important APIs/types/functions: shell variables include GCE_STATE_DIR, GCE_CONFIG_FILE, REGION; functions include print_metadata_value, print_metadata_value_if_exists, get_metadata_value, get_metadata_value_with_retries, gce_attribute, run_hooks, gcs_cp, gcs_rm, gcs_ls, gcs_cat, gcs_rsync, gcs_exists.
- Control flow: loads `util/get-config` or `/usr/local/lib/gce-funcs`, validates required GCE/GCS inputs, composes gcloud/gcloud-storage commands or metadata, performs the cloud action, and records local marker/state files when a long-running service is launched.
- State and persistence: uses local marker files, GCS objects, result directories, generated configs, temporary disks/images, schroot entries, or mounted filesystems depending on the helper; cleanup is generally explicit and failure paths may leave debug artifacts.
- Dependencies/integration: integrates with xfstests-bld frontends, `get-config`, `arch-funcs`, `/root/runtests_utils`, gcloud/gcloud storage, systemd services, Debian tooling, QEMU/KVM, and filesystem utilities as applicable.
- Risks and test signals: most failures come from missing credentials/tools, stale cloud resources, command-line validation gaps, destructive device operations, or partial cleanup; validate with `--no-action` where available, smoke selftests, GCS artifact checks, systemd logs, and generated xUnit summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-funcs -->
