# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.h

## Purpose

`link_hwss_dio_fixed_vs_pe_retimer.h` declares the DIO fixed-VS/PE retimer HWSS extension points and helper routines used by both DIO and HPO retimer variants.

## Important APIs, Types, And Functions

The header exposes `dp_dio_fixed_vs_pe_retimer_lane_cfg_to_hw_cfg()`, `dp_dio_fixed_vs_pe_retimer_exit_manual_automation()`, `enable_dio_fixed_vs_pe_retimer_program_4lane_output()`, `requires_fixed_vs_pe_retimer_dio_link_hwss()`, and `get_dio_fixed_vs_pe_retimer_link_hwss()`. It also declares `dp_dio_fixed_vs_pe_retimer_get_lttpr_write_address()`, but this declaration has no implementation in the reviewed `.c` file, so it is either implemented elsewhere in this source snapshot or is stale.

## Control Flow

The header has no executable flow. It allows the HPO fixed-VS/PE retimer implementation to reuse DIO retimer helpers for lane config, automation exit, and four-lane preprogramming.

## State And Persistence Behavior

No state is stored. Declared functions operate on `struct dc_link` and retimer hardware state through the link service.

## Dependencies And Integration Points

It includes `link_service.h` for `struct dc_link` and `struct link_hwss`. It is consumed by the DIO retimer implementation and `link_hwss_hpo_fixed_vs_pe_retimer_dp.c`.

## Risks And Edge Cases

The unimplemented or externally implemented `dp_dio_fixed_vs_pe_retimer_get_lttpr_write_address()` declaration is a maintenance risk if new callers expect it to link from this object. The header does not include `link_hwss.h` directly, so it relies on `link_service.h` to expose the needed incomplete types.

## Test Signals

Build/link tests catch missing definitions once a caller references every declaration. Runtime signals are fixed-VS link selection, retimer AUX write sequences, and successful test-pattern/training behavior.
