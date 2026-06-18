<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.h

## Purpose

`dt_idle_states.h` declares the DT idle-state parser used by cpuidle platform drivers.

## Important APIs, Types, And Functions

The sole API is `dt_init_idle_driver(struct cpuidle_driver *drv, const struct of_device_id *matches, unsigned int start_idx)`. The `matches` table supplies compatible strings and enter callbacks through `.data`; `start_idx` allows drivers to reserve index 0 for architectural WFI or polling states.

## Control Flow

The header has no control flow. It defines the dependency contract between cpuidle drivers and the parser implementation.

## State And Persistence Behavior

The parser called through this declaration mutates the provided driver; the header owns no state.

## Dependencies And Integration Points

It depends on `struct cpuidle_driver` and `struct of_device_id` being visible to callers. It is used by RISC-V SBI and similar DT-based idle drivers.

## Risks And Test Signals

Risks are mostly build-interface issues: missing include dependencies, signature drift, or callers misunderstanding the return value as total states instead of parsed DT states. Test through compile coverage and DT idle driver probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.h -->
