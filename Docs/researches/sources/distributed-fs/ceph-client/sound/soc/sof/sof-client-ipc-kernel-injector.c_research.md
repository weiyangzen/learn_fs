# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-kernel-injector.c

Purpose: Auxiliary SOF client exposing a debugfs file that injects a user-provided IPC buffer into the kernel RX path, useful for testing kernel-side IPC message handling.

Important APIs/state: `struct sof_msg_inject_priv` stores the `kernel_ipc_msg_inject` debugfs dentry, maximum message size, and kernel buffer. `sof_kernel_msg_inject_dfs_write()` copies user data into the buffer, resumes PM, boots DSP, and calls `sof_client_ipc_rx_message(cdev, hdr, buffer)`.

Control flow: Open takes a debugfs active reference. Write only acts at offset 0, uses `simple_write_to_buffer()` with max payload size, requires full copy, resumes runtime PM, boots DSP, injects the message into RX handling, and autosuspends. Probe allocates state and buffer sized by `sof_client_get_ipc_max_payload_size()`, creates debugfs, and enables runtime PM as active/idle. Remove disables PM and removes debugfs.

Dependencies and integration: Uses SOF client IPC/RX APIs, auxiliary bus, debugfs, runtime PM, and firmware/header layout only enough to treat the buffer as `sof_ipc_cmd_hdr`.

Risks: This is intentionally powerful test/debug functionality; malformed buffers exercise kernel IPC parsers. Unlike the message injector, open does not check firmware crashed state. Write ignores return from `sof_client_ipc_rx_message()` because it is void and returns `count` after PM put even if injection caused parser errors.

Test signals: Oversized writes, partial copy failure, PM resume/boot failure, malformed headers through RX parser, debugfs lifetime, and module unload during open file handling.
