# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/pri_nv_xal_ep.h

## Purpose
Defines GH100 XAL endpoint BAR0 window base field and register address.

## Important APIs, Types, And Functions
Exports `NV_XAL_EP_BAR0_WINDOW_BASE_SHIFT`, `NV_XAL_EP_BAR0_WINDOW_BASE`, and `NV_XAL_EP_BAR0_WINDOW`.

## Control Flow
No executable flow. BAR0 windowing code programs or decodes the window base field.

## State And Persistence
No C state. The BAR0 window register controls hardware address-window mapping until reprogrammed.

## Dependencies And Integration Points
Integrated with endpoint/BAR0 access paths and DRF helpers.

## Risks
Wrong shift or field width can expose the wrong BAR0 window, causing bogus MMIO accesses.

## Test Signals
BAR0 window read/write tests, endpoint register access, and fault-free GH100 initialization validate usage.
