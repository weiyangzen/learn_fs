# sources/distributed-fs/ceph-client/lib/crc/crc32-main.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc32-main.c` provides generic table-driven CRC32, big-endian CRC32, and CRC32C, and dispatches to architecture accelerators when configured.

## Important APIs, Types, and Functions

Exported APIs are `crc32_le`, `crc32_be`, `crc32c`, and when arch support is enabled `crc32_optimizations`. Internal generic helpers are `crc32_le_base`, `crc32_be_base`, and `crc32c_base`. It includes generated `crc32table.h` for `crc32table_le`, `crc32table_be`, and `crc32ctable_le`.

## Control Flow

Each generic helper loops byte-by-byte through the appropriate lookup table and shift direction. With `CONFIG_CRC32_ARCH`, the file includes `$(SRCARCH)/crc32.h`, which defines `crc32_*_arch` wrappers and optimization reporting. Without arch support, those names alias to the base helpers. Optional module init delegates to arch static-key setup.

## State and Persistence Behavior

Generated lookup tables are read-only. Architecture headers may define static keys. CRC state is passed and returned by value.

## Dependencies and Integration Points

Dependencies include generated host-program output, `linux/crc32.h`, module exports, and architecture headers for ARM, ARM64, LoongArch, MIPS, PPC, RISCV, S390, SPARC, or X86. Many filesystems, networking code, and storage protocols use these helpers.

## Risks and Edge Cases

The generic functions do not perform final xor; callers own seed/finalization conventions. Architecture wrappers must preserve exact semantics for LE, BE, and CRC32C variants. Generated table freshness is required for correct builds.

## Test Signals

Signals include standard CRC32/CRC32C vectors, BE vectors, zero and chunked updates, generated-table rebuilds, arch fallback/acceleration comparisons, `crc32_optimizations()` flags, and KUnit benchmark coverage.

## Read Coverage

Source read size: 105 lines, 2763 bytes.
