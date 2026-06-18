# sources/distributed-fs/ceph-client/include/linux/platform_data/ams-delta-fiq.h

Purpose: defines shared offsets into the Amstrad E3/AMS Delta FIQ buffer used by FIQ assembly and drivers that service GPIO-triggered keyboard, modem, and hook-switch events.

Important APIs and types: macros `FIQ_MASK` through `IRQ_SIR_CODE_L2`, `FIQ_CNT_INT_*`, and `FIQ_CIRC_BUFF` define word offsets for mask/state, key counters, circular buffer head/tail/length, missed keys, GPIO interrupt mask, pending IRQ flags, soft interrupt codes, interrupt counters, and circular buffer data start.

Control flow: low-level FIQ code writes event state and counters into the shared buffer using these offsets; normal interrupt or device drivers read/update fields to drain events and coordinate masking.

State and persistence: state lives in a shared in-memory FIQ buffer. It is volatile and platform-specific, but must remain layout-compatible across FIQ and driver code.

Dependencies and integration points: integrates OMAP/AMS Delta board FIQ handling with keyboard/modem/hook-switch GPIO drivers and interrupt dispatch code.

Risks and test signals: risks include offset drift breaking assembly/users agreement, circular-buffer overflow, missed-key accounting errors, and races between FIQ and IRQ context. Test keyboard/modem/hook events, buffer wrap, missed interrupt counters, mask updates, and platform compile coverage.
