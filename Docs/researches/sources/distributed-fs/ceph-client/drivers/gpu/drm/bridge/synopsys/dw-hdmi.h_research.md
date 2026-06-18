# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.h

Purpose: private register and bitfield definition header for the DesignWare HDMI bridge implementation. It maps the controller register space, interrupt status/mute registers, frame composer, video packetizer, PHY, audio, DMA, main controller, CSC, HDCP, DDC I2C, and HDMI 3D TX PHY fields used by `dw-hdmi.c` and sibling audio/CEC support.

Important APIs and types: this file defines register offsets such as `HDMI_FC_INVIDCONF`, `HDMI_VP_CONF`, `HDMI_PHY_CONF0`, `HDMI_AUD_N1`, `HDMI_MC_CLKDIS`, `HDMI_CSC_CFG`, and `HDMI_I2CM_OPERATION`, plus an anonymous enum of masks, shifts, and field values. It also defines the HDMI 3D TX PHY register addresses and field bits used for PHY I2C programming. There are no functions or storage; the header is a hardware contract for register access helpers in the C files.

Control flow: no executable control flow exists here. Runtime code reads these constants to build ordered programming sequences: IRQ initialization masks and clears `HDMI_IH_*`; DDC uses `HDMI_I2CM_*`; video setup uses frame-composer and packetizer fields; PHY bring-up uses `HDMI_PHY_*` and `HDMI_3D_TX_PHY_*`; audio setup uses `HDMI_AUD_*`, `HDMI_FC_AUD*`, and AHB DMA bits; SCDC/scrambling setup uses `HDMI_FC_SCRAMBLER_CTRL` and `HDMI_MC_SWRSTZ`.

State and persistence: the header itself holds no state. The constants describe hardware state persisted in MMIO registers, accessed through regmap with possible register shifting in `dw-hdmi.c`.

Dependencies and integration: included by the Synopsys DW HDMI implementation and related bridge components. The naming and masks must stay consistent with the DesignWare HDMI IP manual and the register access style in `hdmi_writeb()`, `hdmi_readb()`, and `hdmi_modb()`.

Risks: incorrect masks or offsets can silently program unrelated hardware fields. Some fields have inverted or historical names, such as `HDMI_A_HDCPCFG1_ENCRYPTIONDISABLE_DISABLE`, and some comments note IP-specific behavior such as the CTS manual bit. Register offsets are byte offsets and are shifted by `reg_shift` for 32-bit register windows, so duplicate shifting in callers would break access. The header is broad and private, so unused-looking definitions may still support optional audio/CEC or platform PHY paths.

Test signals: full build of DW HDMI, DW HDMI audio, and CEC objects; runtime smoke tests covering HDMI mode set, DDC, audio, CEC, SCDC, and PHY configuration; static review when changing register definitions to compare every mask/shift against the IP documentation and current call sites.
