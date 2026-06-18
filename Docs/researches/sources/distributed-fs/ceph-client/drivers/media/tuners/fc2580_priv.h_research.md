# sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580_priv.h

Purpose: private FC2580 state and hardware lookup tables. It defines initialization register pairs, PLL divider/band LUT, IF filter LUT, frequency-specific register table with `0xff` no-op sentinels, and `struct fc2580_dev`.

The LUTs are consumed by `fc2580_set_params`: PLL LUT selects output divider and band, frequency LUT programs RF/front-end registers, and IF filter LUT selects registers for bandwidth. `struct fc2580_dev` holds clock, client, regmap, V4L2 subdev/control handler, active flag, and cached frequency/bandwidth.

Dependencies include `fc2580.h`, V4L2 controls/subdev, regmap, and math64. Risks: `0xff` sentinel is valid only for the dedicated LUT write helper, frequency/bandwidth sentinels must cover all accepted values, and control ranges must stay consistent with LUT expectations. Test signals: boundary frequencies around 400/538/794/1000 MHz, 6/7/8 MHz bandwidths, active/sleep transitions, and table-sentinel no-op behavior.
