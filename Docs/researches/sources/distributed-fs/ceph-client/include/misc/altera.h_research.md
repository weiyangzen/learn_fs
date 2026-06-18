# sources/distributed-fs/ceph-client/include/misc/altera.h

Purpose: This header exposes a small interface for loading Altera STAPL firmware over a caller-provided JTAG I/O callback.

Important APIs, types, and functions: `struct altera_config` carries an opaque device pointer, an action buffer, and a `jtag_io` callback that drives TMS/TDI and reads TDO. `altera_init()` accepts the config and a firmware blob. When the STAPL driver is not enabled by Kconfig, an inline stub logs a warning and returns success.

Control flow: A board or device driver prepares firmware, fills `altera_config`, and calls `altera_init()`. The enabled implementation interprets the firmware/action data and toggles JTAG through `jtag_io`. In disabled builds the call is a no-op except for a warning.

State and persistence behavior: The header defines no persistent state. Any JTAG state machine, firmware parsing state, or device-specific state is in the implementation or caller.

Dependencies and integration points: It relies on `struct firmware`, kernel logging, Kconfig symbols `CONFIG_ALTERA_STAPL` and module builds. It integrates with firmware loading and hardware-specific JTAG bit-banging callbacks.

Risks: The disabled stub returning 0 can mask missing FPGA programming support. The JTAG callback contract is low-level and easy to invert or time incorrectly. Firmware/action data validation is implementation-dependent.

Test signals: Enabled and disabled Kconfig builds, firmware load failures, callback TMS/TDI/TDO sequencing, action selection, device-specific JTAG timing, and callers that must treat the disabled-stub warning as degraded functionality.
