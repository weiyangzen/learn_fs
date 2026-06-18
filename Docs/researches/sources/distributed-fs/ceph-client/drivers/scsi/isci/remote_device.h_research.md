# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.h

Purpose: declares the ISCI remote-device data structure, state IDs, flags, reference helpers, and public lifecycle/I/O/error-recovery APIs used by libsas callbacks, request handling, and remote-node context code.

Important APIs/types/functions: `struct isci_remote_device` contains flags, `kref`, port/domain-device links, list node, state machine, port width, link rate, owning port, RNC, started request count, SATA/SMP `working_request`, not-ready reason, and abort-resume callback storage. Flags include start/stop pending, allocated, gone, I/O ready, NCQ error, link-hang detection, and abort-path state. `enum sci_remote_device_states` covers initial/stopped/starting/ready, STP idle/CMD/NCQ/error/await-reset, SMP idle/CMD, stopping/failed/resetting/final. Inline helpers implement lookup and reference management under the host lock.

Control flow: the header does not contain the state-machine implementation, but its prototypes define the callable flow: libsas calls found/gone; request code starts and completes I/O/tasks; error paths suspend, terminate, abort, resume, reset, or stop devices; RNC callbacks map back to devices with `rnc_to_dev()`.

State and persistence: remote-device lifetime is controlled by `IDEV_ALLOCATED`, `IDEV_GONE`, and `kref`. `isci_lookup_device()` refuses gone devices and bumps the reference for safe use. `sci_remote_device_decrement_request_count()` warns on underflow. All state is volatile runtime state; persistent device identity remains in libsas/domain discovery, not in this structure.

Dependencies and integration points: includes libsas, Linux kref, remote node context headers, and `port.h`. The type is central to `remote_device.c`, request execution, abort handling, and port teardown. `scics_sds_remote_node_context_callback` integration lets abort recovery preserve and chain RNC callbacks.

Risks and test signals: reference helpers must be called under `scic_lock` as documented; otherwise gone-device races are possible. Request-count underflow, stale `working_request`, abort-resume callback overwrites, and incorrect ready flag transitions are primary risks. Build tests should catch prototype drift, while runtime tests should cover lookup during removal, kref release clearing flags, and every state declared in `REMOTE_DEV_STATES`.
