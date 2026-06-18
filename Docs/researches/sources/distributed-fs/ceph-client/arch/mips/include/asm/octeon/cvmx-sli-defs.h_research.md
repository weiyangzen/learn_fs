# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sli-defs.h

Purpose: defines selected OCTEON SLI/PCIe interface registers used for MSI receive addressing, port interrupt mapping, memory access timing, S2M port control, and memory-access subindex setup.

Important APIs/types/functions: `CVMX_SLI_PCIE_MSI_RCV` expands to `CVMX_SLI_PCIE_MSI_RCV_FUNC`, which returns a model-dependent MSI receive offset. Unions are `cvmx_sli_ctl_portx`, `cvmx_sli_mem_access_ctl`, `cvmx_sli_s2m_portx_ctl`, and `cvmx_sli_mem_access_subidx`, the last with a CN68XX layout variant.

Control flow: the one inline function switches on `cvmx_get_octeon_family()` and uses `OCTEON_IS_MODEL(OCTEON_CN78XX_PASS1_X)` to select the legacy versus newer MSI receive offset. All other content is passive CSR layout data for callers to read and write.

State and persistence: state is live PCIe/SLI hardware configuration. Port disable, interrupt routing, memory access timers, maximum word settings, read/write type, endian-swap controls, and base-address fields persist in CSRs until reset or reconfiguration.

Dependencies and integration points: includes `<uapi/asm/bitfield.h>` and relies on OCTEON model macros from `octeon-model.h`. It integrates with PCIe host/endpoint setup, MSI handling, SLI DMA windows, and memory-mapped access policy.

Risks: MSI address selection is chip-family sensitive; using the wrong offset can break interrupt delivery. CN68XX uses a different base-address field width, so generic programming can write invalid low bits. Port and endian-swap controls are low-level and can make PCIe memory windows inaccessible if misconfigured.

Test signals: runtime PCIe enumeration and MSI delivery are the main tests. Model-matrix tests should verify the returned MSI receive offset for CN6XXX, CN70XX, CN78XX pass 1, and newer CN7XXX families.
