# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-ipc-msg-injector.c

Purpose: Auxiliary SOF client exposing debugfs `ipc_msg_inject` to send arbitrary IPC messages to firmware and read back replies, with IPC3 and IPC4-specific buffer handling.

Important APIs/state: `struct sof_msg_inject_priv` stores debugfs file, max message size, IPC type, TX buffer, and RX buffer. IPC3 fops treat buffers as normal SOF IPC headers/replies. IPC4 fops copy a 64-bit IPC4 header plus optional payload into `struct sof_ipc4_msg`, preserve `data_ptr`, and read back header plus large-config payload when applicable.

Control flow: Open rejects crashed firmware and takes a debugfs reference. Write copies user data into TX storage, zeroes reply storage, resumes PM, boots DSP, sends with `sof_client_ipc_tx_message()`, autosuspends, and returns bytes or error. IPC4 write requires at least header size and initializes RX data capacity before send. Read returns IPC3 reply size or IPC4 header/payload, respecting file offset and user count. Probe chooses fops by `sof_client_get_ipc_type()`, allocates extra space for IPC4 containers, initializes IPC4 data pointers, creates debugfs, and enables runtime PM.

Dependencies and integration: Uses SOF client IPC wrappers, IPC4 header macros, debugfs, auxiliary bus, runtime PM, and firmware support for arbitrary messages.

Risks: Debugfs allows privileged users to send malformed or destructive IPCs. IPC4 data size validation checks payload against max message size but allocated IPC4 buffer includes header plus max payload. Read offset arithmetic copies IPC4 payload at `buffer + *ppos`, which follows header-only offset semantics and must stay consistent. Static `fops` in probe is assigned per probe but values are immutable pointers.

Test signals: IPC3 and IPC4 writes/reads, short IPC4 header, oversized payload, large-config GET reply payload, firmware crash rejection, PM and boot failures, IPC error propagation, and debugfs remove with open files.
