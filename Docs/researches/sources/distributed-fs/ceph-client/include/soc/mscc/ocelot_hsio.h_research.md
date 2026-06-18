# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_hsio.h

Purpose: maps the Ocelot HSIO register space and bitfields for PLL5G, resistance compensation, recovered clock, 1G and 6G SerDes lanes, memory-control-block access, QSGMII, clock division, and the temperature sensor.

Important APIs/types/functions: macro-only API. It defines register offsets such as `HSIO_PLL5G_CFG0`, `HSIO_S1G_*`, `HSIO_S6G_*`, `HSIO_MCB_*`, and `HSIO_TEMP_SENSOR_*`, plus field encoders/extractors for PLL calibration, lane power/reset, signal detect, serializer/deserializer tuning, BIST, QSGMII lane status, and temperature samples.

Control flow: no C control flow is present. Consumer drivers program PLL and lane parameters, trigger one-shot MCB reads/writes, poll calibration/lock/status bits, and enable or reset SerDes lanes. Hardware state machines perform PLL locking, input-buffer calibration, PRBS/BIST, and temperature sampling.

State and persistence: persistent state is in HSIO registers and lane analog configuration. Status bits expose lock, calibration, signal-detect, BIST, revision, and temperature state. These settings are reset-sensitive and board/link-mode dependent.

Dependencies and integration: included by `drivers/phy/mscc/phy-ocelot-serdes.c` and Ocelot Ethernet initialization code. It integrates the switch driver with PHY/SerDes lane configuration, QSGMII setup, recovered-clock output, and thermal/status diagnostics.

Risks: these fields control analog SerDes behavior, so incorrect masks or initialization order can prevent link training, destabilize clocks, or misconfigure QSGMII lanes. BIST/status polarity such as done/not-done bits must be handled carefully. Test signals include SerDes probe, link at 1G/2.5G/QSGMII modes, PLL lock polling, PRBS/BIST where available, and temperature register readback.
