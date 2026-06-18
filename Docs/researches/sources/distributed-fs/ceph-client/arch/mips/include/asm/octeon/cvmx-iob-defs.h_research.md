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
