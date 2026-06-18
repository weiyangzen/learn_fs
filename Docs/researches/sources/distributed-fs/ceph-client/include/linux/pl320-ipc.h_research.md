# sources/distributed-fs/ceph-client/include/linux/pl320-ipc.h

Purpose: declares the minimal public interface for the ARM PL320 inter-processor communication mailbox driver.

Important APIs and types: `pl320_ipc_transmit(u32 *data)` sends a message payload, while `pl320_ipc_register_notifier()` and `pl320_ipc_unregister_notifier()` attach or detach `notifier_block` receivers for incoming IPC events.

Control flow: platform or subsystem code registers a notifier to receive mailbox events, transmits messages through the driver, and unregisters the notifier during teardown. Actual interrupt handling, mailbox register access, and notifier invocation live in the implementation.

State and persistence: this header stores no state. Runtime state is in the PL320 driver: notifier chain membership, mailbox registers, pending interrupts, and synchronization around transfers.

Dependencies and integration points: relies on `u32` and `struct notifier_block` declarations from surrounding includes. It integrates ARM platform code, mailbox/IPI-style communication, interrupt handling, and notifier chains.

Risks and test signals: risks include notifier lifetime races, message buffer ownership ambiguity, concurrent transmit serialization, and unregister during callback. Test registering multiple notifiers, transmit success/failure paths, interrupt delivery, teardown with pending IPC, and build coverage on platforms that expose PL320.
