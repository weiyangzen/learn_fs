# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/smc.c

Purpose: This file implements SCMI over ARM SMCCC SMC/HVC calls with shared memory. It supports standard `arm,scmi-smc`, parameterized shmem address passing, Qualcomm capability ID calls, optional completion IRQ, and optional atomic mode.

Important APIs/types/functions: `struct scmi_smc` stores optional IRQ, cinfo, shmem mapping, IO ops, mutex or atomic in-flight token, SMCCC function ID, optional shmem page/offset parameters, and optional capability ID. `smc_chan_setup()` maps shmem, reads `arm,smc-id`, handles Qualcomm cap ID and `arm,scmi-smc-param`, requests named `a2p` IRQ if present, and initializes locking. `smc_send_message()` prepares shmem and invokes SMCCC. `smc_msg_done_isr()` calls core RX callback. `smc_mark_txdone()` releases the channel.

Control flow: Only TX channels are supported. Send acquires either mutex or atomic busy-wait in-flight lock, writes shared memory, rings SMCCC with cap ID or page/offset parameters, and leaves the lock held until txdone. If the SMCCC return value is nonzero, the lock is released and `-EOPNOTSUPP` is returned. If no IRQ is configured, `cinfo->no_completion_irq` tells the core completion happens without interrupt. Descriptor marks sync commands completed on SMCCC return.

State and persistence: Per-channel runtime state is devm-managed and attached to `cinfo`. Atomic mode stores the active sequence token in an atomic; non-atomic mode uses a mutex. No persistent data exists.

Dependencies and integration points: It depends on ARM SMCCC, OF IRQ/address helpers, shared-memory helpers, SCMI transport registration, and optional `CONFIG_ARM_SCMI_TRANSPORT_SMC_ATOMIC_ENABLE`. It matches `arm,scmi-smc`, `arm,scmi-smc-param`, and `qcom,scmi-smc`.

Risks and edge cases: Atomic mode busy-waits until the in-flight token clears. The shmem page/offset scheme limits shmem addressability to 44 bits. Qualcomm capability ID is read from the last 8 bytes of shmem. Missing IRQ changes completion assumptions. Lock release depends on `mark_txdone()` after response fetch.

Test signals: Test all compatibles, SMCCC unsupported return, IRQ and polling/no-IRQ modes, atomic and mutex locking, parameterized shmem address values, Qualcomm cap ID extraction, timeout recovery, and module unload/free IRQ behavior.
