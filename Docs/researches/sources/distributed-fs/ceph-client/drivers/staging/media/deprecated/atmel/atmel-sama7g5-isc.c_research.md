# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-sama7g5-isc.c

## Purpose
This file is the deprecated SAMA7G5 eXtended ISC platform driver. It adapts the common ISC base to XISC hardware by providing SAMA7G5 formats, larger dimensions, register offsets, full AXI DMA burst settings, XISC-specific DPC/gamma/CBC/RLP programming, optional MIPI front-end mode, runtime PM, and platform driver registration.

## Important APIs and Functions
The controller format table includes SAMA5D2-style formats plus UYVY, VYUY, and Y16 output capability. The input format table includes Bayer 8/10/12-bit, GREY, YUYV, UYVY, RGB565, and Y10. SoC callbacks include `isc_sama7g5_config_csc()`, `isc_sama7g5_config_cbc()`, `isc_sama7g5_config_cc()`, `isc_sama7g5_config_ctrls()`, `isc_sama7g5_config_dpc()`, `isc_sama7g5_config_gam()`, `isc_sama7g5_config_rlp()`, and `isc_sama7g5_adapt_pipeline()`.

`isc_sama7g5_config_dpc()` writes black-level offset and Bayer config for DPC. `isc_sama7g5_config_gam()` enables bipartite gamma mode. `isc_sama7g5_config_cbc()` also sets neutral hue and saturation. `xisc_parse_dt()` extends endpoint parsing with a `microchip,mipi-mode` DT boolean that sets `ISC_PFE_CFG0_MIPI`. `microchip_xisc_probe()` fills `isc_device`, initializes resources, registers async notifiers, enables runtime PM, reads version, and registers compatible `"microchip,sama7g5-isc"`.

## Control Flow and State
Probe flow mirrors SAMA5D2 but does not enable a separate ISPCK because `ispck_required` is false and XISC is clocked by MCK/hclock. It uses SAMA7G5 register offsets for shifted modules, DMA, version, and histogram entries. Runtime PM suspend/resume only disables/enables `hclock`.

Persistent state in `isc_device` includes larger max dimensions, `gamma_max = 0` for the single gamma table, AXI 32-beat DMA config, optional MIPI PFE flags per endpoint, and SAMA7G5 callbacks/offsets.

## Dependencies and Integration Points
It depends on the same platform/V4L2/regmap/clock/runtime PM infrastructure as SAMA5D2 plus the `microchip,mipi-mode` device-tree property. Common functionality is delegated to `atmel-isc-base.c` and `atmel-isc-clk.c`.

## Risks and Test Signals
Risks include MIPI mode being a device-wide property rather than endpoint-specific, offset mistakes for shifted XISC registers, single gamma index semantics, no separate ISPCK cleanup, and error paths around clock cleanup. Test signals include probe on `"microchip,sama7g5-isc"`, MIPI and parallel endpoint parsing, video capture up to 3264x2464, UYVY/VYUY/Y16 format negotiation, DPC/gamma register writes, runtime PM clock balance, and clean async removal.
