# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.c

## Purpose
Core CXD2880 tuner-demodulator control implementation. It creates single or diversity instances, initializes silicon, sequences tune/sleep transitions, manages saved configuration, GPIOs, interrupts, TS output, PID filtering, RF/LNA hooks, and register freeze helpers.

## Important APIs, Types, and Functions
Public APIs include `cxd2880_tnrdmd_create()`, `cxd2880_tnrdmd_diver_create()`, `init1()`, `init2()`, `check_internal_cpu_status()`, `common_tune_setting1()`, `common_tune_setting2()`, `sleep()`, `set_cfg()`, GPIO read/write/config helpers, interrupt helpers, `ts_buf_clear()`, `chip_id()`, `set_and_save_reg_bits()`, `set_scan_mode()`, `set_pid_ftr()`, RF compensation/LNA setters, TS pin/output controls, and `slvt_freeze_reg()`. Static helpers implement long register sequences for power, PLL, tuning, sleep, PID filter, and saved config replay.

## Control Flow
Creation zeroes state and installs IO/create parameters. `init1()` validates main/single mode, resets runtime fields, reads chip IDs, runs power/RF init sequences on main and sub devices, and waits between stages. `init2()` verifies internal CPU completion, finishes RF init, replays saved config, and enters sleep. Common tune setting first sleeps the device, chooses DVB-T versus DVB-T2 power mode, resets PLL, reloads saved config, computes frequency shift for one-seg/diversity/xtal sharing, runs tune stages, checks CPU completion, configures TS clock or PID filter, then the standard-specific `tune2` enables TS output. Sleep disables TS output, runs standard-specific sleep settings, and clears active frequency/system/bandwidth.

## State and Persistence
Runtime state lives in `struct cxd2880_tnrdmd`: chip ID, sleep/active state, clock mode, frequency, system, bandwidth, scan mode, diver mode, sub pointer, cancellation flag, saved register config memory, PID filter config, RF compensation callback, and LNA threshold table pointers. Saved config is replayed after init/tune transitions but is not persistent across driver lifetime.

## Dependencies and Integration Points
Depends on `struct cxd2880_io` register callbacks, standard-specific DVB-T/T2 sleep/tune helpers, monitor CPU status, and Linux atomic operations. Higher-level frontend code uses this as the main hardware control layer.

## Risks and Edge Cases
Most APIs reject direct sub-device use; callers must route through main. Saved config memory is capped at 100 entries and returns `-ENOMEM` when exceeded. Register sequences are hardware-specific and error-prone. Many operations require sleep or active state exactly. Diversity paths must keep main/sub state synchronized. Masked saved writes can race without external SPI serialization.

## Test Signals
Chip-ID validation, init timeout/error paths, single and diversity tuning, sleep from each standard, saved config replay after PLL reset, GPIO/interrupt/TS buffer operations, PID filter behavior for SPI/SDIO output, and register trace comparison with vendor sequences.
