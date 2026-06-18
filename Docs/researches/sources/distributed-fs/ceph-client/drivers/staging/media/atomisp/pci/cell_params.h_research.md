# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/cell_params.h

Purpose: defines SP cell memory/cache/fifo parameter constants for the atomisp CSS build.

Important APIs/types/functions: macros describe SP PMEM log width, icache tag/set/associativity/block address bits, derived `SP_ICACHE_ADDRESS_BITS`, `SP_PMEM_DEPTH`, FIFO depths, and `SP_SLV_BUS_MAXBURSTSIZE`.

Control flow: no executable flow. These constants feed compile-time sizing and hardware model configuration.

State and persistence: none.

Dependencies and integration: uses `BIT()` for `SP_PMEM_DEPTH` and is consumed by CSS/SP low-level code that needs cell dimensions.

Risks and test signals: hardware parameter drift can break firmware memory layout. Build tests and firmware load/boot tests are the main signals; static checks should ensure `BIT()` is available to includers.
