<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm8994-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/wm8994-regulator.c

Purpose: Registers the two WM8994/WM8958/WM1811 internal LDOs, with GPIO-controlled enable support and default consumer constraints for codec supplies.

Important APIs and types: `struct wm8994_ldo` stores regulator device, parent MFD pointer, one consumer supply, and local init data. `wm8994_ldo1_ops` provides linear voltage selection. `wm8994_ldo2_list_voltage()` computes chip-specific LDO2 voltages, including WM1811 selector zero rejection. Descriptor arrays differ for WM8994 versus WM8958-family enable delays/off-on delays.

Control flow: Probe derives LDO index from platform ID, allocates state, constructs a default consumer supply tied to the parent device, obtains an optional nonexclusive enable GPIO from the parent node, picks default constraints when platform data is absent or OF is used, hands the GPIO to regulator core, selects the descriptor array by chip type, registers the regulator, and stores state.

State and persistence: Driver state is local init data and supply metadata. Voltage selector state persists in WM8994 registers. Enable state may be controlled by regulator core through the optional GPIO rather than regmap enable bits.

Dependencies and integration points: Depends on WM8994 MFD core/regmap/platform data, GPIO descriptors named `wlf,ldo1ena` or `wlf,ldo2ena`, and codec supplies `AVDD1` and `DCVDD`.

Risks: `id = pdev->id % ARRAY_SIZE(pdata->ldo)` dereferences `pdata` before checking it, unsafe if parent platform data is absent. Without an enable GPIO, default constraints remove status-change operations. Probe is force-synchronous due to supply ordering needs.

Test signals: WM8994, WM8958, and WM1811 voltage listings, optional GPIO present/absent, OF and platform-data init paths, regulator registration failure, default consumer supply binding, and synchronous probe ordering with codec consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm8994-regulator.c -->
