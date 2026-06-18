# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/health.c

## Purpose
`health.c` implements mlx5 device health polling, fatal sensor detection, firmware syndrome reporting, devlink health reporters, firmware trace/core-dump collection, timestamp updates for firmware logs, and recovery/unload actions after device errors.

## Important APIs, Types, And Functions
- NIC interface helpers `mlx5_get_nic_state` and `mlx5_set_nic_state` read/write the initial segment state bits.
- `mlx5_health_check_fatal_sensors` detects PCI read failure, PCI channel offline, disabled NIC interface, software reset, and firmware syndrome reset requests.
- Error/recovery APIs include `mlx5_enter_error_state`, `mlx5_error_sw_reset`, `mlx5_health_wait_pci_up`, `mlx5_trigger_health_work`, `mlx5_start_health_poll`, `mlx5_stop_health_poll`, `mlx5_drain_health_wq`, `mlx5_health_init`, and `mlx5_health_cleanup`.
- Devlink reporter callbacks diagnose, dump, and recover firmware and fatal firmware health events.

## Control Flow And State
`mlx5_health_init` creates devlink reporters unless the device is lightweight, creates the vNIC reporter, allocates a single-thread workqueue, and initializes report/timestamp work. `mlx5_start_health_poll` arms a timer that periodically reads fatal sensors, health counter, and syndrome fields. A fatal sensor immediately marks the device internal-error and queues fatal report work. Missed health-counter increments or changed syndromes queue nonfatal firmware report work.

Fatal reporter work enters error state, invokes devlink health reporting when available, and can unload the driver if recovery is canceled by graceful-period policy. Recovery disables the bad device, waits for PCI reads to return, calls `mlx5_recover_device`, and rechecks fatal sensors. Optional firmware log timestamp work writes wall-clock time to MRTC hourly.

## State And Persistence Behavior
State lives in `dev->priv.health`: timer, workqueue, reporter pointers, health buffer pointers, previous counter, miss counter, syndrome, fatal error, flags, and crdump size. Hardware state is read from the initial segment health buffer and written through NIC state and MRTC registers. Health reporters expose transient diagnostic dumps through devlink, not persistent files.

## Dependencies And Integration Points
The file depends on initial segment MMIO, PCI channel state, devlink health, firmware tracer, core dump collection, vNIC reporter, notifier chains, command flushing, device load/unload/recovery, PCI VSC reset semaphore helpers, and firmware reset timeout constants.

## Risks And Edge Cases
Health polling runs from a timer and queues work; teardown must cancel work and delete timers in the right order. PCI communication failure makes health-buffer reads unreliable and limits recovery options. Software reset is coordinated across PFs through a VSC semaphore. Devlink graceful periods may suppress recovery, leading to driver unload.

## Test Signals
Inject health counter stalls, firmware syndromes, PCI offline, NIC disabled/software reset states, and RFR/CRR syndrome bits. Verify devlink diagnose/dump output, crdump on PFs, recovery success/failure, unload on canceled recovery, timestamp update scheduling, and no health work after drain/cleanup.
