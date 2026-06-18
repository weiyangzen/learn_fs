# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx-reg.h

## Purpose

`cx231xx-reg.h` is the symbolic hardware register map for Conexant Cx23100/Cx23101/Cx23102 USB video capture devices. It contains no executable code; its role is to centralize register addresses, bit masks, video stream marker constants, and enumerated numeric values used by the rest of the `cx231xx` driver. The register definitions cover VBI and active video SAV/EAV codes, host/chip control, AFE controls, analog video decoder/scaler/VBI slicer, audio demodulation, I2S/AC97 routing, DirectIF-related blocks, and video format/input/output constants.

## Important APIs, Types, and Constants

The most integration-sensitive constants are the SAV/EAV byte codes at the top of the file. `SAV_ACTIVE_VIDEO_FIELD1`, `SAV_ACTIVE_VIDEO_FIELD2`, `SAV_VBI_FIELD1`, and `SAV_VBI_FIELD2` are consumed directly by `cx231xx-video.c` and `cx231xx-vbi.c` to detect field boundaries and decide where bytes belong in vb2 buffers.

Register address groups include `HOST_REG*`, `CHIP_CTRL`, `AFE_CTRL`, `PIN_CTRL`, `AUD_IO_CTRL`, `MODE_CTRL`, `OUT_CTRL*`, `GEN_STAT`, `INT_STAT_MASK`, luma/chroma/scaler registers, VBI configuration registers, DFE/PLL/comb/crush/reset controls, firmware download registers such as `DL_CTL`, and audio-demodulator registers under the `0x800` range. Each register is paired with `FLD_*` bit masks used by helper functions such as `cx231xx_reg_mask_write()` and direct I2C register accessors declared in `cx231xx.h`.

The bottom of the file defines semantic constants such as `VID_FMT_NTSC_M`, `VID_FMT_PAL_BDGHI`, `INPUT_MODE_CVBS_0`, `INPUT_MODE_YC_1`, luma/UV filter values, output modes, audio source selectors, and PLL phase increments. These values allow higher-level driver code to express board and standard setup without scattering magic numbers.

## Control Flow

There is no control flow in this header. The functional control flow appears in implementation files that include it. The header shapes control flow indirectly by giving parser functions stable marker values and by giving hardware programming paths stable register masks for read/modify/write operations.

## State and Persistence Behavior

The file itself has no mutable state. It defines the persistent contract between source code and device firmware/register layout. Runtime state lives in `struct cx231xx`, `struct cx231xx_video_mode`, and block-specific helpers that write these registers over USB control or internal I2C transactions. Any register definition error here can persist across multiple driver paths because the same mask may be reused by initialization, mode switching, tuner frequency changes, VBI setup, and debug register access.

## Dependencies and Integration Points

`cx231xx.h` includes this header and exposes the definitions to most driver modules. `cx231xx-video.c` uses `GEN_STAT`, `FLD_VPRES`, `FLD_HLOCK`, and the SAV/EAV constants. VBI capture uses `SAV_VBI_FIELD*`. Board setup, AV core, DIF, audio, GPIO, and core transfer setup files rely on the register addresses and field masks to program chip sub-blocks through `cx231xx_read_i2c_data()`, `cx231xx_write_i2c_data()`, and `cx231xx_reg_mask_write()`.

## Risks

The primary risk is silent hardware misconfiguration. A wrong mask width, register address, or overlapping field value can compile cleanly but alter unrelated bits in the device. The SAV/EAV constants are also parser-critical; incorrect values would cause dropped frames, incorrectly interleaved fields, or VBI/video buffer corruption. Many masks use raw hexadecimal values without typed wrappers, so call sites depend on accurate register width and endian assumptions. Because the header spans multiple hardware blocks, changes should be treated as ABI-like changes for the driver.

## Test Signals

Useful signals include successful analog video streaming in PAL and NTSC, correct VBI capture line counts, stable tuner input detection through `GEN_STAT`, no USB/URB overrun noise while streaming, and no regressions in `CONFIG_VIDEO_ADV_DEBUG` register reads/writes. Hardware smoke tests should cover composite, S-video, tuner, VBI, and audio paths because this header feeds all of them. Build coverage should include configurations with and without VBI, DVB, radio, and advanced debug support.
