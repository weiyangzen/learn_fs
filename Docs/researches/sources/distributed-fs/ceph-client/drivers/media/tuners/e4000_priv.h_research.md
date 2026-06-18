# sources/distributed-fs/ceph-client/drivers/media/tuners/e4000_priv.h

Purpose: private state and lookup tables for the E4000 driver. It defines `struct e4000_dev`, PLL divider LUT, LNA filter LUT, band register LUT, IF filter LUT, and IF gain register LUT.

Important fields in `e4000_dev` are `client`, `regmap`, `clk`, `fe`, `sd`, `active`, cached frequency/bandwidth, and V4L2 control handler/control pointers. The LUTs drive `e4000_set_params`: frequency chooses PLL output divider, RF/LNA filter, and band registers; bandwidth chooses IF filter; IF gain control indexes `e4000_if_gain_lut`.

State is runtime-private and freed on remove. Dependencies include `e4000.h`, `linux/math64.h`, V4L2 controls/subdev, and regmap. Risks: LUT sentinel values must cover the full accepted frequency/bandwidth/control range, IF gain control max must match the LUT length, and register values are hardware-specific with little self-description. Test signals: boundary frequencies at every LUT transition, bandwidth min/max, manual IF gain index 0 and max 54, and KASAN/UBSAN for out-of-range control indexing.
