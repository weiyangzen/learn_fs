## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/board.c

Purpose: detects the specific BCM47XX router board model from NVRAM variables and exposes the detected board enum and name.

Important APIs and functions: `bcm47xx_board_detect()` initializes detection once. `bcm47xx_board_get()` and `bcm47xx_board_get_name()` are exported. `bcm47xx_board_get_nvram()` checks multiple key patterns and returns a `bcm47xx_board_type`. Static tables map NVRAM keys such as `model_name`, `hardware_version`, `productid`, `ModelId`, `melco_id`/`buf1falo_id`, `boot_hw_model` plus `boot_hw_ver`, `board_id`, `boardtype`/`boardnum`/`boardrev`, and ad hoc key/value pairs to board enums and readable names.

Control flow: detection first avoids rerun if already set. It probes `boardtype` to see whether NVRAM is available; `-ENXIO` means too early and returns without setting a final board. Otherwise it scans the NVRAM matching tables in priority order, defaults to unknown, copies the enum and name into static storage, and later callers retrieve them.

State and persistence: static `bcm47xx_board` stores detected board and name for this boot. NVRAM is read only; no persistent data is modified.

Dependencies and integration: depends on `bcm47xx_nvram_getenv()`, board enum definitions, string helpers, and exported symbol consumers such as buttons/LEDs/setup code.

Risks: matching priority matters and can misidentify boards with overlapping NVRAM strings. One hardware-version plus boardnum condition uses `!strstarts(buf1, e2->value1) && !strcmp(...)`, which appears counterintuitive because most other matches require positive string matching. Buffer sizes are small but bounded. Unknown boards lose model-specific buttons/LEDs.

Test signals: boot logs/consumers should report the expected board name. Validate representative NVRAM sets for each table, unknown fallback, and retry behavior when NVRAM initially returns `-ENXIO`.
