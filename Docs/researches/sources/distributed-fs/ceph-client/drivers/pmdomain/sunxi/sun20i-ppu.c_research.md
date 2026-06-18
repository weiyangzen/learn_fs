<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun20i-ppu.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun20i-ppu.c

## Purpose
Allwinner D1/V853/A523 PPU power-domain driver. It exposes each fixed-size PPU register block as a generic PM domain and drives command/status registers to switch domains on and off.

## Important APIs, Types, And Functions
- `struct sun20i_ppu_desc` lists domain names and count for a compatible.
- `struct sun20i_ppu_pd` wraps genpd and per-domain MMIO base.
- `sun20i_ppu_pd_is_on()` reads `PD_STATUS_STATE`.
- `sun20i_ppu_pd_set_power()` waits for idle, writes `PD_COMMAND_REG`, waits for completion/state, and clears completion.
- `sun20i_ppu_probe()` maps resources, enables clock, deasserts reset, initializes domains, and registers onecell provider.

## Control Flow
Probe matches a descriptor, allocates domain objects and onecell data, maps the controller, enables the clock, deasserts reset, then iterates `num_domains`. Each domain's base is `base + PD_REGS_SIZE * i`, so domain register blocks are contiguous. Genpd is initialized with initial off-state determined from hardware; failures for individual domains warn and continue. Provider registration returns a warning on failure but the driver returns 0.

## State And Persistence Behavior
Runtime state is per-domain genpd plus MMIO base and the onecell provider. Hardware status bits are authoritative. Clock/reset are devm-managed and remain enabled/deasserted for the controller lifetime.

## Dependencies And Integration Points
Depends on platform MMIO, clock, exclusive reset, generic PM domains, bitfield helpers, and DT compatibles `allwinner,sun20i-d1-ppu`, `allwinner,sun8i-v853-ppu`, and `allwinner,sun55i-a523-ppu`. Consumers use onecell indices matching descriptor order.

## Risks
The driver assumes uniform `0x80` register spacing. Poll windows are 1 ms with 100 us intervals; slow transitions may fail. Provider registration failure is only warned, not returned, which can leave a bound driver with no usable provider. Continuing after per-domain init failures can create sparse onecell arrays.

## Test Signals
Boot should deassert reset and register expected domains (`CPU/VE/DSP`, `RISCV/NPU/VE`, or A523 names). Runtime PM should see command/status transitions complete and completion flags clear. DT tests should verify consumer indices match descriptor order.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun20i-ppu.c -->
