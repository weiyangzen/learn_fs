# sources/compression/zstd/tests/test-license.py

Purpose: This Python test enforces zstd's expected Meta copyright and dual BSD/GPL license text across selected source directories.

Important APIs and functions: Constants define `ROOT`, scanned relative directories, excluded subdirectories, suffixes, scan limits, expected license lines, and basename exceptions. `valid_copyright()` checks for a copyright line containing "Meta Platforms, Inc", no year or "present", and the literal "(c)" form. `valid_license()` searches for the expected four-line license block. `valid_file()` reads the first 10 KB and first 50 lines, applies exception sets, and reports failures. `exclude()` filters absolute path prefixes. `main()` globs recursively and returns nonzero if any file fails.

Control flow: On execution, the script builds absolute scan/exclude roots, walks each directory/suffix combination with `glob.glob(..., recursive=True)`, skips excluded files, validates each file, accumulates invalid paths, and prints either "Pass!" or "Fail!" with invalid file names.

State and persistence: There is no persistent state. It reads source files and prints diagnostics to stderr/stdout.

Dependencies and integration points: Uses only Python standard modules. It is intended for CI or release checks over `doc`, `examples`, `lib`, `programs`, `tests`, and `contrib/linux-kernel`.

Risks and test signals: Matching by basename exceptions can exempt files with the same name in other directories. `valid_license()` indexes `lines[b + l]` without an explicit bounds check, relying on the first expected line not appearing too close to EOF. The suffix match includes any path ending with the string, so `Makefile` is treated as a suffix. Pass/fail output and exit status are the test signals.
