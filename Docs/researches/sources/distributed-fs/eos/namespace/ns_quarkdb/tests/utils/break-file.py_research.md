# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/utils/break-file.py

## Purpose
`break-file.py` is a Python 2 test utility for corrupting a target file by overwriting random byte ranges with random bytes. It is intended to generate damaged metadata or data files for corruption-path tests.

## Important APIs, Types, and Functions
The only named function is `printHelp()`, which prints the expected command-line form. The main block reads `filename`, optional `numRegions`, and optional maximum region size values, uses `os.stat()` to determine file size, opens the file in read/write mode, chooses random offsets and sizes, builds an `array.array('c')`, and writes random characters into the file.

## Control Flow
The script validates argument count, parses integer options, stats the requested file, then loops `numRegions` times. Each iteration chooses an offset within the file, chooses a random region size bounded by `maxRegionSize`, clamps the offset so the write stays inside the file, seeks, creates random bytes, and writes them. It exits with distinct nonzero codes for missing arguments, stat failure, and I/O failure.

## State and Persistence Behavior
The script destructively modifies the input file in place. It does not create backups, does not use atomic replacement, and does not seed the PRNG for reproducibility. Because the file is opened as `"r+"`, writes occur directly against the original file descriptor.

## Dependencies and Integration Points
It depends only on Python standard modules `sys`, `os`, `random`, and `array`. It likely feeds namespace or serialization corruption tests by damaging files outside the script.

## Risks and Edge Cases
The code is Python 2-only: print statements, `except OSError, e`, `xrange`, `file()`, and `array('c')` are incompatible with Python 3. There is also an apparent parsing bug: when four arguments are supplied, `numRegions = int(sys.argv[3])` is assigned again instead of assigning `maxRegionSize`, so the documented maximum region size argument is ignored and the region count is overwritten. Empty files can also cause invalid offset behavior because random offset and clamping assume a positive size.

## Test Signals
No direct tests are in this file. Useful signals would verify argument parsing, Python version expectations, non-empty file mutation, and preservation of file length.
