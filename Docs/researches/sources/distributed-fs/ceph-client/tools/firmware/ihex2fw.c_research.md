<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/ihex2fw.c -->
# sources/distributed-fs/ceph-client/tools/firmware/ihex2fw.c

Purpose: Converts Intel HEX firmware data into the binary firmware record format consumed by the Linux kernel firmware loader.

Important APIs/types/functions: `struct ihex_binrec` stores linked records with address, length, and data. Helpers `nybble()` and `hex()` parse bytes while accumulating checksum. `process_ihex()` parses records; `file_record()` inserts into the global list, optionally sorted; `ihex_binrec_size()` calculates serialized size; `output_records()` writes network-endian records and a zero-length EOF record. Options are `-w` for 16-bit length fields, `-s` sorting, and `-j` including start-address records.

Control flow: `main()` parses options, opens or uses stdin/stdout, mmaps the input, parses records, then serializes the accumulated list. `process_ihex()` scans for `:`, validates length/checksum, handles data records, EOF, extended segment/linear address records, and optional start address records.

State and persistence: Runtime globals control sorting, wide records, and jump inclusion; `records` is a global linked list. Persistent output is the binary `.fw` stream. Input is memory-mapped and records are heap allocated until process exit.

Dependencies/integration: Uses POSIX file APIs, `mmap`, endian conversions from `<arpa/inet.h>`, and Linux-style alignment macros. It integrates with firmware build workflows that need `.HEX` to kernel binary firmware conversion.

Risks/tests: Risks include stdin with `mmap` when size is not meaningful, unchecked short `fread` equivalent absent because of mmap, memory leaks on parse errors, wide-record compatibility, checksum edge cases, and integer/address wraparound. Test signals are known Intel HEX fixtures for record types 00-05, bad checksum, unsorted vs sorted output, `-j`, stdin/stdout, and binary EOF record validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firmware/ihex2fw.c -->
