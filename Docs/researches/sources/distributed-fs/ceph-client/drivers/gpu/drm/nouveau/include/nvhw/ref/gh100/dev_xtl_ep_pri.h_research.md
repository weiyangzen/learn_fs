# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_xtl_ep_pri.h

## Purpose
Defines the GH100 endpoint PCFGM PRI register aperture.

## Important APIs, Types, And Functions
Exports the `NV_EP_PCFGM` register range.

## Control Flow
No executable flow. Consumers use the range as an address boundary for endpoint configuration access.

## State And Persistence
The header stores no state; registers in the range are endpoint hardware configuration state.

## Dependencies And Integration Points
Integrated with PCIe/XTL endpoint code and BAR0/PRI access paths.

## Risks
Incorrect range constants can route endpoint configuration reads/writes to the wrong PRI block.

## Test Signals
PCIe endpoint initialization, BAR/window access tests, and register trace correctness validate it.
