# sources/distributed-fs/ceph-client/sound/pci/ice1712/envy24ht.h

## Purpose
Provides VT1724/Envy24HT register, EEPROM, GPIO, DMA, S/PDIF, AC97, and I2C definitions plus I2C helper prototypes. Although this work item focuses on the ICE1712 driver directory, this header is the shared map for the related VT1724 path.

## Important APIs, Types, and Functions
The header defines EEPROM byte indices `ICE_EEP2_*`, direct-register helpers `ICEREG1724()` and `ICEMT1724()`, register offsets such as `VT1724_REG_CONTROL`, `VT1724_REG_GPIO_DATA`, `VT1724_MT_DMA_CONTROL`, and DMA channel register blocks for PDMA/RDMA streams. It names bit masks for IRQs, system config, I2S features, S/PDIF configuration, MPU401 FIFO state, AC97 commands, GPIO direction/mask/data, DMA start/pause/FIFO errors, and I2S format. It declares `snd_vt1724_read_i2c()` and `snd_vt1724_write_i2c()`.

## Control Flow
There is no executable control flow in the header. Including VT1724 code uses these offsets to reset the chip, read EEPROM configuration, configure GPIO width and direction, program multichannel DMA engines, service IRQs, set I2S/S/PDIF formats, and access external codec/control devices over I2C.

## State and Persistence Behavior
The constants describe hardware register state. EEPROM indices represent persistent board configuration bytes read from the device; runtime register state is volatile and must be restored during probe/resume by the VT1724 implementation. GPIO fields extend beyond the 8-bit ICE1712 model to wider VT1724 pins.

## Dependencies and Integration Points
It includes ALSA control, AC97, rawmidi, I2C, PCM, and local `ice1712.h` declarations. The shared `struct snd_ice1712` carries VT1724-specific flags and callbacks, so this header bridges the older ICE1712 base structure and the newer Envy24HT register layout.

## Risks
Register definitions are low-level and many comments encode hardware errata or ambiguous widths, especially GPIO direction and GPIO 16:22 handling. Wrong bit masks can start or pause the wrong DMA engine, mis-handle S/PDIF as PDMA4/RDMA1, or break MPU interrupts. Because the header shares naming with ICE1712 but maps different offsets, accidental use of ICE1712 macros on VT1724 paths is a maintenance risk.

## Test Signals
Build VT1724 users, probe Envy24HT cards, verify EEPROM fields decode to expected channel/S/PDIF/GPIO setup, run all PDMA/RDMA streams including S/PDIF paths, check MIDI FIFO interrupts, validate GPIO read/write for pins above 15, and suspend/resume through rate, route, and DMA state restoration.
