
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_regs.h

Purpose: complete CMI8786/8787/8788 register map and bit definitions for DMA, interrupts, formats, clocks, SPDIF, EEPROM, I2C/SPI, MIDI, GPIO/GPI, routing, AC97, diagnostics, and revision fields.

Important groups: DMA base/count/tcount registers per channel; channel masks matching `PCM_*`; interrupt masks/status; misc/function reset and bus-mode bits; I2S rate/format/MCLK/BCLK/bits; SPDIF input/output status and IEC958 bit fields; EEPROM and 2-wire/SPI controls; GPIO/GPI and device sense; playback/record routing and monitor routing; AC97 control/status/config/register windows.

Integration: every shared C file and board driver uses these definitions to program hardware. `oxygen.h` relies on channel-mask alignment. `oxygen_io.c` uses offsets for saved register cache and transports; PCM/mixer/lib use DMA, interrupt, routing, and PM restore maps.

Risks: this is hardware ABI. Any incorrect offset, mask, or read/write-clear interpretation can cause broken DMA, stuck interrupts, wrong clocks, or unsafe output routing. Test signals are broad hardware smoke tests: probe, DMA on every channel, interrupt ack, I2C/SPI transactions, SPDIF in/out, AC97, GPIO events, EEPROM reads, and resume restore.
