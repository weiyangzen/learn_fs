# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_internal.h

Purpose: private libfdt helpers, alignment macros, unchecked pointer arithmetic, reserve-map accessors, internal endian loads, sequential-write magic, and compile-time validation-assumption controls.

Important APIs/macros: `FDT_ALIGN`, `FDT_TAGALIGN`, `FDT_RO_PROBE`, declarations for internal validators/string search/node end offset, raw `fdt_offset_ptr_` and writable variants, reserve-map pointer helpers, internal `fdt32_ld_`/`fdt64_ld_`, `FDT_SW_MAGIC`, `FDT_ASSUME_MASK`, assumption enum values, `can_assume_()`, and `can_assume(NAME)`.

Control flow/state: assumption bits are compile-time constants controlling whether validation and rollback branches are included or skipped. Helpers themselves are stateless but expose unchecked memory access intended only after probes or when assumptions allow it.

Dependencies/integration: included by every libfdt implementation file, tying modules to shared validation policy and internal memory layout.

Risks: `ASSUME_PERFECT` or related masks deliberately remove safety checks and can make malformed DTBs crash or corrupt memory. The unchecked pointer helpers must not leak as public API. Assumption combinations must be understood by embedders trying to minimize code size.

Test signals: builds with default assumptions and each optimized mask, malformed input behavior under safe defaults, code-size/performance configurations, and sanitizer/fuzzer coverage around unchecked helper call sites.
