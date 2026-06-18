# sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-kaanapali.c

## Purpose
This Kaanapali TCSR driver provides reference-clock gates for PCIe 0, UFS, USB2, and USB3.

## Important APIs, types, and functions
- Four `clk_branch` descriptors target offsets 0x15044, 0x1504c, 0x15054, and 0x1505c.
- USB/UFS clocks declare `DT_BI_TCXO_PAD` parent data; the PCIe branch has no explicit parent data despite the enum.
- `tcsr_cc_kaanapali_clocks[]`, `tcsr_cc_kaanapali_regmap_config`, and `tcsr_cc_kaanapali_desc` provide qcom CC metadata.
- `tcsr_cc_kaanapali_probe()` calls `qcom_cc_probe()`.

## Control flow
The subsys-init platform driver binds `"qcom,kaanapali-tcsr"`, maps the register block up to 0x3d000, and registers four branch clocks. Consumer enable requests set bit 0 at each configured offset.

## State and persistence behavior
State is persistent only in TCSR reference-clock enable registers. There is no runtime PM, cached state, or custom recovery path.

## Dependencies and integration points
The file integrates with qcom common CC, CCF branch ops, regmap, platform bus, and clock binding IDs from `dt-bindings/clock/qcom,sm8750-tcsr.h`. It provides clkrefs to PCIe, UFS, and USB PHY/controller nodes.

## Risks
It reuses the SM8750 TCSR binding include while matching Kaanapali, so binding compatibility must be intentional and kept aligned. The PCIe branch's missing parent data may be fine for a gate-only clock but differs from the other clkrefs. Large max register coverage means wrong offsets could still map without an immediate range failure.

## Test signals
Probe should expose four clock IDs. PCIe/UFS/USB PHY init on Kaanapali hardware should request and enable the clocks. Register readback should confirm bit 0 at the four high offsets.
