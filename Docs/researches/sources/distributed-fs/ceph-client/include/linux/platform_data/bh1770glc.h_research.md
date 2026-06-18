# sources/distributed-fs/ceph-client/include/linux/platform_data/bh1770glc.h

Purpose: defines board calibration and resource hooks for the ROHM BH1770GLC / OSRAM SFH7770 proximity and ambient light sensor driver.

Important APIs and types: `struct bh1770_platform_data` contains IR LED default current (`BH1770_LED_*` constants), `glass_attenuation` with neutral value `BH1770_NEUTRAL_GA`, and setup/release callbacks for interrupt resources.

Control flow: the sensor driver consumes the platform data during probe, configures LED drive current, uses attenuation to convert raw ALS data, and calls resource callbacks around IRQ setup and teardown.

State and persistence: static optical calibration and board resource behavior. Runtime sensor state, thresholds, and IRQ state live in the driver/hardware.

Dependencies and integration points: uses kernel integer typedefs and integrates I2C sensor drivers, IRQ setup, proximity reporting, and board cover-glass calibration.

Risks and test signals: risks include wrong attenuation scaling, invalid LED current, callback failure leaks, and proximity behavior varying with cover glass. Test ALS calibration, proximity detection, IRQ setup/release failure handling, suspend/resume, and neutral attenuation defaults.
