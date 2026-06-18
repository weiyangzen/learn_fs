# sources/distributed-fs/ceph-client/drivers/mtd/devices/st_spi_fsm.c

Purpose: ST Fast Sequence Mode serial flash controller driver. It detects supported SPI NOR chips, synthesizes hardware FSM micro-sequences for read/write/erase/status operations, configures flash vendor features, and registers a NOR MTD.

Important APIs/types/functions: `struct stfsm_seq` is the packed register image for an FSM sequence; `struct stfsm` owns MMIO base, clock, MTD, lock, selected flash info, and prepared sequences; `struct seq_rw_config` and `struct flash_info` drive command selection. Core helpers include `stfsm_load_seq()`, `stfsm_wait_seq()`, `stfsm_read_fifo()`, `stfsm_clear_fifo()`, `stfsm_write_fifo()`, `stfsm_wait_busy()`, `stfsm_read_status()`, `stfsm_write_status()`, `stfsm_prepare_rw_seq()`, vendor config functions, and MTD callbacks `stfsm_mtd_read()`, `stfsm_mtd_write()`, `stfsm_mtd_erase()`.

Control flow: probe maps registers, enables clock, resets and configures the FSM, fetches boot/reset platform flags, probes JEDEC ID, marks >16 MiB parts as 32-bit address capable, runs vendor-specific configuration or defaults, fills MTD geometry, and registers. Read/write callbacks lock the controller and split transfers into 256-byte chunks/pages. Low-level transfers set sequence data size/address, handle FIFO alignment padding, start sequences, drain/fill FIFO, wait for completion, and optionally enter/exit 32-bit address mode around each operation. Erase chooses chip erase for full device or sector sequence loops.

State and persistence: persistent state is NOR data plus flash configuration bits such as QE, dummy-cycle VCR, DYB sector locks, and 32-bit address mode. Runtime state includes prepared sequences, controller mode/frequency, FIFO direction delay, boot-from-SPI reset policy, and status/error handling flags.

Dependencies/integration: platform driver compatible `st,spi-fsm`, MMIO registers, clocks, optional syscon/regmap boot-device data, OF properties `st,reset-signal` and `st,reset-por`, MTD/SPI-NOR command definitions, and local `serial_flash_cmds.h`.

Risks: reset safety is nuanced on boot-from-SPI systems; leaving a flash in 32-bit or quad mode across warm reset can break boot. `stfsm_write()` always returns 0 even when `stfsm_wait_busy()` reports errors, except for status clearing side effects. Several paths use `BUG_ON` for alignment/idleness rather than recoverable errors. Vendor DYB unlock loop and S25FL offset condition deserve scrutiny.

Test signals: JEDEC detection for each vendor family, selected read/write sequence versus flags, QE bit update, 32-bit address enter/exit under boot reset constraints, FIFO clearing with residual bytes, unaligned buffer/size reads and writes, S25FL error flags, chip erase and sector erase timeout paths, suspend/resume clock behavior.
