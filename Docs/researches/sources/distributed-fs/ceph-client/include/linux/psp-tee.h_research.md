# sources/distributed-fs/ceph-client/include/linux/psp-tee.h

Purpose: declares the AMD PSP Trusted Execution Environment command interface used to communicate with AMD-TEE Trusted OS.

Important APIs and types: `enum tee_cmd_id` enumerates loading/unloading trusted applications, opening/closing sessions, invoking TA commands, and mapping/unmapping shared memory. `psp_tee_process_cmd()` submits a command buffer and returns a TEE status; `psp_check_tee_status()` checks whether a usable TEE exists. Disabled PSP builds return `-ENODEV`.

Control flow: the AMD TEE driver checks availability, prepares a command buffer for a TEE operation, calls `psp_tee_process_cmd()`, and reads the updated buffer/status on success. The PSP layer handles command submission and timeout/busy behavior.

State and persistence: session, TA, and shared-memory state is owned by the TEE/PSP implementation and Trusted OS. This header only defines the command IDs and call contract.

Dependencies and integration points: depends on PSP crypto device support, AMD TEE driver, shared memory mapping, and Trusted OS command ABI.

Risks and test signals: risks include invalid command buffer layout, stale shared memory mappings, session lifetime leaks, timeout/busy handling, and disabled-config behavior. Test TA load/session/invoke/unload cycles, map/unmap error paths, unavailable TEE, PSP reset/busy cases, and no-PSP builds.
