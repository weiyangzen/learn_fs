# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.h

## Purpose

`dmub_dcn30.h` declares the DCN30 DMUB register table and the DCN30-specific hardware functions that override DCN20 behavior.

## Important APIs, Types, And Functions

The header includes `dmub_dcn20.h`, declares `extern const struct dmub_srv_common_regs dmub_srv_dcn30_regs`, and declares `dmub_dcn30_backdoor_load` plus `dmub_dcn30_setup_windows`.

## Control Flow And Data Flow

The declarations allow hardware-function tables to select DCN30-specific firmware loading and window setup while keeping the rest of the common DCN20-style DMUB operation surface.

## State And Persistence Behavior

No state is owned in the header. The declared functions mutate hardware state in `dmub_dcn30.c`.

## Dependencies And Integration Points

It depends on the common DCN20 register/function declarations. Service creation code for DCN30 ASICs should use `dmub_srv_dcn30_regs` and substitute the two declared function overrides.

## Risks And Edge Cases

If service code forgets to use the DCN30 overrides, CW2-CW7 addressing can be programmed with the wrong address model. If future DCN30 variants need more overrides, this header will need to expand.

## Test Signals

Build/link success for `dmub_srv_dcn30_regs`, `dmub_dcn30_backdoor_load`, and `dmub_dcn30_setup_windows`, plus runtime DMUB boot on DCN30 hardware, are the key signals.
