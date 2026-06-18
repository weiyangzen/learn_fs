# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_sysfs.c

## Purpose
Registers the `remoteproc` device class and exposes the normal userspace control ABI under `/sys/class/remoteproc/remoteproc*/` for recovery, coredump policy, firmware, state, and name.

## Important APIs, Types, And Functions
Exports `rproc_class`, `rproc_init_sysfs()`, and `rproc_exit_sysfs()`. Attribute handlers implement `recovery`, `coredump`, `firmware`, `state`, and `name`. `rproc_is_visible()` makes control attributes read-only when `rproc->sysfs_read_only` is set.

## Control Flow
Class registration installs the default attribute group for every remoteproc device. `state_store()` maps `start` to `rproc_boot()`, `stop` to `rproc_shutdown()`, and `detach` to `rproc_detach()`. `firmware_store()` delegates to `rproc_set_firmware()`. `recovery_store()` toggles `recovery_disabled` or triggers recovery. `coredump_store()` changes dump policy unless the processor is already crashed.

## State And Persistence Behavior
Writes mutate live `struct rproc` fields or initiate lifecycle transitions. Firmware changes persist only for the lifetime of the rproc instance and are rejected while running. `firmware_show()` reports `unknown` when attached to externally booted firmware. The class and attributes are recreated on module load.

## Dependencies And Integration Points
Used by `remoteproc_core.c` during module init and by `rproc_alloc()` through `rproc_class`. Depends on core lifecycle APIs, coredump enum/string ordering, and the remoteproc state enum remaining synchronized with `rproc_state_string`.

## Risks
This is a userspace ABI, so accepted strings and state names must remain stable. `recovery_disabled` is toggled without taking `rproc->lock`, relying on simple boolean semantics while recovery itself locks. Comments mention "default" coredump but parser accepts `disabled`, `enabled`, and `inline`; tests should follow parser behavior.

## Test Signals
Check class registration, attribute visibility/read-only mode, state strings, start/stop/detach behavior, firmware writes while offline versus running, coredump write rejection while crashed, and recovery writes that recover a deliberately crashed processor.
