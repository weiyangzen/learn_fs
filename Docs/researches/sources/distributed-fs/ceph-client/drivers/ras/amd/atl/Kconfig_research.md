# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Kconfig

## Purpose
Kconfig entries for the AMD Address Translation Library.

## Important APIs, types, and functions
`AMD_ATL` is a tristate depending on `AMD_NB`, `X86_64`, `RAS`, `AMD_NODE`, and `MEMORY_FAILURE`, default `N`. Help text positions it as a library for implementation-specific address translation needed for DRAM ECC and OS-based error handling on Zen systems. `AMD_ATL_PRM` depends on `AMD_ATL && ACPI_PRMT` and defaults to yes.

## Control flow
No runtime control flow. Symbol values decide whether `amd_atl.o` and optional PRM support are built.

## State and persistence
No runtime state in Kconfig; configuration persists in `.config`.

## Dependencies and integration
Connects AMD northbridge/node support, memory failure handling, ACPI PRMT, and RAS consumers such as FMPM or machine-check decoding.

## Risks
`AMD_ATL_PRM` uses `def_bool y`, so enabling ACPI PRMT with ATL automatically builds PRM integration. ATL is unavailable without `MEMORY_FAILURE`, which may limit translation consumers in configs that otherwise want address decoding.

## Test signals
Kconfig dependency/visibility tests across x86_64, RAS, AMD_NB, AMD_NODE, MEMORY_FAILURE, and ACPI_PRMT combinations, plus module and built-in builds.
