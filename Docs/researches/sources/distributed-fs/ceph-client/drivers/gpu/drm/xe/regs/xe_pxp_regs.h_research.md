# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pxp_regs.h

## Purpose

`xe_pxp_regs.h` defines protected Xe Path (PXP) KCR registers that are valid on platforms with a media GT, including KCR initialization, session-in-play status, and global session termination.

## Important APIs, Types, and Definitions

- `KCR_INIT` and `KCR_INIT_ALLOW_DISPLAY_ME_WRITES` for KCR/display ME write enable.
- `KCR_SIP` for hardware DRM session-in-play status.
- `KCR_GLOBAL_TERMINATE` for global PXP session termination.

## Control Flow

The file is a register contract. PXP code programs KCR init state, reads session status, and writes global termination during protected content lifecycle and reset handling.

## State and Persistence Behavior

KCR state is hardware security/session state. Session-in-play bits persist while protected sessions exist, and global termination is a command-like write that affects active sessions.

## Dependencies and Integration Points

It includes `regs/xe_regs.h` and integrates with PXP, KCR interrupt handling from `xe_irq_regs.h`, media GT initialization, and display/protected-content flows.

## Risks and Edge Cases

- Registers are only valid on media-GT platforms; ungated use can access invalid MMIO.
- Global termination is high impact and must not be issued accidentally.
- Session status races with firmware or interrupt-driven state transitions.

## Test Signals

Signals include PXP initialization on media GT systems, KCR interrupt delivery, session status transitions, global termination recovery, and no access attempts on unsupported platforms.
