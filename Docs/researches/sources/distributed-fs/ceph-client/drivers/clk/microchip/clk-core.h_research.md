# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.h

Purpose: This header defines the shared descriptor contract for PIC32 clock implementations and SoC-specific PIC32 clock drivers.

Important APIs, types, and functions: It defines `struct pic32_clk_common`, `pic32_sys_pll_data`, `pic32_sys_clk_data`, `pic32_ref_osc_data`, `pic32_periph_clk_data`, and `pic32_sec_osc_data`. It declares ops tables for PBCLK, SCLK, SPLL, reference oscillator, and secondary oscillator, plus registration helpers for each clock type.

Control flow: The header is declarative. SoC files fill these descriptor structures with init data, register offsets, parent maps, masks, and rates, then call the registration functions in `clk-core.c`.

State and persistence behavior: Descriptor fields are static SoC metadata. `pic32_clk_common` carries shared runtime state: device pointer, MMIO base, and spinlock for protected register updates.

Dependencies and integration points: It includes `linux/clk-provider.h` and is shared by `clk-core.c` and `clk-pic32mzda.c`. It abstracts common PIC32 clock behavior away from SoC-specific clock lists.

Risks and edge cases: Offsets are added to the common MMIO base, so descriptors must use the correct register map. Parent maps must match hardware mux values, not just CCF parent order. Test signals include compile coverage of all constructors and runtime verification that PIC32MZDA descriptors register and expose expected parents/rates.
