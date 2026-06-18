# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/gsp.rs

## Purpose

`falcon/gsp.rs` defines the Falcon engine marker for the GPU System Processor and adds GSP-specific Falcon helper methods.

## Important APIs, Types, And Functions

`struct Gsp(())` implements `RegisterBase<PFalconBase>` at `0x00110000`, `RegisterBase<PFalcon2Base>` at `0x00111000`, and `FalconEngine`. `Falcon<Gsp>::clear_swgen0_intr()` clears SWGEN0 in the Falcon IRQ clear register. `Falcon<Gsp>::check_reload_completed()` polls `NV_PGC6_BSI_SECURE_SCRATCH_14` for the boot-stage handoff bit.

## Control Flow

The type itself is uninstantiable and only supplies compile-time register base selection. During GPU initialization, `Gpu::new()` creates a `Falcon<Gsp>` and clears SWGEN0 so queue messages can signal the CPU. Reload completion, when used, polls until the secure scratch handoff appears or the caller-provided timeout expires.

## State And Persistence Behavior

No Rust state is stored in this file. Hardware effects persist in GSP Falcon IRQ status clear and secure scratch registers. The register bases shape all generic Falcon register accesses for the GSP engine.

## Dependencies And Integration Points

It depends on generic Falcon support, register-base traits, BAR0 IO, polling, and GSP-specific registers. It integrates with `gpu.rs`, GSP boot sequencing, and firmware loading paths that target `FalconFirmware<Target = Gsp>`.

## Risks And Test Signals

Risks include incorrect base addresses, SWGEN0 clearing at the wrong time, and reload polling returning only `true` on success with timeout propagated as an error. Test by confirming GSP Falcon register accesses hit the expected MMIO range, queue interrupts are delivered after boot, and reload handoff polling behaves on resume/reload scenarios.
