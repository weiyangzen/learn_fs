# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er_priv.h

## Purpose
Internal constants and small data types shared by the CXD2841ER implementation. It identifies logical I2C register banks, supported chip IDs, DVB-S polling interval, CNR lookup entries, and DVB-T2 profile choices.

## Important APIs, Types, and Functions
Defines `I2C_SLVX` and `I2C_SLVT` bank selectors. Chip IDs include `CXD2837ER_CHIP_ID`, `CXD2838ER_CHIP_ID`, `CXD2841ER_CHIP_ID`, `CXD2843ER_CHIP_ID`, and `CXD2854ER_CHIP_ID`. `CXD2841ER_DVBS_POLLING_INVL` defines a 10 ms polling interval. `struct cxd2841er_cnr_data` maps raw values to `cnr_x1000`. `enum cxd2841er_dvbt2_profile_t` represents any/base/lite profile selection.

## Control Flow
No executable flow is present. Implementation files use these constants to branch on detected silicon and select standard-specific monitor/tune behavior.

## State and Persistence
No persistent state. The CNR table element type is used for static lookup tables in implementation code.

## Dependencies and Integration Points
This private header is intended for CXD2841ER driver internals, not board code. The chip IDs integrate with device detection and capability selection.

## Risks and Edge Cases
Incorrect chip IDs can reject valid hardware or enable wrong register sequences. The profile enum values need to match the implementation and any frontend delivery-system mapping. Polling interval changes can affect tune latency and CPU wakeups.

## Test Signals
Exercise device identification across all listed chip variants, DVB-S polling timeout paths, and DVB-T2 base/lite profile selection. Compile should reveal accidental external users if the private header becomes inconsistent.
