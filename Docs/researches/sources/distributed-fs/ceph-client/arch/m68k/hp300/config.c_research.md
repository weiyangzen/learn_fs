# sources/distributed-fs/ceph-client/arch/m68k/hp300/config.c

Purpose: provides HP300-specific m68k machine initialization. It parses bootinfo, identifies the HP9000 model, installs machine callback hooks, configures RTC access, exposes LED state, and initializes serial console setup.

Important APIs/types/functions: exported globals are `hp300_model`, `hp300_uart_scode`, and `hp300_ledstate` (`EXPORT_SYMBOL`). Key functions are `hp300_parse_bootinfo`, `hp300_get_model`, `hp300_hwclk`, and `config_hp300`. Static RTC helpers `hp300_rtc_read` and `hp300_rtc_write` access BCD clock registers via fixed IO addresses.

Control flow: bootinfo parsing stores model and UART select code. `config_hp300` assigns `mach_sched_init`, `mach_init_IRQ`, `mach_get_model`, `mach_hwclk`, `mach_reset`, and optional heartbeat callbacks, validates the model range excluding HP_350, appends a string suffix to `HP9000/`, prints the detected model, and calls `hp300_setup_serial_console`. RTC read/write helpers busy-wait on command/status bits with interrupts disabled; `hp300_hwclk` converts between `struct rtc_time` and split BCD registers, including year rollover handling.

State and persistence: runtime state includes model ID/name, UART select code, and LED state. Persistent hardware state is the RTC, read and written through `hp300_hwclk`; the code writes 24-hour mode on hour updates.

Dependencies/integration: uses Linux init/module/console/RTC headers, m68k bootinfo records, machine-dependency callback globals from `machdep.h`, HP300 hardware IDs, fixed HP300 RTC IO addresses, `hp300_sched_init` from `time.c`, and `hp300_reset` from `reboot.S`.

Risks: RTC helpers spin indefinitely if hardware status never changes, and they disable interrupts while polling. Model-name array indexing uses `hp300_model-HP_320` after range checks; new enum values must preserve table layout. Unknown models panic during boot.

Test signals: bootinfo parse for model/UART/address/unknown tags, supported and unsupported model detection, serial console setup with UART scode, RTC read/write BCD conversion including years `00-69`, heartbeat callback assignment under `CONFIG_HEARTBEAT`, and interrupt restoration after RTC polling.
