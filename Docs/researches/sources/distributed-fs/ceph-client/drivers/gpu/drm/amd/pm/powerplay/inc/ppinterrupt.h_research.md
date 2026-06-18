# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/ppinterrupt.h

## Purpose

`ppinterrupt.h` defines the minimal interrupt callback contract used by PowerPlay. It identifies thermal IRQ edge types and the registration record used to bind an interrupt source to a callback and context.

## Important APIs, Types, And Functions

`enum amd_thermal_irq` defines `AMD_THERMAL_IRQ_LOW_TO_HIGH`, `AMD_THERMAL_IRQ_HIGH_TO_LOW`, and `AMD_THERMAL_IRQ_LAST`. `irq_handler_func_t` is a callback taking private data, a source id, and an interrupt-vector entry pointer, returning an int status. `struct pp_interrupt_registration_info` stores callback, context, source id, and IV entry pointer.

## Control Flow And Data Flow

The header has no implementation. Runtime flow is event-driven: an ASIC interrupt handler decodes an IV entry, finds a PowerPlay registration, and invokes `call_back(context, src_id, iv_entry)`.

## State And Persistence Behavior

Registration structures are software state owned by interrupt setup code. Hardware interrupt configuration and registered callback lifetimes persist until unregister, device teardown, or reset.

## Dependencies And Integration Points

It depends on `uint32_t` from kernel integer typedefs supplied by includers. It integrates with hwmgr `register_irq_handlers`, AMDGPU interrupt handling, thermal threshold events, and ASIC-specific PowerPlay interrupt glue.

## Risks And Edge Cases

Callback context lifetime must cover every possible interrupt until unregister completes. `iv_entry` is a raw pointer and must be interpreted with the correct ASIC interrupt format. Source id mismatches can route thermal events to the wrong handler. IRQ handlers must avoid sleeping unless dispatch context permits it.

## Test Signals

Useful signals are thermal low-to-high and high-to-low interrupt tests, handler registration/unregistration during suspend/resume and teardown, synthetic IV entry dispatch, and lockdep coverage for callback context.
