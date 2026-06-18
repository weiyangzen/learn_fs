
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda18271c2dd_maps.h

## Purpose
`tda18271c2dd_maps.h` supplies the static standard, frequency, PLL, RF calibration, gain, thermometer, and band maps used by the TDA18271C2DD tuner implementation.

## Important APIs, Types, and Functions
The header defines `enum HF_S` standards such as analog TV, FM, ATSC, DVB-T 6/7/8 MHz, DVB-C 6/7/8 MHz, and digital max markers. Static tables include `m_StandardTable`, `m_BP_Filter_Map`, `m_RF_Cal_Map`, `m_KM_Map`, `m_Main_PLL_Map`, `m_Cal_PLL_Map`, `m_GainTaper_Map`, `m_RF_Cal_DC_Over_DT_Map`, `m_IR_Meas_Map`, `m_CID_Target_Map`, `m_RF_Band_Map`, and two thermometer maps.

## Control Flow
There is no executable flow; `tda18271c2dd.c` searches these sorted sentinel-terminated maps with `SearchMap*()` helpers to choose calibration constants, PLL divisors, filter settings, RF bands, and standard IF/bandwidth values.

## State and Persistence Behavior
All data is static read-mostly table data. The implementation uses it to derive volatile register values and calibration curves; it does not modify the tables.

## Dependencies and Integration Points
The header relies on struct definitions declared earlier in `tda18271c2dd.c`, so it is implementation-private and included only after those type definitions. It is not a standalone public header.

## Risks and Edge Cases
Map ordering and sentinel rows are essential because the search helpers stop at the first frequency ceiling or zero terminator. Incorrect table ranges can reject tuning or select bad PLL/filter parameters. Because the file is included into a C file after type declarations, moving it or including it elsewhere would fail unless those structs are visible.

## Test Signals
Tests should cover map lookup at lower/upper boundaries, sentinel failure behavior above supported ranges, every RF band row, standard selection for DVB-T and DVB-C bandwidths, and calibration output stability across representative frequencies.
