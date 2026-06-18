# Research Group: subset-b-009097

This grouped report covers two Borg documentation asciinema recordings. Each source file is an asciinema v2 JSON stream: a header object followed by timed terminal output events. The recordings are documentation data rather than executable library code, so the "APIs" discussed below are the serialized asciinema contract and the Borg CLI surfaces demonstrated by the recording.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/asciinema/advanced.json -->
# sources/sync-backup/borg/docs/misc/asciinema/advanced.json

## Purpose

`advanced.json` is an asciinema v2 terminal recording used by the Borg documentation to demonstrate advanced Borg 1.2.1 usage. It records a scripted shell session in an 80x24 `vt100` terminal running `/bin/bash`. The session assumes an existing Borg repository at `/media/backup/borgdemo` and shows how a more experienced user can rely on environment variables, placeholder-based archive names, alternate compression settings, stdin backups, repository inspection, key export, consistency checks, pruning, archive diffs, tar export, and FUSE mounting.

The file is data, not application code. Its runtime purpose is to be consumed by asciinema-compatible players or documentation build steps so users can replay the session with original timing and terminal output.

## Important APIs, Types, and Data Shape

The top-level format follows asciinema v2:

- Header object: `{"version": 2, "width": 80, "height": 24, "timestamp": 1657143034, "env": {"SHELL": "/bin/bash", "TERM": "vt100"}}`.
- Event rows: arrays shaped as `[time_offset_seconds, stream, data]`.
- Stream values: only output stream `"o"` is present in this file.
- `data` values contain terminal bytes as JSON strings. Many events contain one character; others contain larger command output chunks, progress redraws, ANSI-style terminal spacing, prompts, and CRLF boundaries.

The recording has 3,868 event rows, a final event timestamp around 188.567499 seconds, and about 95,407 bytes of output payload. Consumers must process it as newline-delimited JSON values, not as one JSON array.

The main external CLI surfaces demonstrated are:

- `BORG_REPO` and `BORG_PASSPHRASE` environment variables.
- `borg create` with `--stats`, `--progress`, `--compression`, archive placeholders like `::{user}-{now}`, `--exclude`, and stdin input via `-`.
- `borg info :: --last 1`.
- `borg rename ::specialbackup backup-block-device`.
- `borg key export --qr-html :: file.html` and `borg key export --paper ::`.
- `borg check -v ::`.
- `borg prune --list --keep-last 1 --dry-run`.
- `borg diff ::backup1 backup2`.
- `borg export-tar --progress ::backup2 backup.tar.gz`.
- `borg mount :: /tmp/mount` and `borg umount /tmp/mount`.

## Control Flow and Recorded Scenario

The terminal narrative starts by warning that the cast was made with Borg 1.2.1 and that other versions may differ. It then configures `BORG_REPO=/media/backup/borgdemo` and `BORG_PASSPHRASE=1234`, which allows later Borg commands to use the compact `::archive` syntax and skip repeated passphrase prompts.

The advanced creation section creates a backup with `borg create --stats --progress --compression lz4 ::{user}-{now} Wallpaper`. Borg expands the placeholders into an archive named `root-2022-07-06T21:31:12`; the output reports 32 files, about 401.15 MB original size, and only 542 B of deduplicated size because the repository already contains matching content from the basic demo.

The recording then creates a separate archive for `~/Downloads` using `--compression zlib,6` and `--exclude ~/Downloads/big`. The demonstrated run captures no files and reports a 576 B original payload, but it still illustrates mixing source trees and compression policies in the same deduplicated repository.

Next, the cast pipes a block device through stdin: `sudo dd if=/dev/loop0 bs=10M | borg create --progress --stats ::specialbackup -`. The `dd` output shows 419,430,400 bytes copied; Borg stores one stdin-backed archive, with heavy compression and deduplication reducing the new deduplicated size to roughly 33 kB in this demo.

The useful-commands section inspects the most recent archive with `borg info :: --last 1`, renames `specialbackup` to `backup-block-device`, and verifies the renamed archive with another `borg info` call. The archive fingerprint changes after rename while archive metadata such as start/end time and command line remain associated with the original creation command.

The key-management section exports repository key material in two forms: a QR HTML file and a paper key. The paper-key output is intentionally visible in the recording, including `BORG PAPER KEY v1` rows. This is useful as documentation but sensitive as example content if copied into real workflows.

The maintenance section runs `borg check -v ::`, which records repository, index, and archive consistency checks across six archives. It then performs a dry-run prune with `--keep-last 1`, keeping `backup-block-device` and showing five older archives that would be removed.

The restore/export section uses `borg diff ::backup1 backup2` to show `Wallpaper/newfile.txt` as a 14-byte addition, exports `backup2` to `backup.tar.gz` with progress, lists the working directory, mounts the whole repository at `/tmp/mount`, lists archive directories under the mount point, and unmounts it. The mount/ls/unmount output is interleaved in terminal-capture order, so replay correctness depends on preserving the exact event stream.

## State and Persistence Behavior

This file persists only the recording, not Borg repository state. The recorded commands demonstrate persistent Borg effects:

- `BORG_REPO` and `BORG_PASSPHRASE` affect the shell process and all following Borg invocations in the session.
- `borg create` appends archives and chunk/index metadata to `/media/backup/borgdemo`.
- Archive placeholder expansion stores time- and user-derived archive names.
- `borg rename` mutates archive metadata and produces a new fingerprint for the renamed archive.
- `borg key export` writes `file.html` and emits paper key material.
- `borg prune --dry-run` deliberately does not mutate repository state.
- `borg export-tar` writes `backup.tar.gz`.
- `borg mount` creates a transient FUSE view under `/tmp/mount`; `borg umount` tears it down.

For the asciinema file itself, all state is immutable serialized terminal output. Any documentation player should treat timing offsets as replay metadata and strings as opaque terminal output, not as commands to execute.

## Dependencies and Integration Points

Primary data dependency is the asciinema v2 format. Integration points are likely Borg documentation pages that embed or link this recording, asciinema-player or compatible web components, and documentation build/static asset pipelines that copy files under `docs/misc/asciinema/`.

The demonstrated runtime dependencies include Borg 1.2.1, bash, `sudo`, `dd`, a loop device at `/dev/loop0`, a FUSE-capable environment for `borg mount`, `ls`, a repository initialized at `/media/backup/borgdemo`, and previously created archives from the basic screencast. The recording also assumes root-owned files and directories visible in the demo output.

## Risks and Edge Cases

- The recording hard-codes Borg 1.2.1 behavior, command output, fingerprints, timings, and archive names. Newer Borg versions may change help text, defaults, warnings, progress rendering, archive fingerprints, or command aliases.
- `BORG_PASSPHRASE='1234'` is intentionally insecure demo material. Documentation consumers should not treat it as recommended practice.
- The paper key block is example secret material. It is not useful for this repository outside the demo, but scanners may still flag it as key-like content.
- Asciinema event rows include carriage returns and progress redraws. Tools that line-split naively can misread progress sections or reorder mount output.
- The `export-tar --progress` portion dominates the payload and includes many repeated progress updates. This can make diffs noisy and can stress simplistic Markdown or log renderers if converted verbatim.
- `borg mount` requires platform support and may fail in CI or containerized environments; the recording should be replayed, not executed, during docs tests.

## Test Signals

Useful validation signals for this file are structural and transcript based:

- Parse as newline-delimited JSON; the first object must have `version: 2`, `width: 80`, and `height: 24`.
- All subsequent entries should be arrays of length 3 with a numeric timestamp, stream `"o"`, and string payload.
- Timestamps should be nondecreasing and end around 188.567499 seconds.
- A joined transcript should contain the expected advanced commands: `export BORG_REPO`, `borg create ... ::{user}-{now}`, stdin `dd | borg create`, `borg info`, `borg rename`, `borg key export`, `borg check`, `borg prune --dry-run`, `borg diff`, `borg export-tar`, `borg mount`, and `borg umount`.
- Replay in an asciinema-compatible player should show an 80x24 terminal with no JSON parse errors and with progress redraws preserved.

<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/asciinema/advanced.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/asciinema/basic.json -->
# sources/sync-backup/borg/docs/misc/asciinema/basic.json

## Purpose

`basic.json` is an asciinema v2 terminal recording used by the Borg documentation to introduce basic Borg 1.2.1 workflows. It records a guided shell session showing help output, repository initialization, creation of several compressed backups, deduplication behavior after adding a file and moving a directory, archive listing, targeted extraction, verification with `diff`, and remote repository initialization over SSH.

The file is documentation data rather than source code. Its job is to preserve a reproducible terminal demonstration for playback in docs, not to execute commands at build time.

## Important APIs, Types, and Data Shape

The first JSON value is the asciinema header:

- `version`: `2`.
- `width`: `80`.
- `height`: `24`.
- `timestamp`: `1657142858`.
- `env`: `{"SHELL": "/bin/bash", "TERM": "vt100"}`.

Every following line is an asciinema event array `[time_offset_seconds, stream, data]`. This file contains only output events with stream `"o"`. The recording has 2,647 events, ends around 162.062134 seconds, and stores about 16,827 bytes of output payload.

The demonstrated Borg CLI surfaces are:

- `borg help`.
- `borg init --encryption=repokey /media/backup/borgdemo`.
- `borg create --stats --progress --compression lz4 /media/backup/borgdemo::backupN Wallpaper`.
- `borg list /media/backup/borgdemo`.
- `borg list /media/backup/borgdemo::backup3 | grep 'deer.jpg'`.
- `borg extract /media/backup/borgdemo::backup3 Wallpaper/deer.jpg`.
- `borg init --encryption=repokey borgdemo@remoteserver.example:./demo`.

Supporting shell commands include `echo`, `mv`, `grep`, and `diff -s`.

## Control Flow and Recorded Scenario

The recording opens with comments explaining that it is a beginner teaser made with Borg 1.2.1. It runs `borg help` and captures the top-level Borg CLI usage, common options, and command list.

The first repository operation initializes `/media/backup/borgdemo` with `--encryption=repokey`. The session records passphrase prompts, a compatibility warning about older Borg versions up to 1.0.8, a suggested `borg upgrade --disable-tam` command for old-version compatibility, and a key/passphrase backup warning.

The first backup command creates `backup1` from the `Wallpaper` directory using `--stats`, `--progress`, and `--compression lz4`. The output reports 31 files, about 401.15 MB original size, 399.74 MB compressed size, and about 399.55 MB deduplicated size.

The user then adds `Wallpaper/newfile.txt` with `echo "new nice file"` and creates `backup2`. Borg reports 32 files but only 604 B of new deduplicated data, demonstrating chunk-level deduplication for mostly unchanged content.

The demo then moves `Wallpaper/bigcollection` to `Wallpaper/bigcollection_NEW` and creates `backup3`. The archive still represents about 401.15 MB of data, but only 550 B of deduplicated size is added, demonstrating that Borg recognizes moved directory content and does not duplicate file chunks just because paths changed.

The restore portion lists the repository, showing `backup1`, `backup2`, and `backup3` with timestamps and fingerprints. It lists the contents of `backup3` filtered for `deer.jpg`, renames the local `Wallpaper` directory to `Wallpaper.orig`, extracts `Wallpaper/deer.jpg` from `backup3`, and verifies the restored file with `diff -s`, which reports the files are identical.

Finally, the recording demonstrates initializing a remote repository with `borg init --encryption=repokey borgdemo@remoteserver.example:./demo`, again showing passphrase prompts, security compatibility text, and the key backup warning. It closes by pointing users to the advanced screencast.

## State and Persistence Behavior

The JSON file persists the terminal recording only. Inside the recorded scenario, the commands demonstrate these state changes:

- `borg init --encryption=repokey` creates encrypted repository metadata and key material in the target repository.
- Repeated `borg create` calls append immutable archives named `backup1`, `backup2`, and `backup3`.
- Borg's cache and chunk index track already-seen file content so later archives can have large logical sizes but tiny deduplicated sizes.
- `echo` and `mv` mutate the source `Wallpaper` tree between backup runs.
- `borg list` is read-only.
- `borg extract` writes restored content back to the working tree.
- `diff -s` is read-only and provides a verification signal.
- The remote `borg init` would create a repository on a remote SSH target if executed against a real server.

As an asciinema artifact, event order and timing are the state. Consumers should not attempt to infer command success by executing the strings; they should replay or inspect the serialized output.

## Dependencies and Integration Points

The data-level dependency is the asciinema v2 JSON-line format. It likely integrates with Borg documentation pages or static assets under `docs/misc/asciinema/`, where a web player can fetch and replay it.

The demonstrated command-level dependencies are Borg 1.2.1, bash, an accessible `/media/backup/borgdemo` path, a `Wallpaper` directory with demo files, local filesystem permissions, `grep`, `diff`, and SSH/Borg setup on `remoteserver.example` for the remote example. The remote host is clearly illustrative; the recording captures the intended command form, not a reusable live endpoint.

## Risks and Edge Cases

- The cast is version-specific. Borg help text, security warnings, output tables, progress formatting, and archive fingerprints may differ in other versions.
- The repository path `/media/backup/borgdemo`, `Wallpaper` data set, and remote host are demo-specific. Executing the commands directly on another machine can fail or mutate unintended data.
- `--encryption=repokey` requires users to back up key material and remember the passphrase. The recording includes this warning, but automated docs extraction should avoid shortening it away.
- The output stream includes passphrase prompts without typed secret input. Replay tools should preserve the prompts without inventing input events.
- Progress output is carriage-return heavy and may appear as dense repeated status text when rendered as plain logs.
- The recording demonstrates `grep 'deer.jpg'` filtering; if source demo data changes, the transcript and verification narrative would no longer match.

## Test Signals

Validation should cover both serialization and content:

- Parse as newline-delimited JSON with an asciinema v2 header and output event rows.
- Confirm all event rows have numeric offsets, stream `"o"`, and string payloads.
- Confirm the final offset is around 162.062134 seconds and timestamps do not move backward.
- Join output payloads and check for anchor commands: `borg help`, local `borg init`, three `borg create` commands, `borg list`, `borg extract`, `diff -s`, and remote `borg init`.
- Check narrative anchors such as `Archive name: backup1`, `Archive name: backup2`, `Archive name: backup3`, the tiny deduplicated sizes for the second and third backups, and `Files Wallpaper/deer.jpg and Wallpaper.orig/deer.jpg are identical`.
- Replay with an asciinema player to catch malformed JSON-line content or terminal rendering regressions.

<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/misc/asciinema/basic.json -->
