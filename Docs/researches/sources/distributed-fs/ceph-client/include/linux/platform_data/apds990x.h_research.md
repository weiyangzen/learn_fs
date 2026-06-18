# sources/distributed-fs/ceph-client/include/linux/platform_data/apds990x.h

Purpose: defines platform tuning data for the APDS990x combined proximity and ambient light sensor driver.

Important APIs and types: IR LED current constants select 12, 25, 50, or 100 mA. `struct apds990x_chip_factors` contains glass attenuation and clear/IR conversion factors scaled by `APDS_PARAM_SCALE`, plus device factor `df`. `struct apds990x_platform_data` includes chip factors, proximity LED drive `pdrive`, pulse count `ppcount`, and resource setup/release callbacks for interrupt wiring.

Control flow: board code supplies optical calibration and interrupt callbacks at probe. The driver programs proximity pulse/drive settings, converts raw ALS channels to lux using factors, and calls setup/release hooks around IRQ resource lifetime.

State and persistence: calibration data is static board/platform state. Runtime sensor thresholds, IRQ state, and measurements live in the driver and hardware registers.

Dependencies and integration points: uses fixed-width integer types from kernel headers and integrates with I2C sensor drivers, input/IIO-style reporting depending on implementation, IRQ setup, and board-specific optical cover design.

Risks and test signals: risks include bad calibration producing wrong lux/proximity values, invalid pulse/current combinations, callback lifetime errors, and resource leaks on probe failure. Test ALS conversion with known light levels, proximity thresholds, IRQ setup/release failure paths, suspend/resume, and default factors when attenuation is zero.
