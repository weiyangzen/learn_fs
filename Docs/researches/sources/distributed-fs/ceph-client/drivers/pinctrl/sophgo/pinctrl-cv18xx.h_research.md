## `sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv18xx.h`

Purpose: shared type and macro contract for Sophgo CV18xx-family pinctrl drivers. It defines the pin data layout consumed by the common CV18xx implementation and used by generated SoC pin tables.

Important APIs/types/functions: `enum cv1800_pin_io_type` distinguishes 1.8V-only, 1.8V-or-3.3V, audio, and Ethernet pins. `CV1800_PINCONF_AREA_SYS` and `CV1800_PINCONF_AREA_RTC` identify register banks. `struct cv1800_pinmux`, `struct cv1800_pinmux2`, and `struct cv1800_pinconf` carry register offset, area, mux limits, and mux2 parent function information. `struct cv1800_pin` embeds `struct sophgo_pin` plus power domain and register descriptors. `cv1800_pin_io_type()` decodes flags. Macros `CV1800_FUNC_PIN`, `CV1800_GENERAL_PIN`, and `CV1800_GENERATE_PIN_MUX2` are the table-authoring interface used by CV1812H, SG2000, and SG2002.

Control flow: this header has no runtime control flow, but it determines how the shared ops interpret SoC table entries. The `CV1800_PIN_HAVE_MUX2` flag causes validation and mux writes to use a secondary mux register; `CV1800_PIN_IO_TYPE` drives which pinconf operations are supported and which VDDIO conversion maps are chosen.

State and persistence: no runtime state is stored here. The struct layout is part of the persistent compile-time ABI between SoC tables and shared ops; `pinsize` in `struct sophgo_pinctrl_data` must match `sizeof(struct cv1800_pin)` so `bsearch()` can traverse the data safely.

Dependencies and integration: includes Linux bitfield and pinctrl headers plus `pinctrl-sophgo.h`. It exposes `cv1800_pctrl_ops`, `cv1800_pmx_ops`, `cv1800_pconf_ops`, and `cv1800_cfg_ops` for SoC files. Risks include macro misuse, unsorted pin arrays breaking shared `bsearch()`, mismatched mux limits, and stale DT binding IDs. Test signals are build-time coverage of all macro users, probe-time pin lookup success for each binding ID, and DT cases that exercise mux2 and audio/Ethernet unsupported pinconf paths.
