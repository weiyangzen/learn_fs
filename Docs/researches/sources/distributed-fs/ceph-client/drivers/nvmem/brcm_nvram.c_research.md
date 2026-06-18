<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/brcm_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/brcm_nvram.c

## Purpose
Exposes Broadcom I/O-mapped NVRAM as an NVMEM provider and dynamically creates cells for `name=value` variables, including MAC address post-processing.

## Important APIs, Types, And Functions
`struct brcm_nvram` stores copied NVRAM data, detected length, padding byte, and generated cell array. `brcm_nvram_copy_data()` maps flash/NVRAM, trims trailing padding, copies data into RAM, and initializes legacy bcm47xx NVRAM access. `brcm_nvram_parse()` validates the `FLSH` header and length. `brcm_nvram_add_cells()` scans variables and builds `nvmem_cell_info` entries. `brcm_nvram_read()` serves reads from the RAM copy and pads beyond actual data.

## Control Flow
Registered at `subsys_initcall_sync`, probe copies the MMIO region, parses the Broadcom header, discovers variable cells after the header, and registers NVMEM. For `et0macaddr`, `et1macaddr`, and `et2macaddr`, cells expose binary `ETH_ALEN` values rather than ASCII strings, with optional index-based address incrementing.

## State And Persistence
Driver state is a RAM snapshot of NVRAM data and generated cell metadata. The underlying NVRAM persists in flash/firmware storage, but this driver is read-only and does not write back changes. Padding byte preserves reads over unused space.

## Dependencies And Integration Points
Depends on platform MMIO, OF matching, NVMEM provider/consumer APIs, Broadcom bcm47xx NVRAM compatibility initialization, and Ethernet address helpers. Child DT nodes may map generated cells.

## Risks
Parsing modifies temporary delimiters inside the copied data and must restore them. Malformed variables without `=` stop cell generation. MAC string parsing can fail if board data uses unexpected formatting. Very large detected NVRAM only warns above 128 KiB.

## Test Signals
Test valid and invalid magic, length larger than mapped resource, padded trailing bytes, cells for ordinary strings and MAC addresses, indexed MAC consumers, and compatibility with existing bcm47xx NVRAM users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/brcm_nvram.c -->
