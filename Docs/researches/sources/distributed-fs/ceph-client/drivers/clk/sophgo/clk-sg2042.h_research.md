# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042.h

## Purpose
This header defines the common SG2042 clock-provider data container shared by the SG2042 PLL, clock-generator, and RP-gate drivers.

## Important APIs, Types, And Functions
`struct sg2042_clk_data` holds an MMIO base pointer and a trailing `clk_hw_onecell_data` used for OF provider registration. The `onecell_data` member must remain last when allocated with `struct_size()`.

## Control Flow
No executable flow exists. Each SG2042 driver allocates this structure, maps its resource into `iobase`, fills `onecell_data.hws[]`, and passes it to `devm_of_clk_add_hw_provider()`.

## State And Persistence
The structure is devm-managed per platform device. It owns the provider's hardware pointer array and base address for register access. Hardware state lives in the mapped controller registers.

## Dependencies And Integration Points
The header depends on CCF and MMIO types. It is included by `clk-sg2042-pll.c`, `clk-sg2042-clkgen.c`, and `clk-sg2042-rpgate.c`.

## Risks
All users rely on flexible-array-style allocation through `struct_size()`. Mis-sizing `num_clks` or using a binding ID outside the allocation corrupts the provider table. The shared type does not encode which register block is mapped, so each driver must pass the correct resource.

## Test Signals
Compile all SG2042 drivers and verify no allocation warnings. Runtime checks should confirm each provider's `onecell_data.num` covers its highest dt-binding ID and that all expected IDs return valid or intentional missing clocks.
