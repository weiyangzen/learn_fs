## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi.h

### Purpose
`gaudi.h` is the compact Gaudi ASIC constants header. It defines BAR IDs and sizes, major device address windows, interrupt counts, queue-entry sizing, ASID limits, engine counts, and cache-line size used by the Gaudi driver.

### Important APIs, Types, And Functions
The exported constants include `SRAM_BAR_ID`, `CFG_BAR_ID`, `HBM_BAR_ID`, BAR sizes for SRAM and CFG, `CFG_BASE`/`CFG_SIZE`, `SRAM_BASE_ADDR`/`SRAM_SIZE`, `SPI_FLASH_BASE_ADDR`, PSOC and PCIe firmware scratch SRAM ranges, `DRAM_PHYS_BASE`, host physical aperture base/size, `GAUDI_MSI_ENTRIES`, `QMAN_PQ_ENTRY_SIZE`, `MAX_ASID`, `PROT_BITS_OFFS`, MME/TPC/DMA/NIC/IF engine counts, and `DEVICE_CACHE_LINE_SIZE`.

### Control Flow
The header has no executable code. Its constants drive probe-time resource setup, memory aperture validation, queue sizing, interrupt allocation, MMU/protection setup, and engine-array sizing in the Gaudi implementation. Downstream code treats these values as fixed hardware invariants.

### State, Persistence, And Dependencies
The file itself has no mutable state. It describes persistent hardware topology and physical address layout that remain valid across driver operations for a given Gaudi ASIC generation. It is included indirectly by private Gaudi driver headers and depends only on preprocessor use.

### Integration Points
Memory managers use the SRAM, HBM, CFG, host, and firmware regions; interrupt setup uses `GAUDI_MSI_ENTRIES`; command-submission code uses `QMAN_PQ_ENTRY_SIZE`; MMU/security code uses `MAX_ASID` and `PROT_BITS_OFFS`; topology code sizes arrays for 8 TPCs, 8 DMA channels, 4 MME engines, 5 NIC macros, and 10 NIC engines.

### Risks
These constants are global assumptions. A wrong BAR ID or aperture size can break PCI mapping, an incorrect host physical range can allow bad DMA translations, and wrong engine counts cause out-of-bounds register loops or missing hardware initialization. `PROT_BITS_OFFS` is particularly sensitive because security code derives protection registers from it.

### Test Signals
Probe should map all BARs with expected sizes, firmware load should land in the documented SRAM/HBM offsets, MMU tests should respect `MAX_ASID`, and topology reporting should match the expected MME/TPC/DMA/NIC counts. Command-submission tests should verify queue-entry stride assumptions and cache-line alignment behavior.
