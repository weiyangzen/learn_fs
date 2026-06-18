<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.h

## Purpose
Declares linker-provided initrd symbols for OpenRISC setup code.

## Important APIs, Types, And Functions
Under `CONFIG_BLK_DEV_INITRD`, declares `extern char __initrd_start, __initrd_end;`.

## Control Flow
No flow. `setup.c` reads these symbols to reserve and report initrd memory.

## State And Persistence
No state; exposes linker-symbol addresses.

## Dependencies And Integration Points
Depends on linker script/initrd placement and `setup.c`.

## Risks
Symbol declarations must match linker output. Wrong type/address use corrupts initrd reservation.

## Test Signals
Boot with initrd, correct initrd start/end reporting, and no overlap with kernel reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/vmlinux.h -->
