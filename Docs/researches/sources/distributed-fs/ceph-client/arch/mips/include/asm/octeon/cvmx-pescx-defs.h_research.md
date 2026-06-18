# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pescx-defs.h

## Purpose
`cvmx-pescx-defs.h` defines the CSR addresses and typed register layouts for older Octeon PESC PCI Express controller blocks. It overlaps conceptually with the PEM header but targets the PESC register base and model family. The header supports PCIe control/status, configuration read/write, BAR and P2P window programming, BIST, diagnostic, debug, and credit accounting.

## Important APIs, Types, And Functions
The macro API exports `CVMX_PESCX_*` CSR address calculators. Main macros include `CVMX_PESCX_CTL_STATUS`, `CVMX_PESCX_CTL_STATUS2`, `CVMX_PESCX_CFG_RD`, `CVMX_PESCX_CFG_WR`, `CVMX_PESCX_BIST_STATUS`, `CVMX_PESCX_BIST_STATUS2`, `CVMX_PESCX_DBG_INFO`, `CVMX_PESCX_DBG_INFO_EN`, `CVMX_PESCX_P2N_BAR{0,1,2}_START`, `CVMX_PESCX_P2P_BARX_{START,END}`, and `CVMX_PESCX_TLP_CREDITS`.

Important unions are `cvmx_pescx_ctl_status` for link enable, lane swap, QLM configuration, bus/device number, posted-command and ECRC behavior; `cvmx_pescx_ctl_status2` for PCIe clock and reset state; `cvmx_pescx_dbg_info` and enable view for PCIe protocol diagnostics; `cvmx_pescx_bist_status` and `bist_status2` for SRAM/FIFO self-test latches; and BAR start/end unions for physical address windowing. Several unions expose chip-specific alternatives, including CN52xx pass 1 and CN56xx views.

## Control Flow
This file has no functions. The expected control flow is external: board/PCIe code computes a PESC block CSR address, writes configuration values through CSR helpers, and reads status or error latches. A normal bring-up path would hold or release PCIe reset through `CTL_STATUS2`, configure `CTL_STATUS`, program BAR windows, then enable or poll diagnostic/error status.

## State And Persistence
The persistent state is in the PCIe controller hardware. BAR registers determine address translation; control bits affect link behavior; debug and interrupt-like diagnostics expose latched error state; BIST registers expose hardware self-test results. The header itself allocates no state and has no memory persistence.

## Dependencies And Integration Points
It depends on Octeon CSR primitives and endian bitfield configuration. It integrates with the MIPS Octeon PCIe host/endpoint support, especially code that must distinguish PESC generation chips from PEM generation chips. The `CVMX_ADD_IO_SEG` addresses are part of the ABI between the kernel and Octeon coprocessor register map.

## Risks
The highest risk is applying PESC definitions to a PEM-based chip or vice versa, because both families expose similar concepts at different addresses and with different model-specific fields. Offset and block macros mask values, so out-of-range parameters wrap. The CN52xx/CN56xx alternate layouts mean generic `.s` accesses can be wrong on a pass-specific part. Link reset and BAR programming errors can make PCIe devices disappear or route DMA incorrectly.

## Test Signals
Test by validating computed CSR addresses against hardware manuals for block 0 and 1, reading BIST status after reset, toggling `CTL_STATUS2` reset/clock fields during link bring-up, confirming config-space reads and writes through `CFG_RD`/`CFG_WR`, exercising BAR translation with known DMA windows, and injecting or observing PCIe errors to confirm debug-info and enable masks match expected latches.
