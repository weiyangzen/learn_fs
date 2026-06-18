# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/Kconfig

## Purpose

`vc4/Kconfig` declares the Broadcom VC4 DRM driver, HDMI CEC support, and VC4 KUnit tests. It captures platform dependencies and helper libraries needed by the display/audio/GEM driver.

## Important APIs, Types, and Functions

- `config DRM_VC4`: tristate Broadcom VC4 Graphics option for Raspberry Pi/Broadcom platforms or compile-test.
- Dependencies include DRM, firmware availability, common clock, PM, SND, and SND_SOC.
- Selected helpers include DRM client/KMS/display/HDMI/audio helpers, GEM DMA helpers, panel bridge, MIPI DSI, and ALSA HDMI codec pieces.
- `config DRM_VC4_HDMI_CEC`: optional CEC support.
- `config DRM_VC4_KUNIT_TEST`: KUnit test option depending on DRM_VC4 and KUnit.

## Control Flow

Configuration enables the VC4 composite object built by the Makefile. The KUnit option adds mock/test source files to the same object when enabled.

## State and Persistence Behavior

No runtime state. The file controls compiled feature availability in kernel configuration.

## Dependencies and Integration Points

It integrates VC4 with Broadcom/Raspberry Pi platform support, DRM helper subsystems, HDMI audio/CEC support, and KUnit.

## Risks and Edge Cases

The firmware dependency prevents built-in VC4 when Raspberry Pi firmware is a module, except under compile-test constraints. Missing selected helpers surface as build errors.

## Test Signals

Build coverage for platform, compile-test, CEC on/off, KUnit on/off, and `KUNIT_ALL_TESTS` default behavior.
