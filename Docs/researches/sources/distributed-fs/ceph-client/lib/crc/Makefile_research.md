# sources/distributed-fs/ceph-client/lib/crc/Makefile

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/Makefile` maps CRC Kconfig symbols to generic objects, architecture-optimized objects, generated lookup-table headers, and tests.

## Important APIs, Types, and Functions

Important build variables are `obj-$(CONFIG_CRC*)`, composite objects `crc-t10dif-y`, `crc32-y`, and `crc64-y`, architecture additions under `CONFIG_CRC*_ARCH`, `hostprogs := gen_crc32table gen_crc64table`, `clean-files`, and generation commands `cmd_crc32` and `cmd_crc64`.

## Control Flow

The build first adds selected small CRC object files. Composite targets build main generic C files and optionally architecture-specific assembly/C objects while adding `-I$(src)/$(SRCARCH)` so main files include the correct arch header. CRC32 and CRC64 main objects depend on generated `crc32table.h` and `crc64table.h`, which are produced by host programs. ARM64 CRC64 removes no-FPU flags and adds FPU/crypto flags for the NEON inner object.

## State and Persistence Behavior

Build outputs include object files and generated table headers, which are cleaned by `clean-files`. There is no runtime state in the Makefile.

## Dependencies and Integration Points

The Makefile integrates with Kbuild, architecture directories, generated autoconf, host compiler support, and `lib/crc/tests/`. It depends on source names matching Kconfig architecture selections.

## Risks and Edge Cases

Mismatch between Kconfig defaults and object names breaks optimized builds. Generated table headers must be built before main objects. FPU flags for ARM64 CRC64 are sensitive because kernel code normally builds with FPU disabled. The PPC T10DIF object name must match the actual generated/included assembly target.

## Test Signals

Signals are per-architecture build tests for T10DIF/CRC32/CRC64 acceleration, clean rebuilds after deleting generated headers, `make clean` removing generated files, KUnit test object inclusion, and FPU flag inspection for `arm64/crc64-neon-inner.o`.

## Read Coverage

Source read size: 68 lines, 2124 bytes.
