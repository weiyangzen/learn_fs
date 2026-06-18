# sources/distributed-fs/ceph-client/lib/crc/gen_crc64table.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/gen_crc64table.c` is a host build program that generates lookup tables for generic CRC64 ECMA and CRC64-NVME.

## Important APIs, Types, and Functions

Important functions are `generate_reflected_crc64_table`, `generate_crc64_table`, `output_table`, `print_crc64_tables`, and `main`. Constants are `CRC64_ECMA182_POLY` and `CRC64_NVME_POLY`; generated arrays are `crc64table` and `crc64nvmetable`.

## Control Flow

The program fills the ECMA table in MSB-first order and the NVME table in reflected LSB-first order, then prints a generated-file banner, required includes, and two cacheline-aligned `u64` arrays.

## State and Persistence Behavior

Only process-local arrays are mutated. Kbuild redirects stdout to the persistent generated header `crc64table.h`.

## Dependencies and Integration Points

Dependencies include host `stdio.h` and `inttypes.h`. The Makefile builds and runs this host program before compiling `crc64-main.o`.

## Risks and Edge Cases

The two polynomial orientations are different; swapping generator functions or constants would silently corrupt one variant. Output formatting must remain valid kernel C and deterministic.

## Test Signals

Signals include generated header rebuild, known CRC64 ECMA and NVME vectors, deterministic output diffs, and successful compilation of `crc64-main.c` after clean builds.

## Read Coverage

Source read size: 88 lines, 1864 bytes.
