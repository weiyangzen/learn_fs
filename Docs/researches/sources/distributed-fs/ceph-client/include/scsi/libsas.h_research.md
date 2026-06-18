<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libsas.h -->
# sources/distributed-fs/ceph-client/include/scsi/libsas.h

## Purpose
This header defines the libsas host-side class contract for SAS low-level drivers. It describes SAS HA, phy, port, discovery, domain-device, expander, SATA/SSP, task, and task-management abstractions plus callbacks drivers implement for discovery, I/O, resets, and GPIO.

## Important APIs, Types, And Functions
Important state types include `struct sas_ha_struct`, `struct asd_sas_phy`, `struct asd_sas_port`, `struct domain_device`, `struct expander_device`, `struct ex_phy`, `struct sata_device`, `struct ssp_device`, `struct sas_task`, `struct sas_task_slow`, and `struct sas_domain_function_template`. Event enums classify port, phy, and discovery events. Task status is modeled by `enum service_response`, `enum exec_status`, and `struct task_status_struct`.

The public API registers/unregisters HAs, suspends/resumes HAs, queues SCSI commands, allocates/configures targets/devices, handles queue depth and BIOS parameters, executes internal aborts, attaches SAS domain transport, handles EH abort/device/target resets, performs SMP/SSP task response work, finds phys, issues TMFs, and notifies port/phy events. `LIBSAS_SHT_BASE` macros populate common `scsi_host_template` entries.

## Control Flow
An LLDD fills HA/phy arrays and registers with libsas. Phy/port events enqueue `sas_work` on event/discovery workqueues, discovery builds `domain_device` trees, and device-found/gone callbacks notify the LLDD. SCSI commands become `sas_task` objects with SSP/STP/SMP/abort-specific unions. Completion fills `task_status_struct` and invokes `task_done`; errors route into SCSI EH and SAS TMF helpers.

## State And Persistence
State is in-memory and heavily asynchronous. HA state bits track registered, draining, ATA EH, frozen, and resuming modes. Ports maintain device/discovery/destroy lists and phy membership. Devices use krefs and bit-state flags for found/gone/reset/EH-pending. Locks include spinlocks, mutexes, waitqueues, workqueues, timers, and completions.

## Dependencies And Integration Points
libsas depends on SAS protocol definitions, SCSI device/command/transport SAS headers, libata, scatterlists, timers, PCI, workqueues, and block queues. It integrates with SCSI mid-layer host templates, libata for SATA/STP devices, SAS transport sysfs objects, and LLDD callbacks.

## Risks
Discovery and teardown races can leave devices in EH queues or destroy lists. Task completion must not race abort/reset state flags. LLDD callbacks have context constraints; TMFs require process context. Wide-port formation depends on address matching and strict-wide-port policy. ATA EH and SAS EH interactions are subtle.

## Test Signals
Validate HA register/unregister, phy up/down/OOB events, expander discovery/revalidation, SATA device reset/abort, SSP sense handling, queuecommand task creation, TMF abort/task-set/LU reset paths, internal aborts by tag/qid, drain/freeze/resume, and host-template macro behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libsas.h -->
