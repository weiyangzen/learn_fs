# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_falcon_v4.h

## Purpose
Defines GH100 Falcon v4 mailbox and hardware-configuration registers used by firmware-controller code.

## Important APIs, Types, And Functions
Exports `NV_PFALCON_FALCON_MAILBOX0/1` data fields and `NV_PFALCON_FALCON_HWCFG2_RISCV_BR_PRIV_LOCKDOWN` with lock/unlock values.

## Control Flow
No executable flow. Firmware code reads/writes mailboxes and inspects RISC-V branch privilege lockdown state.

## State And Persistence
Mailbox registers carry transient firmware/driver messages. `HWCFG2` is hardware configuration state.

## Dependencies And Integration Points
Integrated with Falcon/RISC-V firmware boot, status, and security bring-up paths.

## Risks
Mailbox interpretation is protocol-specific. Incorrect lockdown handling can misdiagnose firmware privilege state or violate security assumptions.

## Test Signals
Firmware boot logs, mailbox traces, and RISC-V privilege/lockdown status checks validate usage.
