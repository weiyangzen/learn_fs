# subset-b-000724 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-bootmem.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-bootmem.c

## Purpose
This file implements the Octeon bootloader-provided physical memory allocator used early by the kernel and by CVMX executive code. It exposes simple physical and virtual allocation helpers, named boot memory blocks, and free-list maintenance over the bootmem descriptor supplied by firmware.

## Important APIs, Types, And Functions
The central state is the static `struct cvmx_bootmem_desc *cvmx_bootmem_desc`. Public entry points include `cvmx_bootmem_init()`, `cvmx_bootmem_alloc_address()`, `cvmx_bootmem_alloc_named_range()`, `cvmx_bootmem_alloc_named()`, `cvmx_bootmem_alloc_named_range_once()`, `cvmx_bootmem_find_named_block()`, `cvmx_bootmem_free_named()`, `cvmx_bootmem_phy_alloc()`, `cvmx_bootmem_phy_named_block_alloc()`, and `cvmx_bootmem_get_desc()`. Internal helpers read and write physical free-list headers through `cvmx_read64_uint64()` and `cvmx_write64_uint64()` using XKPHYS addressing.

## Control Flow
Initialization records the firmware descriptor pointer in an ABI-aware form. Physical allocation validates descriptor version, size, range, and alignment, then walks the ordered free list first-fit. It may split a free entry once to create an aligned sub-block, then loop again to remove the requested range. Freeing inserts the returned span into sorted free-list order and coalesces with adjacent blocks. Named allocation locks the descriptor, finds an unused named descriptor, rejects duplicate names, allocates a physical span without nested locking, then fills `base_addr`, `size`, and `name`. Named free performs the reverse atomically.

## State, Persistence, And Dependencies
Allocator state lives in firmware bootmem structures, not ordinary heap memory. Named blocks persist across callers through the global bootmem named-block array. Locking uses `cvmx_spinlock_t` embedded in the descriptor unless `CVMX_BOOTMEM_FLAG_NO_LOCKING` is passed for already-locked internal calls. The code depends on Octeon physical address helpers, descriptor version 3 for named blocks, and fixed bootmem block header offsets.

## Integration Points
Other executive modules use named bootmem blocks for shared state, notably command queues. Exported symbols make named allocation and lookup available to kernel modules. `cvmx_phys_to_ptr()` bridges physical addresses to usable kernel pointers.

## Risks
Incorrect descriptor version, uninitialized `cvmx_bootmem_desc`, or overlapping frees corrupt global early-memory state. The allocator assumes sorted non-overlapping free-list entries and power-of-two alignment. `cvmx_bootmem_alloc_named_range_once()` calls named lookup/allocation with no explicit outer lock, relying on no-lock flags and expected call context; concurrent users must be cautious. Physical accesses bypass normal virtual memory safety.

## Test Signals
Useful signals are allocation failures for impossible ranges, duplicate named-block rejection, successful coalescing after free, descriptor-version error prints, and stress tests that allocate/free named spans while checking the free-list remains sorted and non-overlapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-bootmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-cmd-queue.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-cmd-queue.c

## Purpose
This file manages shared command queue state for Octeon hardware engines, especially PKO and DMA queues. It allocates queue metadata from bootmem, initializes FPA-backed command buffers, exposes queue length queries, and shuts queues down.

## Important APIs, Types, And Functions
The exported global `__cvmx_cmd_queue_state_ptr` points to a bootmem named block called `cvmx_cmd_queues`. Main APIs are `cvmx_cmd_queue_initialize()`, `cvmx_cmd_queue_shutdown()`, `cvmx_cmd_queue_length()`, and `cvmx_cmd_queue_buffer()`. The code uses `__cvmx_cmd_queue_get_state()`, `__cvmx_cmd_queue_get_index()`, queue locks, FPA allocation/free, and model-specific PKO/NPEI CSR reads.

## Control Flow
Initialization first resolves or creates the global named bootmem block, optionally inside reserved 32-bit memory. A queue setup validates queue id, max depth, FPA pool, and buffer size. If the queue was already initialized, it verifies compatible parameters and returns `ALREADY_SETUP`; otherwise it requires FPA enabled, allocates one buffer, clears queue state, records pool metadata and the physical base pointer divided by 128, and resets the queue ticket. Shutdown refuses non-empty queues, locks the queue, frees the initial buffer, and clears the base pointer. Length dispatches by queue class and reads hardware doorbell counters where implemented.

## State, Persistence, And Dependencies
Queue metadata persists in bootmem and is shared across cores/users. Command buffers come from FPA pools. Hardware-visible state is in PKO, NPEI, and PEXP CSRs. Ordering uses `CVMX_SYNCWS`.

## Integration Points
PKO configuration calls this module to back each output queue with a command buffer. DMA queue length reads use NPEI counters. Bootmem must be initialized before queue state allocation.

## Risks
FPA must already be enabled and sized correctly. Queue length for some engines is stubbed as zero. `cvmx_cmd_queue_length()` notes weak serialization around `CVMX_PKO_REG_READ_IDX`, so callers should hold queue locks when racing with other readers. Incorrect reserved-memory bounds can prevent shared state allocation.

## Test Signals
Signals include successful bootmem named block reuse, `ALREADY_SETUP` on idempotent queue setup, invalid-parameter returns for bad pools/depths, shutdown rejection when doorbells are nonzero, and correct PKO doorbell counts under enqueue/dequeue tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-cmd-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-board.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-board.c

## Purpose
This board abstraction supplies board-specific networking facts that generic packet I/O helpers cannot infer from chip registers alone. It maps IPD ports to PHY addresses, provides fallback link status, trims probed port counts, and reports USB clock source type.

## Important APIs, Types, And Functions
Key entry points are `cvmx_helper_board_get_mii_address()`, `__cvmx_helper_board_link_get()`, `__cvmx_helper_board_interface_probe()`, and `__cvmx_helper_board_usb_get_clock_type()`. They depend on `cvmx_sysinfo_get()->board_type`, board type enums, `cvmx_helper_get_interface_num()`, `cvmx_helper_get_interface_index_num()`, and GMX/ASX in-band status CSRs.

## Control Flow
PHY address lookup is a large board-type switch with per-board IPD port ranges and encoded bus/address returns. Link lookup warns outside simulation because device-tree based status is preferred, returns fixed simulated links, or for older models reads GMX in-band status and decodes speed/duplex. Interface probe post-processes a generic supported port count for boards with disabled or partially wired interfaces. USB clock selection uses specific board overrides and Octeon generation defaults.

## State, Persistence, And Dependencies
This module has no private persistent state. It reads bootloader-populated sysinfo and selected GMX registers. It encodes board policy in source, making board table accuracy part of runtime behavior.

## Integration Points
`cvmx-helper.c` calls the interface probe override after generic enumeration. RGMII and SGMII link getters call the board link fallback when no PHY-driver result is available. USB initialization code consumes the clock type helper.

## Risks
New boards require source updates; unknown board types print an error and report no PHY. In-band status is hazardous on unsupported boards, and the code explicitly warns that deprecated link status should be replaced by device-tree data. Wrong board mappings can silently disable ports or report incorrect speed.

## Test Signals
Test with representative `board_type` values and IPD ports, checking PHY address mappings, disabled interfaces, simulation link status, in-band speed decoding, and USB clock decisions for known exception boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-board.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-errata.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-errata.c

## Purpose
This small module applies a specific Octeon chip erratum workaround: disabling second-order CDR on CN52XX pass 1 QLMs.

## Important APIs, Types, And Functions
The exported function `__cvmx_helper_errata_qlm_disable_2nd_order_cdr(int qlm)` uses `cvmx_helper_qlm_jtag_init()`, `cvmx_helper_qlm_jtag_shift_zeros()`, `cvmx_helper_qlm_jtag_shift()`, and `cvmx_helper_qlm_jtag_update()`.

## Control Flow
The function initializes the internal QLM JTAG controller, then for each of four lanes shifts a 268-bit lane image. It writes zeros around two nonzero fields: `cfg_cdr_incx<67:64> = 3` and `cfg_cdr_secord<77> = 1`. After loading all 1072 bits, it updates the selected QLM.

## State, Persistence, And Dependencies
State is hardware-latched in the QLM JTAG chain. There is no software persistence. The code depends on exact bit positions from the hardware erratum and on the JTAG helpers selecting the intended QLM.

## Integration Points
`cvmx_helper_initialize_packet_io_global()` invokes this workaround for `OCTEON_CN52XX_PASS1_0` before packet I/O bring-up.

## Risks
The source comments note that invalid JTAG programming can damage hardware. The function does not verify chip model itself, so callers must gate it correctly. Bit position mistakes would be hard to detect except through link failures.

## Test Signals
Signals are successful packet/link initialization on affected CN52XX pass 1 hardware, no invocation on unaffected models, and readable JTAG CSR completion without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-errata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-jtag.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-jtag.c

## Purpose
This file provides low-level helpers for programming Octeon QLM internal JTAG chains through CIU CSRs.

## Important APIs, Types, And Functions
Public functions are `cvmx_helper_qlm_jtag_init()`, `cvmx_helper_qlm_jtag_shift()`, `cvmx_helper_qlm_jtag_shift_zeros()`, and `cvmx_helper_qlm_jtag_update()`. They use `CVMX_CIU_QLM_JTGC`, `CVMX_CIU_QLM_JTGD`, `cvmx_sysinfo_get()->cpu_clock_hz`, and model checks for CN52XX and CN56XX pass 1 behavior.

## Control Flow
Initialization computes a JTAG clock divider from CPU frequency, sets bypass fields, and writes the control CSR. Shift operations write up to 32 bits with shift count and selected QLM, then poll until the hardware clears the shift bit and return bits shifted out. The zero helper loops in 32-bit chunks. Update writes the update bit and polls until complete.

## State, Persistence, And Dependencies
Programming state resides in the hardware JTAG chain and CIU JTAG control registers. No software locks are used, so callers must avoid concurrent QLM programming. The helper depends on CPU clock accuracy for timing and model-specific QLM select/bypass semantics.

## Integration Points
The errata module uses these helpers for CN52XX pass 1 CDR workaround. Other QLM tuning code can use the same primitives.

## Risks
The comments explicitly warn that incorrect values may damage hardware. There is no timeout in the polling loops, so a stuck JTAG operation can hang the caller. Invalid `bits` values are not checked.

## Test Signals
Healthy signals are completion of shift/update polling, correct loopback of shifted data where hardware supports it, and successful downstream QLM link bring-up after programmed workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-jtag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-loop.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-loop.c

## Purpose
This file handles Octeon special LOOP interfaces, which are internal loopback packet ports distinct from external Ethernet loopback modes.

## Important APIs, Types, And Functions
The entry points are `__cvmx_helper_loop_probe(int interface)` and `__cvmx_helper_loop_enable(int interface)`. Probe uses `cvmx_helper_get_ipd_port()`, `CVMX_PIP_PRT_CFGX()`, and `CVMX_IPD_SUB_PORT_FCS`.

## Control Flow
Probe assumes four loopback ports. For each port it disables PIP minimum and maximum length error checks so short packets and jumbo frames do not become errors. It also disables FCS stripping behavior for loopback subports, then returns the port count. Enable is intentionally a no-op because the loop path requires no additional hardware activation here.

## State, Persistence, And Dependencies
State is persistent CSR configuration in PIP and IPD. There is no private memory state. The helper depends on the generic interface-to-IPD-port mapping.

## Integration Points
`cvmx-helper.c` calls this module during interface probe and hardware enable for LOOP mode, and excludes LOOP from normal network link handling.

## Risks
Length-check relaxation is appropriate for internal loop traffic but would be wrong if applied to external ports. The fixed four-port assumption must match the chip mode table.

## Test Signals
Signals include four ports reported for LOOP mode, successful transmission of packets outside normal Ethernet size limits through loopback, and no link-status dependency for those ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-npi.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-npi.c

## Purpose
This file supports NPI, the PCI/host-facing network packet interface, by deciding whether NPI packet ports exist and applying minimal receive-side configuration.

## Important APIs, Types, And Functions
Entry points are `__cvmx_helper_npi_probe(int interface)` and `__cvmx_helper_npi_enable(int interface)`. The code uses `CVMX_PKO_QUEUES_PER_PORT_PCI`, Octeon model checks, `cvmx_helper_ports_on_interface()`, `cvmx_helper_get_ipd_port()`, and `CVMX_PIP_PRT_CFGX()`.

## Control Flow
Probe returns four ports only on supported models and pass levels when PCI PKO queues are configured; otherwise it returns zero. Enable disables PIP min/max length checks on non-CN3XXX/CN58XX chips for each NPI port, then returns success because actual enables are controlled by the remote host.

## State, Persistence, And Dependencies
Only PIP port configuration CSRs are changed. Existence depends on compile-time queue configuration and chip model/pass.

## Integration Points
`cvmx-helper.c` treats NPI as a packet I/O interface during enumeration, IPD/PKO setup, and hardware enable, but not as a normal link-status network interface.

## Risks
Wrong model gating can expose nonexistent packet engines on pass 1 chips. Length-check disabling is broad and assumes remote-host framing. Remote host control means local enable success does not prove traffic can flow.

## Test Signals
Probe should return zero on unsupported/pass1 hardware and four on supported NPI configurations. Traffic tests should verify host-driven NPI packet movement and absence of false length errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-npi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-rgmii.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-rgmii.c

## Purpose
This module probes, enables, loops back, and updates link settings for RGMII/GMII/MII ports.

## Important APIs, Types, And Functions
Important functions are `__cvmx_helper_rgmii_probe()`, `cvmx_helper_rgmii_internal_loopback()`, `__cvmx_helper_rgmii_enable()`, `__cvmx_helper_rgmii_link_get()`, and `__cvmx_helper_rgmii_link_set()`. It uses GMX, ASX, PKO, NPI debug, board link helpers, and interrupt-enabling helpers.

## Control Flow
Probe reads `GMXX_INF_MODE` to distinguish SPI, GMII/MII, and RGMII-style configurations and returns a model-specific port count. Enable checks the interface is active, enables ASX RX/TX port masks, applies pass1 ASX high-water errata or relaxed preamble checking, sets pause timing and clock delays, calls common GMX setup, enables each GMX port, and turns on ASX/GMX error interrupts. Link get returns forced 1 Gbps full duplex for internal loopback or delegates to board link status. Link set disables RX and PKO queue scheduling, disables backpressure, waits for GMX idle, reprograms duplex, speed, slot, burst, and clocks, then restores RX, queue QoS, backpressure, and original enable state.

## State, Persistence, And Dependencies
State is almost entirely in GMX, ASX, PKO, and debug CSRs. Temporary QoS and backpressure settings are saved on the stack and restored. The implementation depends on accurate `interface_port_count`, board link data, and model/pass checks.

## Integration Points
The generic helper coordinator calls this module for RGMII and GMII modes. It uses PKO queue metadata from `cvmx-pko.c` while changing speed, and board helpers for link resolution.

## Risks
Speed changes while GMX is not idle can lock hardware; the code waits but proceeds after timeout comments. Queue QoS save array is fixed at 16 entries, matching expected queue counts. Board link fallback is deprecated. Wrong model mode interpretation can configure SPI as RGMII or vice versa.

## Test Signals
Signals include correct port counts per model/mode, packet TX/RX after enable, link speed changes reflected in GMX clocks, restored queue QoS after link set, and interrupt status for ASX/GMX errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-rgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-sgmii.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-sgmii.c

## Purpose
This file implements SGMII and PICMG port bring-up, autonegotiation status, and GMX speed programming.

## Important APIs, Types, And Functions
Key functions are `__cvmx_helper_sgmii_enumerate()`, `__cvmx_helper_sgmii_probe()`, `__cvmx_helper_sgmii_enable()`, `__cvmx_helper_sgmii_link_get()`, and `__cvmx_helper_sgmii_link_set()`. Internal stages are `__cvmx_helper_sgmii_hardware_init_one_time()`, `__cvmx_helper_sgmii_hardware_init_link()`, and `__cvmx_helper_sgmii_hardware_init_link_speed()`.

## Control Flow
Probe enables the GMX interface early to satisfy GMX-700 errata, then reports four ports. Enable runs common GMX setup, programs PCS timer and advertisement registers once per port, optionally sets simulator links, enables GMX ports, and enables PCS/GMX interrupts. Link get handles simulator and internal loopback, then distinguishes 1000BASE-X, SGMII PHY mode, and SGMII MAC mode. In PHY mode it restarts PCS autonegotiation if the low-level link is down and decodes `AN_RESULTS`; in MAC mode it asks the board helper. Link set reruns PCS link initialization and applies speed/duplex to GMX and PCS sampling/GMXENO fields.

## State, Persistence, And Dependencies
PCS, GMX, and interrupt CSRs hold persistent hardware state. There is no private software state. The code depends on CPU clock for PCS timer counts and on board-mode bits that distinguish MAC/PHY and 1000BASE-X.

## Integration Points
`cvmx-helper.c` delegates SGMII/PICMG modes here. Board link status is used for MAC-mode links. Interrupt decode helpers enable per-port and per-interface PCS errors.

## Risks
1000BASE-X link get is marked FIXME and returns down unless handled elsewhere. Timeouts during reset, autonegotiation, or GMX idle return failures that callers may not deeply diagnose. Simulator paths bypass real link negotiation.

## Test Signals
Signals include PCS reset completion, autonegotiation completion, decoded 10/100/1000 speed, GMX idle before speed writes, packet flow after enable, and PCS/GMX interrupt behavior under cable/link faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-sgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-spi.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-spi.c

## Purpose
This helper connects generic packet I/O initialization to SPI4 Ethernet interfaces and optional SPI4000 PHY/switch devices.

## Important APIs, Types, And Functions
Functions include `__cvmx_helper_spi_enumerate()`, `__cvmx_helper_spi_probe()`, `__cvmx_helper_spi_enable()`, `__cvmx_helper_spi_link_get()`, and `__cvmx_helper_spi_link_set()`. It depends on `cvmx_spi4000_is_present()`, `cvmx_spi_start_interface()`, `cvmx_spi4000_initialize()`, `cvmx_spi4000_check_speed()`, common GMX setup, and SPI/STX/SPX interrupt enables.

## Control Flow
Enumerate/probe report ten ports when SPI4000 is present, otherwise sixteen. Generic SPI probe also enables PKO CRC insertion because non-SPI4000 peers may not append Ethernet CRC. Enable sets IPD CRC checking on each SPI port, starts the SPI4 interface in duplex mode with a timeout, initializes SPI4000 when present, and enables SPI/GMX interrupts. Link get returns simulated or generic 10 Gbps full-duplex links, or decodes SPI4000 in-band speed. Link set is a no-op because SPI4000 speed handling occurs during check-speed and generic SPI has no link information.

## State, Persistence, And Dependencies
Configuration persists in PKO CRC, PIP port, SPI, and GMX CSRs. Behavior depends on board simulation state and SPI4000 presence detection.

## Integration Points
`cvmx-helper.c` uses this module for SPI mode. `cvmx-spi.c` implements the lower-level training sequence. PKO/IPD common setup must be in place before enable.

## Risks
Generic SPI assumes link up at 10 Gbps even when no external status is available. CRC handling differs between SPI4000 and generic devices, so misdetecting SPI4000 corrupts framing. Timeout failures from `cvmx_spi_start_interface()` are not surfaced by this wrapper.

## Test Signals
Signals include correct ten-versus-sixteen port counts, CRC insertion/checking behavior, successful SPI training, SPI4000 speed decode, and SPX/STX interrupt status during link faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-util.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-util.c

## Purpose
This utility file supplies shared helper functions for interface-mode names, Random Early Drop setup, common GMX/PKO port geometry, and IPD port/interface mapping.

## Important APIs, Types, And Functions
APIs include `cvmx_helper_interface_mode_to_string()`, `cvmx_helper_setup_red()`, `__cvmx_helper_setup_gmx()`, `cvmx_helper_get_ipd_port()`, `cvmx_helper_get_interface_num()`, and `cvmx_helper_get_interface_index_num()`. Internal `cvmx_helper_setup_red_queue()` programs RED thresholds and probability settings.

## Control Flow
Mode-to-string maps every helper mode enum to a stable label. RED setup disables page-count backpressure, programs all eight input queues with pass/drop marks and probability slope, disables per-port RED end, and enables RED globally for all ports. GMX setup writes TX/RX port counts, PKO GMX port mode, and GMX TX thresholds based on port count and model limits. Port mapping converts between interface/index and IPD numbering across interfaces 0 through 5.

## State, Persistence, And Dependencies
Persistent state is in IPD, GMX, and PKO CSRs. The module depends on model checks, common config macros, and `cvmx_helper_interface_get_mode()` from the coordinator.

## Integration Points
All mode-specific helpers use `__cvmx_helper_setup_gmx()` and IPD mapping helpers. The global helper initializer may expose RED setup as a user-tunable packet-drop policy.

## Risks
`cvmx_helper_setup_red_queue()` divides by `pass - drop`; invalid thresholds can divide by zero or invert behavior. Interface mapping only covers known ranges and logs illegal IPD ports. GMX setup repeatedly queries interface mode, so mode registers must already be stable.

## Test Signals
Signals include correct port-number translations, expected GMX/PKO register values for 1/2/4/8/16 port modes, RED drop behavior under FPA pressure, and error prints for illegal mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-xaui.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-xaui.c

## Purpose
This module handles XAUI and HiGig2-style high-speed interface probing, enable sequencing, link status, and link recovery.

## Important APIs, Types, And Functions
Entry points are `__cvmx_helper_xaui_enumerate()`, `__cvmx_helper_xaui_probe()`, `__cvmx_helper_xaui_enable()`, `__cvmx_helper_xaui_link_get()`, and `__cvmx_helper_xaui_link_set()`. It manipulates GMX, PCSXX, PCSX, and PKO mapping CSRs.

## Control Flow
Enumerate returns sixteen virtual ports when HiGig2 TX is enabled, otherwise one. Probe enables GMX early for GMX-700 errata, runs common GMX setup for one physical port, and maps all sixteen PKO packet ports to the same XAUI endpoint for per-virtual-port backpressure. Enable sets PKND where supported, disables GMX via PCS, masks interrupts, configures XAUI TX control and PCS reset, waits for reset, alignment, RX readiness, GMX idle, link, and no faults, clears stale interrupt state, restores interrupt enables, enables receive, enables GMX, and turns on PCS/GMX error interrupts. Link get requires TX, RX, and PCS receive-link to be healthy; otherwise it masks interrupts. Link set calls enable to recover when an up link is requested but hardware is not healthy.

## State, Persistence, And Dependencies
Persistent state resides in PKO port maps, GMX, PCSXX, and interrupt CSRs. There is no private software state. Model-specific reset suppression is required for CN66XX/CN68XX variants.

## Integration Points
The generic helper uses this for XAUI mode. PKO setup relies on the virtual-port map configured here. Interrupt decoder helpers provide PCS/GMX error enables.

## Risks
Enable sequencing has many hardware waits; any timeout returns failure and may leave interrupts temporarily altered. Link get masking interrupts on down links can suppress later diagnostics until re-enabled. HiGig2 virtual mapping assumes all virtual ports share one physical XAUI endpoint.

## Test Signals
Signals include port count change with HiGig2, successful PCS alignment and receive-link waits, 10 Gbps full-duplex link status, recovery through link_set, and preserved/restored interrupt masks across enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-xaui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper.c

## Purpose
This is the main packet I/O coordinator for Octeon CVMX helper code. It discovers interface modes, records port counts, configures IPD/PIP/PKO, enables packet hardware, applies errata, and dispatches link get/set operations to mode-specific helpers.

## Important APIs, Types, And Functions
Public APIs include `cvmx_helper_get_number_of_interfaces()`, `cvmx_helper_ports_on_interface()`, `cvmx_helper_interface_get_mode()`, `cvmx_helper_interface_enumerate()`, `cvmx_helper_interface_probe()`, `cvmx_helper_ipd_and_packet_input_enable()`, `cvmx_helper_initialize_packet_io_global()`, `cvmx_helper_link_get()`, and `cvmx_helper_link_set()`. Static state is `interface_port_count[9]`.

## Control Flow
Mode detection first gates invalid interfaces, then uses model-specific paths for CN68XX, Octeon II, CN7XXX, and earlier chips. Enumeration dispatches to each mode helper and then lets board code trim port counts. Probe repeats enumeration and lets mode helpers perform non-traffic setup. Global initialization applies CN52XX pass1 QLM errata, adjusts L2 arbitration priority for I/O, initializes PKO, probes all interfaces, configures IPD/PIP tagging and PKO queues per port, applies global IPD/PKO/backpressure settings, and optionally enables IPD and packet input. Packet enable turns on IPD, enables each interface by mode, then enables PKO. Link get/set validate port index and dispatch by current mode.

## State, Persistence, And Dependencies
The `interface_port_count` array is the key software state and is synchronized with `CVMX_SYNCWS`. Persistent hardware state spans L2C, IPD, PIP, PKO, POW, GMX, ASX, PCS, SPI, and board-specific registers. The code depends heavily on compile-time config macros and `OCTEON_IS_MODEL()` predicates.

## Integration Points
This file ties together all helper mode files, board helpers, PKO, IPD/PIP, FPA, SPI, L2C, POW, and errata handling. Network drivers can call global initialization, packet enable, and link get/set.

## Risks
Mode tables are hardware-generation-specific and easy to regress for new chips. Link status may use deprecated board fallback. The IPD pointer-alignment workaround sends crafted loopback packets and temporarily rewrites port registers, so restore paths are critical. Initialization order matters: PKO remains disabled until packet hardware is enabled.

## Test Signals
Signals include interface count/mode/port enumeration on each supported model, packet I/O initialization return codes, correct queue and PIP tag setup, successful IPD/PKO enable ordering, link dispatch per mode, and errata paths only on affected passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c

## Purpose
This generated file enables selected error interrupt bits for GMX RX, PCS lane/interface, SPI receive, and SPI transmit blocks.

## Important APIs, Types, And Functions
Functions are `__cvmx_interrupt_gmxx_rxx_int_en_enable()`, `__cvmx_interrupt_pcsx_intx_en_reg_enable()`, `__cvmx_interrupt_pcsxx_int_en_reg_enable()`, `__cvmx_interrupt_spxx_int_msk_enable()`, and `__cvmx_interrupt_stxx_int_msk_enable()`. They use model-specific union views for GMX, PCSX, PCSXX, SPXX, and STXX interrupt enable/mask registers.

## Control Flow
Each function first clears pending interrupt status by writing back the current status register. It then constructs a zeroed enable mask and selectively sets bits for the active Octeon model, skipping reserved bits and intentionally leaving noisy normal-operation bits disabled. Finally it writes the enable/mask CSR.

## State, Persistence, And Dependencies
State is persistent interrupt-mask configuration in hardware CSRs. There is no private software state. The generated model checks must match each register layout.

## Integration Points
RGMII, SGMII, SPI, and XAUI helpers call these functions after enabling their hardware. `cvmx-interrupt-rsl.c` calls the GMX RX helper while enabling GMX TX errors.

## Risks
Because register layouts differ by model, enabling a bit on the wrong model can touch reserved or noisy fields. Some useful events are deliberately disabled because they are handled in packet work or occur during normal operation, so this is not a complete diagnostic mask. The `PRINT_ERROR` macro is unused unless overridden.

## Test Signals
Signals include expected mask values per model, no reserved-bit warnings, interrupts generated for overflow/jabber/fault/training errors, and no interrupt storms from FCS, length, or link-speed changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-rsl.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-rsl.c

## Purpose
This file enables ASX and GMX error reporting for RSL interrupt blocks and delegates per-port GMX RX interrupt masks to the generated decoder file.

## Important APIs, Types, And Functions
Functions are `__cvmx_interrupt_asxx_enable(int block)` and `__cvmx_interrupt_gmxx_enable(int interface)`. It uses `CVMX_ASXX_INT_EN`, `CVMX_GMXX_INF_MODE`, `CVMX_GMXX_TX_INT_EN`, and `__cvmx_interrupt_gmxx_rxx_int_en_enable()`.

## Control Flow
ASX enable chooses a three- or four-port mask based on model, then enables TX push, TX pop, and overflow interrupts. GMX enable reads interface mode, determines how many ports report errors for the chip and interface mode, enables TX underflow and selected non-existent-address errors, and then enables RX interrupt masks for each active port.

## State, Persistence, And Dependencies
State is hardware interrupt-enable configuration. The code depends on GMX mode being configured before it runs and on model predicates matching port-count semantics.

## Integration Points
Mode-specific helpers call these functions after interface setup. The RX mask function is implemented in `cvmx-interrupt-decodes.c`.

## Risks
Wrong port count causes either missed interrupts or reserved-port enables. SPI on CN38XX/CN58XX reports GMX errors through port 0 only, a special case that must remain aligned with hardware behavior.

## Test Signals
Signals include ASX/GMX error interrupts when injecting overflow/underflow faults, correct enabled port counts for RGMII, GMII, SPI, XAUI, and SGMII modes, and no interrupts for disabled interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-rsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-l2c.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-l2c.c

## Purpose
This file implements Octeon L2 cache control, partitioning, performance counters, line locking/unlocking, tag inspection, flushing, and cache geometry queries.

## Important APIs, Types, And Functions
APIs include `cvmx_l2c_get_core_way_partition()`, `cvmx_l2c_set_core_way_partition()`, `cvmx_l2c_set_hw_way_partition()`, `cvmx_l2c_get_hw_way_partition()`, `cvmx_l2c_config_perf()`, `cvmx_l2c_read_perf()`, `cvmx_l2c_lock_line()`, `cvmx_l2c_lock_mem_region()`, `cvmx_l2c_flush()`, `cvmx_l2c_unlock_line()`, `cvmx_l2c_unlock_mem_region()`, `cvmx_l2c_get_tag()`, `cvmx_l2c_address_to_index()`, `cvmx_l2c_get_cache_size_bytes()`, `cvmx_l2c_get_set_bits()`, `cvmx_l2c_get_num_sets()`, `cvmx_l2c_get_num_assoc()`, and `cvmx_l2c_flush_line()`.

## Control Flow
Partition functions validate core and way masks, then write CN63XX `WPAR` registers or older `SPAR` fields. Performance configuration uses old `L2C_PFCTL` counters on CN3XXX/CN5XXX and TAD counters on newer models. Locking either uses CN63XX cache instructions and tag verification or older debug-core lockbase/off registers plus fault-in reads. Tag reads on older chips enter L2 debug mode in assembly with interrupts disabled, then convert model-specific tag layouts to a common union. Flush paths iterate all set/way pairs.

## State, Persistence, And Dependencies
Persistent state includes cache partition CSRs, performance counter selection, lock bits, and cache contents. `cvmx_l2c_spinlock` serializes debug-mode operations only within one kernel/application. Interrupts are disabled during fragile debug-mode tag reads.

## Integration Points
Packet I/O initialization modifies L2 arbitration priority outside this file. Diagnostics and low-level drivers can use this module for cache partitioning, performance reads, and locked-memory regions.

## Risks
Debug mode affects all data loads, so interrupts must remain disabled and only one core should operate at a time. The spinlock does not coordinate with other OS instances. Model-specific tag fields and fuse-derived associativity are error-prone. Some range checks use `>` rather than `>=`, so callers should pass known-valid assoc/index values.

## Test Signals
Signals include correct cache geometry on each model/fuse combination, partition masks rejecting all-way masks where unsupported, stable perf counter increments, successful lock-bit verification, no stale debug mode after tag reads, and full-cache flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-l2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-pko.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-pko.c

## Purpose
This module initializes and configures Octeon PKO packet output hardware, including command buffers, port/queue maps, enable/disable/reset, shutdown, and rate limiting.

## Important APIs, Types, And Functions
Public functions are `cvmx_pko_initialize_global()`, `cvmx_pko_enable()`, `cvmx_pko_disable()`, `cvmx_pko_shutdown()`, `cvmx_pko_config_port()`, `cvmx_pko_rate_limit_packets()`, and `cvmx_pko_rate_limit_bits()`. Internal helpers handle CN68XX iport queue allocation and port mapping.

## Control Flow
Global initialization programs command buffer pool/size, performs chip-specific setup, then may optimize PKO queue memory mode based on highest configured queue. CN68XX maps iports and allocates one command queue per iport. Generic chip setup first marks all queues illegal. Port configuration validates port and queue ranges, validates static-priority contiguity, initializes each command queue, converts priorities into QoS masks, writes queue pointer CSRs, and returns detailed status. Enable sets PKO, DWB, and store-endian flags. Shutdown disables PKO, invalidates all queue mappings, shuts command queues down, and resets PKO. Rate limit helpers compute token parameters from CPU clock.

## State, Persistence, And Dependencies
State resides in PKO CSRs and command queue bootmem/FPA buffers. It depends on `cvmx-cmd-queue.c`, FPA output buffer pools, helper interface mappings, model checks, and CPU clock frequency.

## Integration Points
`cvmx-helper.c` calls global initialization and per-port configuration, then enables PKO after IPD and interface hardware are ready. RGMII link changes temporarily manipulate PKO queue QoS. Command queues provide buffer pointers consumed by PKO.

## Risks
PKO must be disabled for configuration and drained before shutdown. Command queue initialization failures map to PKO errors. Rate-limit functions do not guard division by zero. CN68XX has a distinct path where generic `cvmx_pko_config_port()` returns success without programming old queue pointers.

## Test Signals
Signals include successful queue map programming, expected `ALREADY_SETUP`/invalid priority errors, packet output after enable, no queue data before shutdown, correct CN68XX iport mappings, and measured packet/bit rate limits close to configured rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-pko.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-spi.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-spi.c

## Purpose
This file implements the low-level SPI4 interface bring-up and restart sequence for CN38XX/CN58XX Octeon chips using a callback-driven pipeline.

## Important APIs, Types, And Functions
APIs are `cvmx_spi_get_callbacks()`, `cvmx_spi_set_callbacks()`, `cvmx_spi_start_interface()`, `cvmx_spi_restart_interface()`, and default callbacks `cvmx_spi_reset_cb()`, `cvmx_spi_calendar_setup_cb()`, `cvmx_spi_clock_detect_cb()`, `cvmx_spi_training_cb()`, `cvmx_spi_calendar_sync_cb()`, and `cvmx_spi_interface_up_cb()`. The static `cvmx_spi_callbacks` structure is replaceable.

## Control Flow
Start validates model support, then runs reset, calendar setup, clock detect, training, calendar sync, and interface-up callbacks; any nonzero callback aborts. Restart skips calendar setup but repeats reset through interface-up. Reset disables interrupts, runs BIST, clears calendar tables, restores masks, configures clock/DLL and dynamic alignment. Calendar setup fills RX/TX round-robin calendars and parity. Clock detect waits for TX and RX clock transitions with timeout. Training enables send/drop/receive training and waits for enough receive training events. Calendar sync enables status/calendar exchange. Interface-up enables RX/TX interface bits and programs GMX frame bounds.

## State, Persistence, And Dependencies
Persistent state is in SPXX, SRXX, STXX, and GMX CSRs. Callback state is a global function-pointer struct. Timing uses CPU cycle counts and `cpu_clock_hz`.

## Integration Points
`cvmx-helper-spi.c` calls `cvmx_spi_start_interface()` during SPI helper enable. Platform code may override callbacks for board-specific setup.

## Risks
The start/restart functions initialize `res` to -1 and return that if all callbacks are NULL or model unsupported; on normal default callbacks the final callback return controls success. Several waits can take long time or timeout. Callback replacement is global and unsynchronized. BIST failures are printed but do not abort reset.

## Test Signals
Signals include BIST status prints, clock-detect timeout behavior, training event completion, calendar sync completion, interface-up messages, successful restart after link loss, and callback override tests that abort at each stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-sysinfo.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-sysinfo.c

## Purpose
This file owns the global Octeon system-information structure populated from bootloader data and exposes it to CVMX helpers.

## Important APIs, Types, And Functions
The sole API is `cvmx_sysinfo_get()`, which returns a pointer to the static `struct cvmx_sysinfo sysinfo` and is exported.

## Control Flow
There is no initialization logic here. Callers retrieve the address of the singleton structure and read or populate fields such as board type, CPU clock, and core/application information.

## State, Persistence, And Dependencies
`sysinfo` is static kernel memory. Its correctness depends on other boot code filling it before consumers query it. The data persists for the lifetime of the kernel.

## Integration Points
Most helper files read `cvmx_sysinfo_get()` for board type, CPU clock, simulation status, and timing calculations. Board mapping, JTAG, SPI, and packet helpers all depend on it.

## Risks
Because the getter returns a mutable pointer, any caller can modify global platform facts. If boot code does not populate it before use, helpers may choose wrong board paths or compute invalid delays.

## Test Signals
Signals include expected board type and clock values after boot, stable pointer identity across callers, and correct helper behavior when sysinfo fields are initialized in test harnesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-sysinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/octeon-model.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/octeon-model.c

## Purpose
This file decodes Octeon chip IDs, fuses, core counts, cache-disable fuses, and clock rate into human-readable model strings and feature flags.

## Important APIs, Types, And Functions
The exported global `__octeon_feature_bits` records detected features such as crypto. Public API is `octeon_model_get_string(uint32_t chip_id)`. Internal helpers include `cvmx_fuse_read_byte()` and `octeon_model_get_string_buffer()`.

## Control Flow
Model decoding reads fuse and L2 cache fuse registers, determines disabled engines and suffix class, sets crypto feature presence when appropriate, derives pass string from chip ID with family-specific exceptions, maps core count to model suffix, then switches on chip family codes to resolve family, suffix, pass, and special cases. For non-CN3XXX families it may read model override fuses and replace family/core-model strings. It appends current clock MHz and suffix into `CN...p...-...-...` format.

## State, Persistence, And Dependencies
Feature bits persist in `__octeon_feature_bits`. The return string uses a static buffer in `octeon_model_get_string()`. The code depends on fuse-read CSRs, `cvmx_octeon_num_cores()`, `octeon_get_clock_rate()`, and extensive model predicates.

## Integration Points
Early platform initialization and diagnostics use the model string. Feature checks elsewhere depend on `__octeon_feature_bits`, especially crypto availability.

## Risks
The static return buffer is overwritten on each call. Model tables are dense and family-specific; new chips or fuse layouts require careful updates. Fuse reads spin until pending clears with no timeout.

## Test Signals
Signals include known chip IDs producing expected model strings, feature bits matching crypto fuses, pass-number exceptions for older families, fuse override handling, and no hangs reading fuse command status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/octeon-model.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/flash_setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/flash_setup.c

## Purpose
This platform driver maps Octeon bootbus CFI flash into the Linux MTD subsystem using device-tree discovery and bootbus register configuration.

## Important APIs, Types, And Functions
Key functions are `octeon_flash_map_read()`, `octeon_flash_map_write()`, `octeon_flash_map_copy_from()`, `octeon_flash_map_copy_to()`, `octeon_flash_probe()`, and `octeon_flash_init()`. Static state includes `flash_map`, `mymtd`, and `part_probe_types`.

## Control Flow
The late initcall registers an OF platform driver matching `cfi-flash`. Probe reads the `reg` property as chip select, reads `CVMX_MIO_BOOT_REG_CFGX(cs)`, and if enabled computes physical base, size below the boot alias, bank width, and ioremap mapping. It installs map operations that serialize accesses with `octeon_bootbus_sem`, probes CFI flash via `do_map_probe()`, and registers partitions from command line or RedBoot.

## State, Persistence, And Dependencies
The global map and MTD pointer persist after probe. Flash access depends on the bootbus semaphore to serialize with other bootbus users. The driver depends on OF, MTD map APIs, CFI probing, and Octeon bootbus CSR layout.

## Integration Points
It integrates bootbus flash with Linux MTD and partition parsers. The flash map name remains `phys_mapped_flash` for old partition lines.

## Risks
There is no remove path and no explicit iounmap cleanup. Failed `ioremap()` is not checked before map probing. Size calculation assumes bootloader places flash so it aliases under `0x1fc00000`. Unsupported bank widths only warn.

## Test Signals
Signals include platform probe from `cfi-flash`, correct physical map size/base in boot logs, successful CFI probe, partition registration, serialized reads/writes under bootbus contention, and graceful behavior when boot region is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/flash_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/oct_ilm.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/oct_ilm.c

## Purpose
This loadable module measures Octeon interrupt latency using a CIU one-shot timer and exposes statistics through debugfs.

## Important APIs, Types, And Functions
Important functions are `oct_ilm_show()`, `reset_statistics()`, `init_debugfs()`, `init_latency_info()`, `start_timer()`, `cvm_oct_ciu_timer_interrupt()`, `disable_timer()`, `oct_ilm_module_init()`, and `oct_ilm_module_exit()`. State is held in `struct latency_info li`, `reset_stats`, and debugfs `dir`.

## Control Flow
Module init creates debugfs files, requests timer interrupt `OCTEON_IRQ_TIMER0 + TIMER_NUM`, initializes clock-derived intervals, and starts a one-shot timer. The interrupt handler optionally resets stats, otherwise computes latency as current cycle count minus expected timer deadline, updates min/max/sum/count, and restarts the timer. The show function converts cycle counts to nanoseconds using the CPU clock and prints count, average, max, and min. Exit disables the timer, removes debugfs, and frees the IRQ.

## State, Persistence, And Dependencies
Latency counters persist in static memory while the module is loaded. CIU timer registers persist until disabled. The module depends on debugfs, raw local IRQ save/restore, Octeon clock functions, and CIU timer CSR definitions.

## Integration Points
Users read `/sys/kernel/debug/oct_ilm/statistics` and write reset to reset counters. It uses a dedicated CIU timer and IRQ line.

## Risks
`oct_ilm_show()` divides by `interrupt_cnt`, so reading before the first interrupt can divide by zero. `disable_timer()` does not zero-initialize the union before field writes. Stats are read without locking while the interrupt handler updates them. The debugfs `statistics` file is created write-only despite using a show file operation, which may be unintended.

## Test Signals
Signals include successful IRQ registration, periodic interrupt count growth, plausible ns latency values, reset behavior through debugfs, no divide-by-zero before first interrupt, and timer disabled after module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/oct_ilm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-crypto.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-crypto.c

## Purpose
This file provides safe kernel-side enable/disable wrappers for Octeon's COP2 crypto hardware so kernel crypto users do not corrupt user or kernel COP2 state.

## Important APIs, Types, And Functions
The exported APIs are `octeon_crypto_enable(struct octeon_cop2_state *state)` and `octeon_crypto_disable(struct octeon_cop2_state *state, unsigned long crypto_flags)`. They use `preempt_disable()/preempt_enable()`, local IRQ save/restore, CP0 status `ST0_CU2`, `KSTK_STATUS(current)`, `octeon_cop2_save()`, and `octeon_cop2_restore()`.

## Control Flow
Enable disables preemption, disables local interrupts, turns on CU2, then saves either the current task's lazy COP2 state or the currently active kernel COP2 state. It clears the task CU2 flag when stealing userspace state and returns whether CU2 was previously enabled. Disable disables local interrupts, restores saved state if CU2 had been active, otherwise clears CU2, restores interrupts, and re-enables preemption.

## State, Persistence, And Dependencies
State crosses calls through the caller-provided stack `octeon_cop2_state` and the returned flag. It also mutates current thread COP2 metadata and CP0 status. Correctness depends on no context switch between enable and disable, enforced by preemption disable.

## Integration Points
Octeon crypto implementations should wrap hardware COP2 operations with these functions. The symbols are exported GPL-only.

## Risks
Callers must always pair disable with the exact returned flags and saved state before sleeping or returning to userspace. Local IRQ protection only covers status/state transitions, not the full crypto operation. Misuse can corrupt userspace COP2 state.

## Test Signals
Signals include preserved userspace COP2 state across kernel crypto calls, no preemption warnings in wrapped regions, correct CU2 status restoration for both initially-enabled and initially-disabled cases, and successful concurrent crypto workloads across tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-crypto.c -->
