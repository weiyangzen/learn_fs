# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/falcon_boards.c

## Purpose

`falcon_boards.c` provides board-level support for Falcon/SFC4000 NIC products. It translates the board revision value read from Falcon NVRAM into a `struct falcon_board_type` and supplies per-board hooks for initialization, teardown, PHY LED setup, identify LED control, and hardware-health monitoring.

This file owns the board-specific I2C device interactions that are outside the Falcon ASIC itself: LM87 sensor setup and alarm interpretation, MAX6647 temperature monitoring for SFE4001, PCA9539 I/O expander power sequencing for SFE4001, and LED wiring differences across SFE4002, SFE4003, and SFN4112F. It is called by `falcon.c` during NIC probe, remove, monitor, and ID LED operations.

## Important APIs, Types, And Functions

The public entry point is `falcon_probe_board(struct ef4_nic *efx, u16 revision_info)`. It decodes type/major/minor fields with `FALCON_BOARD_TYPE`, `FALCON_BOARD_MAJOR`, and `FALCON_BOARD_MINOR`, then searches `board_types[]` and installs `falcon_board(efx)->type`.

`board_types[]` maps four supported board IDs to operations:

- SFE4001: `sfe4001_init()`, `sfe4001_fini()`, `tenxpress_set_id_led()`, and `sfe4001_check_hw()`.
- SFE4002: `sfe4002_init()`, `sfe4002_init_phy()`, `ef4_fini_lm87()`, `sfe4002_set_id_led()`, and `sfe4002_check_hw()`.
- SFE4003: `sfe4003_init()`, `sfe4003_init_phy()`, `ef4_fini_lm87()`, `sfe4003_set_id_led()`, and `sfe4003_check_hw()`.
- SFN4112F: `sfn4112f_init()`, `sfn4112f_init_phy()`, `ef4_fini_lm87()`, `sfn4112f_set_id_led()`, and `sfn4112f_check_hw()`.

LM87 support is abstracted by `ef4_init_lm87()`, `ef4_fini_lm87()`, and `ef4_check_lm87()` when `CONFIG_SENSORS_LM87` is enabled, with no-op stubs otherwise. `ef4_poke_lm87()` writes register/value arrays, `falcon_lm87_common_regs[]` installs common board/controller critical temperature thresholds, and board-specific arrays set voltage and temperature limits.

SFE4001 power and reflash support is implemented by `sfe4001_poweron()`, `sfe4001_poweroff()`, sysfs attribute handlers `phy_flash_cfg_show()`/`phy_flash_cfg_store()`, `sfe4001_init()`, `sfe4001_fini()`, and `sfe4001_check_hw()`. This board uses a PCA9539 I/O expander at `0x74` and a MAX6647-compatible temperature monitor at `0x4e`.

PHY LED helpers include `sfe4002_init_phy()`, `sfe4002_set_id_led()`, `sfn4112f_init_phy()`, `sfn4112f_set_id_led()`, `sfe4003_init_phy()`, and `sfe4003_set_id_led()`. These call into PHY-specific helpers such as `falcon_qt202x_set_led()` and `falcon_txc_set_gpio_*()`.

## Control Flow

Board selection happens after NVRAM is validated in `falcon_probe_nvconfig()`. `falcon_probe_board()` only records type/revision and does not touch hardware. Later, `falcon_probe_nic()` creates the Falcon bit-banged I2C adapter and calls `board->type->init(efx)`, which performs I2C client creation and any board-specific power/sensor setup.

For LM87 boards, init creates an I2C client, clears alarm registers by reading them, writes board-specific limits, writes common thermal limits, and stores the client in `board->hwmon_client`. Monitor calls read alarm registers, mask board-specific bad/unused channels, optionally read temperature registers to decide whether alarm bits are truly critical, log a detailed problem/failure message, and return `-ERANGE` for critical/electrical failures.

SFE4001 init creates a MAX6647 or dummy hwmon client, raises the local high limit to 90 C, creates a PCA9539 dummy client, optionally stops MAC stats when entering PHY flash mode, powers on the PHY, and creates the `phy_flash_cfg` sysfs file. Power-on clears over-temperature latch, enables expander outputs, optionally performs a full power-cycle, then sequences 1.2 V/2.5 V/3.3 V/5 V rails before 1.0 V and waits for DSP/AFE readiness. In special reflash mode it holds the 3.3 V flash config line low and waits without requiring AFE startup.

`phy_flash_cfg_store()` serializes with `rtnl_lock()`, refuses changes while the netdevice is running or not ready, toggles `PHY_MODE_SPECIAL`, stops stats entering special mode, power-cycles the PHY, reconfigures the port, and restarts stats leaving special mode. This sysfs path is intentionally mutually exclusive with the normal open device.

During periodic monitoring, `falcon_monitor()` in `falcon.c` calls the installed board `monitor()` hook. For SFE4001, monitoring checks power-good inputs rather than directly reading the MAX6647 alarm because the temperature register is read-to-clear and could trigger unwanted power restoration. On detected power loss or I2C read failure, it powers off the board and forces `PHY_MODE_OFF`.

## State And Persistence Behavior

Persistent input is only the NVRAM board revision value used to select `board_types[]`. The file itself does not persist configuration, but it creates runtime I2C client state in `struct falcon_board` (`hwmon_client`, `ioexp_client`, `i2c_adap`, revision fields, and type pointer). SFE4001 exposes transient PHY reflash mode through `efx->phy_mode & PHY_MODE_SPECIAL`; the sysfs value reflects runtime mode and is not stored permanently.

Hardware state changed by this file includes sensor limit registers, PCA9539 output/config registers, PHY power rails, PHY LED registers/GPIOs, and over-temperature alarm latches. Teardown reverses client creation and powers down SFE4001 rails.

The LM87 path gracefully compiles to no-ops without `CONFIG_SENSORS_LM87`, which means board init and monitor succeed but sensor enforcement is absent. SFE4001 can use either a real LM90/MAX6647 hwmon driver client or a dummy I2C device depending on `CONFIG_SENSORS_LM90`.

## Dependencies And Integration Points

The file depends on Linux RTNL and I2C APIs and driver-local `net_driver.h`, `phy.h`, `efx.h`, `nic.h`, and `workarounds.h`. It is tightly integrated with `falcon.c` through `falcon_board(efx)->type` and with PHY code through `tenxpress_set_id_led()`, `falcon_qt202x_set_led()`, and TXC GPIO helpers. It depends on the I2C adapter being created before board init and removed after board fini.

The monitor return contract matters: `0` means healthy, `-ERANGE` means a hardware fault such as critical temperature/electrical failure, and other negative errors mean monitor I/O failed. `falcon_monitor()` reacts by logging and forcing PHY low power.

## Risks And Edge Cases

Sensor reads can be destructive because some alarm/status registers are read-to-clear. SFE4001 avoids direct MAX6647 status polling after power-on to prevent a thermal latch clear from re-enabling a board that has shut itself down. Changes to monitor logic must preserve that behavior.

Power sequencing is timing-sensitive. `sfe4001_poweron()` uses multiple rail orderings, sleeps, and retries waiting for DSP/AFE readiness; short-circuiting failures or changing active-low expander bit handling can leave the PHY partially powered. `sfe4001_poweroff()` is used both for cleanup and fault handling, so it must tolerate partially initialized clients.

Several board revisions have known bad or unwired sensors/LEDs. SFE4002 A0 and SFE4003 A0-A2 mask external temperature alarms, and SFE4003 LED GPIOs are ignored before A3. Removing these masks would cause false hardware-fault shutdowns.

The `phy_flash_cfg` sysfs mode manipulates PHY mode and stats. Incorrect locking or allowing changes while the interface is running could race the data path or stats DMA. The code uses RTNL and state/netif checks to keep the transition out of normal operation.

## Test Signals

Useful test signals include board probe failure on unknown type, I2C client creation failures, LM87 register-write failures, sensor alarm logs identifying board/controller overheating or electrical faults, SFE4001 "waiting for DSP boot" retry logs, timeout return from SFE4001 power-on, and `phy_flash_cfg` returning `-EBUSY` while the netdevice is running.

Regression tests on real or simulated hardware should cover each board ID, LM87-enabled and LM87-disabled builds, SFE4001 power-on failure unwinding, sysfs special-mode toggling with stats stop/start pairing, board revision-specific alarm masks, and LED behavior for QT202x and TXC-based boards.
