# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.h

Purpose: declares the hardware-facing HPD IRQ API used by display interrupt dispatchers and the generic hotplug core.

Important APIs/types/functions: exposes per-platform IRQ decoders, i9xx ack, hotplug interrupt enable updates, per-encoder HPD detection enable, global HPD IRQ setup, and `intel_hotplug_irq_init()`.

Control flow: display IRQ code calls the relevant handler with raw IIR/status values. Hotplug core calls `intel_hpd_irq_setup()` when storm state changes. Encoder setup or Type-C code can call `intel_hpd_enable_detection()` for a single encoder.

State and persistence behavior: no direct state is defined in the header; implementations update `struct intel_display` and HPD MMIO state.

Dependencies and integration points: bridges display IRQ dispatch code, `intel_hotplug.c`, encoder setup, and platform display initialization.

Risks: adding a platform requires both a handler prototype and dispatch integration. Wrong use of locked versus unlocked interrupt update helpers can race HPD enable RMW sequences.

Test signals: compile coverage by platform configs, interrupt dispatch tests, storm reprogramming through `intel_hpd_irq_setup()`, and HPD enable calls for newly initialized encoders.
