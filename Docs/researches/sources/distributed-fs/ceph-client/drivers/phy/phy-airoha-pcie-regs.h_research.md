# sources/distributed-fs/ceph-client/drivers/phy/phy-airoha-pcie-regs.h

Purpose: This header defines the MMIO register offsets and bit masks used by the Airoha EN7581 PCIe PHY driver. It is a pure register map for CSR_2L, PMA, Tx/Rx detection-time, and RX AEQ windows.

Important APIs/types/functions: The file exports no functions or types; it exports `#define` constants. CSR_2L definitions cover common lane enable/trim, JCPLL/TXPLL programming, clock outputs, TX LDO/edge generation, RX0/RX1 CDR and signal-detect tuning, equalization, oscillator calibration, and per-lane frontend settings. PMA definitions cover LCPLL power, RX frequency detector, calibration, reset bits, forced analog controls, PLL force controls, FLL IDAC storage, RX gain/speed, and digital reserve registers. DTIME and RX AEQ groups define fields programmed before PHY initialization.

Control flow: The C driver includes this header and combines masks with `FIELD_PREP`/`FIELD_GET` through helper macros. No executable flow exists here.

State and persistence: There is no software state. Hardware state is produced when `phy-airoha-pcie.c` writes these offsets in mapped resources named `csr-2l`, `pma0`, `pma1`, `p0-xr-dtime`, `p1-xr-dtime`, and `rx-aeq`.

Dependencies and integration points: It assumes Linux `BIT`, `GENMASK`, and bitfield helpers are available through the including C file. Its constants are tightly coupled to `struct airoha_pcie_phy` resource mapping and the initialization functions for PLL, SSC, RX/TX flow, signal detect, and calibration.

Risks: The header contains similarly named lane0/lane1 and JCPLL/TXPLL fields; using the wrong offset with the wrong mapped base can silently program unrelated analog controls. Some macro names preserve hardware naming inconsistencies, so search-based edits are risky. There is no range or resource-size checking at the macro layer.

Test signals: Compile coverage catches missing masks and duplicate names. Runtime signals include PHY init completing, PCIe link training through Gen1/Gen2/Gen3, frequency detector lock bits, stable RX signal detection, and no regression after suspend/resume reinitialization.
