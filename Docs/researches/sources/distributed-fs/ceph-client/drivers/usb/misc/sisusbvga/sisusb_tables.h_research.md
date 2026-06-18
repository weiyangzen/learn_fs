# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_tables.h

Purpose: Static register and timing data for sisusb mode initialization. It contains DAC palettes, standard VGA table entries, mode resolution metadata, extended mode IDs, reference timing indices, CRT1 register sequences, and VCLK data.

Important APIs and types: arrays `SiS_MDA_DAC`, `SiS_CGA_DAC`, `SiS_EGA_DAC`, `SiS_VGA_DAC`, `SiSUSB_SModeIDTable`, `SiSUSB_ModeResInfo`, `SiSUSB_StandTable`, `SiSUSB_EModeIDTable`, `SiSUSB_RefIndex`, `SiSUSB_CRT1Table`, and `SiSUSB_VCLKData`. It depends on the structures in `sisusb_struct.h` and resolution constants/macros from the implementation context.

Control flow: mode-setting code indexes these arrays to translate requested SiS/VESA/display modes into VGA sequencer, graphics, attribute, CRTC, pixel-clock, and timing values. Sentinel entries such as mode ID `0xff`, ref flag `0xffff`, and zero VCLK entries terminate or reserve table ranges.

State and persistence: all content is read-only compile-time data. Hardware state changes only when implementation code programs registers from these tables. Risks include hand-maintained legacy timing constants, implicit cross-table indices (`REFindex`, CRTC indexes, VCLK indexes), custom VCLK slot filled at runtime, and high regression risk from mechanical edits. Test signals include comparing programmed modes to known-good timings, table sentinel handling, all supported depths/resolutions, and ensuring no index points past table bounds.
