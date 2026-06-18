# sources/distributed-fs/ceph-client/scripts/extract_xc3028.pl

Purpose: Extracts XC2028/XC3028 firmware blobs from specific Windows driver files and writes Linux firmware files `xc3028-v24.fw` and/or `xc3028-v27.fw`.

Important APIs/functions: `verify()` checks driver md5 hashes. `get_hunk()` reads exact byte ranges. `write_le16()`, `write_le32()`, and `write_le64()` emit little-endian metadata. `write_hunk()` copies raw bytes. `write_hunk_fix_endian()` copies firmware bytecode while swapping two-byte length words and payloads. `main_firmware_24()` and `main_firmware_27()` encode hard-coded descriptor tables and source offsets. `extract_firmware()` chooses available source drivers and invokes generation.

Control flow: If `UDXTTM6000.sys` exists, verifies the v2.4 hash, opens it, writes a padded firmware name, version 516, descriptor count 77, and many descriptors. If `hcw85bda.sys` exists, verifies the v2.7 hash, writes version 519 and 80 descriptors. Each descriptor writes type, id, optional IF frequency, size, and byte range payload. The script prints `Firmwares generated.` at the end even if no source file was present.

State/persistence: Reads fixed source filenames from the current directory. Writes firmware output files in the current directory. Uses global Perl filehandles `INFILE` and `OUTFILE` and global debug flag.

Dependencies/integration: Perl, `md5sum`, exact vendor driver file versions, and Linux firmware loader expectations for descriptor format.

Risks: The descriptor table is hard-coded and fragile; offset or size mistakes corrupt firmware. `use strict` is commented out, increasing typo risk. It relies on external `md5sum` via shell command string. It does not fail when neither source file exists. Output files are overwritten.

Test signals: Hash verification against known driver files, generated firmware md5/size comparison with known-good outputs, no-source behavior, short read failure, and descriptor count consistency with emitted descriptors.
