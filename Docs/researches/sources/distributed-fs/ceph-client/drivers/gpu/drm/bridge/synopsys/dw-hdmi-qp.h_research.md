# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-qp.h

Purpose: defines the register map and bit fields for the DesignWare HDMI QP transmitter used by `dw-hdmi-qp.c` and platform wrappers.

Important APIs/types/functions: the header covers main-unit identification/config/reset/timer/CMU, I2CM/DDC, SCDC/FRL training, video interface and packing, audio interface and audio packetizer, frame composer, video monitor, HDCP2/HDCP1.4, scrambler/link config, TMDS/FRL packet scheduler, general packet content registers, EMP packetizer, CEC registers, eARC RX CMDC/DMAC registers, and main/AVP/CEC/eARC interrupt registers. It provides masks such as `I2CM_WR_MASK`, `PKTSCHED_*_TX_EN`, `AUDPKT_*`, `CEC_STAT_*`, and interrupt clear/mask bits.

Control flow: no executable flow; C code uses these constants with regmap read/write/update operations to reset blocks, perform I2C transfers, program infoframes/audio, handle CEC, and manage interrupts.

State and persistence: no driver state. The definitions describe volatile hardware register fields, many of which preserve state until reset or explicit write.

Dependencies and integration: includes `linux/bits.h` for `BIT`/`GENMASK`. It is tightly coupled to the QP hardware programming model and the offsets used by the bridge library. Platform code should use exported library APIs rather than directly reprogramming these registers unless implementing PHY-specific setup.

Risks: register definitions are low-level and largely untyped; incorrect masks or offsets can silently corrupt unrelated hardware blocks. Several blocks such as FRL/eARC/HDCP are defined even when the current C implementation only uses a subset, so future code must validate hardware version support. Comments contain minor typos but not behavioral issues.

Test signals: compile use by `dw-hdmi-qp.c`, register access smoke tests through probe/init, DDC/audio/infoframe/CEC paths that exercise the used masks, and review against Synopsys/Rockchip register documentation when enabling currently unused FRL/eARC/HDCP fields.
