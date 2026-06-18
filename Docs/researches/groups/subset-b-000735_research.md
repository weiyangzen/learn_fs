# subset-b-000735 Research

Grouped research for Octeon PCIe, packet input, packet output, and work-queue CSR/interface headers under `sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pemx-defs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pemx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pescx-defs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pescx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pexp-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pexp-defs.h

## Purpose
`cvmx-pexp-defs.h` is a pure CSR address header for the Octeon PCI Express packet/DMA complexes named NPEI and SLI. Unlike the PEM/PESC files, it does not define bitfield unions; it only gives symbolic addresses for many packet input/output, DMA, MSI, interrupt, memory-access, debug, scratch, state, and window-control registers.

## Important APIs, Types, And Functions
The API is the `CVMX_PEXP_NPEI_*` and `CVMX_PEXP_SLI_*` macro set. NPEI macros cover BAR1 indexes, BIST, control status, DMA channels, DMA doorbells and counts, packet input and output queues, instruction FIFO base/size/header registers, scatter-list FIFO registers, MSI receive/enable/map registers, RSL interrupt blocks, debug data/select, state, scratch, and memory window access. SLI macros mirror many of those functions under the SLI base, adding SLI-specific port control, MAC credit counters, packet control, S2M port controls, loopback/port kind registers, and transmit-pipe state.

## Control Flow
There is no local control flow. External code sequences these macros to initialize NPEI or SLI: set memory access/window registers, configure DMA channels and packet queues, enable packet input/output engines, set interrupt/MSI masks, and then poll counters or state registers. Indexed macros use masked offsets, typically for 2, 4, 8, 31, or 32 hardware slots.

## State And Persistence
All state is hardware-resident. Queue base-address, FIFO-size, doorbell, DMA count, MSI map, and interrupt-enable registers remain active until hardware reset or reprogramming. Packet and DMA counters represent device-side progress. The header does not define C storage or helper state.

## Dependencies And Integration Points
This file depends only on `CVMX_ADD_IO_SEG` and the broader Octeon CSR access model. It integrates with PCIe packet I/O, DMA engines, MSI interrupt routing, and packet input/output support. Higher-level code must pair these addresses with definitions from other CSR headers or raw 64-bit accesses.

## Risks
Because the file is address-only, callers lack typed bitfield protection and must know each register layout elsewhere. Masked indexed offsets can hide invalid queue/channel IDs. Some macros contain address aliases or generation-specific names, such as DMA state registers and MSI receive banks, so using the wrong NPEI versus SLI macro can touch a valid but unintended register. Register ordering and doorbell writes are side-effectful and can race with DMA or packet engines if memory barriers are missing in the caller.

## Test Signals
Good tests verify that each macro expands to the documented IO-segment address, especially indexed queue and DMA macros. Runtime signals include successful MSI delivery through receive/enable/map registers, packet queue doorbell progress, DMA count updates, interrupt summary/mask behavior, memory-window reads returning expected data, and stable state/debug register reads during bring-up and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pexp-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip-defs.h

## Purpose
`cvmx-pip-defs.h` is the generated CSR definition file for the Octeon Packet Input Processing block. It names the hardware registers used to parse incoming packets, classify them, assign QoS/group/tag metadata for POW, count per-port traffic and errors, select skip/tag bytes, handle VLAN/DiffServ/HiGig/DSA policy, configure CRC, and expose interrupt/BIST/reset state.

## Important APIs, Types, And Functions
The file defines `enum cvmx_pip_port_parse_mode` with no-parse, skip-to-L2, and skip-to-IP modes. CSR macros cover global control (`CVMX_PIP_GBL_CFG`, `CVMX_PIP_GBL_CTL`), per-port config/tagging (`CVMX_PIP_PRT_CFGX`, `CVMX_PIP_PRT_CFGBX`, `CVMX_PIP_PRT_TAGX`), QoS tables (`QOS_DIFFX`, `QOS_VLANX`, `QOS_WATCHX`, `PRI_TBLX`, `HG_PRI_QOS`), backpressure, frame length checks, CRC controls, interrupts, soft reset, tag masks, byte-select tables, and statistics families.

The union surface is broad. `cvmx_pip_prt_cfgx` controls per-port skip, parse mode, CRC, DSA/HiGig, QoS selection, group watching, raw drop, dynamic RS, tag inclusion, and frame length checking. `cvmx_pip_prt_tagx` controls POW group/tag type and which packet fields contribute to tag generation. `cvmx_pip_gbl_ctl` controls parser exception handling for IP, L4, TCP flags, VLAN stacking, DSA grouping, and ring behavior. Statistics unions `cvmx_pip_stat0_*` through `stat11_*`, inbound packet/octet/error unions, and `xstat*` variants expose drop, octet, packet, multicast, broadcast, length-bin, FCS, runt, oversize, and jabber counters.

## Control Flow
There is no function control flow in this generated header. A PIP setup flow typically programs global parser behavior, configures each input port with parse/skip/QoS/tag settings, sets VLAN/DiffServ watcher tables, optionally programs tag masks and byte-select tables, enables interrupts, and later reads statistics with optional clear-on-read through `CVMX_PIP_STAT_CTL`.

## State And Persistence
State is hardware CSR state. Configuration registers persist parser, classification, and tag-generation policy. Statistics counters persist packet activity until cleared or reset. Interrupt registers expose latched parser/drop/backpressure/error events. The header's unions are transient C views over 64-bit register values.

## Dependencies And Integration Points
The header depends on `CVMX_ADD_IO_SEG`, `uint64_t`, and endian bitfield layout. It integrates directly with `cvmx-pip.h` helper functions, `cvmx-wqe.h` packet metadata semantics, POW groups/tags, IPD packet buffering, GMX/SPI/PCI receive paths, and board configuration defaults from `cvmx-config.h`.

## Risks
The main risks are hardware-model layout variants, silent wrapping of indexed macros, and bitfield endian assumptions. Per-port parse/tag/QoS fields have downstream scheduling effects in POW, so a wrong tag mask or group field can break packet ordering or load balancing. Statistics clear-on-read must be coordinated with readers. Several interrupt bits represent latched error conditions that may require write-one-to-clear behavior not visible from the type definition alone.

## Test Signals
Signals include packet receive tests for each parse mode, QoS mapping checks for VLAN/DiffServ/watcher paths, tag generation checks for IP/TCP/non-IP packets, error-code coverage for malformed L2/IP/L4 and bad FCS/length packets, per-port counter increments and clear behavior, endian build coverage, BIST/reset validation, and integration tests confirming produced work queue entries carry the expected group, QoS, tag type, and tag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip.h

## Purpose
`cvmx-pip.h` is the hand-written interface layer for Octeon Packet Input Processing. It turns the generated PIP CSR definitions into small inline configuration and statistics helpers, defines packet parser error codes, and documents the custom packet input header that external hardware can prepend before PIP parses a packet.

## Important APIs, Types, And Functions
Constants define `CVMX_PIP_NUM_INPUT_PORTS` as 48 and `CVMX_PIP_NUM_WATCHERS` as 4. Error enums define L4 errors (`cvmx_pip_l4_err_t`), IP exceptions (`cvmx_pip_ip_exc_t`), and receive errors (`cvmx_pip_rcv_err_t`), unified by `cvmx_pip_err_t`. `cvmx_pip_port_status_t` aggregates drop, octet, packet, raw PCI, multicast/broadcast, length-bin, FCS/runt/oversize, inbound packet/octet, and inbound error counters. `cvmx_pip_pkt_inst_hdr_t` models the 64-bit external instruction header containing rawfull, parse mode, skip length, QoS, group, RS flag, tag type, and tag.

Inline helpers are `cvmx_pip_config_port()`, `cvmx_pip_config_vlan_qos()`, `cvmx_pip_config_diffserv_qos()`, `cvmx_pip_get_port_status()`, `cvmx_pip_config_crc()`, `cvmx_pip_tag_mask_clear()`, and `cvmx_pip_tag_mask_set()`. A deprecated watcher helper is present under `#if 0`, documenting why direct CSR access is preferred for pass 2 hardware.

## Control Flow
The helpers are direct CSR sequences. `cvmx_pip_config_port()` writes per-port config and tag config. VLAN and DiffServ helpers zero a CSR union, set the QoS field, and write it. `cvmx_pip_get_port_status()` writes `CVMX_PIP_STAT_CTL` to select clear-on-read behavior, reads the stat register family and inbound counters, fills the aggregate status struct, then applies a pass-1 errata workaround that derives drop counts from inbound minus processed counters. `cvmx_pip_config_crc()` programs CRC only on CN38XX/CN58XX. Tag-mask helpers clear 16 CSR entries per mask or read-modify-write byte-selection bits.

## State And Persistence
State changes are hardware-resident PIP configuration and counters. The only memory state is caller-provided `cvmx_pip_port_status_t`. `clear` in `cvmx_pip_get_port_status()` can consume statistics globally for the target reads. Tag-mask programming persists until changed or reset and affects future work queue tag generation.

## Dependencies And Integration Points
The file includes `cvmx-wqe.h`, `cvmx-fpa.h`, and `cvmx-pip-defs.h`. It depends on CSR accessors, `OCTEON_IS_MODEL()`, `cvmx_octeon_is_pass1()`, and packet-buffer/work-queue definitions. It integrates with IPD receive initialization, POW scheduling, network drivers that interpret PIP error codes in WQEs, and statistics reporting.

## Risks
The helpers trust caller-supplied port, VLAN, DiffServ, mask, and offset values; indexed CSR macros mask out-of-range values. The pass-1 drop-counter workaround can underflow if assumptions about CRC bytes or counter ordering change. `cvmx_pip_tag_mask_set()` computes `mask_index * 16 + offset / 8` without validating the 64-entry hardware table, so large offsets can wrap in the CSR macro. Statistics reads are not atomic with packet arrival, and clear-on-read can surprise concurrent readers. CRC configuration silently does nothing on unsupported models.

## Test Signals
Tests should verify CSR writes for port config, VLAN and DiffServ QoS mappings, CRC programming on supported and unsupported models, status aggregation from mocked CSR values, pass-1 drop-counter correction, tag-mask clear and bit-setting across byte boundaries, and packet receive integration where WQE error code, group, QoS, and tag match configured policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko-defs.h

## Purpose
`cvmx-pko-defs.h` is the generated CSR definition file for the Octeon Packet Output unit. It maps PKO configuration, queue pointers, queue QoS, port mapping, command buffers, CRC, debug, BIST, error, interrupt, rate/throttle, timestamp, loopback, queue mode, and engine storage/inflight registers.

## Important APIs, Types, And Functions
The file exports `CVMX_PKO_MEM_*` and `CVMX_PKO_REG_*` address macros. Memory-indexed logical register windows include `CVMX_PKO_MEM_QUEUE_PTRS`, `QUEUE_QOS`, `PORT_PTRS`, `PORT_QOS`, `IPORT_PTRS`, `IQUEUE_PTRS`, `COUNT0`, `COUNT1`, `PORT_RATE0`, `PORT_RATE1`, throttle, and many debug views. Control/status registers include `CVMX_PKO_REG_FLAGS`, `CMD_BUF`, `READ_IDX`, `GMX_PORT_MODE`, `QUEUE_MODE`, `ERROR`, `INT_MASK`, `BIST_RESULT`, `ENGINE_INFLIGHT`, `ENGINE_STORAGE`, `MIN_PKT`, loopback BPID/PKIND, preemption, queue pointer extension, throttle, and timestamp.

Important unions include `cvmx_pko_mem_queue_ptrs` and `cvmx_pko_mem_iqueue_ptrs` for queue-to-port, command-buffer pointer, tail/index, QoS mask, static priority, and static queue state; `cvmx_pko_mem_port_ptrs` for port-to-engine/backpressure mapping; `cvmx_pko_reg_cmd_buf` for FPA pool and command-buffer size; `cvmx_pko_reg_flags` for enable, reset, store endian, DWB, and throttle; `cvmx_pko_reg_error` and `cvmx_pko_reg_int_mask` for parity/doorbell/current-zero/loopback errors; and `cvmx_pko_mem_count0/count1` for packet and octet counters.

## Control Flow
No functions execute here. External PKO code uses `CVMX_PKO_REG_READ_IDX` to select an internal memory row, then reads or writes the `CVMX_PKO_MEM_*` data registers. Bring-up usually resets PKO, configures command-buffer pool and queue/port pointer tables, programs QoS and rate registers, enables PKO, and later reads counters/debug/error registers.

## State And Persistence
All state is in PKO hardware. Queue and port pointer tables persist active output routing and command-buffer ownership. Counters persist transmitted packet/octet counts. Error and BIST registers expose hardware health. Rate and throttle registers affect future scheduling. The unions are only typed overlays for 64-bit CSR values.

## Dependencies And Integration Points
The header depends on Octeon CSR infrastructure and endian bitfield selection. It is consumed by `cvmx-pko.h` and lower-level packet output initialization code, and it links to FPA buffer pools, command queues, GMX network ports, PCI/loopback output ports, and POW ordering when PKO locking is used.

## Risks
PKO internal memories are selected indirectly through `REG_READ_IDX`, so stale or wrong indices can read or clear the wrong port/queue counters. Queue pointer fields control command-buffer ownership; corrupt values can lose packets or leak FPA buffers. Many debug unions have model-specific field alternatives, so portable code should avoid assuming one layout. Error/interrupt bit semantics are not encoded in the C type. Rate, throttle, and preemption fields can starve queues if programmed incorrectly.

## Test Signals
Strong signals include reset/BIST checks, address expansion tests, queue pointer table programming validation, packet transmit tests that increment `COUNT0` and `COUNT1`, error interrupt injection for parity/doorbell/current-zero paths, read-index selection tests, rate-limit behavior checks, and packet ordering tests across static-priority and weighted queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko.h

## Purpose
`cvmx-pko.h` is the hand-written Packet Output interface for Octeon. It defines PKO queue limits, locking modes, packet command/doorbell formats, status structures, initialization/configuration prototypes, inline send helpers, queue mapping helpers, counter reads, and rate-limit APIs.

## Important APIs, Types, And Functions
The file defines `CVMX_PKO_MAX_OUTPUT_QUEUES`, `CVMX_PKO_NUM_OUTPUT_PORTS`, illegal queue constants, and queue-depth constants. `cvmx_pko_status_t` reports success, invalid port/queue/priority, no memory, duplicate setup, and command queue init errors. `cvmx_pko_lock_t` selects no locking, POW atomic-tag locking, or command-queue ll/sc locking. `cvmx_pko_port_status_t` aggregates packets, octets, and doorbell count. `cvmx_pko_doorbell_address_t` builds the IO address used for packet-send doorbells, and `union cvmx_pko_command_word0` models the first PKO command word with checksum, gather, response, free, endian, FAU decrement, segment count, and byte length fields.

External APIs include `cvmx_pko_initialize_global()`, `cvmx_pko_enable()`, `cvmx_pko_disable()`, `cvmx_pko_shutdown()`, `cvmx_pko_config_port()`, `cvmx_pko_rate_limit_packets()`, and `cvmx_pko_rate_limit_bits()`. Inline APIs include `cvmx_pko_doorbell()`, `cvmx_pko_send_packet_prepare()`, `cvmx_pko_send_packet_finish()`, `cvmx_pko_send_packet_finish3()`, `cvmx_pko_get_base_queue_per_core()`, `cvmx_pko_get_base_queue()`, `cvmx_pko_get_num_queues()`, and `cvmx_pko_get_port_status()`.

## Control Flow
Send flow is split. `cvmx_pko_send_packet_prepare()` optionally switches to a POW atomic tag for exclusive queue access. `cvmx_pko_send_packet_finish()` waits for that tag switch if needed, writes a two-word command through `cvmx_cmd_queue_write2()`, rings the doorbell on success, and maps command-queue failures to PKO status codes. `finish3()` does the same for three-word commands and a completion/WQE address. `cvmx_pko_doorbell()` constructs an IO-segment doorbell address, issues `CVMX_SYNCWS`, and writes the command-word count. Counter reads select a port through `CVMX_PKO_REG_READ_IDX`, read count registers, optionally clear them, then read a model-specific debug register for doorbell state.

## State And Persistence
Persistent state lives in global PKO hardware and command-queue named blocks created by external initialization. Inline send helpers mutate POW tag state when atomic locking is selected and mutate command queues plus PKO doorbell state. Counter clear requests write back to PKO memory counters. The header itself stores no global state, although it declares `cvmx_pko_state_elem_t` as internal PKO state shape.

## Dependencies And Integration Points
The file includes FPA, POW, command queue, and PKO CSR definitions. It depends on `cvmx_write_io`, `cvmx_read_csr`, `cvmx_write_csr`, `CVMX_SYNCWS`, `cvmx_cmd_queue_write2/3`, `CVMX_CMD_QUEUE_PKO`, model macros, queue-per-port config macros, and buffer pointer definitions. It integrates with network drivers, packet buffers, POW scheduling, command queue allocation, and PKO global setup/teardown.

## Risks
Prepare and finish must be paired with identical port, queue, and locking arguments. Atomic-tag locking cannot be descheduled because it uses a fake WQE pointer. `CVMX_PKO_LOCK_NONE` relies entirely on caller serialization. Queue mapping depends on compile-time queue-per-port macros and model checks; unmapped ports return `CVMX_PKO_ILLEGAL_QUEUE`. Doorbell writes require prior command data visibility, hence the explicit sync. Counter clear semantics are indirect and can race with transmit activity. The little-endian bitfield branch defines `port:9` where comments describe 6 bits, so ABI assumptions should be checked against compiler layout and hardware expectations.

## Test Signals
Tests should cover status-code mapping for command queue success/full/no-memory/invalid results, doorbell address formation, memory barrier placement in send paths, atomic-tag prepare/finish ordering, command-queue locking mode, queue mapping for interface, PCI, loopback, CN68XX, and invalid ports, two-word versus three-word send commands, counter read and clear behavior, model-specific doorbell debug fields, and rate-limit API behavior on supported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow-defs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow-defs.h

## Purpose
`cvmx-pow-defs.h` is the generated CSR definition file for Octeon POW, the Packet Order/Work scheduler, plus SSO-compatible work-queue interrupt aliases. It defines hardware registers for group masks, QoS thresholds and randomization, input queue counts and interrupts, work queue interrupts, no-schedule counters, ECC and BIST status, performance counters, reset masks, and per-core work-schedule accounting.

## Important APIs, Types, And Functions
Primary macros include `CVMX_POW_PP_GRP_MSKX`, `CVMX_POW_QOS_THRX`, `CVMX_POW_QOS_RNDX`, `CVMX_POW_WQ_INT`, `CVMX_POW_WQ_INT_THRX`, `CVMX_POW_WQ_INT_CNTX`, `CVMX_POW_IQ_CNTX`, `CVMX_POW_IQ_THRX`, `CVMX_POW_IQ_INT`, `CVMX_POW_IQ_INT_EN`, `CVMX_POW_ECC_ERR`, `CVMX_POW_BIST_STAT`, `CVMX_POW_NOS_CNT`, `CVMX_POW_NW_TIM`, `CVMX_POW_PF_RST_MSK`, and performance counter macros for work add, work schedule, tag switch, deschedule, and combined counters. SSO aliases include `CVMX_SSO_WQ_INT`, `CVMX_SSO_WQ_IQ_DIS`, `CVMX_SSO_WQ_INT_PC`, `CVMX_SSO_PPX_GRP_MSK`, and `CVMX_SSO_WQ_INT_THRX`.

Important unions include `cvmx_pow_pp_grp_mskx` for per-processor group masks and QoS priorities; `cvmx_pow_qos_thrx` for min/max/free/buffer/deschedule thresholds; `cvmx_pow_qos_rndx` for QoS randomization; `cvmx_pow_wq_int*` for interrupt summary, thresholds, pending counts, and IQ disable bits; `cvmx_pow_ecc_err` for single/double-bit ECC, syndrome, remote pointer, and illegal operation reporting; and `cvmx_pow_bist_stat` for multiple internal RAM/CAM self-test fields.

## Control Flow
There are no functions. External POW code programs group masks for each core, sets QoS threshold/randomization policy, configures work queue and input queue interrupt thresholds, monitors counters, and handles ECC or BIST status. Interrupt flow is external: read summary, inspect count/threshold registers, then clear or mask according to hardware semantics.

## State And Persistence
POW state is hardware scheduling state. Group masks and QoS priorities decide which cores can receive which work groups. Thresholds and randomization influence scheduler admission and fairness. Interrupt registers persist pending state. ECC status persists hardware error latches. Performance counters accumulate scheduler events until reset or cleared by external mechanisms.

## Dependencies And Integration Points
The header depends on CSR address infrastructure and endian bitfields. It integrates with `cvmx-pow.h` operation helpers, `cvmx-wqe.h` work queue entries, PIP-generated group/QoS/tag metadata, PKO atomic-tag locking, and interrupt controllers that route POW/SSO work-queue interrupts to cores.

## Risks
Misconfigured group masks can make work unreachable or send it to unintended cores. Threshold mistakes can cause interrupt storms or delayed scheduling. ECC fields are hardware-fault indicators and may require precise clear/recovery sequences not visible in the type definitions. Indexed macros mask core, QoS, and group offsets, so invalid inputs can silently target valid slots. SSO aliases share the same broad hardware region but not necessarily identical semantics on every Octeon generation.

## Test Signals
Test signals include group-mask scheduling tests, QoS threshold and randomization fairness tests, WQ/IQ interrupt threshold trigger and mask behavior, no-schedule counter changes under disabled groups, performance counter increments for add/schedule/deschedule/tag-switch paths, ECC injection or error-latch handling, BIST validation after reset, and cross-block tests confirming PIP-assigned groups and PKO atomic tags interact correctly with POW scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pow-defs.h -->
