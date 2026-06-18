# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.c

Purpose: manages SM750 display power management, chip power modes, and clock gates for major engines.

Important APIs/types/functions: public functions are `ddk750_set_dpms()`, `sm750_set_power_mode()`, `sm750_set_current_gate()`, `sm750_enable_2d_engine()`, `sm750_enable_dma()`, `sm750_enable_gpio()`, and `sm750_enable_i2c()`. Internal `get_power_mode()` selects current gate register context.

Control flow: DPMS writes either `CRT_DISPLAY_CTRL` fields on SM750LE or `SYSTEM_CTRL` fields on other chips. Power mode ignores changes on SM750LE, otherwise updates `POWER_MODE_CTRL` mode bits and oscillator/validation clock bits. Current gate writes to `MODE1_GATE` when in mode 1, else `MODE0_GATE`. Engine enable helpers read `CURRENT_GATE`, set or clear their gate bits, and write back via `sm750_set_current_gate()`.

State and persistence: power mode, DPMS, and gate state persist in hardware registers. No software cache is kept.

Dependencies and integration: uses chip detection from `ddk750_chip.c`, MMIO helpers, and register masks. Called by hardware init, display output code, acceleration setup, GPIO/I2C users, and suspend-like paths.

Risks: read-modify-write gate operations can race if multiple contexts manipulate gates without external locking. SM750LE silently ignores power-mode changes. Gate writes depend on current power mode, so callers must set power mode before gate configuration.

Test signals: verify DPMS on SM750 and SM750LE, power mode 0/1/sleep transitions, gate toggles for 2D/DMA/GPIO/I2C, and init sequences that enable display/localmem before mode setting.
