# sources/distributed-fs/ceph-client/drivers/macintosh/therm_windtunnel.c

Purpose: controls the fan in PowerMac3,6 "windtunnel" G4 systems using a DS1775 CPU thermostat and ADM1030 fan controller. The policy is tuned from observed Mac OS X behavior.

Important APIs and functions: global `x` stores clients, platform device, current temperatures, fan table indices, saved fan registers, and lock. `read_reg()`/`write_reg()` perform I2C register access. `setup_hardware()` saves registers, configures the thermostat/fan controller, lowers overheat thresholds if at defaults, and creates temperature sysfs files. `poll_temp()` reads CPU/case temperature and chooses fan settings from `fan_table`; `control_loop()` runs this every 8 seconds. I2C callbacks are `do_probe()` and `do_remove()`; platform callbacks are `therm_of_probe()`/`therm_of_remove()`.

Control flow: module init verifies `power-mgt` thermal-info design ID 3 and machine compatibility, creates a platform device for the fan OF node, and registers a platform driver. Probe waits for I2C adapter 0, registers the I2C driver, scans consecutive Uni-N I2C adapters for missing DS1775/ADM1030 nodes, and starts `g4fand` once both clients attach. The thread sets up hardware, repeatedly polls, and restores registers on stop.

State and persistence: all runtime state is in global `x`. Original ADM1030 registers are restored when the thread exits. No persistent configuration is stored.

Dependencies and integration: depends on OF machine identification, I2C scanning/driver APIs, platform device creation, sysfs device files, and PowerMac MacIO/I2C topology.

Risks: single global state means only one supported thermal design. Device scanning assumes consecutive Mac I2C bus numbers starting at 0. Thermal thresholds are empirical and narrow to tested hardware. `therm_of_probe()` can return after starting without putting the current adapter reference. Register restore depends on orderly remove.

Test signals: PowerMac3,6 detection, DS1775/ADM1030 attachment by OF or scan, `g4fand` lifecycle, sysfs CPU/case temperatures, fan level changes across table thresholds, overheat threshold lowering, and register restoration on module removal.
