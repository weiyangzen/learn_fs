# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-api.c

Purpose: This file implements the CEC character-device userspace API: open/release, poll, and ioctl handling for adapter capabilities, physical/logical addresses, connector info, transmit/receive, event dequeue, and filehandle mode selection.

Important APIs, types, and functions: The exported `cec_devnode_fops` provides `.open`, `.unlocked_ioctl`, `.compat_ioctl`, `.release`, and `.poll`. Key internal functions are `cec_poll()`, `cec_is_busy()`, `cec_adap_g_caps()`, `cec_adap_g_phys_addr()`, `cec_validate_phys_addr()`, `cec_adap_s_phys_addr()`, `cec_adap_g_log_addrs()`, `cec_adap_s_log_addrs()`, `cec_adap_g_connector_info()`, `cec_transmit()`, `cec_receive_msg()`, `cec_receive()`, `cec_dqevent()`, `cec_g_mode()`, `cec_s_mode()`, `cec_ioctl()`, `cec_open()`, and `cec_release()`.

Control flow and state: `cec_open()` allocates a `struct cec_fh`, initializes message/event queues and waitqueue, acquires the adapter device reference, queues initial state and optional HPD/5V events, then links the filehandle into `devnode.fhs`. `cec_ioctl()` checks registration and dispatches commands. Setters validate capabilities and busy/exclusive state before calling core helpers. Transmit copies a user `struct cec_msg`, invokes `cec_transmit_msg_fh()`, and copies completion state back. Receive and event dequeue block or return `-EAGAIN` based on file flags and user timeouts. `cec_release()` clears exclusive ownership, monitor counts, follower count, pending transmit filehandle links, queued messages/events, and adapter references.

State and persistence behavior: Filehandle state is per open descriptor: mode bits, queued received messages, queued events, pending transfer links, and waitqueue. Adapter global state is changed only through locked helper calls. Nothing persists beyond the file descriptor or adapter lifetime.

Dependencies and integration points: Depends on the internal adapter API in `cec-priv.h`, public CEC uAPI structs/ioctls, optional pin APIs for initial HPD/5V reads, waitqueues, mutexes, copy_to/from_user, capabilities, and poll semantics. It is the only file attached directly to the char-device fops created by `cec-core.c`.

Risks and edge cases: Risks include user/kernel copy failures, leaking padding from `struct cec_log_addrs` (explicitly avoided with `memcpy`), invalid physical addresses, invalid mode combinations, monitor modes without privileges, exclusive initiator/follower conflicts, file release while blocking transmit is pending, and event/message queue lifetime cleanup.

Test signals: Validate all ioctls with good/bad user pointers, blocking and nonblocking receive/transmit, poll readiness transitions, invalid mode combinations, CAP checks for raw/monitor modes, initial events on open, release cleanup while a transmit waits for a reply, and unregistration returning `ENODEV`/poll hangup.
