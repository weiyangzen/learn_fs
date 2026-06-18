# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.h

Purpose: declares STMMAC integrated PCS register bits, state structures, conversion helper, exported PCS APIs, and inline AN control helper.

Important APIs and types: register macros define `GMAC_AN_CTRL()` and bits for restart AN, enable AN, external loopback, comma detect, lock-to-reference, and SGMII RAL. `struct stmmac_pcs_info` is the per-core static description: PCS offset, RGSMII offset, RGSMII status mask, and interrupt mask. `struct stmmac_pcs` stores owner `stmmac_priv`, register pointers, masks, embedded `phylink_pcs`, and TBI/RTBI support. `phylink_pcs_to_stmmac_pcs()` converts from phylink object to STMMAC object. `dwmac_ctrl_ane()` updates the AN control register.

Control flow: DWMAC core files provide `stmmac_pcs_info` to `stmmac_integrated_pcs_init()`. Phylink uses the embedded PCS, and callbacks use this header’s conversion and `dwmac_ctrl_ane()` helper. Interrupt paths call the declared `stmmac_integrated_pcs_irq()`.

State and persistence: no header-owned runtime state. It defines the devm-allocated PCS state kept at `priv->integrated_pcs`.

Dependencies and integration: includes phylink, slab, IO, and `common.h`; consumed by `stmmac_pcs.c`, DWMAC core files, and MAC configuration code.

Risks and test signals: register bit definitions are hardware ABI. `dwmac_ctrl_ane()` only clears AN enable when disabling and optionally leaves SGMII RAL set, so hardware sticky behavior matters. Build and runtime test through PCS initialization, phylink AN, and MAC-to-MAC SGMII cases.
