<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dbi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dbi_regs.h

## Purpose
`pcie_dbi_regs.h` maps the PCIe DesignWare DBI/configuration-space register block for Gaudi2. It gives the driver symbolic addresses for standard PCI header fields, capabilities, AER, secondary PCIe capabilities, link training features, lane margining, LTR, RAS/vendor-specific areas, and analysis counters.

## Important APIs, types, and functions
The file exports `mmPCIE_DBI_*` macros only. Key groups include device/vendor, command/status, class/revision, BAR0-BAR5, subsystem IDs, capability pointer, MSI and MSI-X capability registers, PCIe capability and device/link control/status registers, AER uncorrectable/correctable status/mask/severity and header-log registers, secondary PCIe and 16 GT/s capability/status/control registers, lane margin control/status per lane, LTR capability/latency registers, RAS/vendor-specific headers, and event/time-based analysis control/data registers.

## Control flow
There is no executable flow. PCIe setup and diagnostics write DBI registers to expose endpoint identity, BAR layout, MSI/MSI-X tables, capability behavior, and error handling. Error paths read AER and lane/link logs. Some writes may require toggling DBI read-only write enable through the auxiliary block before touching normally read-only fields.

## State and persistence
DBI state is PCIe endpoint configuration state. It can be reset by FLR, hot reset, conventional reset, or controller reinitialization and must align with Linux PCI core expectations. AER/log registers persist error evidence until cleared.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pcie_aux_regs.h` for controller-side command and DBI access policy and with `pcie_wrap_regs.h` for MSI-X and transaction wrapping. It interfaces indirectly with Linux PCI enumeration and error recovery.

## Risks and test signals
Incorrect DBI definitions can cause invalid PCI identity, broken BAR mapping, missing MSI-X, or misleading AER logs. Test signals include successful enumeration with expected vendor/device/class IDs, correct BAR resources, enabled MSI-X vectors, valid link capabilities, AER injection/reporting, and no DBI write failures when changing writable config-space fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_dbi_regs.h -->
