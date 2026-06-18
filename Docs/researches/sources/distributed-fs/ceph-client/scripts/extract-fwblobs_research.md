# sources/distributed-fs/ceph-client/scripts/extract-fwblobs

Purpose: Extracts built-in firmware blobs from a non-stripped `vmlinux`.

Important APIs/commands: Uses `readelf -SW` to find `.rodata` address and file offset, `readelf -sW` plus awk to pair firmware start/end symbols, shell arithmetic to compute file offsets and sizes, and `dd` with byte skip to write each firmware file.

Control flow: Validates one argument, derives `.rodata` mapping, builds entries from symbol stream when `fw_end` is seen after a start symbol, strips `_fw_` prefix and `_bin` suffix from symbol names, computes offset/size, and writes `./${FW_NAME}`.

State/persistence: Writes extracted firmware files into the current directory. No temp files.

Dependencies/integration: Depends on bash, readelf, awk, dd, and Linux built-in firmware symbol naming conventions.

Risks: Assumes firmware symbols appear in start/end order in readelf output. Filename derivation trusts symbol names. It does not check `.rodata` discovery or duplicate names robustly. Firmware output can overwrite existing files.

Test signals: Run on a known non-stripped vmlinux with built-in firmware and compare extracted bytes/sizes; test missing argument, stripped image, no firmware symbols, and existing output names.
