## sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada720_kbd.c

Purpose: HP Jornada 710/720/728 keyboard driver. It drains keyboard scancodes from the Jornada SSP interface on a falling-edge platform IRQ.

Important APIs/types/functions: `struct jornadakbd` holds the keymap and input device. `jornada720_kbd_interrupt()` wraps the SSP transaction with `jornada_ssp_start()`/`jornada_ssp_end()`, sends `GETSCANKEYCODE`, reads a pending count, and reports each queued byte.

Control flow: probe gets IRQ, allocates driver/input state, copies `jornada_std_keymap`, sets input bits, requests a falling-edge IRQ, and registers input. On interrupt, the handler reads the number of waiting keycodes and then consumes each byte; low 7 bits are scancode and bit 7 is release, so `!(kbd_data & 0x80)` is reported as pressed.

State/dependencies/integration: state is only the keymap and input pointer. It depends on machine-specific `mach/jornada720.h` SSP helpers, platform IRQ resources, and input core.

Risks and test signals: SSP timeout handling logs but does not otherwise recover beyond bus flushing by the helper path. Keymap index trust requires the firmware/scanner to emit values below 128. Test queued multi-key packets, release-bit polarity, falling IRQ configuration, SSP failure path, and input registration cleanup.
