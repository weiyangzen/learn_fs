<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/sl28vpd.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/sl28vpd.c

## Purpose
Parses the Kontron SMARC-sAL28 VPD layout and creates cells for serial number and base MAC address after validating header and CRC8.

## Important APIs, Types, And Functions
`struct sl28vpd_header` and `struct sl28vpd_v1` define the layout. `sl28vpd_v1_check_crc()` validates the CRC8 over the v1 structure. `sl28vpd_add_cells()` reads the header, checks magic/version, validates CRC, and adds cells from `sl28vpd_v1_entries`. `sl28vpd_mac_address_pp()` validates and increments MAC addresses by cell index.

## Control Flow
Probe assigns `layout->add_cells` and registers the layout. The add-cells callback reads the header from the backing provider, rejects invalid magic or unsupported versions, validates CRC, gets the layout DT container, and adds two cells: `serial-number` and `base-mac-address`.

## State And Persistence
No private persistent state. Generated cells live in the NVMEM core. VPD contents persist in the underlying provider.

## Dependencies And Integration Points
Depends on the NVMEM layout bus, direct NVMEM reads, OF layout child lookup, CRC8, and Ethernet address helpers. Consumers can reference serial and MAC cells by DT phandle.

## Risks
Only version 1 is supported. MAC post-processing rejects invalid base addresses and negative indexes, so consumers expecting derived MACs depend on correct `#nvmem-cell-cells` indexing. CRC polynomial/table must match board firmware.

## Test Signals
Valid v1 VPD parse, invalid magic, unsupported version, bad CRC, serial cell read, base MAC read, indexed MAC derivation, invalid base MAC rejection, and layout unbind/rebind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/sl28vpd.c -->
