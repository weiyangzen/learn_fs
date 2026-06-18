# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-qserdes-lalb-v8.h

Purpose: Provides a large QSERDES v8 LALB register map for a combined lane analog/lane-B style block. It spans BIST/PRBS, reset, TX0/TX1 drive and emphasis, restrim, interface select, per-rate RX mode settings, DCC, CDR/VCO/KVCO/KP calibration, IVCM/IDAC/signal detect, receiver/equalizer, CTLE/VGA/VTH/DFE, IQ tune, BLW/IVTH, extensive status/debug, and digital backup registers.

Important APIs/types/functions: Exports about 630 `QSERDES_V8_LALB_*` macros. The map includes paired TX0/TX1 controls, rate0-rate4 RX/CDR fields, calibration controls, readback/status registers, and backup/RO buses. No functions or types are defined.

Control flow: No code executes. The umbrella QMP header exposes the constants to v8 tables; common QMP write helpers perform actual register programming.

State and persistence: The header is immutable. Runtime state is entirely in lane hardware and calibration/readback registers after table writes or hardware calibration.

Dependencies and integration points: Included by `phy-qcom-qmp.h`; intended for newest v8 PHY descriptors that need LALB offsets beyond generic TX/RX maps.

Risks: This is a high-risk map because it is dense, rate-indexed, and contains many similarly named control/status registers. Offset drift can corrupt calibration or debug readbacks without compiler errors.

Test signals: Build of v8 LALB users, lane bring-up, BIST/PRBS when available, high-rate link training, calibration status reads, equalizer margin, and suspend/resume reinit.
