<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_oss.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_oss.h

## Purpose
`mac_oss.h` describes the OSS interrupt and ROM-control chip used in place of VIA2 on Macintosh IIfx systems.

## Important APIs, Types, and Functions
It defines `OSS_BASE`, interrupt source indexes and pending bits for NuBus slots, IOPs, sound, SCSI, 60 Hz, VIA1, parity, and unused lines, `OSS_POWEROFF`, `struct mac_oss`, globals `oss` and `oss_present`, plus interrupt registration/enable/disable APIs.

## Control Flow, State, and Persistence
The header is declarative. Runtime state is the OSS register block, including interrupt level assignments, pending bits, poweroff control, and 60 Hz acknowledgement.

## Dependencies and Integration Points
Mac IRQ setup uses OSS for IIfx interrupt routing. Poweroff and timer acknowledgment code use `rom_ctrl` and `ack_60hz`.

## Risks
OSS is not VIA-compatible beyond selected behavior. Interrupt pending bits are 16-bit fields and require correct endian/access width. Poweroff is a ROM-control bit with machine-wide effect.

## Test Signals
IIfx boot should detect `oss_present`, route NuBus/SCSI/IOP/sound interrupts, acknowledge 60 Hz ticks, and power off through `OSS_POWEROFF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/mac_oss.h -->
