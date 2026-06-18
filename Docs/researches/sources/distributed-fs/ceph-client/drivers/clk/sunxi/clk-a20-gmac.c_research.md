# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a20-gmac.c

## Purpose
This legacy provider models the A20/A31 GMAC clock module as a two-parent mux plus gate composite for MAC/PHY transmit clock selection.

## Important APIs, Types, And Functions
Important data includes `sun7i_a20_gmac_mux_table`, gate bit `SUN7I_A20_GMAC_GPIT`, mux mask `SUN7I_A20_GMAC_MASK`, and `sun7i_a20_gmac_clk_setup()` declared for `allwinner,sun7i-a20-gmac-clk`.

## Control Flow
Early init reads the output name, allocates mux/gate, requires exactly two parents, maps the register, registers a composite, and adds a simple provider.

## State And Persistence
State is the mux selector and PHY output gate bit. The GMAC driver is expected to select parent/rate according to MII/GMII/RGMII mode.

## Dependencies And Integration Points
It depends on CCF composite helpers, OF parent data, and GMAC DT wiring. It integrates directly with the sunxi GMAC Ethernet driver and external PHY clocking.

## Risks
Selecting the wrong parent can allow RX but prevent TX traffic. The optional external 125 MHz path is intentionally not fully modeled for simplicity.

## Test Signals
Test with Ethernet link-up and traffic in MII/GMII/RGMII modes, parent selection changes from the GMAC driver, and clk-summary parent/gate state.
