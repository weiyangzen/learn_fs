# sources/distributed-fs/ceph-client/arch/x86/include/asm/mce.h

## Purpose
Defines x86 machine-check architecture constants, error record structures, notifier APIs, polling flags, vendor-specific Scalable MCA IDs, and initialization hooks.

## Important APIs, Types, And Functions
Important macros cover `MCG_CAP`, `MCG_STATUS`, `MCi_STATUS`, AMD SMCA MSR address calculation, MCACOD masks, MCE handling flags, and `MAX_NR_BANKS`. Types include `struct mce_log_buffer`, `enum mce_notifier_prios`, `struct mce_hw_err`, `mce_banks_t`, `enum mcp_flags`, and AMD `enum smca_bank_types`. Functions include `mcheck_init()`, `mca_bsp_init()`, `mcheck_cpu_init()`, `mce_prep_record()`, `mce_log()`, `machine_check_poll()`, `do_machine_check()`, `mce_register_decode_chain()`, Intel/AMD feature init hooks, APEI reporting helpers, and copy-machine-check helpers.

## Control Flow
CPU init discovers MCA banks and vendor features, machine-check exceptions populate `struct mce_hw_err`, records are decoded through notifier chains, and polling checks selected banks with flags controlling timestamps and uncorrected-error logging. Intel CMCI and AMD deferred error paths use vector hooks declared here.

## State And Persistence
State includes per-CPU MCE devices, exception/poll counters, poll bank bitmaps, injection records, MCE log buffers, bank state, and hardware MSRs. Logs persist only in kernel memory or downstream reporting facilities.

## Dependencies And Integration Points
Depends on UAPI MCE records, CPU feature data, percpu/atomic APIs, APEI/CPER, EDAC, NFIT, mcelog consumers, and vendor-specific MCA decoders.

## Risks And Edge Cases
Bit definitions are hardware ABI. Recovery decisions depend on `PCC`, `AR`, `S`, address validity, and kernel-copy flags. Vendor structure offsets are externally parsed and must remain stable. Polling, CMCI, deferred interrupts, and firmware-claimed banks must not double-report or clear errors incorrectly.

## Test Signals
RAS/MCE injection tests, APEI error injection, EDAC/mcelog decode paths, copy_mc fault tests, Intel CMCI rediscovery, AMD SMCA bank typing, and build coverage with MCE disabled are important signals.
