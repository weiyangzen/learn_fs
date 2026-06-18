# sources/distributed-fs/ceph-client/samples/nitro_enclaves/ne_ioctl_sample.c

Purpose: comprehensive user-space sample for creating, loading, configuring, starting, and monitoring an AWS Nitro Enclave through `/dev/nitro_enclaves` ioctls.

Important APIs/functions: `NE_CREATE_VM`, enclave fd polling thread, memory allocation with hugepage-aligned regions, image loading into user memory regions, `NE_SET_USER_MEMORY_REGION`, `NE_ADD_VCPU`, `NE_START_ENCLAVE`, vsock heartbeat check, and pthread/poll/ioctl helpers.

Control flow: main parses enclave image and resource options, opens the NE device, creates a VM/enclave fd, starts a polling thread for enclave fd events, allocates user memory regions, loads the enclave image across regions, registers memory with the driver, adds vCPUs, starts the enclave, waits/checks for boot heartbeat over vsock, sleeps for demonstration lifetime, and frees resources.

State and persistence: process owns enclave fd, slot UID, allocated memory mappings, vCPU IDs, poll thread, and start info while running. Enclave lifetime is tied to descriptors and driver state.

Dependencies and integration: Nitro Enclaves kernel driver, `/dev/nitro_enclaves`, ioctl UAPI, pthreads, poll, mmap/madvise-like memory behavior, and vsock connectivity.

Risks: large memory allocation/registration can fail or exhaust host resources. Image loading must align region sizes and offsets. Enclave creation/start ioctls are privileged and hardware/platform-specific. Cleanup must handle partial setup to avoid leaked mappings or live enclave resources.

Test signals: compile on an EC2 Nitro Enclaves-capable instance, run with a valid EIF, verify create/load/start logs and heartbeat response, then confirm enclave fd poll events and cleanup.
