# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.h

## Purpose
This header declares CN23XX VF-specific LiquidIO chip state and public VF setup/mailbox helper APIs.

## Important APIs, Types, And Functions
`struct octeon_cn23xx_vf` stores the VF configuration pointer. Constants include `BUSY_READING_REG_VF_LOOP_COUNT` and `CN23XX_MAILBOX_MSGPARAM_SIZE`. Declarations cover PF-requested FLR, PF/VF handshake, VF device setup, and VF OQ tick conversion.

## Control Flow
The VF front end calls `cn23xx_setup_octeon_vf_device()` during chip setup, then the generic LiquidIO core uses installed function pointers. The PF/VF handshake helper is called to exchange readiness, version, and ring metadata with the PF.

## State And Persistence
The header defines in-memory state only. VF runtime state is kept in `octeon_device`, the mailbox object, and hardware CSRs.

## Dependencies And Integration Points
It includes `cn23xx_vf_regs.h` and assumes `struct octeon_device` and `struct octeon_config` are visible from LiquidIO core headers.

## Risks
The header keeps VF configuration minimal; callers must not expect PF-like interrupt pointer fields. Mailbox parameter size is fixed at six bytes and must match protocol users copying into `pfvf_hsword`.

## Test Signals
Compile VF-only and core builds, validate handshake message parameter sizing, and exercise all declared helpers under PF-present and PF-absent conditions.
