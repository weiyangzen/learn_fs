# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_crtc.h

## Purpose
Public CRTC declarations for the TIDSS DRM driver. The header defines the driver-specific CRTC container, extended CRTC atomic state, conversion macros, IRQ hooks, and CRTC creation entry point.

## Important APIs, Types, And Functions
`struct tidss_crtc` embeds `struct drm_crtc`, stores `hw_videoport`, a pending `drm_pending_vblank_event *event`, and `struct completion framedone_completion`. `to_tidss_crtc()` converts a DRM CRTC pointer to the driver container. `struct tidss_crtc_state` embeds `struct drm_crtc_state` first and adds `plane_pos_changed`, `bus_format`, and `bus_flags`; `to_tidss_crtc_state()` converts base state pointers. Exported functions are `tidss_crtc_vblank_irq()`, `tidss_crtc_framedone_irq()`, `tidss_crtc_error_irq()`, and `tidss_crtc_create()`.

## Control Flow
The header itself has no executable flow. It defines the type contracts used by CRTC implementation, IRQ dispatch, KMS initialization, and other TIDSS modules that need to create CRTCs or notify them of videoport interrupts.

## State And Persistence
State fields declared here persist for the lifetime of the CRTC object and individual atomic CRTC states. The pending event and completion coordinate asynchronous IRQ-driven state transitions. No external persistence exists.

## Dependencies And Integration Points
The header depends on Linux completion/wait declarations and DRM CRTC types. It forward-declares `struct tidss_device` to avoid pulling in full driver headers. It is included by `tidss_crtc.c` and likely by IRQ/KMS setup code.

## Risks And Maintenance Notes
`struct tidss_crtc_state` requires `base` to remain first because helper conversion assumes container layout. Any new fields added to the state must be copied/reset in duplicate/reset paths in `tidss_crtc.c`. Event and completion fields are concurrency-sensitive and must be accessed with the locking/waiting rules implemented by the C file.

## Test Signals
Signals are compile-time and integration-time: correct container conversions, successful CRTC creation, IRQ code linking to declared hooks, and extended state fields preserved across duplicate/reset/destroy operations.
