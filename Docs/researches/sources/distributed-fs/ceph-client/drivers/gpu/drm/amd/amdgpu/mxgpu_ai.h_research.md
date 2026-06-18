# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.h

## Purpose

`mxgpu_ai.h` declares the AI SR-IOV mailbox interface and protocol constants used by `mxgpu_ai.c` and SOC15 virtualization setup. It defines request/event IDs shared between VF driver and PF mailbox firmware.

## Important APIs, Types, And Functions

It defines timeout constants for ACK, message, FLR, and retry count; `enum idh_request` for GPU init/fini/reset access, init data, VF error logging, ready-to-reset, RAS poison, and bad-page requests; `enum idh_event` for PF responses and notifications; `extern const struct amdgpu_virt_ops xgpu_ai_virt_ops`; IRQ helper prototypes; and byte-offset macros for transmit and receive mailbox control fields.

## Control Flow

No executable flow is present. The constants drive `mxgpu_ai.c` control flow: polling durations, request selection, receive IRQ event dispatch, reset wait, RAS handling, and mailbox control byte access.

## State And Persistence Behavior

The header stores no state. The enums and macros define protocol state values written to or read from PF0 mailbox registers. The control offsets are byte offsets into `mmBIF_BX_PF0_MAILBOX_CONTROL`.

## Dependencies And Integration Points

It integrates with SOC15/NBIO register definitions for `SOC15_REG_OFFSET` and `mmBIF_BX_PF0_MAILBOX_CONTROL`, and with AMDGPU virtualization via `struct amdgpu_virt_ops`. `soc15.c`, `amdgpu_vf_error.c`, and `mxgpu_ai.c` include it.

## Risks

Protocol numeric values are ABI-sensitive. Changing enum values or timeouts can break PF/VF negotiation. The misspelled `AI_MAIBOX_*` macro names are part of local API compatibility. The header assumes includers have already included types and register macros needed by prototypes and offset definitions.

## Test Signals

Build all includers, verify mailbox offsets compile with NBIO register headers, run SR-IOV mailbox negotiation and reset tests, and confirm PF event IDs decode correctly in receive IRQ paths.
