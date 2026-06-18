# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218_priv.h

Purpose: private register map and state definitions for the TDA18218HN driver.

Important APIs and types: defines register offsets `R00_ID` through `R3A_FMAX2`, `TDA18218_NUM_REGS`, and `struct tda18218_priv` containing config, adapter, IF cache, and register image.

Control flow: the C file uses symbolic offsets to build bulk writes for default init, IF/filter programming, LO divider programming, AGC sequences, and standby power bits.

State and persistence: the `regs` array acts as a baseline software image of default register values and selected loop-through modifications. Hardware state is programmed from this image during init and selectively changed during tuning.

Dependencies and integration points: includes only the public TDA18218 header. It is private to the implementation and not a board-driver API.

Risks: register comments are terse and some labels appear copy-pasted, so field-level meaning is not self-validating. Any mismatch between `TDA18218_NUM_REGS` and default image length would corrupt init coverage. Since the config pointer is stored directly, lifetime is external.

Test signals: build-time coverage of all offsets, attach/init writing exactly 59 registers, and hardware readback or trace comparison after loop-through and standby changes.
