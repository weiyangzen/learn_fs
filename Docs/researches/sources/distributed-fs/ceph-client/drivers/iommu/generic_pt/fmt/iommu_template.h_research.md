# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_template.h

## Purpose

`iommu_template.h` is the thin preprocessor dispatcher that includes the selected format header, the shared IOMMU page-table implementation, and optional KUnit suites for one format instantiation.

## Important APIs, Types, and Functions

- `PTPFX_RAW` and `PTPFX`: generated prefix names based on `PT_FMT` and optional `PT_FMT_VARIANT`.
- Includes `PTFVMOD(PT_FMT, h)`: the selected format header.
- Includes `../iommu_pt.h`: shared map/unmap/init/deinit implementation.
- Under `GENERIC_PT_KUNIT`, includes `../kunit_generic_pt.h` and `../kunit_iommu_pt.h`.

## Control Flow

Wrapper `.c` files define `PT_FMT`, optional variants, and supported features, then include this file. The preprocessor constructs unique symbol prefixes and expands the same shared implementation for each format.

## State and Persistence Behavior

The file has no state but determines symbol names and which code is compiled into each object.

## Dependencies and Integration Points

It depends on the macro utilities in `linux/generic_pt/common.h`, format headers under `fmt/`, and KUnit headers when building test objects.

## Risks and Edge Cases

Preprocessor naming must avoid collisions between base formats and variants. Any wrapper missing `PT_FMT` or defining an inconsistent variant will fail or generate wrong symbol names.

## Test Signals

Build all wrappers together, including `iommu_mock.c`, and verify distinct exported symbols and distinct KUnit suite names for each instantiation.
