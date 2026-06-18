# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_global.h

## Purpose
Defines global AtomISP CSS hardware topology, memory classes, bus widths, device ids, and platform-wide constants shared by host and firmware-facing code.

## Important APIs, Types, and Functions
Important macros include DMA workaround flags, max burst lengths, HRT bus/register byte sizes, input formatter reset offsets/masks, memory counts, and `N_*` constants. It defines ids for DDR, ISP, SP, MMU, DMA, GDC, VAMEM, BAMEM, HMEM, IRQ, timers, GPIO, timed controller, input formatters, input system, RX, MIPI ports, subsystems, ISP memories, ISP2401 ISYS IRQ, IBUF controllers, stream2MMIO, CSI RX front/back ends and lanes, ISYS DMA, pixel generators, input ports, and DMA channels.

## Control Flow
No runtime flow. The enums size hardware base-address arrays and provide ids for low-level device APIs.

## State and Persistence Behavior
The file is static topology. Values are effectively ABI for register maps and firmware assumptions.

## Dependencies and Integration Points
Includes `hive_isp_css_defs.h`, `type_support.h`, and deprecated `hive_types.h`. Used throughout AtomISP PCI code, system-local maps, SP code, input formatter, MMU/DMA/GDC/timer drivers, and ISP2401 input system code.

## Risks
Changing ids or counts can misindex base-address arrays in `system_local.c` and can break preprocessor users that depend on `N_GDC_ID_CPP` or fixed port ids. The file mixes ISP2400 and ISP2401 topology, so platform-specific callers must still gate behavior correctly.

## Test Signals
Compile-time array sizing, probe-time register access on ISP2400/2401, input formatter reset, MMU/DMA/GDC operations, and MIPI port selection are the practical signals.
