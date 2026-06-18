# sources/distributed-fs/ceph-client/tools/perf/util/debuginfo.h

## Purpose

`debuginfo.h` declares perf's DWARF debuginfo wrapper and provides no-op fallback definitions when libdw or debuginfod support is unavailable.

## Important APIs, Types, and Functions

With `HAVE_LIBDW_SUPPORT`, `struct debuginfo` contains `Dwarf *`, `Dwfl_Module *`, `Dwfl *`, bias, and build ID. It declares `debuginfo__new()`, `debuginfo__delete()`, and `debuginfo__get_text_offset()`. Without libdw, the same APIs are inline stubs returning `NULL` or `-EINVAL`. `get_source_from_debuginfod()` is declared or stubbed depending on `HAVE_DEBUGINFOD_SUPPORT`.

## Control Flow

The header chooses real or stub APIs at compile time. Stub paths avoid linking DWARF/debuginfod code while allowing callers to compile with graceful failure handling.

## State and Persistence Behavior

Real state is allocated in `debuginfo.c`; stub state is an empty struct. Debuginfod output path allocation is available only with support enabled.

## Dependencies and Integration Points

It depends on errno values and Linux compiler annotations. With libdw, it includes `dwarf-aux.h`. It integrates symbol/source/probe code with optional DWARF availability.

## Risks and Edge Cases

Callers must check for `NULL` debuginfo and negative offsets because unsupported builds compile successfully but do not provide functionality. The stub typedef `Dwarf_Addr` as `void` can expose misuse if callers assume arithmetic in unsupported builds.

## Test Signals

Build matrix tests should include libdw on/off and debuginfod on/off. Runtime tests should confirm unsupported builds return `-EINVAL` or `-ENOTSUP` and supported builds open real DWARF and source lookup data.
