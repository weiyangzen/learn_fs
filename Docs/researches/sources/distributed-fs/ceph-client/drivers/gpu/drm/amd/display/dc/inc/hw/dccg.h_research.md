# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dccg.h

## Purpose

`dccg.h` defines the Display Clock Generator abstraction. DCCG controls DPP DTOs, display/DP/audio/DSC/DTB clocks, PHY symbol clocks, pixel-rate dividers, clock gating, root-clock control, and register-state readback.

## Important APIs, Types, And Functions

Key enums include PHYD32 clock source, PHYSYMCLK source, stream clock source, DISPCLK change mode, and pixel-rate divider. Key structs include `dp_dto_params`, `dcn_dccg_reg_state`, `dccg`, `dtbclk_dto_params`, and `dccg_funcs`. The vtable covers DPP DTO update, DCCG ref frequency, FIFO error override, OTG add/drop pixel, init, refclk setup, clock gating, memory low power, HPO DP stream/symclk setup, PHY symclk, DTB/audio DTO, DISPCLK change mode, DSC clock enable/disable, pixel-rate dividers, DIO FIFO resync, DP DTO, DTB source selection, DSC DTO/ref clocks, root gate control, register-state readback, and global fine-grain clock gating.

## Control Flow

HWSS and clock code program DCCG when pipes, links, clocks, DSC, or HPO resources change. DPP clocks are updated per DPP instance. DP/HDMI stream clocks and DTB/audio DTOs are configured from timing/link parameters. DSC clock paths are enabled and referenced before DSC use. Pixel-rate dividers are set for ODM/encoding policies and can be read back.

## State And Persistence Behavior

`struct dccg` persists in the resource pool, tracking context, vtable, per-pipe DPP clock requests, reference DPP clock, and clock-gated state. Hardware retains DCCG register programming until reprogrammed or reset. `dcn_dccg_reg_state` is a diagnostic snapshot.

## Dependencies And Integration Points

It includes DC and shared HW types. It integrates with clock manager, HWSS, timing generators, link encoders, HPO DP encoders, DSC, audio, PHY programming, HUBP/DPP setup, and debug logging.

## Risks And Edge Cases

Clock source selections must match signal type, link encoding, PHY instance, and OTG instance. DTO modulo/phase values are unit-sensitive. Incorrect pixel-rate dividers break timing. Clock gating/root-gate controls can disable active hardware. DSC clock setup must align with slice count and instance.

## Test Signals

Tests should cover DP/HDMI/eDP/HPO link clocks, DSC enable/disable, ODM pixel-rate dividers, audio DTO, DTB clock, DPP clock changes, low-power clock gating, FIFO resync, and register readback. Link training failures, audio drift, blank displays, and underflow are practical signals.
