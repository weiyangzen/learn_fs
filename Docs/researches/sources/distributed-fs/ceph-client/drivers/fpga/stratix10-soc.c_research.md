# sources/distributed-fs/ceph-client/drivers/fpga/stratix10-soc.c

Purpose: FPGA manager for Intel Stratix10 and Agilex SoC devices where reconfiguration must be performed through a privileged firmware service channel. It requests reconfiguration, allocates service-layer buffers, streams image data through mailbox/service calls, and polls service completion.

Important APIs and functions: `struct s10_priv` stores the service channel, service client, completion, four service buffers, and status bitset. `s10_svc_send_msg` wraps `stratix10_svc_send`. `s10_receive_callback` records service status bits, unlocks returned buffers, and completes waiters. Manager ops are `s10_ops_write_init`, `s10_ops_write`, and `s10_ops_write_complete`. Buffer helpers manage the four `SVC_BUF_SIZE` allocations from the service layer.

Control flow: module init finds a DT `svc` node containing a compatible FPGA manager and populates platform devices before registering the driver. Probe requests the `fpga` service channel and registers the manager. Write-init sends `COMMAND_RECONFIG` with optional partial flag, waits for OK, and allocates four 512 KiB service buffers. Write repeatedly locks a free buffer, copies image data into it, submits `COMMAND_RECONFIG_DATA_SUBMIT`, waits for buffer-submitted or buffer-done statuses, and when no data remains claims/free buffers until all are returned. Write-complete repeatedly sends `COMMAND_RECONFIG_STATUS` until completed, error, or timeout, then calls `stratix10_svc_done`.

State and persistence: state includes the service channel, callback status bitset, completion, and service buffers with bit locks. Hardware state is managed by the privileged firmware service and persisted as FPGA configuration. Buffer ownership is asynchronous and depends on service callbacks returning kernel addresses.

Dependencies and integration points: depends on `stratix10-svc-client`, OF platform population under `svc`, FPGA manager core, completions, and compatible strings `intel,stratix10-soc-fpga-mgr` and `intel,agilex-soc-fpga-mgr`.

Risks and test signals: risks include asynchronous status-bit races, busy-looping on `-ENOBUFS`, buffer-free correctness when errors occur, service timeouts, and no explicit low-level state callback. Test signals are service-channel acquisition, OK response to `COMMAND_RECONFIG`, buffer submitted/done callbacks, all buffers freed after write, completed status from firmware, and clean channel release on remove.
