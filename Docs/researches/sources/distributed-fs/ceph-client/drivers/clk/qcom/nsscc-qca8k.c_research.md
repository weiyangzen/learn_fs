# sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-qca8k.c

## Purpose
This driver exposes the QCA8084/QCA8K NSS clock controller over an MDIO-attached device. It registers a large set of switch-core, APB/AHB, TLMM, MDIO, SERDES, GEPHY, and MAC0-MAC5 RX/TX clocks plus reset lines through the Qualcomm common clock framework. Unlike normal memory-mapped qcom clock controllers, its register access is implemented through Clause 22 MDIO transactions.

## Important APIs, types, and functions
- `nss_cc_qca8k_clocks[]` maps dt-binding clock IDs to `struct clk_regmap` instances: RCGs (`clk_rcg2`), dividers (`clk_regmap_div`), muxes (`clk_regmap_mux`), and branches (`clk_branch`).
- `nss_cc_qca8k_resets[]` maps reset IDs to register/bit or bitmask entries consumed by `qcom_reset_ops` through `qcom_cc_really_probe()`.
- `convert_reg_to_mii_addr()` splits an NSSCC register address into MDIO register, PHY address, and page fields using the QCA8K masks/prefix constants.
- `qca8k_regmap_read()`, `qca8k_regmap_write()`, and `qca8k_regmap_update_bits()` are the custom regmap bus callbacks. They add `QCA8K_CLK_REG_BASE`, select the MDIO page, and perform 32-bit access as two 16-bit MDIO accesses while holding `bus->mdio_lock`.
- `nss_cc_qca8k_clock_enable_and_reset()` enables the reference clock and optionally toggles the `"reset"` GPIO after a 100 ms high pulse.
- `nss_cc_qca8k_probe()` initializes the custom regmap with `devm_regmap_init()` and calls `qcom_cc_really_probe()`.

## Control flow
The MDIO core matches `"qcom,qca8084-nsscc"` and invokes `nss_cc_qca8k_probe()`. Probe first enables the unnamed input clock and releases optional reset GPIO, then creates a regmap whose read/write/update callbacks translate qcom CC register operations into MDIO page select plus lower/upper 16-bit transactions. The common qcom CC registration then publishes clocks and resets to consumers. Runtime clock operations go through standard CCF branch/RCG/divider/mux ops, but all register traffic is serialized by the MDIO bus lock.

## State and persistence behavior
Persistent hardware state is the NSSCC register block behind MDIO: clock source selectors, dividers, branch enables, reset bits, and page-selected MDIO access. The driver keeps no dynamic software state beyond static descriptors and devres-managed clock/regmap/GPIO handles. Reset operations persist in hardware until deasserted. `disable_locking = true` delegates serialization to explicit `mdio_lock` critical sections rather than regmap's internal lock.

## Dependencies and integration points
The file integrates with the MDIO driver model (`mdio_module_driver`), CCF, qcom common CC helpers, qcom reset support, device-tree clock/reset bindings, optional GPIO reset, and the parent MDIO bus. Consumers reference the clocks/resets by `qcom,qca8k-nsscc` binding IDs. Parent sources include UNIPHY/SERDES and fixed external clocks represented through `clk_parent_data`.

## Risks
MDIO access is fragile because every 32-bit operation depends on correct page selection and two 16-bit transfers; a failed write logs but `qca8k_mii_write()` itself returns void, so write failures can be partially hidden after page selection succeeds. The custom update-bits path performs read/modify/write under the MDIO lock, which is correct for bus serialization but cannot prevent hardware-side concurrent changes. Register address masks and dt-binding array indices must remain synchronized with hardware documentation. The reset GPIO pulse depends on the reference clock being enabled first.

## Test signals
Probe success should show all NSSCC clocks and reset controls registered for a matching MDIO node. Useful validation includes boot logs without MDIO read/write/page errors, `clk_summary` visibility for MAC/SERDES/AHB clocks, successful clock rate changes for RCG/divider-controlled MAC paths, reset-controller assertions for GEPHY/global/XPCS lines, and network bring-up across all switch ports. Fault tests should cover missing reference clock, absent optional reset GPIO, and MDIO transaction failures.
