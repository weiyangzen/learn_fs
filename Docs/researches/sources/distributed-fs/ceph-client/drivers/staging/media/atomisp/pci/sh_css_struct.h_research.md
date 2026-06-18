# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_struct.h

## Purpose
Defines the global `struct sh_css` driver context for AtomISP CSS, separated from the historical `sh_css.h` naming.

## Important APIs, Types, and Functions
`struct sh_css` tracks active and all pipes, allocation/free/flush callbacks, ISP2401 extended allocation hooks, copy-preview stop flag, idle-check flag, continuous raw/MIPI frame arrays, metadata arrays, MIPI size checks, SP binary address, page-table base, deprecated memory sizing, IRQ type, pipe counter, and IPU type. Macros define `IPU_2400`, `IPU_2401`, `IS_2400()`, and `IS_2401()`, with `extern struct sh_css my_css`.

## Control Flow
The header defines context accessed across CSS setup, stream configuration, memory management, interrupt, and MIPI buffering paths. Runtime flow is in users of `my_css`.

## State and Persistence Behavior
`my_css` is long-lived global driver state. It persists pipe objects, current buffering state, platform type, and callback ownership across stream operations.

## Dependencies and Integration Points
Includes local system address maps and CSS public pipeline/pipe/frame/queue/IRQ headers. Integrates with code that allocates pipes, stores MIPI buffers, and branches between ISP2400 and ISP2401.

## Risks
The comment notes pipe-count assumptions tied to SP thread ids; expanding pipe object counts without revisiting arrays can break scheduling. Global mutable state and platform-type macros make concurrent or multi-device operation risky.

## Test Signals
Probe/init should set `my_css.type`, pipe create/destroy should update active/all arrays, continuous MIPI capture should fill frame and metadata arrays, and ISP2400/2401-specific paths should branch correctly.
