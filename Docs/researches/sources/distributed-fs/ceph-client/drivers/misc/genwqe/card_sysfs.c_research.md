# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_sysfs.c

## Purpose
`card_sysfs.c` defines GenWQE device sysfs attributes for card status, IDs, type, temperature, timers, queue working time, clock, bitstream selection, and bitstream reload requests.

## Important APIs, Types, and Functions
Read-only attributes are `status`, `appid`, `version`, `type`, `tempsens`, `freerunning_timer`, `queue_working_time`, `base_clock`, and `curr_bitstream`. Writable or write-only attributes are `next_bitstream` and `reload_bitstream`. `genwqe_is_visible()` filters PF-only attributes from VFs. `genwqe_attribute_groups` is exported for device creation.

## Control Flow
`device_create_with_groups()` installs `genwqe_attribute_groups`. Show functions read `struct genwqe_dev` or MMIO registers and format text. `next_bitstream_store()` parses partition 0 or 1 and writes the softreset register. `reload_bitstream_store()` sets card state to `GENWQE_CARD_RELOAD_BITSTREAM` only from unused/used states. Attribute visibility returns all attributes for privileged PFs and only normal attributes for VFs.

## State and Persistence
Most attributes expose live card registers. `next_bitstream` updates `cd->softreset` and hardware softreset selection; `reload_bitstream` changes in-memory card state to trigger a later reload path. No sysfs text itself is persisted.

## Dependencies and Integration Points
The file depends on GenWQE MMIO helpers, card type/clock/app-id helpers, device core attributes, and `genwqe_is_privileged()` policy. It is integrated by `card_dev.c` when creating the device node.

## Risks and Edge Cases
Some bitstream data is documented as unreliable with older CPLD versions. Sysfs stores parse integers but do not serialize against all other card-state transitions. VF visibility is critical because many registers are PF-only.

## Test Signals
Validate PF versus VF attribute visibility, register formatting, invalid partition/reload writes, reload state transitions, app-id sanitization, and behavior when MMIO reads return all ones during PCI error handling.
