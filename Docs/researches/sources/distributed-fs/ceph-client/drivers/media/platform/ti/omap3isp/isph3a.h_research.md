# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a.h

## Purpose
`isph3a.h` provides shared H3A Auto Exposure/White Balance and Auto Focus register constants and lifecycle declarations for the OMAP3 ISP statistics engines.

## Important APIs, Types, And Functions
- AEWB constants define packet size, saturation limits, change-flag bits, PCR enable/busy masks, and AEW mask composition.
- AF constants define register offsets, PCR masks, paxel field masks, coefficient masks, and bit shifts used by the AF programming code.
- Public lifecycle functions are `omap3isp_h3a_aewb_init()`, `omap3isp_h3a_aewb_cleanup()`, `omap3isp_h3a_af_init()`, and `omap3isp_h3a_af_cleanup()`.

## Control Flow
No executable control flow is present. The constants are used by the AEWB and AF implementations when validating userspace configs, converting them to register values, enabling hardware, and checking busy state.

## State And Persistence
The header has no persistent state. It defines the bit-level contract that lets `isph3a_aewb.c` and `isph3a_af.c` keep their cached `ispstat` private configs consistent with hardware registers.

## Dependencies And Integration Points
It includes the OMAP3 ISP userspace ABI header `linux/omap3isp.h`, so the limits and struct definitions used by ioctls are shared with driver code. It also references `struct isp_device` through function prototypes.

## Risks And Edge Cases
Incorrect mask/shift updates would corrupt H3A hardware programming and stats buffer sizing. AEWB and AF share the H3A PCR register, so constants must remain non-overlapping where the implementations use `isp_reg_clr_set()`.

## Test Signals
Compile coverage of AEWB/AF files exercises these constants. Functional tests should verify PCR programming for AF and AEWB can be enabled independently without clobbering unrelated bits.
