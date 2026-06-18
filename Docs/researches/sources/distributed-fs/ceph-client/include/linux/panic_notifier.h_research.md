# Research: sources/distributed-fs/ceph-client/include/linux/panic_notifier.h

Purpose: `panic_notifier.h` exposes the atomic panic notifier chain and the `crash_kexec_post_notifiers` policy flag to subsystems that need last-chance panic callbacks.

Important APIs/types/functions: it declares `panic_notifier_list` as an `atomic_notifier_head` and `crash_kexec_post_notifiers` as a global boolean. There are no inline helpers; registration uses the generic notifier API from `linux/notifier.h`.

Control flow and state: panic code invokes the notifier list during panic processing. Registered callbacks run in a highly constrained failure context, and the boolean controls whether crash-kexec happens after notifier execution. State is global boot-lifetime kernel state.

Dependencies and integration points: depends on notifier and type definitions. Integrates with panic core, crash dump capture, platform watchdogs, logging backends, firmware notifiers, and drivers that need emergency shutdown notification.

Risks and test signals: notifier callbacks can deadlock, sleep, recurse into broken subsystems, or delay crash capture. Tests should check notifier registration/unregistration, callback ordering, panic-time constraints, and crash-kexec behavior with the post-notifier knob enabled and disabled.
