# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.c

## Purpose

`dcn30_dwb.c` implements the DCN3.0 Display Writeback Controller lifecycle and function table. It reports capabilities, configures frame capture source/cropping/stereo/rate, enables and disables capture, updates color processing, and checks hardware enable state.

## Important APIs, Types, And Functions

Key functions are `dwb3_get_caps`, `dwb3_config_fc`, `dwb3_enable`, `dwb3_disable`, `dwb3_set_fc_enable`, `dwb3_update`, `dwb3_is_enabled`, `dwb3_set_stereo`, `dwb3_set_new_content`, `dwb3_set_denorm`, and `dcn30_dwbc_construct`. The function table also exposes OGAM transfer function programming through `dwb3_ogam_set_input_transfer_func`.

## Control Flow

Enable turns on DWB, programs FC source/crop/capture rate/stereo, programs HDR multiplier, gamut remap, OGAM transfer function, output denorm, enables frame capture, and sets first pixel delay. Update preserves any pre-existing DWB update lock; if unlocked, it locks, reprograms FC/color/denorm, then unlocks. Disable clears FC capture and DWB enable. `set_fc_enable` similarly preserves caller lock state while toggling capture.

## State, Dependencies, Risks, And Test Signals

State lives in DWB registers. The code mutates clock/enable, frame-capture, crop window, source size, stereo, new-content, output format/denorm/min/max, and update lock registers. It depends on `reg_helper`, `resource.h`, `dwb.h`, and `dcn30_dwb.h`, and calls color-management helpers. Risks include update-lock imbalance, active-capture reprogramming, unsupported output formats skipping denorm, and capability assumptions. Tests should cover enable/update/disable, crop, stereo, lock-preserving update, `is_enabled`, and capture with color transforms.
