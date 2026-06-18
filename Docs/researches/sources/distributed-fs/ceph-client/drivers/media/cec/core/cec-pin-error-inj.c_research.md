# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-error-inj.c

Purpose: This file implements debugfs command parsing and reporting for CEC pin-level error injection, allowing tests to force malformed receive/transmit behavior such as NACKs, low-drive, arbitration loss, bad timings, custom pulses, and byte insertion/removal.

Important APIs, types, and functions: `struct cec_error_inj_cmd` maps command text to bit offsets and argument slots. Exported/internal-to-core functions are `cec_pin_rx_error_inj()`, `cec_pin_tx_error_inj()`, `cec_pin_error_inj_parse_line()`, and `cec_pin_error_inj_show()`. It operates on `struct cec_pin` fields `error_inj`, `error_inj_args`, `rx_toggle`, `tx_toggle`, `rx_no_low_drive`, `tx_ignore_nack_until_eom`, custom pulse/glitch timing, and glitch flags.

Control flow and state: The debugfs write handler in `cec-core.c` feeds lines here. Global commands clear RX/TX state or set custom/glitch options. Opcode-scoped commands parse an opcode or `any`, optional mode (`off`, `once`, `always`, `toggle`), command name, and optional position/argument. The parser validates bit positions and command-specific constraints, updates the packed error-injection mask, and stores arguments. `cec_pin_rx_error_inj()`/`cec_pin_tx_error_inj()` choose opcode-specific settings when available, otherwise fallback to `any`. The show function prints command help and current non-default settings.

State and persistence behavior: Error injection state is per pin adapter, volatile, and debugfs-controlled. `once` modes clear themselves in `cec-pin.c` after firing; `toggle` depends on tx/rx toggle bits flipped when the pin state machine returns to idle.

Dependencies and integration points: Depends on `cec-pin-priv.h`, debugfs seq output, kstrto parsing helpers, and the pin state machine consuming offsets/arguments. It is compiled only when `CONFIG_CEC_PIN_ERROR_INJ` is enabled.

Risks and edge cases: Parser bugs can make tests inject unintended line states. Position validation must avoid ACK-bit misuse for certain TX timing errors and must distinguish opcode-specific vs any-opcode arbitration loss. There is a likely typo in the source path for `tx-custom-high-usecs`: it assigns `tx_glitch_high_usecs` instead of `tx_custom_high_usecs`, which should be reviewed against upstream intent before changing. Long custom pulses are bounded to 10,000,000 usec; glitch pulses to 100 usec.

Test signals: Write/read debugfs `error-inj`, verify clear/rx-clear/tx-clear, opcode-specific and any-opcode matching, once/always/toggle modes, invalid syntax rejection, CEC compliance tests for low-drive/arbitration/NACK/timing errors, and status behavior after pin state-machine consumption.
