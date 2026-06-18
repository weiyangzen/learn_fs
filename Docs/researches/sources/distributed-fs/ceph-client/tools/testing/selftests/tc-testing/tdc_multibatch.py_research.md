# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_multibatch.py

## Purpose
Thin wrapper that generates multiple flower filter batch files by repeatedly invoking `tdc_batch.py`.

## Important APIs, Types, and Functions
Arguments are `device`, output `dir`, `num_filters`, `num_files`, `operation`, `--file_prefix`, `--duplicate_handles`, `--handle_start`, and `--mac_prefix`.

## Control Flow
After parsing arguments, it builds output filenames from prefix, operation, and index. It calls `./tdc_batch.py` via `os.system()` for each file, passing filter count, handle start, operation, MAC prefix, device, and output path. Unless `--duplicate_handles` is set, it advances the handle start by `num_filters` per file.

## State and Persistence Behavior
Persists generated batch files in the requested directory. Handle and MAC-prefix state are local loop variables.

## Dependencies and Integration Points
Depends on Python `argparse`, `os.system`, the current working directory containing `tdc_batch.py`, and a pre-existing output directory. It supports TDC batch-scaling tests that need several batch files.

## Risks and Edge Cases
Uses shell command construction without quoting, so paths/devices should be trusted simple strings. It does not check `os.system()` return status. Output directory creation is left to the caller.

## Test Signals
Signals include the expected number of files, expected line count per file, non-overlapping or duplicated handle ranges depending on the flag, and distinct MAC prefixes per file.
