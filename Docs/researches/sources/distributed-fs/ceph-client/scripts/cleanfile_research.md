# sources/distributed-fs/ceph-client/scripts/cleanfile

## Purpose
`cleanfile` rewrites text files in place to remove trailing whitespace, normalize space-tab sequences to tab stops, drop blank lines at EOF, and report lines exceeding a configurable width.

## Important APIs, Types, and Functions
`clean_space_tabs()` converts runs of spaces before tabs into the minimal tab-aligned form while preserving visual alignment. `strwidth()` computes visual width with tabs expanding to 8 columns. Argument parsing accepts `-width` or `-w`; all other arguments are files.

## Control Flow and State
For each file, the script verifies it is a regular file, opens it read/write in binary mode, scans for NUL bytes to avoid binary input, then rereads line by line. It tracks input and output byte counts, buffers non-final blank lines, and only rewrites/truncates when output size differs. State is in process memory and the target file is the only persistence.

## Dependencies and Integration
It depends on Perl and `File::Basename`. It is a developer cleanup helper and is intentionally destructive.

## Risks and Test Signals
Files are rewritten in place and `.swp` protection is not used here, so interruption during write can damage the target. Unicode width is not semantically handled beyond Perl character iteration. Test with binary files, CRLF endings, trailing blank lines, tab alignment cases, unchanged files, and width reporting.
