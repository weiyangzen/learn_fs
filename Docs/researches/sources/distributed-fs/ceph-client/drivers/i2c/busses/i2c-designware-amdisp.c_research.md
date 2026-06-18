# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdisp.c

## Purpose
AMD ISP DesignWare I2C platform glue. It instantiates a Synopsys DesignWare controller in AMD ISP hardware where transfers run in polling mode because no IRQ is connected.

## Important APIs, Types, And Functions
The driver uses shared `struct dw_i2c_dev` from `i2c-designware-core.h`. Local helpers are `amd_isp_dw_i2c_get_clk_rate()` and PM callbacks. Probe is `amd_isp_dw_i2c_plat_probe()`, removal is `amd_isp_dw_i2c_plat_remove()`, and shared setup is delegated to `i2c_dw_fw_parse_and_configure()`, `i2c_dw_configure()`, `i2c_dw_probe()`, `i2c_dw_disable()`, `i2c_dw_prepare_clk()`, and `i2c_dw_init()`.

## Control Flow
Probe allocates `dw_i2c_dev`, sets `ACCESS_POLLING`, maps MMIO, installs a fixed 100 MHz clock-rate callback in kHz units, parses firmware timings, configures DesignWare master/slave capability, initializes adapter metadata using `AMDISP_I2C_ADAP_NAME`, sets PM driver flags, resumes the generic PM domain, probes the shared DesignWare core, then suspends the PM domain and enables runtime PM. Transfers are handled entirely by shared DesignWare code in polling mode.

## State And Persistence
State lives in `dw_i2c_dev`, runtime PM state, and controller registers. Probe starts with the PM domain resumed for initialization, then marks the device suspended and runtime-PM managed. No persistent storage is used.

## Dependencies And Integration Points
Depends on AMD ISP misc definitions, generic PM domains, runtime PM, platform MMIO resources, ACPI/OF device nodes, and DesignWare core/master modules under namespaces `I2C_DW` and `I2C_DW_COMMON`.

## Risks
Clock rate is hard-coded; wrong hardware assumptions would break timing. Polling mode increases CPU work and shifts timeout behavior into shared code. PM-domain ordering is important: failures after `i2c_dw_probe()` must disable runtime PM cleanly. Suspend callbacks mark adapters suspended and reinitialize hardware on resume.

## Test Signals
Validate no-IRQ probe path, firmware timing parsing, adapter naming, runtime suspend disables the controller, runtime resume reinitializes it, system suspend marks the adapter suspended, and polling transfers complete without IRQ registration.
