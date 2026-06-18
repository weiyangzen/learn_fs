# File Research: sources/block-storage/util-linux/libblkid/src/fuzz.c

## Purpose
Fuzz harness for libblkid probing over arbitrary byte inputs.

## Main Components
- `process_file()` opens a probe from a filename, enables partition and superblock probing, requests broad superblock flags including bad-checksum allowance, and runs `blkid_do_safeprobe()`.
- `LLVMFuzzerTestOneInput()` writes fuzz data to a temporary file, processes it, closes/unlinks the file, and returns 0.
- Non-fuzzer `main()` processes files listed on the command line and prints `OK` or `FAILED`.

## Dependencies and Interactions
Built by Autotools test/fuzz targets. It exercises partition and superblock parsers together through the safe-probe path.

## Research Notes
The harness deliberately enables many result flags to increase parser coverage. It treats safe-probe internal failures as fuzz-relevant only through return status, not assertions.
