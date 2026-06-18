## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/defs.h

Purpose: this header centralizes Libertas constants, debug macros, firmware capability bits, buffer sizes, radio/mesh/security constants, and core enums.

Important definitions: debug masks and `lbs_deb_*` macros are active under `CONFIG_LIBERTAS_DEBUG`. Buffer and protocol constants include command buffer counts/sizes, upload sizes, multicast limits, channel/rate limits, EEPROM/TX/RX packet sizing helpers, WOL criteria/rules, mesh IE values, firmware version macros, TX/RX descriptor flags, key lengths/types, band/rate constants, and default FWT values. Enums define SNR/NF selection, power modes, PS states, download states, media state, privacy filter, message type, key type, and WPA key info flags.

Control flow and integration: code throughout Libertas uses these macros to size allocations, parse firmware capabilities, decide power-save transitions, build mesh/crypto commands, and emit debug output. `extern unsigned int lbs_debug`, `lbs_driver_version`, and `lbs_region_code_to_index` are provided by other compilation units.

State and persistence: no storage except extern declarations. Values become compile-time constants or runtime flags in other files.

Risks and tests: changing sizes or enum values affects firmware ABI and buffer safety. Debug macros must compile away cleanly without debug config. Test signals include compile with and without `CONFIG_LIBERTAS_DEBUG`/`MESH`, command buffer stress, WOL option mapping, and firmware version/capability handling.
