# sources/distributed-fs/ceph-client/include/dt-bindings/clock/stratix10-clock.h

## Purpose

`stratix10-clock.h` is a Linux device-tree binding header for Intel/Altera Stratix 10 clock-manager binding IDs. It enumerates Stratix 10 oscillator, boot, PLL, divided PLL, peripheral, EMAC/PTP, GPIO debounce, storage, USB, SPI, NAND, and total-count clock IDs. The file is part of the dt-bindings ABI: DTS and DT overlay sources compile these macro names into integer cells, and the corresponding kernel clock controller interprets those cells at runtime. It contains `86` lines and `65` exported binding macros after the include guard.

## Important APIs, Types, and Functions

This header exports preprocessor constants, not C functions or runtime types. The include guard is `__STRATIX10_CLOCK_H`. Representative early exports are `STRATIX10_OSC1`, `STRATIX10_CB_INTOSC_HS_DIV2_CLK`, `STRATIX10_CB_INTOSC_LS_CLK`, `STRATIX10_F2S_FREE_CLK`, `STRATIX10_L4_SYS_FREE_CLK`, `STRATIX10_MPU_PERIPH_CLK`, `STRATIX10_MPU_L2RAM_CLK`, `STRATIX10_SDMMC_CIU_CLK`; representative trailing exports are `STRATIX10_SDMMC_CLK`, `STRATIX10_PSI_REF_CLK`, `STRATIX10_USB_CLK`, `STRATIX10_SPI_M_CLK`, `STRATIX10_NAND_CLK`, `STRATIX10_NAND_X_CLK`, `STRATIX10_NAND_ECC_CLK`, `STRATIX10_NUM_CLKS`. Numeric analysis shows plain decimal IDs span `0` (`STRATIX10_OSC1`) through `64` (`STRATIX10_NUM_CLKS`). Sentinel or count-style macros are `STRATIX10_NUM_CLKS`. The dominant macro prefixes are `STRATIX10`:65, which reflect the binding namespaces rather than runtime class names.

## Control Flow

There is no executable control flow. The only control behavior is C preprocessor inclusion through the guard, plus any explicit include chaining. The header has no direct include dependencies; its integration dependency is the Intel/Altera Stratix 10 clock/reset driver and device-tree sources that include this binding by path. At build time, DTS files include the header and the device-tree compiler substitutes macro values into `clocks`, `clock-names`, `assigned-clocks`, reset, or related phandle cells. At runtime, the platform clock driver receives those integer IDs through the common clock framework and maps them to fixed factors, gates, muxes, PLLs, dividers, or reset lines implemented elsewhere.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its values become persistent ABI once compiled into DTBs distributed with boards or firmware. Renumbering, deleting, or reusing an existing ID changes the meaning of already-built device trees. Gaps and non-contiguous values should therefore be treated as intentional layout, often mirroring hardware register indices, legacy ABI reservations, or driver array positions. End/count macros such as `STRATIX10_NUM_CLKS` are especially important because drivers often size descriptor tables or validate upper bounds with them.

## Dependencies and Integration Points

The binding integrates with Linux OF/device-tree parsing, the common clock framework, and platform-specific clock controller drivers under the same vendor family. Consumers are board and SoC `.dts`/`.dtsi` files, peripheral drivers that request named clocks, reset-controller users when reset IDs are present, and YAML binding schemas that document acceptable `compatible`, `clocks`, and `resets` shapes. Include dependencies are: none.

## Risks and Maintenance Notes

The main risk is ABI drift: changing numeric assignments breaks DTBs even when the C compiler still succeeds. Other risks are duplicate IDs, stale max/end macros, adding new IDs in the middle of an existing range, losing include chaining for extension headers, or mixing clock and reset namespaces in a way the driver does not implement. Because these are macro-only headers, review should compare identifier order and values against the clock driver tables and the vendor reference manual rather than looking for local algorithmic bugs.

## Test Signals

Useful checks include compiling all affected DTBs, running `make dt_binding_check` for schemas that include this header, building the corresponding clock/reset drivers, and grepping in-tree DTS consumers for representative macros such as `STRATIX10_OSC1`, `STRATIX10_CB_INTOSC_HS_DIV2_CLK`, `STRATIX10_NAND_ECC_CLK`, `STRATIX10_NUM_CLKS`. For changes, confirm old IDs are unchanged, new IDs are appended or intentionally placed in reserved gaps, max/end/count macros still match the driver table size, and extension headers still include their base namespace.
