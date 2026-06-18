# sources/control-plane/longhorn-engine/integration/data/test_restore_to_file.py

## Purpose
This module verifies the `restore-to-file` engine command for raw and qcow2 output images, both with and without a backing file. It checks byte-level reconstruction of snapshot chains into standalone image files and guarantees that backing images remain unchanged.

## Important APIs, types, and functions
- Constants: `OUTPUT_FILE_RAW`, `OUTPUT_FILE_QCOW2`, `IMAGE_FORMAT_RAW`, and `IMAGE_FORMAT_QCOW2`.
- Helpers: `read_qcow2_file_without_backing_file`, `check_backing`, `check_empty_volume`, `restore_to_file_with_backing_file_test`, and `restore_to_file_without_backing_file_test`.
- Test entry points: `test_restore_to_file_with_backing_file` and `test_restore_to_file_without_backing_file`.
- Uses `pyqcow.file()` to read generated qcow2 outputs and backing qcow2 data without relying on backing-file support in the library.
- Uses `common.cmd.restore_to_file`, snapshot/backup helpers, snapshot revert, snapshot removal, and checksum utilities.

## Control flow
The backing-file path starts from an empty volume whose content equals the backing file, creates a backup, restores it to raw and qcow2 output, compares content and full-volume checksums, and removes output files. It then repeats with one snapshot containing changed data and with a two-snapshot chain where newer data partially overwrites older data. Between phases it reverts to the initial snapshot, removes snapshots/backups, and rechecks backing file integrity.

The no-backing path creates one and then two snapshots on a normal volume, creates backups, restores to raw/qcow2 without passing a backing file, and verifies that the output contains only the expected snapshot-chain data. It also uses snapshot revert and backup cleanup between phases.

## State and persistence behavior
The tests create temporary output files in the integration utility path and assert they are removed after validation. Persistent state under test includes snapshot disk chains, backup objects, backing raw/qcow2 file data, restored output image bytes, and device checksums. Snapshot reverts reset the tested volume to a known baseline before subsequent chains.

## Dependencies and integration points
The file depends on engine controller/replica fixtures, backing-file fixtures, backup targets, pyqcow, Longhorn CLI restore-to-file support, local file utilities, and backing file constants. It bridges live block-device data, backupstore data, generated image files, and qcow2 decoding.

## Risks and edge cases
- The qcow2 reader helper explicitly cannot handle qcow2 files with backing files, so it reads generated images as standalone content and relies on restore-to-file producing self-contained images.
- There is a likely typo in the final backing qcow2 assertion: it concatenates `output1_qcow2_backing` instead of `output2_qcow2_backing`, so the expected value works only if those backing ranges are equivalent.
- Raw output for the second no-backing phase is not removed before qcow2 restore, leaving cleanup dependent on later test/fixture behavior.
- Tests use string decoding for bytes read from qcow2, which assumes test data is compatible with UTF-8-like generated strings.

## Test signals
Signals include exact byte equality between output images and expected snapshot/backing composition, matching volume checksums, non-empty volume/backing reads, absence of output files after cleanup, preserved backing-file bytes after restore-to-file, and correct behavior across both raw and qcow2 formats.
