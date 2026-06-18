# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/optee.c

Purpose: This file implements SCMI over the OP-TEE SCMI PTA. It supports both static SMT shared memory channels and dynamic OP-TEE MSG shared memory buffers, registers an SCMI platform transport after discovering the OP-TEE service, and enforces a single OP-TEE SCMI service instance.

Important APIs/types/functions: `enum scmi_optee_pta_cmd` defines PTA commands for capabilities, SMT processing, MSG processing, and channel acquisition. `struct scmi_optee_channel` stores channel ID, TEE session, caps, rx length, mutex, SCMI cinfo, static shmem or dynamic msg buffer, IO ops, TEE shm, and list node. `struct scmi_optee_agent` stores TEE context and channel list. Key functions include `open_session()`, `get_capabilities()`, `get_channel()`, `setup_dynamic_shmem()`, `setup_static_shmem()`, `scmi_optee_chan_setup()`, `scmi_optee_send_message()`, fetch/clear/mark helpers, and the TEE client probe/remove.

Control flow: The TEE client driver probes the SCMI PTA UUID, opens a TEE context, queries capabilities, publishes `scmi_optee_private`, and registers the SCMI platform transport driver. Channel setup reads `linaro,optee-channel-id`, chooses static shmem if the SCMI node has `shmem` or dynamic TEE shm otherwise, opens a session, tries to convert it to a system session, asks PTA for a channel handle, marks the channel polling-only, and links it. Send locks the channel and either prepares a MSG buffer then invokes `PTA_SCMI_CMD_PROCESS_MSG_CHANNEL`, or prepares SMT shmem then invokes `PTA_SCMI_CMD_PROCESS_SMT_CHANNEL`. Mark txdone unlocks the channel.

State and persistence: Global `scmi_optee_private` stores the single agent. Channel state and sessions are runtime only. Dynamic TEE shared memory is freed during channel free. The agent context is closed after platform driver unregister if no channels remain.

Dependencies and integration points: It depends on OP-TEE TEE client APIs, UUID matching, device tree channel IDs, SCMI shared memory helpers, SCMI message-buffer helpers, and platform transport registration. It matches `linaro,scmi-optee` for SCMI platform nodes and a fixed PTA UUID for service discovery.

Risks and edge cases: Only one OP-TEE SCMI service is allowed. Remove unregisters the platform driver, then returns early if channel list is not empty, leaving context cleanup deferred by design but worth testing. Dynamic MSG mode uses one TEE shm for request and response memrefs. All channels are polling-only (`no_completion_irq`), so timeout settings matter. `scmi_optee_private` publication uses memory barriers; consumers must not race before probe completes.

Test signals: Test PTA absent, capabilities lacking SMT/MSG, static and dynamic channel setup, invalid channel IDs, session open failures, system-session warning path, MSG and SMT send/response paths, channel free list removal, and service remove with active/inactive channels.
