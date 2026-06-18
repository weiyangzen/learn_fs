<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-priv.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-priv.h

## Purpose
Private IPC3 header tying together IPC3 PCM, topology, control, firmware loader, tracing, ready-message helpers, RX dispatch, and platform trace callback wrappers.

## Important APIs, Types, and Functions
Declares `ipc3_pcm_ops`, `ipc3_tplg_ops`, `tplg_ipc3_control_ops`, `ipc3_loader_ops`, `ipc3_dtrace_ops`, `sof_ipc3_get_ext_windows()`, `sof_ipc3_get_cc_info()`, `sof_ipc3_validate_fw_version()`, `ipc3_dtrace_posn_update()`, and `sof_ipc3_do_rx_work()`. Inline wrappers `sof_dtrace_host_init()`, `sof_dtrace_host_release()`, and `sof_dtrace_host_trigger()` call optional platform trace ops from the selected descriptor.

## Control Flow, State, and Persistence
The header owns no persistent state. The inline wrappers make platform trace callbacks optional and return success when unsupported, allowing generic IPC3 dtrace code to run on platforms without host-specific trace setup.

## Dependencies and Integration
Includes `sof-priv.h` and is included by IPC3 core, topology, loader, control, PCM, and dtrace files. It is the internal contract that lets `ipc.c` use `ipc3_ops` as a coherent ops aggregate.

## Risks and Test Signals
Risks include missing declarations when new IPC3 sub-ops are added, optional trace wrappers hiding unsupported platform functionality, and descriptor ops accessed through `sdev->pdata->desc->ops` rather than runtime-mutated ops. Build coverage of all IPC3 objects and trace init on platforms with and without trace callbacks are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-priv.h -->
