# sources/distributed-fs/ceph-client/sound/hda/controllers/intel.h

## Purpose
`intel.h` defines the Intel PCI HDA driver's private wrapper structure around the shared `struct azx` controller.

## Important APIs, Types, and Functions
`struct hda_intel` embeds `struct azx chip` and adds work/completion/list members plus bitfield flags for pending IRQ warnings, probe continuation, runtime PM disablement, vga_switcheroo state, delayed init failure, resource-free status, i915 clock/power needs, and probe retry count.

## Control Flow
The header has no executable control flow. Its fields are consumed by `intel.c`: delayed probe uses `probe_work`/`probe_wait`, IRQ timing workaround uses `irq_pending_work`, power-save parameter updates use `list`, vga_switcheroo checks use the switcheroo flags, and teardown checks `freed`/`init_failed`.

## State and Persistence Behavior
The structure is allocated device-managed during PCI probe and lives as long as the ALSA card/PCI device binding. Its embedded `azx` is the object passed to most shared controller helpers.

## Dependencies and Integration Points
It depends on `hda_controller.h` for `struct azx`. The struct layout is the contract between the Intel controller implementation and the shared HDA core.

## Risks
Flag semantics are tightly coupled to asynchronous probe, PM, and teardown ordering. Misusing `container_of()` or failing to update completion/list state can deadlock switcheroo or leak power-save list entries.

## Test Signals
Build coverage with `intel.c`, delayed probe completion under success/failure, repeated remove during pending probe, power-save parameter iteration after card removal, and vga_switcheroo transitions.
