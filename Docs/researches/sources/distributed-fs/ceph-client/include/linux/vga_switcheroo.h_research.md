# sources/distributed-fs/ceph-client/include/linux/vga_switcheroo.h

## Purpose
This header defines the VGA switcheroo framework for laptops with integrated/discrete GPUs sharing outputs, including mux handler and client callback contracts.

## Important APIs, types, and functions
Key enums are handler flags, client power state, and client IDs. Important types are `vga_switcheroo_handler` and `vga_switcheroo_client_ops`. APIs register/unregister GPU and audio clients, set framebuffer association, register/unregister handlers, query flags, lock/unlock DDC, process delayed switches, defer probing, query client power state, and install/finalize PM domain ops. Disabled builds mostly return success/no-op or `-ENODEV` for DDC.

## Control flow, state, and persistence
GPU/audio clients register with callbacks for power state, reprobe, switch readiness, and audio binding. A platform handler supplies mux/DDC/power operations and client ID detection. The framework coordinates delayed switching and power-domain behavior based on client readiness. State is runtime client/handler registration and power/mux ownership.

## Dependencies and integration points
It depends on framebuffer and PCI declarations. It integrates DRM GPU drivers, HDA audio, platform mux handlers, DDC/EDID probing, and runtime power management.

## Risks and test signals
Risks include switching while device files are open, DDC/AUX ownership mismatches, audio/GPU ID mismatch, and disabled-config behavior hiding missing dependencies. Tests should cover dual-GPU registration, handler registration, delayed switch, DDC locking, audio binding, PM domain ops, and unregister cleanup.
