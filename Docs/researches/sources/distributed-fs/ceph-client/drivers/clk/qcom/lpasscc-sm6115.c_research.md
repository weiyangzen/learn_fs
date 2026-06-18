# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sm6115.c

## Purpose

This SM6115 LPASSCC driver is a small reset-controller provider for LPASS audio CSR and TCSR blocks. It exposes SoundWire RX and TX configuration reset controls and no clocks.

## Important APIs, types, and functions

The driver defines `lpass_audiocc_sm6115_resets`, `lpasscc_sm6115_resets`, corresponding regmap configs, reset descriptors, match data for `"qcom,sm6115-lpassaudiocc"` and `"qcom,sm6115-lpasscc"`, and `lpasscc_sm6115_probe()`. Both reset map entries target bit 1 and include a 500 microsecond delay.

## Control flow, state, and persistence

Probe selects the descriptor from OF match data and calls `qcom_cc_probe_by_index(pdev, 0, desc)`. The only runtime state is the reset-controller registration and the reset bit state in the selected register bank.

## Dependencies and integration points

Dependencies are SM6115 LPASSCC binding IDs, Qualcomm reset/common helpers, and DT resource index 0. SoundWire and LPASS audio drivers consume the exported reset controls.

## Risks and test signals

Risks include reset pulse timing, wrong CSR/TCSR bank selection, and bit-offset mistakes. Test both compatibles, assert/deassert RX and TX SoundWire resets, verify the 500 microsecond reset delay is sufficient on hardware, and confirm audio/SoundWire recovery after reset.
