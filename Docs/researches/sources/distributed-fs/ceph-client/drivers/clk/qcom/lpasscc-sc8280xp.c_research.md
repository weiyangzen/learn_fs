# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc8280xp.c

## Purpose

This SC8280XP LPASSCC driver is a reset-controller-only provider for LPASS audio and LPASS TCSR register blocks. It exposes reset bits for SoundWire RX/WSA/WSA2 and TX clock-gate control registers.

## Important APIs, types, and functions

The file defines two reset maps, two regmap configs, two `qcom_cc_desc` reset descriptors, an OF match table carrying descriptor match data, and `lpasscc_sc8280xp_probe()`. Audio CSR resets are at offsets `0xa0`, `0xb0`, and `0xd8` bit 1. TCSR reset is at `0xc010` bit 1.

## Control flow, state, and persistence

Probe retrieves the matched descriptor with `of_device_get_match_data()` and calls `qcom_cc_probe_by_index(pdev, 0, desc)`. The common helper maps resource index 0 and registers reset controls. Persistent state is the reset bit state in hardware and the reset-controller registration.

## Dependencies and integration points

It depends on `qcom,sc8280xp-lpasscc.h`, Qualcomm common clock/reset helpers, and compatible strings `"qcom,sc8280xp-lpassaudiocc"` and `"qcom,sc8280xp-lpasscc"`. Consumers are LPASS audio and SoundWire controller drivers.

## Risks and test signals

Risks are wrong compatible-to-register-bank mapping, wrong bit polarity/delay assumptions, and insufficient register range for future resets. Test by probing both compatibles, asserting/deasserting each SoundWire reset, verifying SoundWire RX/TX/WSA bus recovery, and confirming no clocks are expected from this provider.
