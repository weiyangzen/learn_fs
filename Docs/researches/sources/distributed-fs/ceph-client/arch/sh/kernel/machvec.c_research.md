# sources/distributed-fs/ceph-client/arch/sh/kernel/machvec.c

Purpose: selects and finalizes the SH machine vector used for board-specific operations.

Important APIs and control flow: `get_mv_byname()` scans the linker-provided `__machvec_start` to `__machvec_end` section. `early_parse_mv()` parses `sh_mv=`, copies the named vector into global `sh_mv`, or panics if unknown. `sh_mv_setup()` selects the first vector when none was specified, validates section alignment, prints the booting vector, and fills missing hooks such as `irq_demux`, `mode_pins`, and `mem_init` with generic implementations.

State, dependencies, and risks: global `sh_mv` is the central persistent state and is exported. Dependencies include linker sections, early command-line parsing, generic machine-vector functions, and setup/IRQ/memory users. Risks include malformed machvec sections, wrong command-line name, missing hooks hidden by generic fallback, and early lifetime of `__initmv` data. Test signals are boot logs showing expected machvec, command-line override, board IRQ/mode-pin behavior, and panic on bad vector names.
