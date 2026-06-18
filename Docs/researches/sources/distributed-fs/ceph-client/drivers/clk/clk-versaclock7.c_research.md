# sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock7.c

## Purpose
`clk-versaclock7.c` is a CCF I2C driver for Renesas VersaClock7-family timing devices, currently represented by the `renesas,rc21008a` compatible. It exposes a fixed APLL rate derived from the current device state, three fractional output dividers (FODs), four integer output dividers (IODs), and eight exported output clocks mapped from the RC21008A package's physical outputs.

## Important APIs, Types, And Functions
The driver defines 16-bit paged register access through regmap range configuration and field definitions for XO/APLL configuration, FOD/IOD divider blocks, output-bank source selection, and output driver enable bits. `struct vc7_chip_info` describes model output mapping. `struct vc7_apll_data`, `struct vc7_fod_data`, `struct vc7_iod_data`, and `struct vc7_out_data` hold the CCF-visible state for each clock block. `struct vc7_driver_data` ties the client, regmap, parent input, APLL, FODs, IODs, and outputs together.

Important helpers include the local 128-bit math routines `vc7_64_mul_64_to_128()` and `vc7_128_div_64_to_64()`, bank routing resolver `vc7_get_bank_clk()`, register accessors `vc7_read_apll()`, `vc7_read_fod()`, `vc7_write_fod()`, `vc7_read_iod()`, `vc7_write_iod()`, `vc7_read_output()`, and `vc7_write_output()`, and rate calculators `vc7_get_apll_rate()`, `vc7_calc_iod_divider()`, `vc7_calc_fod_1st_stage()`, `vc7_calc_fod_1st_stage_rate()`, `vc7_calc_fod_2nd_stage_rate()`, and `vc7_calc_fod_divider()`.

## Control Flow
Probe allocates state, requires a parent clock named `xin`, creates a paged I2C regmap, selects a node name from `clock-output-names` or the OF node, reads the current APLL configuration, computes the APLL rate, and registers the APLL as a fixed-rate clock. It then registers all FOD and IOD internal clocks as children of APLL. For each exported output, it maps the logical provider index to a physical output, derives the output bank, reads the bank's current source selection, resolves that source to a supported FOD or IOD, and registers the output clock with that existing parent. The driver explicitly does not remap output banks; it mirrors the chip's programmed routing.

FOD rate determination computes a first-stage integer/fractional divider and optionally searches the second-stage integer divider when the first-stage rate would be below 33 MHz. It prefers integer solutions before fractional ones and enforces output range checks in `set_rate`. IOD rate handling is simpler: it computes and writes a bounded integer divisor. Output prepare/unprepare toggles the output disable bit; `is_enabled` reads the same register and reports inverted state.

## State And Persistence
Persistent state is the VC7 register file: APLL registers are read but not changed, FOD/IOD divider registers are updated, bank source mapping is read but not changed, and output driver disable bits are written during prepare/unprepare. In memory, the driver stores the most recent divider values in FOD/IOD structs and the current output disable state in each output struct. The fixed-rate APLL clock persists as a manually registered clock and is unregistered in remove; FOD/IOD/output clocks are devm-managed.

## Dependencies And Integration Points
The driver integrates with I2C, CCF, OF clock providers, regmap range windows, and kernel math helpers. Consumers receive only exported output clocks from `vc7_of_clk_get()`. The driver depends on board or firmware initialization to configure APLL and output bank routing before Linux probes, because APLL changes and FOD/IOD-to-bank remapping are outside the supported runtime surface.

## Risks
The largest risk is arithmetic correctness: FOD rates combine 10 GHz parent rates, 34-bit fractional denominators, and 128-bit intermediate math. The local division routine returns all-ones on overflow or divide-by-zero, so caller-side validation matters. `vc7_get_apll_rate()` returns an `unsigned long` but may return a negative error value cast through that type if APLL reads fail. Several regmap bulk reads cast stack scalar addresses to `u32 *`, `u16 *`, or `u64 *`; the regmap endian configuration is intended to make this work, but alignment and endian changes would be delicate. The driver does not validate APLL rate against the documented 9.5-10.7 GHz range after reading hardware. Unsupported bank source values abort output registration, so firmware routing outside the driver's supported map prevents probe. There is no PM regcache restore path.

## Test Signals
Validation should probe RC21008A hardware or emulation with expected output mapping `{1,2,3,6,7,8,10,11}` and known bank routing. `clk_summary` should show APLL, FODs, IODs, and eight outputs with parents matching existing bank source registers. Rate tests should cover FOD outputs below and above the 33 MHz first-stage threshold, integer and fractional FOD solutions, IOD min/max bounds, and out-of-range rate rejection. Output enable tests should verify prepare/unprepare toggles `VC7_REG_OUT_DIS`. Firmware-routed unsupported bank sources should be tested as probe failures so board integration catches invalid preconfiguration.
