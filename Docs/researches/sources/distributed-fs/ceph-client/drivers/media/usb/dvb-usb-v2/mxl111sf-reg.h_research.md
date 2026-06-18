# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-reg.h

Purpose: register constant map for the MxL111SF USB bridge/tuner/demod helper stack. It names chip ID/revision registers, DVB-T demod status/TPS/error/SNR registers, MPEG/I2S/SPI transport controls, tuner IF/RF tuning registers, GPIO/GPO bits, ATSC config, mode/start-tune registers, IDAC registers, and digital RF power registers.

Important APIs/types/functions: this header exports macros only. Important groups include `CHIP_ID_REG`, `TOP_CHIP_REV_ID_REG`, `V6_*` demod/TPS/status fields, `TSIF_INPUT_*`, `V6_MPEG_*`, `V6_I2S_*`, `TUNER_*`, `V6_TUNER_*`, `V6_GPO_*`, `MXL_111SF_GPO_*`, `MXL_MODE_REG`, `START_TUNE_REG`, and IDAC bit masks.

Control flow: all MxL111SF modules include these constants to interpret register reads and compose masked writes. Demod status/TPS reads, tuner tune calculations, PHY transport setup, GPIO helpers, chip-info detection, and antenna RF strength all depend on these names.

State and persistence: no software state exists here. The file documents persistent on-chip register state that survives until reset, page change, or explicit overwrite by the driver.

Dependencies and integration: used by `mxl111sf.c`, `mxl111sf-demod.c`, `mxl111sf-tuner.c`, `mxl111sf-phy.c`, and `mxl111sf-gpio.c`. It is the shared ABI between high-level DVB operations and chip register programming.

Risks: register constants are not type checked, and several names encode revision-specific assumptions (`V6_*`) while being used by v8 paths too. Typo-like names such as `V6_TPS_HIERACHY_REG` can propagate into callers. Any mismatch with the vendor register map can cause silent tuning, GPIO, or transport failures.

Test signals: build all MxL111SF modules; chip ID/revision reads match expected values; frontend status/TPS reporting maps correctly; transport pin and SPI/I2S setup registers match hardware traces; RF strength and antenna switching work after page changes.
