# sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-pdc.c

Purpose: Qualcomm PDC global reset controller for SDM845 and SC7280, exposing PDC synchronous reset bits through the reset-controller framework.

Important APIs/types/functions: `qcom_pdc_reset_map`, `qcom_pdc_reset_desc`, and `qcom_pdc_reset_data` describe binding IDs, per-SoC register offsets, and the controller instance. `qcom_pdc_control_assert()` and `qcom_pdc_control_deassert()` use `regmap_update_bits()` against the selected PDC sync-reset register. `qcom_pdc_reset_probe()` maps MMIO, initializes a 32-bit regmap, gets OF match data, and registers `qcom_pdc_reset_ops`.

Control flow: compatible matching selects the descriptor, probe maps the single resource and registers `nr_resets` equal to the SoC reset table length. Consumers call reset core operations, which translate IDs into table bits and set or clear the matching register bit.

State and persistence: no persisted software state beyond the regmap and descriptor pointer; hardware reset bits hold current state. Device-managed allocation and registration own cleanup.

Dependencies and integration: depends on platform device probing, OF compatible strings, `dt-bindings/reset/qcom,sdm845-pdc.h`, MMIO regmap, and reset-controller consumers in device tree.

Risks and test signals: operations trust the reset core to keep `idx < nr_resets`; sparse binding tables would make holes unsafe. Test with SDM845 and SC7280 DT bindings, invalid IDs through reset-core tests, regmap failure injection, and checking that assert/deassert touches only the expected offset and bit.
