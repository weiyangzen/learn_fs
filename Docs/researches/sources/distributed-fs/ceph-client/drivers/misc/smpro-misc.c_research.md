# sources/distributed-fs/ceph-client/drivers/misc/smpro-misc.c

## Purpose
`smpro-misc.c` provides miscellaneous Ampere Altra SMpro sysfs controls for boot progress reporting and SoC power limit access through a parent regmap.

## Important APIs, Types, and Functions
`struct smpro_misc` stores the parent `regmap`. `boot_progress_show()` reads current boot-stage registers and emits a packed six-byte progress value. `soc_power_limit_show()` and `soc_power_limit_store()` expose register `SOC_POWER_LIMIT` as a read/write sysfs value. `smpro_misc_probe()` allocates private data and retrieves the parent regmap. Attributes are grouped with `ATTRIBUTE_GROUPS(smpro_misc)`.

## Control Flow
Probe binds the regmap from the parent. Reading `boot_progress` compares the firmware-reported boot stage with the current stage, rejects impossible stage advancement, reads low/high progress words, and writes an acknowledgement bit when firmware should advance to the next boot stage. Reading or writing `soc_power_limit` directly maps to a single SMpro register.

## State and Persistence
The only software state is the regmap pointer. Boot progress and power-limit state are firmware/register backed. Reading boot progress can mutate firmware-visible state by writing the bootstage register when the reported stage lags the current stage.

## Dependencies and Integration Points
The driver is a platform child named `smpro-misc` and depends on a parent regmap provider, sysfs attribute groups, and SMpro firmware register semantics.

## Risks and Edge Cases
`soc_power_limit_store()` accepts any unsigned long value and casts it to `unsigned int` without range validation. `boot_progress_show()` returns `-EINVAL` when boot stage exceeds current stage, making firmware ordering bugs visible to userspace. The boot-progress output uses byte-swapped 16-bit words, so consumers need to know the firmware format.

## Test Signals
Check sysfs file creation, boot progress output across stage transitions, acknowledgement writes when `boot_stage < cur_stage`, invalid stage rejection, power-limit read/write success, and regmap error mapping to sysfs errors.
