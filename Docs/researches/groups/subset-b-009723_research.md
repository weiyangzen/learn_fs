# Research: subset-b-009723

Grouped research for NFS-Ganesha container/build scripts, mountpoint smoke tests, and support-library sources. Each source file has its own marker-delimited section so the reconciliation lane can split this report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/ganesha-container -->
# sources/user-network-fs/nfs-ganesha/src/scripts/podman/ganesha-container

## Purpose
This POSIX-shell helper builds and runs Podman containers with NFS-Ganesha build dependencies for supported Linux distributions. It is intended for developers who want a repeatable build/test environment across distro versions, with special modes for listing supported versions, building/running every supported container, and deleting all generated images.

## Important APIs, Types, and Functions
The script's public interface is `ganesha-container {distro [version] | all | delete-all | list} [[--] cmd...]`. `list_versions` emits the supported matrix. `default_version` selects the current default for each distro family. `validate_distro_version` rejects unsupported pairs. `container_image` maps distro/version pairs to upstream image names, including CentOS Stream and SLE registry naming. `container_1` builds the local image tag, removes stale stopped containers, detects SELinux enforcing mode for bind-mount relabeling, and runs the container. `container_foreach` loops over the version matrix for `all` and `delete-all`.

## Control Flow
Argument parsing chooses a distro, optional version, and optional command. If a non-special distro is used without a version, `default_version` fills it in; a `--` separator is consumed before the command. `container_1` changes into the script directory so `buildah bud` can use the local `Containerfile`, creates an image tag like `ubuntu:24.04.ganesha`, then starts a one-shot `podman container run` with `--rm`, `--userns=keep-id`, a bind mount of the caller's original working directory, and an interactive login shell when no command is supplied.

## State and Persistence Behavior
Persistent state is held in local Podman/Buildah images named `<distro>:<version>.ganesha`; running containers are named `<distro><version>.ganesha` and are removed automatically. The caller's working tree is bind-mounted in place, so commands inside the container can modify repository files. `delete-all` removes generated images but does not touch source files.

## Dependencies and Integration Points
The script depends on `/bin/sh`, `podman`, `buildah`, `realpath`, `id`, `tty`, and optional `sestatus`. It integrates with `scripts/podman/Containerfile` and `install-packages.sh` through build arguments for base image and user/group ids. It is a developer-facing bridge between the NFS-Ganesha tree and distro package ecosystems.

## Risks and Test Signals
Risks include distro matrix drift, missing credentials for SLE registry access, stale running containers blocking reuse, SELinux relabeling only being enabled when `sestatus` reports enforcing, and bind-mounting the whole workdir at the same path inside the container. The `podman container inspect` assignment redirects command output, so the `running` variable receives no formatted value; that path can fail to detect the running state as intended. Test signals include `list`, default-version runs, explicit-version runs, `all true`, `delete-all`, non-TTY command execution, TTY shell launch, and SELinux enforcing/non-enforcing hosts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/ganesha-container -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/install-packages.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/podman/install-packages.sh

## Purpose
This shell script installs NFS-Ganesha build dependencies inside supported container base images. It is used by the Podman `Containerfile` rather than by normal runtime deployments, and it encodes per-family package-manager logic for Debian/Ubuntu, Red Hat-family images, Fedora, and SUSE/SLE.

## Important APIs, Types, and Functions
The script is function-oriented: `install_debian`, `install_rh`, and `install_suse` perform package installation for their release families. After sourcing `/etc/os-release`, a `case` maps `ID` to a `family` name and invokes `"install_${family}"`. Package-variable knobs include `libnsl_pkg`, `python3_distutils`, `python_pkg`, and `extra_repos`, which account for distro-version differences.

## Control Flow
For Debian-family systems the script sets `DEBIAN_FRONTEND=noninteractive`, runs `apt-get update`, suppresses `libnsl-dev` on older Debian/Ubuntu variants, suppresses `python3-distutils` on Ubuntu 24.04, then installs compilers, CMake, Doxygen, ACL/cap/dbus/krb5/jemalloc/urcu development packages, Python, Qt tools, rsync, sudo, and UUID headers. For Red Hat-family systems it patches CentOS 8 mirror URLs, installs EPEL except on Fedora, enables `powertools`, `crb`, or `devel` repositories as needed, and installs development tools plus equivalent libraries. SUSE installs the `devel_basis` pattern and explicit development packages via `zypper`.

## State and Persistence Behavior
The script mutates the container image filesystem by installing packages and may edit `/etc/yum.repos.d/CentOS-*` for CentOS 8. It does not persist repository state outside the container build context. Package-manager caches and enabled repositories become part of the resulting image layer.

## Dependencies and Integration Points
It depends on the package managers and release metadata available in the base image: `apt-get`, `yum`/DNF compatibility tools, or `zypper`, plus `/etc/os-release`. It is tightly coupled to `ganesha-container`, which constrains the distro versions before building. The installed dependency set feeds CMake builds, documentation generation, Qt-based tooling, and sanitizer-linked builds.

## Risks and Test Signals
Risks include package name drift, missing repositories in minimal images, CentOS 8 vault assumptions becoming stale, Fedora packages diverging from RHEL names, SLE library version changes such as `libasan4`, and intentionally empty package variables relying on unquoted expansion. Test signals are successful container builds for every supported distro/version, CMake configure success inside each image, and smoke builds using DBus, Kerberos, jemalloc, ACL, UUID, and URCU headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/install-packages.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/pycheckpatch -->
# sources/user-network-fs/nfs-ganesha/src/scripts/pycheckpatch

## Purpose
`pycheckpatch` runs the repository's Linux-style `checkpatch.pl` against one or more Git commits. It accepts normal `git rev-list` arguments and optionally checks all commits with `-a`; without `-a`, it stops at the first failing commit.

## Important APIs, Types, and Functions
The script has no reusable functions beyond a local Python 2.6-compatible `subprocess.check_output` shim. Important variables are `checkpatch = "./src/scripts/checkpatch.pl"`, `rev_list_args`, `check_all`, and `result`, a list of `(commit, passed, output)` tuples. External command APIs are `git rev-parse --show-toplevel`, `git rev-list --no-merges`, and `git show <commit> --format=email | checkpatch.pl -`.

## Control Flow
The script validates that at least one revision argument is present, removes `-a` if supplied, changes to the Git top-level directory, expands commits with `git rev-list --no-merges`, and exits if the range is empty. It then streams each commit as email-format patch text into `checkpatch.pl`. Failures are recorded; if the failure is the known missing `.checkpatch.conf` message, the script exits with setup guidance. Otherwise it breaks after the first failure unless `-a` was requested, then prints an aggregate pass/fail summary.

## State and Persistence Behavior
The only state is in memory and process current working directory. It reads Git history and checkpatch configuration but writes no files. Exit status is zero only if every checked commit passed.

## Dependencies and Integration Points
It depends on Python, Git, `src/scripts/checkpatch.pl`, and the repository's `.checkpatch.conf` setup. It is part of developer and CI review tooling, complementing `runcp.sh`, Gerrit checkpatch scripts, and pre-commit hooks.

## Risks and Test Signals
Risks include Python 2/3 byte-string mismatches because `subprocess.check_output` returns bytes on Python 3 while string comparisons use text, shell injection if commit identifiers were untrusted, assumptions about running from a checked-out repository, and no handling for merge commits by design. Test signals include empty ranges, a known-good single commit, a failing commit with and without `-a`, missing `.checkpatch.conf`, and execution under both Python 2-compatible and Python 3 interpreters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/pycheckpatch -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/reindenture -->
# sources/user-network-fs/nfs-ganesha/src/scripts/reindenture

## Purpose
`reindenture` bulk-formats C and header files under one or more directories using GNU `indent` with the project's historical formatting options. It is a developer maintenance tool rather than part of the build.

## Important APIs, Types, and Functions
The script exposes a command-line interface `reindenture dir1 [dir2 ... dirn]`. It has no shell functions. For each directory argument it runs `find <dir> -type f \( -name *.c -o -name *.h \) -print0 | xargs -0 indent ...` with a fixed option set, while `VERSION_CONTROL=simple` asks `indent` to keep simple backup files.

## Control Flow
If no arguments are provided, the script prints usage and exits nonzero. Otherwise it loops over each directory, prints a progress line, finds C/header files recursively, and pipes them to `indent`. Each directory is processed independently.

## State and Persistence Behavior
This script rewrites source files in place and may create backup files according to `indent`'s `VERSION_CONTROL=simple` behavior. It has no rollback logic and no file exclusion list.

## Dependencies and Integration Points
It depends on `/bin/sh`, `find`, `xargs`, and GNU `indent`. It integrates with the C codebase only as an external formatting pass; it is separate from checkpatch enforcement and CMake.

## Risks and Test Signals
Risks are broad formatting churn, accidental processing of vendored or generated C files, portability issues with unquoted directory names, and compatibility with non-GNU `indent` implementations. Because it uses `find $dir` unquoted, paths containing whitespace can be misparsed. Test signals are dry-run review through Git diff after running on a small directory, backup creation behavior, handling of empty directories, and shellcheck-style validation for argument quoting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/reindenture -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/runcp.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/runcp.sh

## Purpose
`runcp.sh` is a wrapper around `checkpatch.pl` for checking source files or Git diffs and collecting reports under an output directory. It encodes NFS-Ganesha-specific exclusions and per-file ignored checkpatch classes for generated, external, or historically nonconforming code.

## Important APIs, Types, and Functions
The main functions are `check_one_file`, `check_files`, `check_find`, `check_git_files`, `check_git`, and `show_help`. CLI options control clean-file reporting (`-c`), warning suppression (`-w`), quiet mode (`-q`), per-file reports (`-1`), target directory (`-d`), exclusions (`-x`), inclusion of normally ignored/generated/external files (`-i`, `-e`), Git diff mode (`-g`, `-k`), output directory (`-o`), final report printing (`-r`), typedef ignoring (`-t`), special ignore disabling (`-v`), and cruft filtering (`-K`).

## Control Flow
The script initializes defaults, parses options with `getopts`, normalizes `DIR`, creates the output directory, and initializes `results.cp`, `results.temp`, and `results.err`. It builds an exclusion expression from always-excluded files, generated/config parsing files, and external code unless overridden. `check_find` scans `*.[ch]` files; `check_git` scans `git diff --name-only <commit>`. `check_one_file` decides report paths, applies special `--ignore` switches by matching the file path against configured regexes, runs `checkpatch.pl --file`, and appends interesting output to the aggregate report.

## State and Persistence Behavior
The script writes persistent report files under `ODIR` (default `/tmp/checkpatch`), including `results.cp`, temporary/error files, and optionally one `.cp` file per source. It reads the source tree and Git diff but does not modify source files.

## Dependencies and Integration Points
It depends on `/bin/sh`, `readlink`, `sed`, `egrep`, `grep`, `find`, `sort`, `git`, and `src/scripts/checkpatch.pl`. It integrates with NFS-Ganesha's generated XDR/RPC headers, external libraries, and project-specific checkpatch exceptions.

## Risks and Test Signals
The implementation uses many unquoted variables and legacy backticks, so paths with whitespace or regex metacharacters can misbehave. Several shell constructs assume a forgiving shell; `return` is used at top level in error paths. The exclusion and ignore regexes can mask real style regressions if they become too broad. Test signals include `-g` against a small diff, `-1` per-file output, `-c` and `-w` filters, `-i`/`-e` inclusion toggles, invalid output directory handling, and a file that matches each special ignore class.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/runcp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/systemd/nfs-ganesha-config.service-in.cmake -->
# sources/user-network-fs/nfs-ganesha/src/scripts/systemd/nfs-ganesha-config.service-in.cmake

## Purpose
This CMake-templated systemd unit defines a oneshot service for processing NFS-Ganesha configuration before or during service startup.

## Important APIs, Types, and Functions
The unit has `[Unit]` metadata with `Description=Process NFS-Ganesha configuration` and `DefaultDependencies=no`. The `[Service]` section sets `Type=oneshot` and runs `@LIBEXECDIR@/ganesha/nfs-ganesha-config.sh`, where `@LIBEXECDIR@` is substituted by CMake at install/configuration time.

## Control Flow
Systemd starts the unit, runs the config helper once, and treats the service as complete when the script exits. This file does not define ordering dependencies itself; those are expected to be supplied by packaging or other unit relationships.

## State and Persistence Behavior
The unit itself stores no state. The invoked `nfs-ganesha-config.sh` may generate or validate runtime configuration depending on package layout. Systemd records normal service status and logs.

## Dependencies and Integration Points
It depends on systemd and the installed helper script in the configured libexec directory. It integrates with CMake packaging and the broader `nfs-ganesha.service` unit set.

## Risks and Test Signals
Risks include incorrect CMake substitution, missing executable install permissions, and insufficient ordering because `DefaultDependencies=no` removes standard unit dependencies. Test signals are package install checks, `systemd-analyze verify`, `systemctl start nfs-ganesha-config.service`, and startup behavior when the helper exits nonzero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/systemd/nfs-ganesha-config.service-in.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create.sh

## Purpose
This mountpoint smoke test creates 500 files with long names in a temporary subdirectory, renames every file to a second long-name prefix, renames them back, and removes the directory. It targets NFS directory-entry create and rename behavior through a mounted export.

## Important APIs, Types, and Functions
The script takes one argument, `TEST_DIR`, and uses variables `SUB_DIR1`, `FILENAME_1`, `FILENAME_2`, `NB_ENTREES`, and `ERR`. It uses shell arithmetic loops, `touch`, `mv`, `ls -li`, and `rm -rf`.

## Control Flow
After validating that `TEST_DIR` exists, it creates `create_rename-$$`, loops from 0 to 499 creating `FILENAME_1-$I`, loops again renaming each file to `FILENAME_2-$I`, then loops a third time renaming each file back. Each operation increments `ERR` and prints inode diagnostics if it fails. Cleanup removes the subdirectory and prints the total error count.

## State and Persistence Behavior
Temporary state is confined to `$TEST_DIR/create_rename-$$`. The test cleans the subdirectory at the end but does not trap signals or early exits, so interrupted runs can leave files behind.

## Dependencies and Integration Points
It depends on Bash-style `[[ ]]` and `(( ))` syntax despite using `#!/bin/sh`, plus core utilities. It is meant to run against an NFS-Ganesha mounted export and exercise create/rename/remove paths in the server and backing FSAL.

## Risks and Test Signals
Risks include non-portability under strict `/bin/sh`, no nonzero exit on accumulated `ERR`, and destructive `rm -rf` if variables are unexpectedly empty. Test signals are zero reported errors, no leftover subdirectory, and NFS/server logs showing successful CREATE and RENAME sequences under long file names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_ls.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_ls.sh

## Purpose
This mountpoint test creates 100 files in a temporary directory and repeatedly lists the directory, sleeping between reads. It is aimed at readdir stability and visibility of created entries through an NFS-Ganesha mount.

## Important APIs, Types, and Functions
Inputs and variables mirror `test_create.sh`: `TEST_DIR`, `SUB_DIR1=create_ls-$$`, two long filename constants, `NB_ENTREES=100`, and `ERR`. The operational commands are `mkdir -p`, `touch`, `ls`, `sleep 10`, and `rm -rf`.

## Control Flow
The script validates the target directory, creates the subdirectory, creates 100 files with the first filename prefix, then performs 100 `ls "$TEST_DIR/$SUB_DIR1"` calls redirected to `/dev/null`, sleeping ten seconds between calls. It increments `ERR` on create or list failure, removes the test directory, and reports the error count.

## State and Persistence Behavior
Filesystem state is the temporary `create_ls-$$` directory. Runtime duration is intentionally long because of the 100 ten-second sleeps. Cleanup is best-effort at normal script completion.

## Dependencies and Integration Points
It depends on Bash extensions under a `/bin/sh` shebang and standard utilities. It integrates with the mounted export by forcing repeated directory reads after a burst of creates, which can expose server cache, readdir, or stale handle problems.

## Risks and Test Signals
Risks include high wall-clock runtime, no exit-status propagation for `ERR`, and no verification that all expected filenames appear in listings. Test signals are zero reported errors, stable directory listings, and absence of server-side readdir/getattr errors during the sleep-heavy loop.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_ls.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_rm.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_rm.sh

## Purpose
This mountpoint smoke test stresses repeated create, remove, rename, list, and remove sequences on one temporary directory. It is intended to expose stale cache and operation ordering issues for simple file lifecycle operations.

## Important APIs, Types, and Functions
The script uses `TEST_DIR`, `SUB_DIR1=touch_rm-$$`, two long filename constants, `NB_LOOP=100`, and an `ERR` counter. It invokes `touch`, `rm`, `mv`, `ls -li`, `ls -l`, and `rm -rf`.

## Control Flow
After setup, the first loop alternates `touch` and `rm` for each of two filenames. The second loop creates `FILENAME_1`, renames it to `FILENAME_2`, and removes it. The third loop adds an intervening `ls -l` before the rename/remove. Each failed operation increments `ERR` and prints diagnostics. The test directory is removed at the end.

## State and Persistence Behavior
All created files are transient within `touch_rm-$$`. There is no durable state beyond console output. Early interruption can leave the temporary directory in the mounted export.

## Dependencies and Integration Points
It depends on Bash-style tests/arithmetic and core utilities. It exercises NFS-Ganesha's create, unlink, lookup/getattr through `ls`, rename, and directory cache invalidation paths.

## Risks and Test Signals
Risks include accepting success with nonzero `ERR`, unquoted diagnostic paths in a few commands elsewhere in this test family, and race sensitivity if multiple tests share the same target with colliding names. Test signals are zero errors and server traces showing removed names disappearing before reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_create_rm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createrenameunlink.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createrenameunlink.sh

## Purpose
This test repeatedly creates, renames, unlinks, and then rereads a surviving file through a mounted export. It targets rename/unlink consistency and directory/getattr visibility after many short file lifecycle operations.

## Important APIs, Types, and Functions
The main variables are `SUB_DIR1=create_rename_unlink-$$`, `FILENAME1`, `FILENAME2`, `NB_ITER_1=100`, `NB_ITER_2=10`, and `ERR`. Commands include `touch`, `mv`, `rm -f`, `ls -li`, and `mkdir -p`.

## Control Flow
For each outer iteration, the script performs 100 repetitions of two sequences: create `FILENAME1`, rename it to `FILENAME2`, unlink it; then create `FILENAME1`, rename to `FILENAME2`, rename back, and unlink. It then creates `FILENAME2`, performs 100 cycles of `ls -li` on the file and directory, removes the file, and repeats. Existence checks before create/rename detect stale names.

## State and Persistence Behavior
State lives in one temporary directory. Unlike several sibling tests, this script does not remove `SUB_DIR1` at the end, so the empty test directory can persist after a successful run. Interrupted runs can also leave files behind.

## Dependencies and Integration Points
It uses Bash-specific syntax under `/bin/sh`. It integrates with NFS-Ganesha by exercising CREATE, RENAME, REMOVE, LOOKUP, GETATTR, and READDIR sequences that are sensitive to directory entry cache invalidation.

## Risks and Test Signals
Risks include missing final cleanup, success exit despite nonzero `ERR`, and reliance on `rm -f` status even when targets are already absent. Test signals are zero reported errors, no unexpected pre-existing filenames, and repeated file/directory listings succeeding after churn.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createrenameunlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createunlink.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createunlink.sh

## Purpose
This mountpoint smoke test repeatedly creates and unlinks one file, then creates it once more and verifies lookup/getattr and readdir visibility before removal. It focuses on stale negative/positive cache behavior around a single name.

## Important APIs, Types, and Functions
Variables include `SUB_DIR1=create_unlink-$$`, `FILENAME`, `NB_ITER_1=100`, `NB_ITER_2=10`, and `ERR`. It uses `touch`, `rm -f`, `ls -li`, and shell existence tests.

## Control Flow
For each of 10 outer iterations, the script performs 100 create/unlink cycles, checking before each create that the file is absent. It then creates the file, runs 100 cycles of `ls -li` on the file and containing directory, removes the file, and proceeds to the next outer iteration.

## State and Persistence Behavior
Temporary state is created under `create_unlink-$$`. The script does not remove the temporary directory at the end, so a successful run leaves an empty directory unless cleaned externally. No durable metadata is written outside the mount.

## Dependencies and Integration Points
It depends on Bash-specific conditionals/arithmetic under a `/bin/sh` shebang. It exercises server-side create, remove, lookup, getattr, and readdir semantics through standard client utilities.

## Risks and Test Signals
Risks include final directory leakage, no failure exit based on `ERR`, and false confidence because it does not verify that `ls` output contains exactly the expected entry. Test signals are zero errors and absence of stale file visibility after unlink in both direct lookup and directory listing paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_createunlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_mkdircascade.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_mkdircascade.sh

## Purpose
This script performs a pseudo-random cascade of file and directory creation/removal while moving up and down a nested path. It stresses mkdir, rmdir, file create/remove, and path traversal behavior through an NFS-Ganesha mount.

## Important APIs, Types, and Functions
The script defines Bash functions `random`, `create_file`, `create_dir`, `remove_file`, `remove_dir`, `go_up`, and `go_in`. It tracks `depth`, current `path`, and French-named state `etat` with values `vide`, `fichier`, and `directory`. `NB_ITER=5000` controls operation count and `RAND` is generated by a simple linear congruential formula seeded with PID and time.

## Control Flow
After creating `mkdir_cascade-$$`, the main loop dispatches by `etat`. In the empty state it randomly creates a file, creates a subdirectory, or moves up if not at depth zero. In the file state it removes the file. In the directory state it either enters the directory or removes it. Helper functions exit immediately on command failure. At the end the whole test tree is removed.

## State and Persistence Behavior
The script mutates a nested temporary tree under the supplied mountpoint and normally deletes it. It exits nonzero immediately on operation failures in helper functions, which can leave the tree partially populated for diagnosis.

## Dependencies and Integration Points
It requires Bash syntax (`function`, `[[ ]]`, `(( ))`) despite a `/bin/sh` shebang. It integrates with NFS-Ganesha path walk, create, remove, mkdir, and rmdir behavior, especially around nested directory state changes.

## Risks and Test Signals
Risks include non-portability, unquoted `$path` in helper invocations, random operation sequences that are not logged with a reproducible seed command, and possible deep path growth depending on random choices. Test signals are successful completion, final cleanup success, and server logs without stale handle or directory-not-empty surprises.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_mkdircascade.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_read_write.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_read_write.sh

## Purpose
This script verifies basic read/write fidelity through a mounted export by copying a generated reference file into the export and back, first with `cp` and then with `cp -p`.

## Important APIs, Types, and Functions
It accepts `REPERTOIRE` as the mountpoint directory, builds a date-stamped `FICH_TEST`, and uses `TEMOIN=/tmp/TEST_RW.$DATE`. The content source is `COMMANDE_CONTENU="find /etc -ls"`. It uses `cp`, `cp -p`, `ls -l`, `diff`, and `rm`.

## Control Flow
The script validates that the argument is a directory, writes `find /etc -ls` output to the local reference file, copies it into the mount, compares source and mounted copy, copies the mounted file back to `/tmp`, compares again, removes the mounted file, repeats the same flow with `cp -p`, then removes all test files.

## State and Persistence Behavior
It writes one temporary local file and one mounted-export file named with the current day/month/year. Because the filename granularity is one day, concurrent or repeated runs on the same day can collide. There is no trap-based cleanup on failure.

## Dependencies and Integration Points
It depends on Bash-style `[[ ]]`, `/etc` being readable enough for `find /etc -ls`, local `/tmp`, and core utilities. It exercises NFS-Ganesha write, read, metadata preservation, and remove paths.

## Risks and Test Signals
Risks include unquoted paths, date-based filename collisions, no explicit exit-on-error despite `diff` failures, and environmental noise from changing `/etc` traversal output before the reference is created. Test signals are zero `diff` output/status for both normal and preserved copies and matching size/metadata expectations after `cp -p`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_read_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename.sh

## Purpose
This test repeatedly renames one long-named file within a directory and across two directories. It targets NFS rename correctness, especially when moving names between sibling directories under an export.

## Important APIs, Types, and Functions
It uses `SUB_DIR1=hercule-$$/depouillement`, `SUB_DIR2=hercule-$$/protections`, two long file names, `NB_LOOP_1=10`, `NB_LOOP_2=100`, and `ERR`. Commands are `mkdir -p`, `touch`, `mv`, `ls -li`, and `rm -rf`.

## Control Flow
The script creates the two directories and one initial file. Each outer pass first does 100 back-and-forth renames inside `SUB_DIR1`. It then moves the file to `SUB_DIR2`, performs 100 cycles of renaming inside `SUB_DIR2`, moving the second name back to `SUB_DIR1`, and moving it again to `SUB_DIR2` under the first name. Finally it moves the file back to `SUB_DIR1` and repeats. It exits immediately on most inner rename failures.

## State and Persistence Behavior
The test creates a `hercule-$$` tree and removes the two child directories at the end. It does not explicitly remove the parent `hercule-$$`, so an empty parent directory can remain after success.

## Dependencies and Integration Points
It depends on Bash arithmetic/conditionals under `/bin/sh`. It integrates with mounted-export rename paths, directory entry invalidation, and cross-directory move behavior.

## Risks and Test Signals
Risks include leftover parent directories, success exit despite some non-fatal `ERR` increments, and no verification of final directory emptiness. Test signals are the reported rename count, zero errors, and successful repeated cross-directory renames without stale name lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename2.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename2.sh

## Purpose
This is the multi-file variant of `test_rename.sh`. It creates 100 long-named files and performs intensive within-directory and cross-directory rename cycles for each file.

## Important APIs, Types, and Functions
Important variables are `SUB_DIR1`, `SUB_DIR2`, `FILENAME_1`, `FILENAME_2`, `NB_LOOP_1=10`, `NB_LOOP_2=100`, `NB_FILES=100`, and `ERR`. The command set is `mkdir`, `touch`, `mv`, `ls -li`, and cleanup with `rm -rf`.

## Control Flow
After creating both directories, the script creates 100 files named `FILENAME_1.<index>`. In each outer loop it runs "test 1", where every file is renamed back and forth 100 times inside `SUB_DIR1`. It then runs "test 2", where each file is moved to `SUB_DIR2`, cycled among names and directories 100 times, and returned to `SUB_DIR1`. It removes both child directories and prints the computed rename count.

## State and Persistence Behavior
It mutates many files under a `hercule-$$` parent. As with `test_rename.sh`, cleanup removes the child directories but can leave the parent directory. Most inner failures exit early and leave state for inspection.

## Dependencies and Integration Points
It uses Bash-specific syntax under `/bin/sh`. It stresses NFS-Ganesha rename scalability, directory cache invalidation, and repeated cross-directory moves with many distinct entries.

## Risks and Test Signals
Risks include high operation count, leftover parent directory, no final assertion that all files returned to the expected names, and non-portability to shells such as `dash`. Test signals are zero errors, successful completion of all progress dots, expected rename count, and no stale entries in final server/client listings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rename2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rm_stat_readdir.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rm_stat_readdir.sh

## Purpose
This mountpoint test validates consistency between create, getattr/stat, readdir, remove, negative lookup, and readdir-after-remove. It is more assertive than the simpler create/unlink tests because it checks both positive and negative visibility.

## Important APIs, Types, and Functions
The script uses `SUB_DIR1=TESTDIR_RMSTAT-$$`, `FILENAME_1`, `FILENAME_2`, `NB_FILES=1000`, and `ERR`. It uses `touch`, `stat`, `ls`, `egrep`, `rm`, and `rm -rf`.

## Control Flow
The first phase creates 500 pairs of files, checking for each first file that `stat` succeeds before readdir membership, and for each second file that readdir membership succeeds before `stat`. The second phase removes each pair, checks that direct lookup via `ls -l` returns exit code 2, and checks that the removed names no longer appear in directory listings. The final phase recreates the same pairs and repeats the positive stat/readdir checks before cleanup.

## State and Persistence Behavior
Temporary state lives under `TESTDIR_RMSTAT-$$` and is removed at normal completion. The script accumulates errors but still exits with the status of the final commands rather than explicitly failing on `ERR`.

## Dependencies and Integration Points
It requires Bash-style syntax and standard Unix tools. It integrates with NFS-Ganesha lookup cache, directory cache, remove, getattr, and readdir behavior.

## Risks and Test Signals
Risks include assuming GNU/coreutils `ls -l missing` returns `2`, unquoted path variables, slow execution on large directories, and no explicit nonzero exit for accumulated errors. Strong test signals are zero reported errors, removed names absent from readdir, missing names returning ENOENT-like status, and successful recreate after removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/test_through_mountpoint/test_rm_stat_readdir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/support/CMakeLists.txt

## Purpose
This CMake file defines the object libraries that make up NFS-Ganesha's support-layer code: string utilities, hash functions, UID/group mapping, netgroup cache, and the main support object library.

## Important APIs, Types, and Functions
The build targets are `string_utils`, `hash`, `uid2grp`, `netgroup_cache`, and `support`, all created as `OBJECT` libraries with `-fPIC` and passed through `add_sanitizers`. Source groups include `strlcpy.c`, `strnlen.c`, `refstr.c`, `murmur3.c`, `city.c`, `uid2grp.c`, `uid2grp_cache.c`, `netgroup_cache.c`, and the larger `support_STAT_SRCS` list containing ACL, credential, filehandle, config, conversion, data-server, export, delayed execution, base64, stats, transport, and IP utilities. `err_inject.c` is included only under `ERROR_INJECTION`.

## Control Flow
CMake conditionally adds DBus include directories when `USE_DBUS` is enabled. For each object library it attaches sanitizer settings and PIC flags. Under `USE_LTTNG`, selected targets depend on generated trace headers and include generated file properties.

## State and Persistence Behavior
The file produces build-system state: object library targets, compile flags, dependencies, and source lists. It does not install files directly in the shown content.

## Dependencies and Integration Points
It depends on top-level CMake variables such as `USE_DBUS`, `DBUS_INCLUDE_DIRS`, `USE_LTTNG`, and `ERROR_INJECTION`, plus project macros like `add_sanitizers`. These object libraries are consumed by higher-level daemon and test targets.

## Risks and Test Signals
Risks include missing trace-header dependencies for sources that include generated LTTng headers, inconsistent PIC/sanitizer settings across object libraries, and optional `err_inject.c` compiling unused globals. Test signals are clean CMake configure for DBus/LTTng/error-injection permutations and successful link of binaries consuming the support object libraries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/bsd-base64.c -->
# sources/user-network-fs/nfs-ganesha/src/support/bsd-base64.c

## Purpose
This file provides fallback BSD-style Base64 encoding and decoding when the platform lacks `b64_ntop` and `__b64_ntop`. It also adds URL/file-name-safe Base64 encoding.

## Important APIs, Types, and Functions
Compiled only when neither `HAVE_B64_NTOP` nor `HAVE___B64_NTOP` is defined, the exported functions are `b64_enc`, `b64_ntop`, `base64url_encode`, and `b64_pton`. `Base64`, `Base64url`, and `Pad64` define the encoding alphabets and padding. `b64_enc` is the shared encoder; `b64_ntop` uses the normal alphabet, while `base64url_encode` uses `-` and `_`.

## Control Flow
`b64_enc` processes complete 3-byte groups into four 6-bit indexes, handles a final 1- or 2-byte group with `=` padding, checks target capacity, and NUL-terminates the output. `b64_pton` skips whitespace, decodes Base64 characters through a four-state machine, stops at padding, validates padding position and trailing whitespace, verifies unused low bits are zero, and returns decoded byte count or `-1`.

## State and Persistence Behavior
The functions are stateless and operate only on caller-provided buffers. They do not allocate or persist data.

## Dependencies and Integration Points
The code depends on `config.h`, C library headers, and `bsd-base64.h`. It supplies compatibility for support code needing Base64 across platforms without libc/resolver Base64 helpers.

## Risks and Test Signals
Risks include caller-provided buffer sizing, `int` return truncation for very large encoded lengths, and `isspace(ch)` receiving values from signed `char` inputs outside ASCII. `b64_pton` can be used in length-counting mode with `target == NULL`, which callers must understand. Test signals include RFC 4648 known vectors, URL-safe output checks, whitespace-tolerant decode, bad padding rejection, target-too-small rejection, and builds on platforms with and without native Base64 APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/bsd-base64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city-test.c -->
# sources/user-network-fs/nfs-ganesha/src/support/city-test.c

## Purpose
This is a known-answer test program for the vendored C implementation of CityHash. It validates CityHash64, seeded CityHash64, CityHash128, seeded CityHash128, and optionally SSE4.2 CRC variants against a large static table.

## Important APIs, Types, and Functions
Important constants are `kSeed0`, `kSeed1`, `kSeed128`, `kDataSize=1<<20`, `kTestSize=300`, the global `data` buffer, and `testdata[300][15]`. `setup` fills the data buffer with deterministic pseudo-random bytes. `Check` compares expected and actual `uint64` values and increments global `errors`. `Test` runs the hash functions for one offset/length pair. `main` initializes data, runs 299 small tests with offset `i*i` and length `i`, then runs one full-buffer test.

## Control Flow
The test constructs deterministic input, iterates through the expected table, and compares low/high halves of 128-bit outputs. Under `__SSE4_2__`, `Test` also validates `CityHashCrc128`, `CityHashCrc128WithSeed`, and all four words of `CityHashCrc256`.

## State and Persistence Behavior
State is process-local: a 1 MiB static input buffer and an integer error counter. The test writes failures to stderr and returns nonzero if any mismatch occurs.

## Dependencies and Integration Points
It depends on `city.h` and optionally `citycrc.h` when SSE4.2 is enabled. It is a direct regression test for `support/city.c` and compiler/endian behavior in the hash implementation.

## Risks and Test Signals
Risks include the large static expected table being hard to audit, `%llx` format assumptions for `uint64`, and coverage focusing on deterministic vectors rather than collision or distribution quality. Test signals are a zero exit status on little- and big-endian targets, with and without `__SSE4_2__`, and failure output identifying expected versus actual hash words.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city.c -->
# sources/user-network-fs/nfs-ganesha/src/support/city.c

## Purpose
This file is a C port of Google's CityHash family. It provides fast non-cryptographic 64-bit and 128-bit hashes, plus optional SSE4.2 CRC-accelerated variants for longer buffers.

## Important APIs, Types, and Functions
Public functions include `CityHash64`, `CityHash64WithSeed`, `CityHash64WithSeeds`, `WeakHashLen32WithSeeds`, `CityHash128`, `CityHash128WithSeed`, and, under `__SSE4_2__`, `CityHashCrc256`, `CityHashCrc128`, and `CityHashCrc128WithSeed`. Internal helpers include endian-safe `UNALIGNED_LOAD64/32`, `Fetch64/32`, `Hash128to64`, `Rotate`, `ShiftMix`, `HashLen0to16`, `HashLen17to32`, `HashLen33to64`, and `CityMurmur`.

## Control Flow
`CityHash64` dispatches by input length: specialized paths for 0-16, 17-32, 33-64, and a 64-byte chunk loop for longer strings. Seeded variants hash the base output with seed values. `CityHash128` seeds from the first 8 or 16 bytes when available, then delegates to `CityHash128WithSeed`; the latter uses `CityMurmur` for inputs under 128 bytes and an unrolled 128-byte loop plus tail processing for larger inputs. CRC variants use `_mm_crc32_u64` in 240-byte chunks and fall back to padded short-buffer handling for inputs under 240 bytes.

## State and Persistence Behavior
All functions are pure with respect to process state and operate on caller-provided memory. There is no allocation, locking, or persistence.

## Dependencies and Integration Points
The file depends on `city.h`, `misc/portable.h`, endian macros from configuration, and optionally `citycrc.h` plus `<nmmintrin.h>` for SSE4.2. The `support/CMakeLists.txt` builds it into the `hash` object library for use anywhere NFS-Ganesha needs stable non-cryptographic hashes.

## Risks and Test Signals
Risks include non-cryptographic misuse, architecture-specific behavior if endian or unaligned-load assumptions regress, signed `long` use in `CityMurmur` for very large `size_t` lengths, and optional CRC APIs only existing in SSE4.2 builds. Test signals are `city-test.c` known-answer vectors, builds under big-endian and little-endian configurations, sanitizer runs for boundary lengths 0, 1, 16, 17, 32, 33, 64, 65, 127, 128, 239, and 240, and comparison against upstream CityHash outputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/city.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/client_mgr.c -->
# sources/user-network-fs/nfs-ganesha/src/support/client_mgr.c

## Purpose
`client_mgr.c` manages live NFS-Ganesha client records keyed by network address and provides reusable export/client-list parsing and matching logic. When DBus is enabled, it also publishes client management and per-client statistics methods.

## Important APIs, Types, and Functions
The live-client store is `static struct client_by_ip`, containing an AVL tree, rwlock, and hash-front cache. Core APIs are `get_gsh_client`, `put_gsh_client`, `remove_gsh_client`, `foreach_gsh_client`, `client_pkginit`, and `client_mgr_cleanup`. DBus-facing helpers include `arg_ipaddr`, `lookup_client`, `dbus_client_init`, `reset_client_stats`, and `reset_clnt_allops_stats`. Export/client-list APIs include `StrClient`, `LogClientListEntry`, `LogClientList`, `FreeClientList`, `base_client_allocator`, `is_base_client_exact_match`, `add_client`, `delete_base_client`, `client_match`, and `haproxy_match`.

## Control Flow
`get_gsh_client` hashes the sockaddr, checks the front cache under a read lock, falls back to AVL lookup, and creates a new `server_stats`-backed `gsh_client` under a write lock if needed. It initializes locks and connection-manager state for new clients and returns with the client refcount incremented. `remove_gsh_client` removes an unused client from cache/tree, frees statistics and QoS memory, finalizes connection state, and destroys locks. `add_client` converts config tokens into base client entries: wildcard-any, netgroups, CIDR/address entries, wildcard host patterns, or resolved DNS names that may expand into multiple network entries. `client_match` checks client lists using CIDR containment, netgroup membership via IP-name cache, wildcard matching against IP and hostname, or match-any.

## State and Persistence Behavior
State is in-memory only: AVL nodes, cache slots, refcounts, per-client locks, statistics, connection-manager state, and configured base-client lists owned by callers. DBus methods expose and reset runtime statistics but do not persist them to disk.

## Dependencies and Integration Points
This file depends on pthread rwlocks, AVL and glist utilities, sockaddr/CIDR helpers, server statistics, FSAL/export management, QoS, IP-name and netgroup caches, DBus support, SAL connection functions, and global `nfs_param`. It integrates with request dispatch for client lookup, export access checks, HAProxy proxy-host validation, and management tooling under `/org/ganesha/nfsd/ClientMgr`.

## Risks and Test Signals
Risks include refcount lifetime mistakes, stale front-cache entries if removal paths miss a slot, DNS expansion producing duplicate or surprising entries, hostname/netgroup cache freshness, compile-time DBus/stat feature permutations, and the DBus `disconnect_nfsv41_client` path parsing the address twice while holding a client reference that is not explicitly released after disconnect. `client_match` is caller-locking dependent for configured lists. Test signals include concurrent get/remove stress, refcount assertions, DBus Add/Remove/Show/Get stats calls, duplicate client config errors, CIDR/netgroup/wildcard matching tests, IPv4-mapped IPv6 matching, HAProxy host list tests, and cleanup under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/client_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/delayed_exec.c -->
# sources/user-network-fs/nfs-ganesha/src/support/delayed_exec.c

## Purpose
This module implements NFS-Ganesha's delayed execution system: callers submit callbacks with nanosecond delays, and a detached executor thread runs them when their wall-clock deadline arrives.

## Important APIs, Types, and Functions
Internal types are `delayed_multi`, grouping all tasks for one `timespec`; `delayed_task`, carrying a callback and argument; and `delayed_thread`, tracking executor threads. Public APIs are `delayed_start`, `delayed_shutdown`, and `delayed_submit`. The worker entry point is `delayed_thread`, and `delayed_get_work` selects ready work from the AVL timer tree.

## Control Flow
`delayed_start` initializes mutex, condition variable, thread list, AVL tree, submission gates, and starts one detached executor thread. The thread registers with RCU, enables asynchronous cancellation, then loops while running: if no work exists it waits indefinitely, if future work exists it timed-waits until the earliest deadline, and if work is ready it removes one task, unlocks, executes the callback, and relocks. `delayed_submit` computes the deadline, inserts or reuses a tree node for that exact time, adds the task to the node list, and wakes the executor if the new task is earlier than the previous first node. `delayed_shutdown` blocks new submissions, waits for active submitters to drain, signals stop, waits up to 120 seconds for threads, then cancels any remaining thread.

## State and Persistence Behavior
State is process-local: a mutex, condition variable, AVL tree, task lists, thread list, `deny_submission`, `active_submitters`, and executor state. There is no durable persistence.

## Dependencies and Integration Points
It depends on pthreads, RCU bulletproof registration, project AVL/queue utilities, time helpers, atomic wrappers, logging, and memory wrappers. It integrates with subsystems that need deferred callbacks without owning their own timer thread.

## Risks and Test Signals
Risks include callback functions running on a shared executor and blocking all later delayed work, asynchronous cancellation hazards during forced shutdown, wall-clock time sensitivity if system time jumps, unchecked allocation failures through `gsh_malloc`, and lack of pending-task cleanup during shutdown after the executor exits. Test signals include ordering tests for earlier/later deadlines, multiple tasks with the same deadline, shutdown while submissions are active, callback blocking behavior, `EAGAIN` after shutdown starts, and sanitizer/thread-sanitizer runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/delayed_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/ds.c -->
# sources/user-network-fs/nfs-ganesha/src/support/ds.c

## Purpose
`ds.c` parses and manages pNFS data server (DS) configuration blocks. It stores active `fsal_pnfs_ds` records by configured server id, coordinates FSAL DS creation, and removes DS records during export or daemon cleanup.

## Important APIs, Types, and Functions
The central store is `static struct server_by_id`, with rwlock, AVL tree, and a 193-slot front cache; `dslist` tracks active DS entries. Public management APIs are `pnfs_ds_alloc`, `pnfs_ds_free`, `pnfs_ds_insert`, `pnfs_ds_get`, `pnfs_ds_put`, `pnfs_ds_remove`, `remove_all_dss`, `ReadDataServers`, `ds_cleanup`, and `server_pkginit`. Config callbacks include `fsal_cfg_commit`, `pds_init`, `pds_commit`, and `pds_display`.

## Control Flow
`server_pkginit` initializes the lock, AVL tree, list, cache, and cleanup hook. Config parsing uses `pds_block`: `pds_init` allocates a DS record, `fsal_cfg_commit` loads/initializes the named FSAL and calls its `create_fsal_pnfs_ds` method, and `pds_commit` rejects duplicate `Number` values before inserting. `pnfs_ds_insert` adds the node to the AVL tree and list, updates the cache, takes the table reference, and pins a related MDS export if present. `pnfs_ds_get` checks cache then AVL under read lock and increments the DS refcount. `pnfs_ds_remove` removes the DS from cache/tree/list, releases any related export through an op context, drops table and FSAL-created references, and lets `pnfs_ds_put` finalize resources on the last reference.

## State and Persistence Behavior
State is runtime-only: active DS objects, refcounts, AVL/cache/list membership, FSAL references, and optional MDS export references. The source of truth for persistence is the parsed NFS-Ganesha config, not this module.

## Dependencies and Integration Points
The module depends on config parsing, FSAL module loading, pNFS utility types, export reference management, op-context helpers, glist/AVL utilities, pthread locks, atomics, and logging. It integrates with pNFS file handles carrying `id_servers`, FSAL-specific DS initialization, and export lifecycle cleanup.

## Risks and Test Signals
Risks include delicate two-reference lifetime semantics, special static `special_ds` behavior for no-config paths, needing `Client`/`FSAL` config blocks last as documented, cache invalidation on removal, and possible leaks if FSAL creation partially succeeds. Test signals include duplicate DS id rejection, successful FSAL DS creation for supported FSALs, lookup cache hit/miss behavior, remove while references are held, export reference release, `remove_all_dss` at shutdown, and config-error paths for missing or invalid FSAL names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/err_inject.c -->
# sources/user-network-fs/nfs-ganesha/src/support/err_inject.c

## Purpose
This file is a dormant error-injection support module. It currently only compiles two global delay variables when included by the build; the intended SNMP administration accessors and registration are disabled under `#if 0`.

## Important APIs, Types, and Functions
Active symbols are `int worker_delay_time` and `int next_worker_delay_time`. Disabled code contains `getErrInjectInteger`, `setErrInjectInteger`, an `snmp_error_injection` table with `worker_delay` and `next_worker_delay`, and `init_error_injector`.

## Control Flow
There is no active control flow beyond global variable definition. If the disabled block were re-enabled, getters/setters would map option 0 to `worker_delay_time` and option 1 to `next_worker_delay_time`, and initialization would register the table with SNMP administration.

## State and Persistence Behavior
The two active globals are mutable process state and are not persisted. No locking or atomic access is provided in this file.

## Dependencies and Integration Points
The file includes core NFS-Ganesha headers, logging, export/tool headers, pthread/time/stat headers, and is conditionally added to the `support` object library when `ERROR_INJECTION` is enabled. The disabled code references legacy SNMP admin types and registration functions.

## Risks and Test Signals
Risks include dead code drifting away from current admin infrastructure, unsynchronized global variables if other modules read/write them, and builds enabling `ERROR_INJECTION` getting symbols that are not controllable. Test signals are compile tests with `ERROR_INJECTION=ON`, searches for active references to the delay globals, and any future admin/DBus replacement tests that set delays and verify worker behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/err_inject.c -->
