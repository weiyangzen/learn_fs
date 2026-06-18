# sources/distributed-fs/ceph-client/include/uapi/linux/lirc.h

Purpose: defines the Linux infrared remote-control userspace ABI for raw pulse/space streams, scancode reporting, device feature discovery, and LIRC ioctl controls.

Important APIs and types: mode2 encoding macros include `LIRC_SPACE`, `LIRC_PULSE`, `LIRC_FREQUENCY`, `LIRC_TIMEOUT`, `LIRC_OVERFLOW`, `LIRC_VALUE`, `LIRC_MODE2`, and type predicates. Feature flags describe send/receive modes, carrier/duty/transmitter controls, receive timeout, carrier measurement, wideband receiver, and masks. Ioctls include `LIRC_GET_FEATURES`, mode getters/setters, carrier/duty/timeout controls, transmitter mask, wideband receiver, and receive timeout retrieval. `struct lirc_scancode` carries timestamp, flags, protocol, keycode, and scancode. `enum rc_proto` enumerates supported IR protocols.

Control flow: userspace queries features, selects a send or receive mode, configures carrier/timeout behavior when supported, then reads mode2 words or `lirc_scancode` records or writes transmit data. Kernel drivers encode raw timing and decoded protocol state according to mode and feature flags.

State and persistence: runtime state lives in each LIRC/rc device: selected modes, carrier settings, timeout reporting, protocol decoding, and queued events. No persistent state is stored by the header.

Dependencies and integration points: depends on `linux/types.h` and `linux/ioctl.h`; integrates rc-core drivers, `/dev/lirc*`, lircd-style userspace, input keycode mapping, and protocol decoders.

Risks and test signals: risks include mode2 high-bit encoding mistakes, feature flags advertising unsupported ioctls, protocol enum drift, timestamp expectations, and unused compatibility flags. Test ioctl feature/mode negotiation, raw pulse read/write, timeout and overflow events, scancode flags for toggle/repeat, protocol-specific decode/encode, and unsupported ioctl rejection.
