# sources/distributed-fs/ceph-client/rust/kernel/io/resource.rs

## Purpose
`io/resource.rs` wraps Linux `struct resource` and requested resource regions. It exposes resource metadata and RAII release for busy I/O or memory ranges.

## Important APIs, Types, and Functions
`Region` owns a non-null resource returned by `__request_region` and the `CString` name passed to C. It derefs to `Resource` and releases in `Drop`. `Resource` wraps `bindings::resource` and provides `from_raw`, `request_region`, `size`, `start`, `name`, and `flags`. `Flags` wraps resource flag bits with `contains`, bitwise operators, and constants `IORESOURCE_IO`, `IORESOURCE_MUXED`, `IORESOURCE_MEM`, and `IORESOURCE_MEM_NONPOSTED`.

## Control Flow
`request_region` calls `__request_region` with start, size, name pointer, and flags. A null return means the region was unavailable. `Region::drop` inspects flags to call `release_mem_region` for memory ranges or `release_region` otherwise. Resource accessors directly read C fields or call `resource_size`.

## State and Persistence
`Resource` is a borrowed view of C resource state. `Region` owns an active busy reservation until dropped and keeps the name allocation alive because C stores its pointer.

## Dependencies and Integration Points
This module is used by `io::mem` exclusive mapping and bus resource wrappers. It depends on C ioport resource APIs and kernel `CString`.

## Risks
`Resource::from_raw` is unsafe and requires the pointer to remain valid and exclusively accessed through the returned reference. Dropping `Region` chooses release function based on current flags; inconsistent flags could release through the wrong API. Callers must pass correct start/size subranges.

## Test Signals
Tests should cover successful and conflicting reservations, memory versus I/O release paths, null resource names, nonposted flag detection, flag operators, and name lifetime through drop.
