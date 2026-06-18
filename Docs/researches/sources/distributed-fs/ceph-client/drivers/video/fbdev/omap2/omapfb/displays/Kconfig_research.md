# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/Kconfig

## Purpose
This Kconfig menu defines OMAPFB panel, connector, and encoder driver options for the OMAP2 DSS fbdev stack.

## Important APIs, Types, And Functions
- The menu depends on `FB_OMAP2_DSS`.
- Encoder options include OPA362, TFP410, and TPD12S015.
- Connector options include DVI, HDMI, and analog TV; DVI depends on I2C.
- Panel options include generic DPI, generic DSI command mode, Sony ACX565AKM, LG Philips LB035Q02, Sharp LS037V7DW01, TPO panels, and NEC NL8048HL11.
- Several fbdev panel options depend on equivalent DRM panel drivers being disabled to avoid duplicate binding.

## Control Flow
These symbols control which display modules are compiled by the displays Makefile.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
The file integrates fbdev display subdrivers with DSS, I2C, SPI, backlight class, and DRM-panel mutual-exclusion symbols.

## Risks
Incorrect dependency expressions can either hide valid drivers or allow duplicate fbdev/DRM panel drivers to bind the same hardware.

## Test Signals
Config matrix checks should verify each option appears with its dependencies and maps to the expected object file.
