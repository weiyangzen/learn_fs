# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_shared.c

## Purpose
`mpc512x_shared.c` contains common MPC512x SoC support: restart mapping, DIU framebuffer handoff, IPIC setup, platform-device population, PSC FIFO sizing, chip-select configuration, and board-shared init sequencing.

## Important APIs, Types, and Functions
`mpc512x_restart()` resets through the reset module. `mpc512x_init_early()` maps restart support and preserves pre-initialized DIU state when enabled. `mpc512x_init()` initializes clocks, populates OF devices, and configures PSC FIFO slices. `mpc512x_setup_arch()` installs DIU callbacks. `mpc512x_init_IRQ()` initializes IPIC and default priorities. `mpc512x_select_psc_compat()` chooses PSC compatible strings, and exported `mpc512x_cs_config()` writes LocalPlus chip-select config.

## Control Flow, State, and Persistence
Persistent boot state includes `reset_module_base`, `diu_shared_fb`, and a cached LPC mapping in `mpc512x_cs_config()`. DIU preservation copies area descriptor/gamma data, reserves the existing framebuffer with memblock, and releases those pages when fbdev opens.

## Dependencies and Integration Points
It integrates the common clock provider, OF platform bus probing, FSL DIU framebuffer hooks, memblock, IPIC, PSC FIFO hardware layout, and LocalPlus Bus clients.

## Risks and Test Signals
Risks include bootloader-dependent DIU handoff, permanent mappings, FIFO space exhaustion across PSC nodes, integer/pointer casts in `FIFOC`, missing reset nodes, and static LPC mapping lifetime. Test signals include display continuity during boot, memblock release on fbdev open, PSC serial/FIFO operation, LocalPlus chip-select writes, OF device population, and restart.
