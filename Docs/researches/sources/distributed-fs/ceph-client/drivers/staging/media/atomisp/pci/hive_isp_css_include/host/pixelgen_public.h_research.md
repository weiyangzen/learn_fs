<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h` declares the host-visible public interface for the pixel generator state/register interface within the Intel AtomISP CSS hardware abstraction layer. It is a declaration/ABI header rather than an implementation file.

## Important APIs, Types, and Functions

Important APIs/types are pixelgen_ctrl_get_state(), pixelgen_ctrl_dump_state(), and pixel generator register load/store. These calls expose register access, state snapshots, command submission, or queue operations for the component depending on the device.

## Control Flow

Callers use this interface after CSS device base addresses and system IDs have been initialized. State-read helpers usually load a set of registers into caller-provided state structures; register helpers perform direct load/store operations; command helpers write hardware command registers or queue tokens. The header itself has no loops or branching beyond declarations.

## State and Persistence Behavior

The header owns no memory. State lives in CSS hardware registers, DMEM/VMEM/HMEM memories, debug/event queues, or caller-provided state structures. Store/command calls can mutate live device state and may have persistent effects until the hardware block is reset or reconfigured.

## Dependencies and Integration Points

It depends on the matching local/global type definitions supplied through the AtomISP CSS include tree, especially `system_local.h`, `type_support.h`, and component-specific ID/state typedefs. Integration points are the host-side CSS driver, SP/ISP firmware synchronization, and low-level device access functions.

## Risks and Edge Cases

Risk is primarily hardware-facing: invalid IDs or register offsets can touch the wrong block; state snapshots can race with hardware updates; and placeholder public headers such as VMEM/VAMEM expose little compile-time protection. Callers also need to preserve ordering when enabling IRQs, changing FIFO modes, or sending timed-control commands.

## Test Signals

Build tests should include this header from host code. Runtime signals are register read/write smoke tests on the target block, state dump consistency, interrupt/event loop tests where relevant, and fault tests using invalid component IDs or disabled hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/host/pixelgen_public.h -->
