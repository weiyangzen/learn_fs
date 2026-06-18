## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.c

Purpose: `matroxfb_Ti3026.c` is the low-level RAMDAC driver for Matrox Millennium/Millennium II boards using the TI TVP3026 RAMDAC. It provides the `matrox_millennium` switch used by the base Matrox PCI driver for setup, clocking, mode programming, and restore.

Important APIs and functions: the exported object is `matrox_millennium`. Internal functions include `Ti3026_calcclock()` for TVP3026 PLL encoding, `Ti3026_setpclk()` for pixel/loop PLL state calculation, `Ti3026_init()` for DAC/VGA register image construction, `ti3026_setMCLK()` for memory clock programming through a temporary pixel-clock path, `ti3026_ramdac_init()`, `Ti3026_restore()`, `Ti3026_reset()`, and `Ti3026_preinit()`. Register constants define palette, cursor, latch, mux, clock, PLL, color-key, and misc control registers.

Control flow: preinit identifies Millennium generation, sets capabilities, output descriptors, PCI option register bits, reads RAMDAC revision, stops DAC clocks, resets VGA-ish state, and resets the accelerator. Reset initializes PLL feature limits and MCLK unless `noinit`. Init chooses register images for 4/8/16/24/32 bpp, initializes VGA timing, adjusts sync/cursor/interleave settings, and calculates pixel/loop PLL bytes. Restore writes PCI, VGA, CRTC extension, DAC control, pixel PLL, and loop PLL registers, waiting for PLL lock when needed.

State and persistence: software state is stored in `minfo->hw.DACreg`, `DACclk`, `MXoptionReg`, `CRTCEXT`, and `minfo->accel.ramdac_rev`, plus capability flags such as `millenium`, `milleniumII`, `interleave`, and `cfb4`. Hardware state persists in TVP3026 extended registers, PLLs, PCI option register, and Matrox accelerator reset/memory registers.

Dependencies and integration points: depends on `matroxfb_base.h` for device state and MMIO/PCI helpers, `matroxfb_misc` for generic VGA/PLL calculations, `matroxfb_accel` for capability interplay, and `linux/matroxfb.h` for output mode constants. The base driver invokes this file through `hw_switch` for Millennium device IDs.

Risks: clock programming is slow and heavily sequenced; the code waits up to roughly five seconds for several PLL lock paths. `ti3026_setMCLK()` temporarily repurposes pixel PLL output for MCLK, so interruption or wrong register order can destabilize display memory. 24 bpp handling has RAMDAC revision and interleave-specific workarounds plus an `inv24` option. Many bit settings are historical magic values.

Test signals: validate Millennium and Millennium II with 4/8/15/16/24/32 bpp modes, interleaved and non-interleaved memory sizes, and repeated mode switches. Watch for pixel/loop/memory PLL timeout messages, correct hardware cursor blanking, stable acceleration after reset, and correct palette/directcolor behavior.
