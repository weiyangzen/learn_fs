# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.c

## Purpose
Programs DCN2 VMID page-table context registers for display GPUVM access and waits for hardware acknowledgement.

## Important APIs, Types, And Functions
`dcn20_vmid_setup()` writes start/end logical page numbers, page-table depth and block size, high page-directory address, then low page-directory address last. `dcn20_wait_for_vmid_ready()` polls `PAGE_TABLE_BASE_ADDR_LO32` until bit 0 becomes set, with a 10000 iteration limit and 5 microsecond delay.

## Control Flow
Setup writes start and end address high/low fields, control fields, base high, base low, then calls the wait helper. The wait helper repeatedly reads `VM_CONTEXT0_PAGE_DIRECTORY_ENTRY_LO32`; success returns immediately, timeout logs a warning and asserts.

## State And Persistence
Persistent state is the VM context hardware register set for the VMID. No software state is retained except descriptor pointers in `struct dcn20_vmid`.

## Dependencies And Integration Points
Depends on Linux `udelay`, `dcn20_vmid.h`, `reg_helper`, and logger/assert infrastructure. It integrates with DCN memory hub/display VM setup before surfaces or writeback clients use GPU virtual addresses.

## Risks
Programming order is critical: hardware requires the low base register last. Timeout constants are marked TODO and may be too long or short for some ASICs. The ready check uses bit 0 of the full field rather than `REG_WAIT` on a named field.

## Test Signals
VMID setup should complete without timeout, page-table register readback should match config values, GPUVM-backed scanout/writeback should work, and fault logs should remain clean under VM context updates.
