# subset-b-000732 Research

Grouped research for Octeon MIPS helper and CSR headers under `sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gmxx-defs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gmxx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gpio-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gpio-defs.h

## Purpose
`cvmx-gpio-defs.h` maps Octeon GPIO CSRs and their bit layouts. It covers per-pin configuration, pin input/output data, interrupt enable/clear behavior, boot/debug enables, clock generator outputs, QLM-derived GPIO clocks, multicast behavior, and extended GPIO pin enable/configuration registers.

## Important APIs, Types, And Functions
Important address macros include `CVMX_GPIO_BIT_CFGX`, `CVMX_GPIO_XBIT_CFGX`, `CVMX_GPIO_RX_DAT`, `CVMX_GPIO_TX_SET`, `CVMX_GPIO_TX_CLR`, `CVMX_GPIO_INT_CLR`, `CVMX_GPIO_DBG_ENA`, `CVMX_GPIO_BOOT_ENA`, `CVMX_GPIO_CLK_GENX`, `CVMX_GPIO_CLK_QLMX`, `CVMX_GPIO_MULTI_CAST`, and `CVMX_GPIO_PIN_ENA`. The unions expose fields such as output enable, receive XOR, interrupt enable/type, debounce/filter count and select, clock selection/generation, sync selection, output selection, data masks, and special pin enables.

## Control Flow
The header has no code flow. Drivers configure each pin by composing `union cvmx_gpio_bit_cfgx`, then use set/clear CSRs to drive outputs and interrupt clear CSRs to acknowledge events. Clock-related GPIO uses the clock generator and QLM selector registers before a pin is configured to emit that source.

## State And Persistence
State lives in GPIO hardware CSRs. Pin muxing, output enable, filters, interrupt settings, and output latch state persist until changed or reset. Reading `CVMX_GPIO_RX_DAT` observes current pin state rather than maintained software state.

## Dependencies And Integration Points
The definitions require `CVMX_ADD_IO_SEG`, fixed-width integer types, and the kernel/endian bitfield configuration. Board support code, LED/control-plane drivers, management PHY reset code, and boot/debug pin handling use these CSRs. QLM clock fields tie GPIO behavior to high-speed lane clocking.

## Risks
Different Octeon families expose different GPIO counts and bit layouts; the generic, `cn30xx`, `cn52xx`, `cn61xx`, and `cn63xx` union variants must not be mixed blindly. Address macros mask offsets, so invalid pin numbers can target an unintended valid register. Misconfigured `tx_oe`, `rx_xor`, or interrupt type can invert signals or create interrupt storms.

## Test Signals
Test with pin loopback where available, verify set/clear changes the expected bit in `RX_DAT`, check debounce/filter behavior under toggling inputs, confirm interrupt clear semantics, and validate board-specific GPIO consumers such as reset lines, LED outputs, and QLM clock output selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gpio-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-board.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-board.h

## Purpose
`cvmx-helper-board.h` defines the board abstraction layer used by generic Octeon packet helper code. It isolates per-board PHY addressing, link discovery, interface port count overrides, management-port handling, PHY link set flags, and USB reference clock selection from common interface bring-up logic.

## Important APIs, Types, And Functions
The file defines `enum cvmx_helper_board_usb_clock_types`, `cvmx_helper_board_set_phy_link_flags_types_t`, and the fake management-port marker `CVMX_HELPER_BOARD_MGMT_IPD_PORT`. The exported hooks are `cvmx_helper_board_get_mii_address(int ipd_port)`, `__cvmx_helper_board_link_get(int ipd_port)`, `__cvmx_helper_board_interface_probe(int interface, int supported_ports)`, and `__cvmx_helper_board_usb_get_clock_type(void)`.

## Control Flow
Common helper code probes an interface, computes the hardware-supported port count, then calls the board probe hook to clamp or override the result for actual wiring. Link get/set logic asks this layer for PHY bus/address and current link state before programming GMX/PCS state. USB setup calls the clock hook to choose the reference source.

## State And Persistence
This header stores no state. Implementations usually consult bootloader-provided `cvmx_sysinfo` board type/revision and may read PHY registers through MDIO. Results affect persistent hardware state only when callers subsequently program link, PHY, or interface registers.

## Dependencies And Integration Points
It includes `cvmx-helper.h`, and therefore uses `union cvmx_helper_link_info`. It is integrated by RGMII/SGMII/XAUI/SPI helper implementations, PHY drivers, management Ethernet support, and USB initialization code.

## Risks
Every new board needs accurate switch cases. A wrong PHY address, bus encoding, port-count override, or USB clock type can make otherwise-correct generic helper code fail. The negative management IPD port is a sentinel and must not be treated as a normal port number by range checks.

## Test Signals
Board bring-up should verify expected port counts, MDIO reads for each IPD port, management-port PHY access, reported link speed/duplex under cable changes, and USB operation with the selected reference clock. Regression tests should cover unknown board types falling back safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-board.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-errata.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-errata.h

## Purpose
`cvmx-helper-errata.h` declares helper support for known Octeon hardware errata. In this slice it exposes one QLM workaround hook used to disable second-order clock-data-recovery behavior where required by the affected silicon.

## Important APIs, Types, And Functions
The single exported function is `__cvmx_helper_errata_qlm_disable_2nd_order_cdr(int qlm)`. It takes a QLM lane group number and has no return value, implying the implementation directly programs low-level QLM configuration registers.

## Control Flow
There is no inline flow. Interface bring-up or lane initialization code calls the errata helper before or during high-speed link setup when the chip model and QLM mode require the workaround.

## State And Persistence
Persistent state is the altered QLM hardware configuration. The header itself has no data. Because the function likely changes analog/serdes behavior, effects last until reset or later QLM reconfiguration.

## Dependencies And Integration Points
The declaration is included by `cvmx-helper.h` and is relevant to SGMII, XAUI, PCIe, or other helpers that share QLM lanes. It usually depends on model detection and low-level JTAG/QLM CSR access in its implementation.

## Risks
Errata hooks are deliberately hardware-specific. Calling the workaround on an unaffected model or wrong QLM can degrade link training, while omitting it on affected silicon can cause intermittent high-speed link failures. The absence of a return code means callers need external verification.

## Test Signals
Test by comparing link stability, error counters, and negotiation success across affected and unaffected chip revisions. Validate the hook is invoked only for intended model/QLM combinations and that repeated calls are harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-errata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-jtag.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-jtag.h

## Purpose
`cvmx-helper-jtag.h` declares QLM JTAG utilities used by Octeon helper code to initialize, shift, and update serial configuration state in QLM blocks. It is a low-level support interface for serdes/QLM tuning rather than a packet I/O API.

## Important APIs, Types, And Functions
The exported calls are `cvmx_helper_qlm_jtag_init()`, `cvmx_helper_qlm_jtag_shift(int qlm, int bits, uint32_t data)`, `cvmx_helper_qlm_jtag_shift_zeros(int qlm, int bits)`, and `cvmx_helper_qlm_jtag_update(int qlm)`. The shift function returns shifted-out data, letting callers read or verify QLM scan-chain state.

## Control Flow
Typical use is initialize the JTAG helper, shift a command or field sequence into a selected QLM, optionally shift zeros for padding, then issue update to latch the scan-chain value into live QLM controls. The header itself contains only declarations.

## State And Persistence
State is the QLM JTAG scan chain and latched QLM hardware configuration. Partial shifts are order-dependent and persist in the scan chain until completed or reset. No C storage is defined here.

## Dependencies And Integration Points
The functions integrate with QLM errata workarounds, SGMII/XAUI lane configuration, and any helper code that cannot configure QLM behavior through ordinary CSRs. They depend on Octeon low-level register access and correct model-specific scan-chain layout in the implementation.

## Risks
Wrong bit counts or QLM indexes can leave a lane group in a bad analog state. Because shifting is sequential, interrupted or reordered calls can corrupt configuration. Tests must account for silicon revisions with different scan-chain fields.

## Test Signals
Useful validation includes readback from `cvmx_helper_qlm_jtag_shift`, successful link training after update, idempotent init/update sequences, and regression coverage for every QLM index present on the target model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-jtag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-loop.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-loop.h

## Purpose
`cvmx-helper-loop.h` declares the helper implementation for Octeon's internal LOOP packet interface. LOOP is used for internal packet path testing or loopback-style traffic without external PHY link negotiation.

## Important APIs, Types, And Functions
The exported functions are `__cvmx_helper_loop_probe(int interface)` and `__cvmx_helper_loop_enable(int interface)`. It also defines `__cvmx_helper_loop_enumerate(int interface)` as an inline function that always returns 4 ports.

## Control Flow
Generic `cvmx_helper_interface_probe()` dispatches to the LOOP probe for interfaces reported in loop mode. Enumeration is fixed at four logical ports. After IPD is enabled and before normal packet I/O, common helper code calls the LOOP enable hook to configure the loop interface.

## State And Persistence
The header has no storage. The implementation programs packet-interface hardware state for LOOP operation, and that hardware configuration persists until changed or reset.

## Dependencies And Integration Points
It is included by `cvmx-helper.h` and participates in the common interface mode dispatcher. It interacts with IPD/PIP/PKO setup through the same helper framework as external Ethernet modes, but has no link-get or link-set API because there is no external PHY.

## Risks
The fixed four-port enumerate result can be wrong if used on unsupported silicon or without matching implementation checks. Code that assumes all helper interfaces have link APIs must special-case LOOP. Misconfiguring LOOP can hide real external-interface failures by passing only internal traffic tests.

## Test Signals
Test signals are successful probe counts, ability to send and receive internal packets on all four loop ports, no external PHY dependencies, and clean enable/disable behavior when packet I/O is reinitialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-loop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-npi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-npi.h

## Purpose
`cvmx-helper-npi.h` declares helper hooks for the NPI packet interface, a non-PHY packet path used by some Octeon systems to exchange packets with host or internal bus-side logic.

## Important APIs, Types, And Functions
The exported declarations are `__cvmx_helper_npi_probe(int interface)` and `__cvmx_helper_npi_enable(int interface)`. `__cvmx_helper_npi_enumerate` is a macro alias for the probe function, so enumeration and probing share one implementation.

## Control Flow
When generic helper code identifies an interface as NPI, it calls the probe/enumerate hook to determine available ports and later calls enable after IPD is ready. There are no per-port link APIs because NPI does not use ordinary Ethernet PHY autonegotiation.

## State And Persistence
State is entirely in hardware registers programmed by the implementation. The header stores no data. Enabled NPI state affects how IPD/PKO traffic is routed through the NPI block.

## Dependencies And Integration Points
The file is included by `cvmx-helper.h` and integrates with common packet I/O initialization, IPD enablement, and PKO port routing. It is related to IOB/NPI hardware definitions outside this header set.

## Risks
Aliasing enumeration to probe means probe side effects must be safe to repeat. Code that expects link status for every interface must avoid calling Ethernet PHY paths for NPI. Incorrect port counts can misroute PKO queues.

## Test Signals
Validate probe counts on boards that expose NPI, packet ingress and egress through the host/NPI path, repeated probe/enumerate idempotence, and correct interaction with IPD and PKO global initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-npi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-rgmii.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-rgmii.h

## Purpose
`cvmx-helper-rgmii.h` declares helper hooks for RGMII, GMII, and MII Ethernet interfaces. It provides the mode-specific operations used by the common helper layer to probe ports, enable ASX/GMX/PKO programming, query PHY link state, set MAC link parameters, and force internal loopback.

## Important APIs, Types, And Functions
The file exports `__cvmx_helper_rgmii_probe(int interface)`, aliases `__cvmx_helper_rgmii_enumerate` to that probe, declares `cvmx_helper_rgmii_internal_loopback(int port)`, and provides `__cvmx_helper_rgmii_enable`, `__cvmx_helper_rgmii_link_get`, and `__cvmx_helper_rgmii_link_set`.

## Control Flow
Generic helper code probes an interface, optionally lets board code override physical port count, enables the interface after IPD setup, then uses link get/set around PHY autonegotiation changes. Loopback can be requested per IPD port to echo internal and external packets through the RGMII path.

## State And Persistence
The implementation changes ASX, GMX, PKO, and possibly PHY hardware state. Link-set updates MAC speed, duplex, and flow-control-related settings to match PHY state. The header stores no software state.

## Dependencies And Integration Points
It depends on `union cvmx_helper_link_info` from `cvmx-helper.h` and integrates with board PHY hooks, GMX CSR definitions, ASX registers, IPD, and PKO. It is the mode backend for `CVMX_HELPER_INTERFACE_MODE_RGMII` and related GMII/MII operation.

## Risks
RGMII timing and PHY wiring are board-specific. Probe/enumerate aliasing requires a side-effect-safe probe. Link-set must match PHY autonegotiation exactly or traffic can fail despite link-up reporting. Loopback can mask external wiring faults if tests do not distinguish internal from external paths.

## Test Signals
Test all configured ports for PHY address discovery, link up/down transitions, 10/100/1000 speed and duplex combinations, packet traffic in both directions, internal loopback behavior, and absence of GMX RX/TX errors after link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-rgmii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-sgmii.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-sgmii.h

## Purpose
`cvmx-helper-sgmii.h` declares the mode-specific helper operations for SGMII interfaces. SGMII requires PCS/QLM configuration plus MAC setup, so the common helper layer delegates probe, enumeration, enablement, and link synchronization to this backend.

## Important APIs, Types, And Functions
The exports are `__cvmx_helper_sgmii_probe(int interface)`, `__cvmx_helper_sgmii_enumerate(int interface)`, `__cvmx_helper_sgmii_enable(int interface)`, `__cvmx_helper_sgmii_link_get(int ipd_port)`, and `__cvmx_helper_sgmii_link_set(int ipd_port, union cvmx_helper_link_info link_info)`.

## Control Flow
Probe determines how many SGMII ports are connected while leaving the interface down. Enable runs after IPD is enabled and before full packet I/O. Link get reads negotiated PCS/PHY state, and link set programs Octeon MAC/PCS state to match that result.

## State And Persistence
Persistent state is PCS/GMX/QLM and PHY hardware configuration. The header stores no variables. Link-set changes affect future packet transmission until the link is reconfigured.

## Dependencies And Integration Points
The API integrates with QLM/JTAG/errata helpers, board PHY hooks, GMX definitions, and the common `cvmx_helper_link_get/set` dispatcher. It is selected for `CVMX_HELPER_INTERFACE_MODE_SGMII`.

## Risks
SGMII depends on PCS autonegotiation and high-speed lane configuration. Calling link set with stale link info can misconfigure speed or duplex. Probe and enumerate are separate declarations, so implementations may have different side effects that common code must respect.

## Test Signals
Exercise probe counts, PCS link-up, PHY link changes, speed/duplex propagation into GMX, QLM errata paths on affected silicon, and packet traffic with error counters checked after negotiation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-sgmii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-spi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-spi.h

## Purpose
`cvmx-helper-spi.h` declares helper operations for SPI packet interfaces. It gives the common packet I/O helper layer a mode backend for probing connected SPI ports, enabling the interface, and translating link state into Octeon hardware settings.

## Important APIs, Types, And Functions
The declarations are `__cvmx_helper_spi_probe(int interface)`, `__cvmx_helper_spi_enumerate(int interface)`, `__cvmx_helper_spi_enable(int interface)`, `__cvmx_helper_spi_link_get(int ipd_port)`, and `__cvmx_helper_spi_link_set(int ipd_port, union cvmx_helper_link_info link_info)`.

## Control Flow
Probe leaves the interface down while determining port count. Enable is called with IPD enabled and PKO disabled so SPI/GMX state can be initialized before traffic begins. Link get and link set are used by the generic helper API to synchronize MAC state with negotiated or externally supplied link state.

## State And Persistence
The implementation writes SPI, GMX, PKO, and possibly PHY state; the header stores none. Configured link state persists in hardware until reset or a later link-set call.

## Dependencies And Integration Points
It is included by `cvmx-helper.h` and selected for `CVMX_HELPER_INTERFACE_MODE_SPI`. It depends on `union cvmx_helper_link_info` and integrates with board link discovery, GMX SPI CSR fields, IPD, and PKO queue setup.

## Risks
SPI packet interfaces have stricter bring-up ordering and timing than simple GMII modes. Calling enable before IPD readiness or after PKO is active can produce dropped or malformed traffic. Stale link info and board-specific port-count mistakes are common failure points.

## Test Signals
Validate SPI training/enable status, expected port count, link-state propagation, traffic under each configured port, GMX/SPI interrupt counters, and clean behavior across disable/reinitialize cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-util.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-util.h

## Purpose
`cvmx-helper-util.h` contains small common utilities for Octeon packet helpers. It declares mode-to-string, RED setup, version, GMX setup, IPD port mapping, and interface reverse-mapping functions, and it implements inline helpers for first/last IPD port lookup and freeing packet data attached to a work queue entry.

## Important APIs, Types, And Functions
Key APIs are `cvmx_helper_interface_mode_to_string`, `cvmx_helper_setup_red`, `cvmx_helper_get_version`, `__cvmx_helper_setup_gmx`, `cvmx_helper_get_ipd_port`, `cvmx_helper_get_first_ipd_port`, `cvmx_helper_get_last_ipd_port`, `cvmx_helper_free_packet_data`, `cvmx_helper_get_interface_num`, and `cvmx_helper_get_interface_index_num`.

## Control Flow
`cvmx_helper_get_first_ipd_port()` delegates to `cvmx_helper_get_ipd_port(interface, 0)`. `cvmx_helper_get_last_ipd_port()` adds the interface port count minus one. `cvmx_helper_free_packet_data()` reads the WQE buffer count, handles the special `NO_WPTR` case where the first packet buffer is also the WQE and must not be freed, then walks the linked buffer chain by reading the next pointer from `buffer_ptr.s.addr - 8` before returning each buffer to FPA.

## State And Persistence
Most APIs return derived configuration or program hardware elsewhere. The inline packet-free function mutates persistent FPA pool state by returning buffers and does not free the WQE itself. It relies on packet buffer back-pointers and next-buffer metadata stored in packet memory.

## Dependencies And Integration Points
It depends on `struct cvmx_wqe`, `union cvmx_buf_ptr`, `cvmx_ptr_to_phys`, `cvmx_phys_to_ptr`, and `cvmx_fpa_free`, plus common helper APIs. It is used by packet receive paths and helper initialization code for IPD/PKO/GMX setup and RED configuration.

## Risks
Incorrect buffer metadata can cause freeing the wrong physical address or pool. The `NO_WPTR` detection compares the WQE physical address to the packet buffer start and must stay aligned with IPD configuration. `cvmx_helper_get_last_ipd_port()` assumes the interface is initialized and has a positive port count.

## Test Signals
Packet lifecycle tests should verify all buffers are returned for single- and multi-buffer packets, the WQE is preserved in `NO_WPTR` mode, FPA pool counts recover after receive/free loops, and first/last IPD port calculations match interface probe results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-xaui.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-xaui.h

## Purpose
`cvmx-helper-xaui.h` declares helper operations for XAUI packet interfaces. XAUI uses high-speed serial lanes and GMX XAUI controls, so the common helper framework delegates port probing, enablement, and link state synchronization to this backend.

## Important APIs, Types, And Functions
The exported calls are `__cvmx_helper_xaui_probe(int interface)`, `__cvmx_helper_xaui_enumerate(int interface)`, `__cvmx_helper_xaui_enable(int interface)`, `__cvmx_helper_xaui_link_get(int ipd_port)`, and `__cvmx_helper_xaui_link_set(int ipd_port, union cvmx_helper_link_info link_info)`.

## Control Flow
Probe identifies available XAUI ports without bringing the interface up. Enable is called after IPD is enabled but before PKO is active, so lane and GMX state are ready before packet transmission. Link get/set synchronize negotiated or externally determined link state with Octeon MAC configuration.

## State And Persistence
The implementation writes QLM/PCS/GMX/PKO hardware state. The header defines no data. Link configuration remains active until another link-set or interface reset.

## Dependencies And Integration Points
It is included by `cvmx-helper.h`, uses `union cvmx_helper_link_info`, and is selected for `CVMX_HELPER_INTERFACE_MODE_XAUI`. It integrates with QLM JTAG/errata support, GMX XAUI CSR definitions, board-specific link handling, IPD, and PKO.

## Risks
XAUI lane setup is model and board dependent. Incorrect QLM selection, errata handling, or link-set values can prevent link training or cause packet errors. The helper must be called in the expected packet I/O initialization order.

## Test Signals
Validate probe counts, lane lock/link-up, 10G traffic, error counters, link-down recovery, model-specific QLM workarounds, and that link set follows the exact state returned by link get.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-xaui.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper.h

## Purpose
`cvmx-helper.h` is the central public include for Octeon packet helper functionality. It defines interface modes, link-state representation, includes the mode-specific helper headers, and declares the common packet I/O initialization, interface probing, port count, and link get/set APIs.

## Important APIs, Types, And Functions
The key type `cvmx_helper_interface_mode_t` enumerates disabled, RGMII, GMII, SPI, PCIe, XAUI, SGMII, PICMG, NPI, and LOOP modes. `union cvmx_helper_link_info` packs `link_up`, `full_duplex`, and 18-bit Mbps `speed` into a 64-bit value. Public APIs include `cvmx_helper_ipd_and_packet_input_enable`, `cvmx_helper_initialize_packet_io_global`, `cvmx_helper_ports_on_interface`, `cvmx_helper_get_number_of_interfaces`, `cvmx_helper_interface_get_mode`, `cvmx_helper_link_get`, `cvmx_helper_link_set`, `cvmx_helper_interface_probe`, and `cvmx_helper_interface_enumerate`.

## Control Flow
Users normally initialize global packet I/O, probe/enumerate interfaces to populate port counts, make any extra IPD configuration, then call `cvmx_helper_ipd_and_packet_input_enable()`. Link management flows through `cvmx_helper_link_get()` to observe PHY/PCS state and `cvmx_helper_link_set()` to program Octeon MAC state.

## State And Persistence
The header itself stores no state, but implementations maintain probed interface port counts and write persistent IPD/PIP/PKO/GMX/PCS/PHY hardware state. Link info is a value object passed between helper layers.

## Dependencies And Integration Points
It includes configuration, FPA, WQE, errata, loop, NPI, RGMII, SGMII, SPI, util, and XAUI headers. It is a high-level integration point for packet I/O consumers, board code, and Ethernet mode backends.

## Risks
Initialization order matters: packet interfaces must be enabled after IPD, and link set must match link get. Some interfaces lack normal PHY link semantics. The central include creates dependency coupling across helper backends, so type or enum changes have broad impact.

## Test Signals
System tests should cover global packet I/O init, every interface mode present on a board, port-count reporting before and after probe, link get/set under cable changes, packet ingress/egress on all ports, and clean behavior when unsupported interfaces return disabled or negative errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-iob-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-iob-defs.h

## Purpose
`cvmx-iob-defs.h` defines CSR addresses and bitfield unions for the Octeon I/O bridge. The IOB arbitrates and monitors traffic between cores/L2, FAU, DWB, PKO/FPA, NPI/NCB, and outbound/inbound bus transactions.

## Important APIs, Types, And Functions
Address macros cover BIST and control status, priority counters (`DWB`, `I2C`, `N2C`, `P2C`, outbound request/common/FPA), inbound and outbound data/control match registers and enables, interrupt enable/sum, packet error status, CMB credits, and per-NCB-device credit registers. Unions include `cvmx_iob_bist_status`, `cvmx_iob_ctl_status`, priority count layouts, match/mask registers, `cvmx_iob_int_enb`, `cvmx_iob_int_sum`, `cvmx_iob_pkt_err`, and NCB credit counters.

## Control Flow
There is no code flow. Diagnostics and platform initialization read BIST/status fields, configure match and interrupt enables, tune priority counters, and observe or reset error conditions through CSR accessors.

## State And Persistence
IOB CSRs hold persistent hardware control, priority, match, interrupt, error, and credit state. The header defines no software storage. Some status bits represent live or latched hardware events.

## Dependencies And Integration Points
The definitions require `CVMX_ADD_IO_SEG`, endian bitfield support, and CSR access functions. IOB state integrates with packet I/O, DMA, FAU, NPI, L2 cache, and interrupt handling, especially when diagnosing bus errors or throughput contention.

## Risks
The file has many chip-specific `bist_status` and control variants; using the wrong layout can misread failures or program reserved bits. Match registers can generate high interrupt volume if masks are broad. Priority counter tuning can change system performance and fairness.

## Test Signals
Useful checks include clean BIST at boot, interrupt summary/enable behavior for injected errors, packet error reporting, stable NCB/CMB credit counts under load, and performance measurements before and after priority counter tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-iob-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd-defs.h

## Purpose
`cvmx-ipd-defs.h` is the CSR definition file for the Octeon Input Packet Data unit. IPD receives packets from packet interfaces, allocates WQEs and packet buffers, applies backpressure and RED policy, tracks FIFO pointer state, and reports packet/input errors.

## Important APIs, Types, And Functions
Address macros define buffer skip/back-pointer sizing, packet buffer size, WQE FPA pool, control status, BIST, interrupt enable/sum, pointer FIFO controls and valid pointers, port backpressure counters, RED thresholds and enable bits, QoS counters/marks, BPID counters, SOP state, credits, request weights, sub-port state, and packet error registers. The union families mirror these groups: skip/back unions, `cvmx_ipd_ctl_status`, BIST, ECC, FIFO controls, interrupt status, pointer-valid registers, per-port counters, RED/QoS, and WQE FPA selection.

## Control Flow
The header contains no functions. `cvmx-ipd.h` and helper implementations compose these unions and write CSRs to configure receive buffer layout, caching mode, backpressure, WQE allocation, and RED policy. Shutdown paths read pointer count and FIFO control registers to drain prefetched buffers.

## State And Persistence
All state is hardware state in the IPD block: enable/reset, buffer sizing, FIFO pointers, in-flight prefetched buffers, packet counters, backpressure/RED thresholds, interrupt latches, and error status. Misprogramming these values affects every incoming packet path.

## Dependencies And Integration Points
The definitions are included by `cvmx-ipd.h` and used by packet helper initialization, FPA pool management, PIP/PIP reset, interrupt handlers, RED setup, and receive buffer reclamation. They rely on `CVMX_ADD_IO_SEG`, bitfield layout, and Octeon model feature checks in callers.

## Risks
Many macros mask offsets, so invalid ports or queues can alias. Buffer skip, back-pointer, and size fields must agree with FPA pool object sizes and WQE layout; mistakes can corrupt packet memory. Some pointer FIFO registers require `cena`/`raddr` sequencing. Interrupt/status fields vary across chip families.

## Test Signals
Validate IPD configuration by receiving packets of varying sizes, checking WQE and buffer pointer layout, exercising backpressure and RED thresholds, draining/freeing IPD during shutdown without FPA leaks, and inspecting interrupt/error counters under malformed packet tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd.h

## Purpose
`cvmx-ipd.h` provides the C helper interface for configuring, enabling, disabling, and draining the Octeon Input Packet Data unit. It builds on the IPD CSR definitions and includes inline routines used by packet I/O initialization and FPA shutdown.

## Important APIs, Types, And Functions
`enum cvmx_ipd_mode` selects cache placement for packet blocks: all DRAM, all L2, first block L2, or first two blocks L2. `cvmx_ipd_config()` writes buffer skip sizes, packet buffer size, first/second back pointers, WQE FPA pool, cache mode, and port backpressure enable. `cvmx_ipd_enable()` and `cvmx_ipd_disable()` toggle IPD. `cvmx_ipd_free_ptr()` drains prefetched WQE and packet pointers and resets IPD/PIP.

## Control Flow
Configuration writes each layout CSR, then updates `IPD_CTL_STATUS` for cache mode and backpressure. Enable reads control status, warns if already enabled, optionally sets `len_m8`, then writes `ipd_en`. Disable clears that bit. `cvmx_ipd_free_ptr()` skips early CN38XX revisions that cannot expose pointers, detects `NO_WPTR`, reads pointer counts, drains prefetched WQE, WQE FIFO, prefetched packet, per-port packet FIFO, holding FIFO, and packet FIFO using FIFO-control `cena/raddr` sequences, frees each pointer to the proper FPA pool, then resets IPD and PIP.

## State And Persistence
The functions directly mutate IPD/PIP hardware and FPA pool state. `cvmx_ipd_free_ptr()` returns prefetched buffers to FPA pools and clears receive hardware state by reset. There is no heap or filesystem persistence.

## Dependencies And Integration Points
It depends on `octeon-feature.h`, `cvmx-ipd-defs.h`, `cvmx-pip-defs.h`, model macros, `cvmx_read_csr`, `cvmx_write_csr`, `cvmx_fpa_free`, and `cvmx_phys_to_ptr`. It is integrated with global packet I/O setup, receive shutdown, and FPA pool teardown.

## Risks
The drain logic is hardware-specific and easy to break: wrong pool selection in `NO_WPTR`, wrong FIFO address arithmetic, or running while traffic is active can free live buffers or leak prefetched buffers. Resetting IPD/PIP is disruptive. `CVMX_ENABLE_LEN_M8_FIX` changes receive length behavior except on CN38XX pass2.

## Test Signals
Tests should verify IPD enable/disable status, packet receive layout for configured skip/back/size values, warning on double enable, no FPA leaks after `cvmx_ipd_free_ptr()`, correct `NO_WPTR` pool handling, and successful receive reinitialization after IPD/PIP reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c-defs.h

## Purpose
`cvmx-l2c-defs.h` maps Octeon L2 cache controller CSRs for configuration, debugging, performance counters, way partitioning, lock address windows, and tag/data ECC error reporting.

## Important APIs, Types, And Functions
Address macros include `CVMX_L2C_CFG`, `CVMX_L2C_CTL`, `CVMX_L2C_DBG`, `CVMX_L2C_PFCTL`, `CVMX_L2C_PFCX`, `CVMX_L2C_TADX_PFCX`, `CVMX_L2C_TADX_PRF`, `CVMX_L2C_TADX_TAG`, `CVMX_L2C_ERR_TDTX`, `CVMX_L2C_ERR_TTGX`, `CVMX_L2C_WPAR_PPX`, `CVMX_L2C_WPAR_IOBX`, `CVMX_L2C_LCKBASE`, and `CVMX_L2C_LCKOFF`. Unions expose ECC single/double-bit status and syndrome, cache controller config/control, debug selector fields, performance counter selection/enable/clear, tag state, and lock window base/offset.

## Control Flow
There are no runtime functions. L2C helper implementations use these definitions to configure counters, partition ways, inspect tags, lock or unlock regions, and manipulate debug flush features.

## State And Persistence
Persistent state is hardware L2 controller state: performance counter configuration and counts, cache policy/control bits, way partition masks, lock windows, and ECC error latches. The header itself has no data.

## Dependencies And Integration Points
It uses `<uapi/asm/bitfield.h>` and `CVMX_ADD_IO_SEG`. It is consumed by `cvmx-l2c.h` implementations, cache/ECC error handlers, low-level platform initialization, and performance monitoring.

## Risks
Debug and lock registers affect global cache behavior and are not generally safe for concurrent use. Wrong partition masks can starve cores or hardware blocks of evictable ways. ECC status interpretation depends on TAD/block IDs and model-specific geometry.

## Test Signals
Validate performance counter event selection and clear-on-read behavior, way partition readback, lock/unlock operations on test memory, controlled flush behavior, and ECC interrupt/status paths using injected or simulated errors where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c.h

## Purpose
`cvmx-l2c.h` declares the public Octeon L2 cache control API. It covers cache geometry, performance counters, core and hardware way partitioning, line and region locking/unlocking, tag inspection, index calculation, and flush operations.

## Important APIs, Types, And Functions
It defines deprecated geometry macros `CVMX_L2_ASSOC`, `CVMX_L2_SET_BITS`, `CVMX_L2_SETS`, index/alias constants, `union cvmx_l2c_tag`, `enum cvmx_l2c_event`, and `enum cvmx_l2c_tad_event`. Public functions include `cvmx_l2c_config_perf`, `cvmx_l2c_read_perf`, partition get/set APIs, `cvmx_l2c_lock_line`, `cvmx_l2c_lock_mem_region`, `cvmx_l2c_unlock_line`, `cvmx_l2c_unlock_mem_region`, `cvmx_l2c_get_tag`, deprecated wrapper `cvmx_get_l2c_tag`, `cvmx_l2c_address_to_index`, `cvmx_l2c_flush`, geometry getters, and `cvmx_l2c_flush_line`.

## Control Flow
The header is declaration-heavy. Implementations configure counter selectors before reads, compute index/alias geometry from model-specific cache shape, use debug registers for tag reads and flushes, and use lock/unlock routines over individual lines or regions. The deprecated wrapper simply calls `cvmx_l2c_get_tag`.

## State And Persistence
Functions mutate hardware cache state: counters, way partitions, locked-line state, tag state, and flush effects. Region locks persist until explicitly unlocked or flushed/reset. No software persistence is declared in the header.

## Dependencies And Integration Points
It includes bitfield helpers and is backed by the L2C/L2D/L2T CSR definitions. It is used by platform initialization, performance tooling, memory management, DMA-sensitive code, and diagnostics.

## Risks
Several functions must only be called by one core at a time because they use L2C debug features. Partition masks can make all ways unavailable if combined badly across cores/hardware. Locking too much memory can severely hurt cache performance. Deprecated macros still execute geometry functions, so they are not compile-time constants.

## Test Signals
Test counter configuration/readback, geometry results on each model, address-to-index calculations, line lock/unlock return values, region lock coverage, full and per-line flush behavior, and multi-core exclusion around debug-register users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2d-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2d-defs.h

## Purpose
`cvmx-l2d-defs.h` defines the small CSR set for the Octeon L2 data array error and fuse/control state. It is part of the broader L2 cache diagnostics surface.

## Important APIs, Types, And Functions
The address macros are `CVMX_L2D_ERR` and `CVMX_L2D_FUS3`. `union cvmx_l2d_err` exposes ECC enable, single-error interrupt enable/status, double-error interrupt enable/status, and a BMH selector bit. `union cvmx_l2d_fus3` exposes `ema_ctl` and a fuse field `q3fus`.

## Control Flow
There is no executable code. Error handlers and initialization code read or write these CSRs through generic CSR accessors.

## State And Persistence
State is hardware error latch, interrupt enable, ECC enable, and fuse/control state. Changing ECC enable or fuse-related controls affects L2 data-array behavior until reset or reprogramming.

## Dependencies And Integration Points
The unions use `__BITFIELD_FIELD`, so callers must include the bitfield macro environment through surrounding headers. The file integrates with L2 cache ECC handling, boot diagnostics, and cache-controller initialization.

## Risks
Disabling ECC or clearing error bits incorrectly can hide real data-array faults. Fuse/control fields are hardware-specific and should not be modified without model documentation. Error status handling must coordinate with L2T/L2C error sources.

## Test Signals
Test signals include expected ECC enable state at boot, correct interrupt delivery for injected single/double-bit data errors, stable readback of `CVMX_L2D_ERR`, and no unexpected changes to fuse/control fields during normal cache operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2d-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2t-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2t-defs.h

## Purpose
`cvmx-l2t-defs.h` maps the Octeon L2 tag array error CSR. It exposes ECC enable/status, lock-error reporting, failed address/set/syndrome fields, and model-specific field widths for older Octeon families.

## Important APIs, Types, And Functions
The sole address macro is `CVMX_L2T_ERR`. `union cvmx_l2t_err` contains generic fields `ecc_ena`, single/double-error interrupt enables and status, syndrome, failed address/set, lock error bits, second lock-error bits, and `fadru`. It also provides model-specific layouts for CN30XX, CN31XX, CN38XX, CN50XX, and CN52XX where failed address and set widths differ.

## Control Flow
The header has no functions. Platform code reads this CSR during ECC or lock-error interrupts, decodes the model-appropriate union view, and writes back as required to clear latches or control interrupt enables.

## State And Persistence
Persistent state is the L2 tag ECC enable, interrupt enables, and latched tag/lock error information. The reported failed address and syndrome are hardware-captured until cleared or overwritten by later faults.

## Dependencies And Integration Points
It includes `<uapi/asm/bitfield.h>`. It integrates with L2 cache error handling, lock/unlock routines from `cvmx-l2c.h`, and platform RAS diagnostics.

## Risks
Using the generic layout on older chips with different field widths can misreport the failing address or set. Lock-error fields are coupled to cache-lock operations and may be triggered by unsafe concurrent debug/lock use. Clearing status without logging loses important failure information.

## Test Signals
Validate boot ECC enable state, interrupt enable behavior, model-specific field decoding, lock-error reporting for forced invalid operations, and ECC syndrome/address logging through injected or simulated tag faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-l2t-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-led-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-led-defs.h

## Purpose
`cvmx-led-defs.h` maps Octeon LED controller CSRs. The LED block drives port status LEDs and user-defined LED data with configurable enable, phase, blink/cylon rates, polarity, port enable masks, format selection, and set/clear operations.

## Important APIs, Types, And Functions
Address macros include `CVMX_LED_EN`, `CVMX_LED_CLK_PHASE`, `CVMX_LED_PRT`, `CVMX_LED_DBG`, `CVMX_LED_UDD_CNTX`, `CVMX_LED_PRT_FMT`, `CVMX_LED_UDD_DATX`, `CVMX_LED_BLINK`, `CVMX_LED_POLARITY`, `CVMX_LED_PRT_STATUSX`, `CVMX_LED_UDD_DAT_SETX`, `CVMX_LED_UDD_DAT_CLRX`, and `CVMX_LED_CYLON`. Unions expose single-bit enables/polarity, blink/cylon rates, phase, port mask, format, per-port status, user-defined data counts, and 32-bit set/clear/data fields.

## Control Flow
The header has no functions. Drivers program the LED controller by enabling the block, selecting format/phase/rates, enabling port bits, and using UDD data set/clear registers for custom LED output.

## State And Persistence
State is hardware LED controller configuration and data output. Port LED status reflects controller state and packet/MAC inputs depending on format. UDD data persists until set, cleared, or reset.

## Dependencies And Integration Points
It depends on `CVMX_ADD_IO_SEG` and endian bitfield settings. It integrates with board LED drivers, Ethernet port status, GPIO/physical LED wiring, and diagnostics that use debug or cylon modes.

## Risks
Incorrect polarity or format can invert or misrepresent board LEDs. Offset masks restrict port and UDD indexes, so invalid indexes can alias. Debug/cylon modes can override normal status and confuse operational monitoring.

## Test Signals
Verify LED enable and polarity on real board hardware, blink/cylon timing, per-port link/activity status, UDD set/clear behavior, and that invalid or disabled ports do not light unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-led-defs.h -->
