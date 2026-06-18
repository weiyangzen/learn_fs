# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.h

## Purpose

`dmub_dcn301.h` declares the DCN301 DMUB register table and inherits common DCN20 declarations.

## Important APIs, Types, And Functions

It includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn301_regs`.

## Control Flow And Data Flow

There is no executable flow. The declaration supports generation selection in DMUB service setup.

## State And Persistence Behavior

No state is owned by this header.

## Dependencies And Integration Points

The header's dependency on `dmub_dcn20.h` means DCN301 uses the common DMUB register structure and hardware function API. Integration occurs wherever ASIC-specific setup maps Van Gogh/DCN301 to `dmub_srv_dcn301_regs`.

## Risks And Edge Cases

The empty hardware-functions section signals that this generation is register-table-only in this subset. Any undocumented generation behavior would be easy to miss unless covered by runtime tests.

## Test Signals

Build/link success and runtime DMUB initialization on DCN301 hardware are the relevant signals.
