# sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.h

## Purpose
`core.h` is the shared hardware and software contract for the DWC3 driver family. It defines register offsets, bit fields, hardware revision constants, event formats, transfer descriptors, endpoint/request/controller state structures, feature flags, and function prototypes used by core, gadget, host, OTG, debugfs, and glue drivers.

## Important APIs, Types, and Functions
Key data types are `struct dwc3`, `struct dwc3_ep`, `struct dwc3_request`, `struct dwc3_trb`, `struct dwc3_event_buffer`, `struct dwc3_hwparams`, `struct dwc3_glue_ops`, `union dwc3_event`, `struct dwc3_event_depevt`, and `struct dwc3_event_devt`. The header also defines endpoint flags, request status constants, EP0 states, USB link states, DWC3/DWC31/DWC32 revision identifiers, and register helpers such as `DWC3_GUSB2PHYCFG(n)`, `DWC3_GUSB3PIPECTL(n)`, `DWC3_DEPCMD(n)`, and TRB field macros.

The public prototypes cover role switching, FIFO-space reads, event-buffer setup, core soft reset, SUSPHY control, host/gadget/DRD/OTG/ULPI entry points, and PM suspend/resume hooks. Static inline fallbacks make host, gadget, DRD, and ULPI calls compile away when the related Kconfig support is disabled.

## Control Flow
The header does not execute control flow directly, but it shapes every driver path. `struct dwc3` is the hub of probe, mode switching, interrupt/event processing, PM, and debugfs. `work_to_dwc()` connects the DRD work item back to the controller. Version macros such as `DWC3_VER_IS_WITHIN()` gate workarounds in `core.c` and gadget paths. Event structures define how raw 32-bit event-buffer entries are decoded into endpoint, device, and global events.

## State and Persistence Behavior
The header defines volatile in-memory state only. `struct dwc3` stores hardware-derived fields, role state, endpoint arrays, DMA buffers, PHY/clock/reset handles, quirk flags, PM flags, debugfs handles, and gadget transfer state. Endpoint state tracks TRB enqueue/dequeue positions, request lists, resource indexes, stream flags, and workaround fields. None of this is persistent across driver unload or full hardware power loss; `core.c` and glue drivers rebuild it during probe or resume.

## Dependencies and Integration Points
The contract depends on Linux USB gadget, OTG, role-switch, ULPI, PHY, DMA, debugfs, wait/completion, workqueue, power-supply, mutex, and spinlock types. Integration points include `dwc3_glue_ops` callbacks for platform-specific role/run-stop notifications, Kconfig-gated host/gadget/dual-role functions, and hardware register definitions consumed by core, gadget, ep0, host, OTG, debugfs, and platform glue sources.

## Risks
This file is high blast-radius because field layout, bit definitions, and helper macros are used across the entire DWC3 subsystem. Risks include incorrect packed event bitfields, mismatched revision constants, unsafe assumptions about `DWC3_TRB_NUM` fitting in `u8` enqueue/dequeue indexes, multiport array limits, fallback stubs hiding missing Kconfig functionality, and broad `struct dwc3` state coupling across locking domains.

## Test Signals
Build coverage across host-only, gadget-only, dual-role, debugfs, and ULPI Kconfig combinations is essential. Runtime signals include correct event decoding, endpoint ring traversal, role switch state, PM callbacks, multiport bounds, and version-specific workarounds. Static analysis should pay attention to bitfield packing, DMA structure sizes, and uses of version macros that assume a local `dwc` variable.
