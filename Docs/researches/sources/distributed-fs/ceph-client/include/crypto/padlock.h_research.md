# sources/distributed-fs/ceph-client/include/crypto/padlock.h

Purpose: defines shared constants for VIA PadLock hardware crypto drivers.

Important APIs, types, and flow: constants set hardware alignment requirements, module log prefix, normal and composite crypto priorities, and stack alignment per architecture word size.

State and persistence: no runtime state.

Dependencies and integration: integrates with PadLock AES/SHA drivers and build-time architecture choices.

Risks and test signals: wrong alignment or priority can cause hardware faults or unintended algorithm selection. Signals include PadLock hardware self-tests, alignment stress tests, `/proc/crypto` priority inspection, and 32-bit/64-bit build coverage.
