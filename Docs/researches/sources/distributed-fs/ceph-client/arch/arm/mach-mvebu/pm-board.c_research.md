<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm-board.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm-board.c

Purpose: Board-level suspend glue for Armada 370/XP/38x/39x. It locates SDRAM and SDRAM controller registers and supplies a board-specific `pm_enter` hook to the generic MVEBU PM layer.

Important APIs/types/functions: `mvebu_armada_pm_enter` programs SDRAM self-refresh and low-power commands; `mvebu_armada_pm_init` parses `marvell,armada-xp-sdram-controller` and memory nodes and calls `mvebu_pm_suspend_init`.

Control flow, state, and persistence: Suspend state is hardware register state: source-command bits, SDRAM windows, and controller timing. The init path derives the first memory resource and maps the SDRAM controller once for later suspend.

Dependencies and integration points: `mvebu_armada_pm_enter` programs SDRAM self-refresh and low-power commands; `mvebu_armada_pm_init` parses `marvell,armada-xp-sdram-controller` and memory nodes and calls `mvebu_pm_suspend_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT memory nodes, SDRAM controller compatible strings, `mvebu_pm_suspend_init`, and low-level suspend code. Risks are incorrect memory-node assumptions, missing register maps, and board PM registration failing silently. Test suspend-to-RAM on each Armada family, resume address correctness, and systems with multiple memory banks.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 144 lines, 3312 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm-board.c -->
