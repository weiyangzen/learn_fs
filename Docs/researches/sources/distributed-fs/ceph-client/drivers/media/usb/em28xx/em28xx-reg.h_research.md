# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-reg.h

Purpose: centralizes em28xx bridge register addresses, bit masks, GPIO/GPO flags, output/capture format values, transport-stream enable bits, audio source constants, and chip IDs used by the em28xx modules.

Important APIs/types/functions: this header is macro/enum only. It defines GPIO bit helpers (`EM_GPIO_*`, `EM_GPO_*`), endpoint constants, chip configuration bits, I2C clock and bus-select bits, XCLK/IR mode bits, video input/output registers (`EM28XX_R10_VINMODE`, `EM28XX_R11_VINCTRL`, `EM28XX_R27_OUTFMT`), color defaults, capture window/scaler registers, VBI registers, AC97 registers, IR registers, TS packet/enable registers, audio source values, and `enum em28xx_chip_id`.

Control flow: none directly; consumers use the constants to program bridge hardware. Video setup writes output/scaler/VBI constants, I2C code manipulates `EM28XX_R06_I2C_CLK`, input code reads IR registers and writes IR config, DVB code enables transport streams and GPIO sequences, and core/audio code controls suspend/audio paths.

State and persistence: no runtime state. The risk profile is contractual: values here encode hardware semantics and are shared across all em28xx source files.

Dependencies and integration points: included by `em28xx.h`, which exposes it to the driver family. It depends on kernel `BIT()` being available through including context. It is an integration point with datasheet/USB-trace-derived bridge programming and with board definitions in `em28xx-cards.c`.

Risks: wrong constants silently program hardware incorrectly. Several comments flag uncertain or family-specific meanings, especially camera bridge registers and built-in decoder behavior. Chip IDs are incomplete by comment, so new boards may need updates. Tests should be indirect: validate I2C bus switching, IR protocol selection, VBI capture dimensions, analog color control registers, DVB TS enablement, suspend/resume GPIO effects, and chip-id-specific branches on representative hardware.
