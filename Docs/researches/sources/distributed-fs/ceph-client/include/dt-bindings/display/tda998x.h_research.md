# sources/distributed-fs/ceph-client/include/dt-bindings/display/tda998x.h

## Purpose
Defines audio input mode constants for the NXP TDA998x HDMI transmitter binding.

## Important APIs, Types, and Constants
Exports `TDA998x_SPDIF` value 1 and `TDA998x_I2S` value 2. The mixed-case macro prefix matches the existing binding name and should be preserved for compatibility.

## Control Flow and State
No control flow or state. The HDMI transmitter driver interprets the constants from DT properties.

## Dependencies and Integration Points
Self-contained header included by DTS files configuring TDA998x audio routing.

## Risks and Test Signals
Wrong values select the wrong audio transport and can produce silent HDMI audio. Test signals include DTS compilation, schema validation, and HDMI audio playback tests for SPDIF and I2S configurations.
