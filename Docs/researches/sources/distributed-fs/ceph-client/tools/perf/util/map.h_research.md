# sources/distributed-fs/ceph-client/tools/perf/util/map.h

## Purpose

`map.h` defines the public structure and inline helpers for perf address maps. It is the contract for translating between process/kernel IPs and DSO offsets and for managing map lifetime.

## Important APIs, Types, and Functions

`DECLARE_RC_STRUCT(map)` stores start, end, pgoff, reloc, DSO pointer, refcount, protection, flags, mapping type, and status bits. `enum mapping_type` selects DSO-relative or identity address translation. Inline accessors expose fields and implement `map__dso_map_ip()`, `map__dso_unmap_ip()`, `map__map_ip()`, and `map__unmap_ip()`. Declared APIs cover constructors, get/put/zput, printing, source lines, loading, symbol lookup, fixups, kernel/BPF/OOL classification, address conversions, kmap access, and mutators.

## Control Flow

Most local flow is inline address conversion: DSO mappings subtract start and add pgoff for map IPs, while identity mappings return the input unchanged. The symbol-by-name iteration macros repeatedly call indexed lookup and advance through DSO name-sorted symbols until the default symbol-name match fails.

## State and Persistence Behavior

The header exposes mutable map state through setters. Refcounting is explicit with `map__get()`, `map__put()`, and `map__zput()`. Kernel map metadata is represented by trailing `struct kmap` storage accessed through functions declared here.

## Dependencies and Integration Points

The header depends on Linux refcount/list/rbtree/compiler/types, internal rc checking, DSO declarations, and symbol/thread/machine declarations. It is included by machine, maps, thread, annotation, mem, branch, and symbol code.

## Risks and Edge Cases

Inline access through `RC_CHK_ACCESS()` means callers must pass valid map objects. Incorrect mapping type silently changes all address resolution. The `map__for_each_symbol_by_name()` macro assumes DSO symbols are loaded and sorted by name. Anonymous/no-DSO detection is string based and must stay aligned with event filename conventions.

## Test Signals

Compile and unit tests should cover inline address translations for DSO and identity maps, refcount get/zput, setter/getter consistency, symbol iteration macros, anonymous/no-DSO classification strings, BPF image name recognition, and kernel map access error paths.
