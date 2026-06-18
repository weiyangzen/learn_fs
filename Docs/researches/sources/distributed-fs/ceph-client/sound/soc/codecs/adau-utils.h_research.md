# sources/distributed-fs/ceph-client/sound/soc/codecs/adau-utils.h

## Purpose
Header declaring shared ADAU PLL helper functionality.

## Important APIs, Types, and Functions
Declares `adau_calc_pll_cfg(unsigned int freq_in, unsigned int freq_out, uint8_t regs[5])`, which fills five hardware PLL configuration bytes.

## Control Flow
No executable flow. The declaration is consumed by ADAU codec drivers before calling into `adau-utils.c`.

## State and Persistence
No state. The output buffer belongs to the caller.

## Dependencies and Integration Points
Requires `uint8_t` to be available from included kernel headers in callers. It is included by ADAU-family codec drivers that need PLL programming.

## Risks
The header does not document input constraints; callers need to know the helper can reject unsupported ratios and that nonzero output requires nonzero input.

## Test Signals
Build coverage in all users and direct tests of the implementation function.
