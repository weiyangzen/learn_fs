# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-reg.h

Purpose: provides the Medusa video decoder/encoder register address map used by cx25821 I2C register programming.

Important APIs and constants: defines chip configuration registers (`CHIP_CTRL`, `AFE_*`, `DENC_AB_CTRL`, `BYP_AB_CTRL`, `MON_A_CTRL`, `PIN_OE_CTRL`), DENC A/B register blocks, decoder A-H blocks with 0x200 spacing, scaler/timing/procamp registers, comb-filter controls, version/reset registers, and byte-oriented aliases such as `VDEC_A_BRITE_CTRL`, `VDEC_A_CNTRST_CTRL`, `VDEC_A_USAT_CTRL`, `VDEC_A_VSAT_CTRL`, and `VDEC_A_HUE_CTRL`.

Control flow: `cx25821-medusa-video.c` combines base register constants with `0x200 * decoder` or `0x100 * encoder` offsets to initialize all decoders/encoders, set standard-specific timing, set resolution, enable blue-field output, and update brightness/contrast/hue/saturation.

State and persistence: no software state. The constants identify persistent hardware register addresses reachable through the cx25821 I2C adapter.

Dependencies and integration points: included by `cx25821.h`, making Medusa register names globally visible across the driver. It pairs with `cx25821-i2c.c` for actual access and `cx25821-medusa-video.c` for programming policy.

Risks: this is a manually maintained register map; a single incorrect address can program the wrong decoder field. `VDEC_H_INT_STAT_MASK` is `0x1E1E` while the pattern suggests `0x1E10`, which may be a hardware-specific exception or typo. Byte aliases for procamp controls rely on the I2C helper and hardware accepting byte-offset-style addresses even though the helper reads/writes four bytes.

Test signals: hardware register readback, video standard initialization on all decoder channels, procamp controls affecting the selected channel only, and regression checks for decoder-H interrupt/status behavior.
