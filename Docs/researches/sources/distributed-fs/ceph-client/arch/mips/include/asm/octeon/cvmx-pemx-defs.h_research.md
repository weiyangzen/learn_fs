# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pemx-defs.h

## Purpose
`cvmx-pemx-defs.h` is the generated-style CSR map for Octeon PEM PCI Express MAC blocks. It gives kernel and SDK code symbolic addresses and typed 64-bit views for endpoint/root-complex PCIe configuration, BAR translation, interrupt, diagnostic, BIST, credit, and peer-to-peer window registers. The file contains no executable logic beyond address macros; its purpose is to let callers perform correctly named `cvmx_read_csr()` and `cvmx_write_csr()` accesses against PEM block 0 or 1.

## Important APIs, Types, And Functions
The exported API surface is macro based. `CVMX_PEMX_*` macros compute CSR addresses with `CVMX_ADD_IO_SEG()`, masking `block_id` to one bit and array offsets to the register-supported width. Key address families include `CVMX_PEMX_BAR1_INDEXX`, `CVMX_PEMX_BAR2_MASK`, `CVMX_PEMX_BAR_CTL`, `CVMX_PEMX_CFG_RD`, `CVMX_PEMX_CFG_WR`, `CVMX_PEMX_P2N_BAR{0,1,2}_START`, `CVMX_PEMX_P2P_BARX_{START,END}`, `CVMX_PEMX_INT_{SUM,ENB,ENB_INT}`, and `CVMX_PEMX_TLP_CREDITS`.

Important typed register views include `union cvmx_pemx_bar1_indexx` for BAR1 address-valid, endian-swap, cache, and address-index fields; `cvmx_pemx_bar_ctl` for BAR1 sizing and BAR2 enable/cache/endian policy; `cvmx_pemx_ctl_status` for PCIe link/control behavior; `cvmx_pemx_dbg_info` and `cvmx_pemx_dbg_info_en` for PCIe protocol error latches and masks; `cvmx_pemx_int_sum` and enable variants for interrupt causes; and `cvmx_pemx_tlp_credits`, including a CN61xx-specific view.

## Control Flow
There is no runtime control flow in this header. Consumers build a union, set or read bitfields, then access the CSR address macro. Configuration flows normally program BAR translation windows, set `CVMX_PEMX_CTL_STATUS` link/error policy bits, enable interrupt summary bits, and inspect BIST, diagnostic, debug, and credit registers during PCIe bring-up or fault handling.

## State And Persistence
All state represented by the file is hardware state in PEM CSRs. Writes persist in the PCIe block until reset or later reconfiguration, not in memory owned by this header. `CFG_RD` and `CFG_WR` model PCI configuration transactions by packing a 32-bit config address and 32-bit data word into one CSR view. BAR and P2P/P2N start/end registers persist address-translation policy that directly affects DMA and memory-window routing.

## Dependencies And Integration Points
The header depends on Octeon CSR access infrastructure, `uint64_t`, `CVMX_ADD_IO_SEG`, and `__BIG_ENDIAN_BITFIELD` layout selection. It integrates with PCIe initialization, interrupt handling, and low-level board support that knows which PEM blocks are present. The bitfield unions are shared contracts between C code and Cavium hardware documentation.

## Risks
The address macros mask invalid block IDs and offsets instead of rejecting them, so caller mistakes can silently target a different PEM or BAR slot. Register bitfield layout depends on the compiler honoring the expected endian bitfield convention. Hardware errata or model differences matter: the `cvmx_pemx_tlp_credits` union already carries a CN61xx-specific view, and other fields may be reserved or differently interpreted on unsupported chips. BAR and P2P window mistakes can corrupt PCIe address translation, while debug and interrupt bits may be write-one-to-clear or latch-sensitive depending on hardware semantics outside this header.

## Test Signals
Useful signals are compile coverage for both endian layouts, CSR address checks for each `block_id` and indexed macro, PCIe link bring-up that validates `CTL_STATUS` and `DIAG_STATUS`, BIST pass bits after reset, interrupt-mask and interrupt-summary behavior under injected PCIe errors, and BAR translation tests that confirm endpoint-to-node and peer-to-peer windows route to the expected physical addresses.
