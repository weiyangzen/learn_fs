<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/adl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/adl.c

## Purpose
Provides Alder Lake PMC register maps and bit-name tables consumed by the shared Intel PMC core.

## Important APIs, Types, And Data
Static `pmc_bit_map` tables name PFET acknowledge bits, LTR sources, clock-source status, power-gating status groups, D3 status groups, VNN request status groups, and miscellaneous low-power-mode status bits. `adl_lpm_maps[]` orders the LPM status maps. `adl_reg_map` supplies offsets, counter steps, LTR ignore limits, map pointers, LPM register offsets, residency offsets, and read-disable metadata. `adl_pmc_dev` selects `adl_reg_map` with Cannon Lake suspend/resume hooks.

## Control Flow
There are no functions in this file. The PMC core selects `adl_pmc_dev` for Alder Lake class IDs, then uses the map tables to decode debugfs/status output, read residency counters, manage LTR ignore/show, and perform suspend/resume quirk handling.

## State And Persistence
All structures are static const except the exported `adl_pmc_dev` descriptor. Runtime state is held by the PMC core; hardware state lives in PMC MMIO/MSR registers described by these offsets and bit masks.

## Dependencies And Integration Points
Depends on `core.h` for register-offset constants, shared maps such as `msr_map` and `tgl_signal_status_map`, and shared suspend/resume functions `cnl_suspend`/`cnl_resume`.

## Risks And Test Signals
Risks are incorrect bit names, wrong offsets/counter steps, LPM map order mismatches, and inherited CNP/TGL constants that may not fit all Alder Lake variants. Test PMC debugfs decoding, S0ix and PSON residency counters, LTR ignore/show, LPM live/latch status, suspend/resume on Alder Lake systems, and compare against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/adl.c -->
