# sources/distributed-fs/ceph-client/include/linux/soc/apple/rtkit.h

Purpose: This header defines the client API for Apple RTKit, the mailbox-based runtime protocol used to boot, manage, and exchange messages with Apple coprocessors.

Important APIs/types/functions: `struct apple_rtkit_shmem` describes shared-memory buffers with IOVA, size, buffer pointer, DMA address, and private cookie. `struct apple_rtkit_ops` provides callbacks for crashed state, received messages, shared-memory setup/destruction, and power/state events. The opaque `struct apple_rtkit` is created by `devm_apple_rtkit_init` or `apple_rtkit_init`. Lifecycle APIs include `apple_rtkit_free`, `reinit`, `boot`, `quiesce`, `wake`, `shutdown`, `poweroff`, `idle`, state queries, endpoint start, message send with completion control, and polling.

Control flow: A device initializes RTKit with ops and cookie, boots the coprocessor, starts endpoints, handles callbacks as messages arrive, sends endpoint messages, and transitions through idle/wake/quiesce/shutdown as the device power state changes.

State and persistence: RTKit owns mailbox protocol state, running/crashed flags, endpoint state, shared-memory mappings, and DMA buffers. Firmware-side state persists while the coprocessor remains powered.

Dependencies and integration: Uses `struct device`, DMA addresses, completions/timeouts, and Apple mailbox/coprocessor providers. Integrates with Apple GPU, ISP, audio, storage, and other RTKit-managed devices.

Risks and test signals: Message ordering, endpoint readiness, shared-memory lifetime, and crash recovery are high risk. Test boot/reboot, endpoint start failure, timeout behavior, crash callback delivery, suspend/resume, DMA mapping cleanup, and polling paths.
