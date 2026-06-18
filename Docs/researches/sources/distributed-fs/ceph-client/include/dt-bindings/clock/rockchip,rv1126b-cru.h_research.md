# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126b-cru.h

## Purpose
`rockchip,rv1126b-cru.h` defines the RV1126B clock ID ABI. It covers PLLs, root dividers, DDR and CPU clocks, many peripheral gates, and a secure clock subsection.

## Important APIs, types, and functions
The exported macros start with `PLL_GPLL`, `PLL_CPLL`, `PLL_AUPLL`, `ARMCLK`, `SCLK_DDR`, and CPLL/GPLL divider roots. Families include `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `DCLK_*`, `MCLK_*`, `DBCLK_*`, `TCLK_*`, `BUSCLK_*`, and `LRCK_*`. Secure-tail IDs include `PCLK_OTPC_S`, `PCLK_KEY_READER_S`, `HCLK_KL_RKCE_S`, `PCLK_WDT_S`, `TCLK_WDT_S`, secure timers, RNG, PKA, and `ACLK_RKCE_S`.

## Control flow
Consumers use the macro IDs in device trees; runtime operations are handled by the RV1126B CRU provider. Secure clock requests may require firmware or secure-world cooperation depending on platform policy.

## State and persistence
The file itself is immutable macro data. The ABI persists across kernel versions, while hardware clock state lives in CRU registers and secure register banks.

## Dependencies and integration points
It integrates with RV1126B DTS, Rockchip CRU support, secure crypto/key ladder/OTPC/RNG devices, watchdog/timer blocks, audio clocks, camera/video/display blocks, storage, networking, USB, UART/I2C/SPI/PWM/GPIO, and DDR/CPU frequency management.

## Risks and test signals
Risks include accidental misspelling such as `PLK_STIMER` becoming part of ABI, confusing secure and non-secure clock names, and regression from numeric changes. Test signals include schema validation, secure clock probe behavior, watchdog and secure timer operation, crypto self-tests, and media/storage/network smoke tests.
