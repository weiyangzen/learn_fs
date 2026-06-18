# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.c

Purpose: implements common operations for the Marvell switch Global 1 register block: reset/readiness, PPU control, switch MAC, priority maps, monitor/CPU ports, RMU disabling, device numbering, and statistics capture/read/clear.

Important APIs/types/functions: `mv88e6xxx_g1_read/write/wait_bit/wait_mask()` are the base accessors. Chip-family operations include `mv88e6185_g1_reset()`, `mv88e6250_g1_reset()`, `mv88e6352_g1_reset()`, EEPROM-done waits, PPU enable/disable, max-frame setup, IP/IEEE priority map reset, CPU/PTP CPU destination selection, management reserved multicast programming, RMU disable, statistics snapshot/read/clear, and device-number programming.

Control flow: most functions are read-modify-write helpers around Global1 registers. Reset paths set reset bits, wait for InitReady, and optionally wait for PPU polling. Statistics capture writes a busy command, waits for completion, then reads two counter registers.

State and persistence: settings live in switch hardware registers and are reset by switch reset or EEPROM reload. Counter snapshots are transient hardware latches. The code does not maintain private software state except through hardware side effects.

Dependencies/integration: used through per-chip ops tables in `chip.c`, and relies on `global1.h` bit definitions, core MDIO accessors, and caller-side `mv88e6xxx_reg_lock()` serialization.

Risks: EEPROM done status clears on read, so polling must be sequenced immediately after reset/reload. Family-specific bit layouts make wrong ops-table selection harmful. `mv88e6xxx_g1_stats_read()` silently returns zero on errors.

Test signals: reset should reach InitReady on supported chips; PPU enable/disable should transition status; ethtool stats should be stable after snapshot; CPU/monitor port setup should deliver management/PTP frames to the CPU port.
