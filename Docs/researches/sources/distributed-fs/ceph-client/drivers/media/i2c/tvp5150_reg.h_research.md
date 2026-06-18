# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150_reg.h

## Purpose

This header defines the TVP5150 register map and key bit encodings consumed by `tvp5150.c`. It is not a standalone module; it is the symbolic contract between the driver and the TVP5150 hardware register layout.

## Important APIs, Types, And Functions

The file contains only preprocessor definitions. Important groups include input, analog, operation, miscellaneous, autoswitch, luma/chroma, brightness/saturation/hue/contrast, crop, genlock, interrupt, video-standard, device ID, ROM version, status, closed-caption/WSS/VPS/VITC data, teletext filter, VDP configuration RAM, FIFO, line mode, and full-field registers. Bit helpers include `TVP5150_MISC_CTL_*`, `TVP5150_INT_A_LOCK_STATUS`, `TVP5150_INT_A_LOCK`, and `TVP5150_VDPOE`. Video standard constants encode fixed and autoswitch modes for NTSC, PAL variants, NTSC 4.43, and SECAM.

## Control Flow

There is no executable control flow. The register constants are used by the driver init tables, status logging, standard selection and detection, VBI programming, crop programming, IRQ handling, runtime PM, regmap access tables, and debug register operations.

## State And Persistence

The header declares symbolic register addresses, not state. Persistence is entirely in hardware registers and the driver's `struct tvp5150` fields.

## Dependencies And Integration Points

The header expects Linux `BIT()` to be available through included kernel headers in the C file. Its integration point is the TVP5150 driver; external users should not rely on it as a public UAPI.

## Risks

Incorrect constants directly corrupt hardware programming. The `VIDEO_STD_MASK` definition is unusual and should be treated carefully if reused. Reserved ranges are documented only by comments; future writes outside declared readable ranges in the driver may require coordinated updates in both files.

## Test Signals

Validation is indirect: successful chip initialization, correct standard selection/detection, readable debug status dumps, VBI configuration, interrupt lock events, and crop register behavior indicate that the symbolic addresses and bit definitions match the hardware.
