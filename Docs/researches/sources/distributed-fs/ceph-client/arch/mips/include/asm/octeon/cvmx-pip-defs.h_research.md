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
