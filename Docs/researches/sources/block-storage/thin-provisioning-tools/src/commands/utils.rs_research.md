# File Research: sources/block-storage/thin-provisioning-tools/src/commands/utils.rs

Shared command utility functions for path validation, range parsing, report selection, overwrite prompting, XML/metadata sniffing, and error-to-exit-code conversion.

Key items:
- `RangeU64` parses `start..end`, requiring two unsigned integers and `end > start`.
- `check_input_file`: requires regular file or block device, with clear ENOENT handling.
- `check_file_not_tiny`: requires at least 4096 bytes.
- `check_output_file`: requires at least 40960 bytes.
- `mk_report`: quiet report, terminal progress bar report, or simple report depending on flags/stderr TTY.
- `check_not_xml`: reads first 16 bytes and rejects files that look like XML metadata.
- `is_metadata`: reads first block and classifies known thin/cache/era superblock checksums.
- `check_overwrite_metadata`: prompts before overwriting a path that appears to contain metadata.
- `to_exit_code`: reports errors unless root cause is broken pipe and maps success to `OK`, failure to `USAGE`.

Notable details:
- XML sniffing treats read errors as non-XML in `check_not_xml`.
- Broken pipe handling accounts for both direct `io::Error` and `Arc<io::Error>` as wrapped by `quick_xml`.
