# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.h

Purpose: MaxLinear GSW1xx-specific register and bitfield definitions for standalone switches.

Important APIs/types/functions: constants for port counts and special MII/SGMII ports, SMDIO base-address register, SGMII PCS/TBI autonegotiation and status, SGMII PHY access/reset/equalization/polarity/boost, register-window bases, GPIO alternate-select values, shell manufacturer/part fields, RGMII slew settings, and SGMII clock NCO settings.

Control flow: no executable flow. `mxl-gsw1xx.c` uses these definitions for regmap windows, chip ID validation, PCS reset/configuration, and clock selection.

State and persistence: no software state; defines hardware state locations that persist until reset or reconfiguration.

Dependencies and integration: depends on `linux/bitfield.h`; complements generic GSWIP definitions in `lantiq_gswip.h`.

Risks and test signals: wrong offsets/masks can break ID probing or PCS links. Test ID extraction, SGMII/1000BASE-X/2500BASE-X negotiation, clock switching, polarity settings, and GPIO MMDIO pinmux.
