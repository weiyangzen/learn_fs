
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/intel_th.h

Purpose: central private Intel TH header defining bus device/driver types, controller state, capability quirks, output descriptors, resource offsets, scratchpad bits, and core APIs.

Important APIs/types/functions: `struct intel_th_device` represents SOURCE, OUTPUT, or SWITCH subdevices. `struct intel_th_output` is the switch/output handshake object. `struct intel_th_driver` defines probe/remove plus switch, output, file, IRQ, and source callbacks. `struct intel_th` holds parent controller state including subdevices, resources, IRQs, char major, hub pointer, and controller activation hooks. Inline helpers include `intel_th_device_get_resource()`, `intel_th_output_assigned()`, `to_intel_th_parent()`, `to_intel_th()`, and `to_intel_th_hub()`.

Control flow: no standalone execution; it shapes all Intel TH driver interactions. Parent drivers allocate `struct intel_th`; child drivers register `struct intel_th_driver`; output and source drivers use the exported trace and routing helpers.

State and persistence: defines in-memory topology and volatile hardware resource layout. Quirk bits (`tscu_enable`, `multi_is_broken`, `has_mintctl`, `host_mode_only`) persist only as static driver data selected by PCI/ACPI IDs.

Dependencies and integration: depends on Linux device, resource, IRQ, and file-operation types. It integrates the core, GTH, MSU, PTI/LPP, STH, PCI, and optional ACPI frontend.

Risks: because this header encodes object ownership and callback contracts, changes can break several modules at once. Parent/child conversions are type-sensitive; misuse of `to_intel_th()` on output devices depends on correct parent linkage.

Test signals: all Intel TH modules should build; probe/remove and output activation should be tested for every callback combination; static analysis should check resource array bounds and callback NULL handling.
