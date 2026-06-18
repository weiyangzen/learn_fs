<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_ofw.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_ofw.c

## Purpose
Detects and calls OLPC OpenFirmware from x86 Linux, including preserving its page-directory mapping.

## Important APIs, Types, And Functions
`olpc_ofw_detect()` validates the boot header and records the client interface pointer. `setup_olpc_ofw_pgd()` copies OFW's PDE into `swapper_pg_dir`. `__olpc_ofw()` serializes client-interface calls. `olpc_ofw_present()` and `olpc_ofw_is_installed()` expose availability.

## Control Flow
Early detection checks the `OFW ` signature and rejects too-low CIF addresses, then reserves top memory containing OFW. Page-table setup maps OFW's PGD and installs the relevant PDE permanently. Calls pack name, argument count, result count, and arguments into an array, call the CIF under a spinlock, then unpack results.

## State And Persistence
Stores `olpc_ofw_cif` and boot-time `olpc_ofw_pgd`. The OFW memory reservation and kernel page-table entry persist to allow later callbacks.

## Dependencies And Integration Points
Depends on x86 boot parameters, early ioremap, page tables, `reserve_top_address()`, and OLPC DT/EC code using `olpc_ofw()`.

## Risks And Edge Cases
The CIF uses 32-bit integer argument packing, so pointer assumptions are x86/OLPC-specific. Bad OFW PGD mapping disables OFW. Calls are serialized but still execute firmware code with interrupts disabled by the spinlock.

## Test Signals
OFW detection logs, successful DT build callbacks, and absence of page faults during OFW calls validate this support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_ofw.c -->
