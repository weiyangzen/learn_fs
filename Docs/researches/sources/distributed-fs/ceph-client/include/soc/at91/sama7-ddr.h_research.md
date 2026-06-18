# sources/distributed-fs/ceph-client/include/soc/at91/sama7-ddr.h

Purpose: defines Microchip SAMA7 DDR3 PHY and UDDRC register offsets and bit definitions used for DDR initialization and low-power transitions.

Important APIs and types: DDR3PHY definitions include PHY initialization, DLL bypass/lock/reset, clock disable values, initialization-done status, AC/data/power-down controls, ZQ impedance status offsets, and DATX8 DLL disable bits. UDDRC definitions include operating mode/self-refresh status, low-power control, and software/automatic self-refresh controls.

Control flow: DDR setup code resets/initializes PHY DLLs, waits for `PGSR_IDONE`, configures power-down drivers and impedance status, then monitors/controls UDDRC self-refresh and power-down modes.

State and persistence: state is live DDR PHY/controller MMIO state. Incorrect values directly affect memory reliability and power retention; no software state is stored here.

Dependencies and integration points: standalone macro header integrated by SAMA7 DDR initialization, suspend/resume, and SoC power-management code.

Risks and test signals: risks include typo-sensitive bit names, invalid DLL bypass/reset sequencing, insufficient wait for PHY done, wrong self-refresh mode interpretation, and memory loss during low-power entry. Test DDR training/init, suspend/resume with self-refresh, impedance calibration reads, DLL-disable variants, and memory stress across temperature/clock changes.
