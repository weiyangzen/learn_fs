# sources/distributed-fs/ceph-client/drivers/memory/dfl-emif.c

## Purpose
`dfl-emif.c` implements the Intel FPGA Device Feature List (DFL) private EMIF feature driver. It exposes per-memory-interface sysfs status for initialization and calibration failure, and revision-0-only write triggers for clearing memory.

## Important APIs, Types, And Functions
`struct dfl_emif` contains the device, mapped feature base, and a spinlock protecting `EMIF_CTRL`. `struct emif_attr` embeds a `device_attribute` plus bit shift and channel index, allowing one show/store implementation for all interface attributes.

`emif_state_show()` reads `EMIF_STAT` and returns one bit for `init_done` or `cal_fail`. `emif_clear_store()` accepts only `"1"`, writes the channel clear-enable bit under lock, then polls `EMIF_STAT` until that channel's clear-busy bit clears. Attribute-generation macros create `inf0` through `inf7` status and clear files. `dfl_emif_visible()` hides attributes for absent channels and hides clear attributes for feature revisions greater than zero. `dfl_emif_probe()` maps the DFL MMIO resource and initializes driver data.

## Control Flow
DFL core matches feature id `0x9`. Probe maps resources and sysfs groups are installed via `dev_groups`. Attribute visibility reads the capability/channel mask from offset `0x10`, interpreting it as the revision-0 control register or later capability register. Writes to `infN_clear` serialize the control-register update, then poll with a 5-second timeout.

## State And Persistence
The driver keeps only MMIO base and lock state. Hardware status and clear state live in EMIF registers. Sysfs attributes are dynamically visible based on channel mask and feature revision.

## Dependencies And Integration Points
It depends on DFL device infrastructure, 64-bit MMIO accessors, `readq_poll_timeout()`, sysfs groups, and spinlocks. The ABI is per-channel sysfs under the DFL device.

## Risks
The clear path assumes `EMIF_CTRL_CLEAR_EN` is write-only but preserves other read/write bits by clearing the whole clear field before setting one bit. Incorrect revision or capability interpretation could expose invalid channels. The 5-second polling timeout is the main failure signal for hung hardware.

## Test Signals
Test by probing revision 0 and revision greater than 0 devices, verifying channel-specific visibility, reading `infN_init_done` and `infN_cal_fail`, writing invalid values to `infN_clear`, and checking timeout/error handling when clear-busy never drops.
