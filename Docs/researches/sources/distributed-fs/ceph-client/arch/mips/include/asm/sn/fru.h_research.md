<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/fru.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/fru.h

Purpose: Defines field-replaceable-unit confidence records used by SGI SN firmware/kernel diagnostics for memory, CPU, and PCI bus components.

Important APIs/types/functions: `confidence_t`, `kf_mem_t`, `kf_cpu_t`, and `kf_pci_bus_t` with maximum DIMM and PCI-device counts.

Control flow: Diagnostic code fills confidence values indicating likely failing components, and inventory/error reporting code interprets those values.

State and persistence: The structs persist diagnostic belief/confidence state associated with FRUs. They do not allocate or update state themselves.

Dependencies and integration points: Used by `klconfig.h` and SN diagnostic/inventory paths.

Risks: Array sizes are fixed ABI-like firmware assumptions. Misinterpreting confidence values can lead to bad service/inventory reports.

Test signals: KLCONFIG/FRU parsing, synthetic error injection, and diagnostic inventory output tests are useful.

Source read size: 44 lines, 1489 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/fru.h -->
