<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.h

## Purpose
Defines the shared VFE data model and public interfaces used by CAMSS core, hardware-specific VFE implementations, and video-node code.

## Important APIs, Types, And Functions
- Defines pad constants, write-master limits, halt/frame-drop constants, `enum vfe_output_state`, `enum vfe_line_id`, `struct vfe_output`, `struct vfe_line`, `struct vfe_hw_ops`, `struct vfe_isr_ops`, `struct vfe_subdev_resources`, and `struct vfe_device`.
- Declares VFE initialization/registration, power, reset, stream, buffer, WM, ISR, and helper APIs.
- Declares external format tables and hardware ops tables including Gen1, Titan/IFE generations, and Gen3.

## Control Flow
The header has no implementation, but it defines the contracts used by runtime flow. `camss.c` resource tables point each VFE instance at a `struct vfe_hw_ops`; `camss-vfe.c` calls those ops from power and stream paths; hardware-specific files call back into shared helpers for buffer queues and completions.

## State And Persistence
`struct vfe_device` holds the persistent in-memory state for a VFE instance while the driver is bound: MMIO bases, IRQ name/id, clocks, completions, locks, counters, output map, line array, ops pointers, video ops, and power-domain links. `struct vfe_output` tracks per-line buffer state and pending queues. No state survives driver unload or reboot.

## Dependencies And Integration Points
Includes Linux clock/spinlock types and media/V4L2 headers, plus `camss-video.h` and Gen1 declarations. It is included broadly by CAMSS core, VFE hardware files, VBIF helpers, and CSID parent integrations.

## Risks And Edge Cases
The ABI is internal but highly coupled: changes to enum values, line counts, WM limits, or union members affect several hardware generations. `to_vfe()` relies on array layout and line IDs matching array indices. The `vfe_hw_ops` table mixes optional and mandatory callbacks, so users must guard optional entries consistently.

## Test Signals
Compile coverage across all enabled SoC variants is the first signal. Runtime signals are successful VFE probe, stream, interrupt, power, and buffer tests using all ops tables that instantiate these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.h -->
