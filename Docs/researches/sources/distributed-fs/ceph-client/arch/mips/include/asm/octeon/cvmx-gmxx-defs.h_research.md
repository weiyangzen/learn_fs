# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gmxx-defs.h

## Purpose
`cvmx-gmxx-defs.h` is the generated-style CSR map for Octeon GMX Ethernet MAC blocks. It gives C code address helpers for per-interface and per-port GMX registers, plus 64-bit union layouts for interface mode, port configuration, receive filtering, receive and transmit interrupt status, XAUI/SPI controls, backpressure override, pause packet timing, and MAC address state.

## Important APIs, Types, And Functions
The exported address helpers include `CVMX_GMXX_INF_MODE`, `CVMX_GMXX_PRTX_CFG`, RX address CAM registers `CVMX_GMXX_RXX_ADR_CAM0` through `CAM5`, `CVMX_GMXX_RXX_ADR_CAM_EN`, `CVMX_GMXX_RXX_ADR_CTL`, `CVMX_GMXX_RXX_FRM_CTL`, `CVMX_GMXX_RXX_INT_EN`, `CVMX_GMXX_RXX_INT_REG`, `CVMX_GMXX_RX_PRTS`, `CVMX_GMXX_SMACX`, TX timing/control registers, `CVMX_GMXX_TX_INT_EN`, `CVMX_GMXX_TX_INT_REG`, `CVMX_GMXX_TX_OVR_BP`, and XAUI/SPI-specific controls. Offset macros mask port offsets to 0..3 and block IDs to the supported GMX block range.

The main union families are `cvmx_gmxx_inf_mode`, `cvmx_gmxx_prtx_cfg`, RX frame/address/int unions, `cvmx_gmxx_rxx_rx_inbnd`, `cvmx_gmxx_rx_xaui_ctl`, TX threshold/int/backpressure unions, and SPI/XAUI TX controls. Several unions contain chip-specific layouts, so callers must select fields matching the active Octeon model.

## Control Flow
There is no runtime algorithm beyond static inline address calculation. Consumers call the helpers, read or write the CSR with `cvmx_read_csr()`/`cvmx_write_csr()`, fill the appropriate union, and interpret status bits. Higher-level helper implementations use these definitions when probing, enabling, and link-setting RGMII, SGMII, SPI, and XAUI packet interfaces.

## State And Persistence
All persistent state is hardware state in GMX CSRs. Writes can enable or disable MAC ports, change duplex/speed, change accepted frame types, set multicast/address CAM behavior, configure pause/backpressure, and clear or enable interrupt bits. No software state is stored in the header.

## Dependencies And Integration Points
The file depends on `CVMX_ADD_IO_SEG`, `uint64_t`, endian bitfield configuration, and Octeon CSR accessors supplied elsewhere. It integrates with the `cvmx-helper-*` interface bring-up code, interrupt setup through `__cvmx_interrupt_gmxx_enable(int interface)`, PHY/link configuration, and packet input/output blocks such as ASX, IPD, PIP, and PKO.

## Risks
Register programming is model and port-mode sensitive. The masked address helpers can silently alias out-of-range offsets, so caller validation is important. Using the wrong chip-specific union view can program reserved or differently-defined bits. Interrupt status fields are generally write-one-to-clear hardware state, so read/modify/write code needs care. Link settings must stay synchronized with PHY autonegotiation and board wiring.

## Test Signals
Useful signals include successful helper probe/enable for every interface mode, observed GMX mode matching board straps, link transitions reflected in RX in-band and helper link info, no unexpected RX/TX interrupt bits after traffic, correct pause/backpressure behavior, and loopback or packet tests that exercise per-port address CAM and frame control settings.
