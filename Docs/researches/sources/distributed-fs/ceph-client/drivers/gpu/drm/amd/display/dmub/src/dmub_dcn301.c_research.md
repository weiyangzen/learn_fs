# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c

## Purpose

`dmub_dcn301.c` provides the DCN 3.0.1 DMUB register table for Van Gogh style hardware. It does not implement additional hardware operations in this file.

## Important APIs, Types, And Functions

The exported object is `dmub_srv_dcn301_regs`, a `struct dmub_srv_common_regs` populated by expanding the common DMUB register and field macros against DCN 3.0.1 generated offset/mask/shift definitions.

## Control Flow And Data Flow

Runtime hardware access is indirect. Service code points `dmub->regs` at `dmub_srv_dcn301_regs` and uses common function implementations from the DCN20 model unless another table overrides them elsewhere.

## State And Persistence Behavior

The file defines immutable register metadata only.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn301.h`, generated DCN 3.0.1 headers, and `vangogh_ip_offset.h`. It integrates with ASIC selection logic that chooses DCN301 register metadata for DMUB operations.

## Risks And Edge Cases

The file assumes common DCN20-style function behavior is enough for DCN301. Any DCN301-specific window, reset, mailbox, or boot-option behavior would need explicit functions added elsewhere.

## Test Signals

Signals include clean build with Van Gogh register headers, successful link of `dmub_srv_dcn301_regs`, and DMUB boot/command execution on DCN301 hardware using the selected table.
