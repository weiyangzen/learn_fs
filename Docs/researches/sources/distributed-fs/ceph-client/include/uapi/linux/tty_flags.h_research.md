# sources/distributed-fs/ceph-client/include/uapi/linux/tty_flags.h

Purpose: Defines serial/TTY async flag bit positions and masks shared with userspace.

Important APIs/types/functions: User-visible bit positions include hangup notification, fourport, SAK, speed aliases, skip test, auto IRQ, hard PPS, low latency, buggy UART, autoprobe, and magic multiplier. Kernel/internal positions include initialized, suspended, normal active, boot autoconfig, closing, CTS flow, carrier detect, shared IRQ, and console flow. Masks include `ASYNC_FLAGS`, `ASYNC_DEPRECATED`, `ASYNC_USR_MASK`, speed masks, and `ASYNC_INTERNAL_FLAGS`.

Control flow: Userspace observes or sets allowed flags through serial ioctls; the kernel masks user inputs, preserves internal bits, and applies behavior such as baud aliasing or low-latency handling.

State and persistence behavior: Flags are per-serial-port runtime/configuration state, often initialized from driver defaults or boot probing. Persistence depends on userspace reconfiguration and driver behavior.

Dependencies and integration points: Integrates with serial core, TTY ioctls, setserial-style tools, and driver-specific port configuration.

Risks: User and kernel bit ranges overlap only by explicit masks; incorrect masking can leak internal state or let userspace corrupt driver state. Several user flags are deprecated but retained for ABI.

Test signals: Verify mask behavior, deprecated flag preservation, user/kernel flag separation, speed alias interactions, and 32-bit unsigned shift correctness.
