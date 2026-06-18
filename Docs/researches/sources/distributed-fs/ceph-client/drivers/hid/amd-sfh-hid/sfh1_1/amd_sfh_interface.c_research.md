# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.c

## Purpose

`sfh1_1/amd_sfh_interface.c` implements SFH 1.1 command operations and exports platform sensor information to other AMD platform code through `amd_get_sfh_info()`.

## Important APIs, Types, and Functions

Internal command helpers include `amd_sfh_wait_response()`, `amd_start_sensor()`, `amd_stop_sensor()`, and `amd_stop_all_sensor()`. `sfh_interface_init()` installs the SFH 1.1 `amd_mp2_ops` and stores the global `emp2` pointer; `sfh_deinit_emp2()` clears it. Query helpers `amd_sfh_mode_info()`, `amd_sfh_hpd_info()`, and `amd_sfh_als_info()` feed exported `amd_get_sfh_info()`.

## Control Flow

SFH 1.1 init calls `sfh_interface_init()`. Start/stop callbacks write command bitfields into revision-selected C2P registers and response polling checks P2C registers. `amd_get_sfh_info()` dispatches by message type: HPD reads HPD status, ALS reads the mapped sensor memory and converts lux, and SRA reads mode bits to derive platform type and laptop placement.

## State and Persistence Behavior

The global `emp2` pointer is the main state and makes exported info queries refer to the active SFH device. It is cleared during remove. The file also reads persistent `mp2->dev_en` flags to decide whether data is available.

## Dependencies and Integration Points

It depends on `linux/amd-pmf-io.h` for the exported info ABI, MMIO polling, register helpers, and SFH 1.1 structures. The exported symbol integrates with AMD PMF and any platform code querying HPD/ALS/SRA.

## Risks and Test Signals

Risks include single-device global state, queries racing removal, ambiguous laptop placement states, and returning `-ENODEV` until SRA/ALS/HPD flags are set. Test signals include AMD PMF consumers reading correct placement/light/presence values, remove clearing `emp2`, and response timeout handling.
