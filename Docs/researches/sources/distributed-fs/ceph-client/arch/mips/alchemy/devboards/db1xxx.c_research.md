## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1xxx.c

Purpose: central dispatcher for Alchemy DB/PB1xxx development boards. It maps CPU type and BCSR board ID to the correct per-board setup, PCI setup, and device registration functions, and supplies the machine name string.

Important APIs and functions: `board_setup()` is the early board initialization hook. `get_system_type()` returns the string from `board_type_str()`. `db1xxx_arch_init()` is an `arch_initcall()` that registers PCI for DB/PB1500 and DB/PB1550 variants. `db1xxx_dev_init()` is a `device_initcall()` that sets the MIPS machine name and calls the correct per-board device setup function.

Control flow: `board_setup()` switches on `alchemy_get_cputype()` and calls `db1000_board_setup()`, `db1550_board_setup()`, `db1200_board_setup()`, or `db1300_board_setup()`. Any failure panics because the board support package cannot safely continue without BCSR and board identification. Later initcalls read `BCSR_WHOAMI` and branch by board ID for PCI and platform-device registration.

State and persistence: this file owns no persistent state. It relies on BCSR state initialized by per-board setup and sets global kernel machine name through `mips_set_machine_name()`.

Dependencies and integration: depends on every per-board C file, BCSR IDs, Alchemy CPU detection, PROM declarations, and MIPS initcall ordering. It is the glue that makes object files listed in the Makefile participate in architecture boot.

Risks: unsupported or misdetected CPU/board IDs panic or skip device setup. `board_type_str()` depends on BCSR being initialized before `get_system_type()` is used. PCI setup must remain at `arch_initcall()` because MIPS PCI scanning happens during `subsys_initcall()`.

Test signals: boot should print the board name and set the machine name. PCI should appear only on supported DB/PB1500/1550 boards. Device init should call exactly one board-specific setup path, visible through registered platform devices.
