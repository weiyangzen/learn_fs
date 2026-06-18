
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.c

## Purpose
Provides the CPM1/QE Time Slot Assigner platform driver and exported serial-handle API. It maps SI registers and SI RAM, parses TDM routing from device tree, programs CPM1 or QE SI RAM entries and mode registers, manages TDM clocks, and lets QMC/other clients connect serial endpoints to TSA and query per-serial rates/time-slot counts.

## Important APIs, Types, and Functions
- Internal types: `struct tsa`, `struct tsa_tdm`, `struct tsa_entries_area`, and embedded `struct tsa_serial`.
- Exported APIs: `tsa_serial_get_num()`, `tsa_serial_connect()`, `tsa_serial_disconnect()`, `tsa_serial_get_info()`, `tsa_serial_get_byphandle()`, `tsa_serial_put()`, and `devm_tsa_serial_get_byphandle()`.
- Key setup helpers: CPM/QE endian accessors, `tsa_*_serial_connect()`, SI RAM area initializers, `tsa_*_add_entry()`, `tsa_of_parse_tdm_route()`, `tsa_of_parse_tdms()`, `tsa_init_si_ram()`, `tsa_cpm1_setup()`, and `tsa_qe_setup()`.

## Control Flow
Probe allocates `struct tsa`, determines CPM1 versus QE from match data, initializes serial ids, maps `si_regs` and `si_ram`, fills SI RAM with terminal entries, parses all TDM child nodes, and writes final SI mode/global enable registers. Parsing first validates all child `reg` ids, then for each TDM reads signal timing flags, gets/enables required clocks, assigns QE start address fields, parses Rx and Tx route arrays, appends SI RAM entries, and accumulates serial info.

The exported phandle getter resolves a fixed-args phandle with one serial id, verifies the provider node matches the TSA driver, obtains the platform device/drvdata, bounds-checks the serial index, and returns a pointer to the embedded serial while holding the platform device reference until `tsa_serial_put()`.

## State and Persistence
The driver persists TDM enable flags, clock handles, programmed SI RAM entries, serial rates, bit rates, and number of assigned Rx/Tx time slots for the life of the platform device. It has no disk persistence. Register read/modify/write sequences for connection state are protected by `tsa->lock`.

## Dependencies and Integration Points
Depends on CPM/QE DT binding constants, Linux common clock framework, OF/platform APIs, `soc/fsl/qe/ucc.h` for QE muxing, and consumers such as QMC. Device tree must supply `si_regs`, `si_ram`, TDM children, clock names (`l1*` on CPM1, short names on QE), and `fsl,{rx,tx}-ts-routes` arrays.

## Risks
- The error and remove paths for `l1tsync_clk`/`l1tclk_clk` call `clk_disable_unprepare()` and `clk_put()` on the Rx clock members instead of the Tx members, which can leak or double-release clock references.
- Route arrays are accepted as count/serial pairs; malformed counts can exhaust SI RAM and fail probe, while zero counts are not explicitly special-cased.
- QE/CPM1 entry layout differs, making version match data critical.
- The API returns embedded serial pointers with provider device references; consumers must always call the matching put or devm helper.

## Test Signals
Probe with CPM1 and QE compatible data, invalid TDM ids, missing clocks, shared/common pin cases, SI RAM exhaustion, unsupported serial ids, route arrays with odd length, phandle deferral before provider drvdata, connect/disconnect register changes, and clock cleanup on parse failure/remove are the main signals.
