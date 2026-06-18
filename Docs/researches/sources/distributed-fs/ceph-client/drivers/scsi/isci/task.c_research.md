# sources/distributed-fs/ceph-client/drivers/scsi/isci/task.c

Purpose: implements Intel ISCI libsas task submission and task-management callbacks, bridging `struct sas_task` and libsas error handling into SCI controller requests, tags, remote-device state, and completions.

Important APIs and functions: `isci_task_execute_task()` is the normal I/O entry point; it looks up `isci_remote_device`, checks `IDEV_IO_READY` or NCQ recovery, allocates a tag, builds an `isci_request`, and calls `isci_request_execute()`. `isci_task_abort_task()`, `isci_task_lu_reset()`, and `isci_task_I_T_nexus_reset()` are libsas error-handler paths. `isci_task_execute_tmf()` sends SSP task-management requests with a stack completion and timeout. `isci_task_request_complete()` is the SCI completion hook for TMFs. Unsupported callbacks such as clear nexus and task-set operations currently return `TMF_RESP_FUNC_FAILED`.

Control flow: submission refuses missing devices with `SAS_DEVICE_UNKNOWN`, refuses unready devices or tag exhaustion as `SAS_QUEUE_FULL`, and frees tags if a command never reaches hardware. Abort first validates `task->lldd_task` under host and task locks, suspends and terminates the remote node context, then either completes locally for SMP/SATA/already-complete/gone targets or sends SSP abort TMF. LUN reset terminates pending I/O and either schedules SATA reset or sends SSP LUN reset. I_T nexus reset performs phy hard reset/local reset after terminate.

State and persistence: state is in live kernel objects only: task flags, request flags (`IREQ_COMPLETE_IN_TARGET`, `IREQ_TERMINATED`, abort-path bits), controller tags, RNC/device flags, and TMF completion/status fields. No persistent on-disk state exists.

Dependencies and integration: depends on libsas, SCSI midlayer status conventions, ISCI host/device/request APIs, SCI controller calls, port/phy reset helpers, and kernel completions/spinlocks. It is invoked by the SAS domain template and by SCI completion code.

Risks and test signals: race coverage around task completion versus abort is critical because stale `lldd_task` or double tag free would corrupt I/O state. Validate missing-device, tag-exhaustion, NCQ recovery, SATA reset, SSP abort, TMF timeout, hot-unplug, and eventq wakeup paths. Dynamic signals include `dev_dbg/dev_warn`, successful SCSI retry behavior on queue full, and no leaked tags after failed `isci_request_execute()`.
