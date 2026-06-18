# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.c

## Purpose
Implements Matrox G450/G550 on-chip secondary output support for the matroxfb driver. It registers a TV-capable secondary output and a DVI output, computes PAL/NTSC CVE2 encoder register images, programs those registers through the DAC index/data ports, and exposes V4L2-style controls for TV brightness, contrast, saturation, hue, and test output.

## Important APIs, Types, and Functions
- `struct mctl` maps a `v4l2_queryctrl` descriptor to a field offset inside `struct matrox_fb_info`.
- `g450_controls[]` defines supported TV controls and defaults stored in `minfo->altout.tvo_params`.
- `cve2_get_reg()`, `cve2_set_reg()`, and `cve2_set_reg10()` access CVE2 encoder registers through `matroxfb_DAC_out()` and `matroxfb_DAC_in()` while holding the Matrox DAC IRQ lock.
- `computeRegs()` derives CVE2 timing, chroma subcarrier, sync, blanking, and modified `struct my_timming` values for TV output.
- `cve2_init_TVdata()` seeds PAL or NTSC register templates and output timing descriptors.
- `matroxfb_g450_compute()`, `matroxfb_g450_program()`, and `matroxfb_g450_verify_mode()` implement `struct matrox_altout` callbacks for the secondary TV/monitor output.
- `g450_dvi_compute()` implements the DVI output clock programming path.
- `matroxfb_g450_connect()` and `matroxfb_g450_shutdown()` are exported entry points used by the base matroxfb device code.

## Control Flow
On connect, if `minfo->devflags.g450dac` is set, the driver takes `minfo->altout.lock`, fills TV control defaults, and installs two output descriptors: output 1 as `matroxfb_g450_altout` and output 2 as `matroxfb_g450_dvi`. The compute callback distinguishes CRTC2 TV modes from monitor modes. For TV modes, it copies the PAL/NTSC template, patches brightness/contrast/saturation/hue/test bits, then calls `computeRegs()` to adjust clock and timing. For monitor modes or DVI, it programs the G450 pixel/video PLL if `mt->mnp` is unset. The program callback writes the prepared CVE2 register image for TV modes.

## State and Persistence
Persistent runtime state lives in `struct matrox_fb_info`: `outputs[]` entries, `altout.tvo_params`, and the prepared `minfo->hw.maven` register image. The module has no independent persistent storage. Control writes immediately update both stored parameters and hardware registers, so state changes are visible without a full mode reprogram for supported controls.

## Dependencies and Integration Points
The file depends on matroxfb core types and locking from `matroxfb_base.h`, DAC helpers from `matroxfb_misc.c`, G450 PLL helpers from `g450_pll.h`, and public output/control constants from `<linux/matroxfb.h>`. It integrates through the `matrox_altout` callback table and exported connect/shutdown functions.

## Risks
The TV register programming is hardware-specific and mostly magic constants; invalid timing math can generate unusable output. `computeRegs()` mutates the caller's `struct my_timming`, so ordering with CRTC programming matters. DAC register access relies on correct lock discipline. The control lookup assumes ordered control IDs. Some arithmetic is constrained by CVE2 line length assumptions and can silently clamp visible width.

## Test Signals
Useful validation signals include successful module load with `g450dac`, output 1 and 2 registration, PAL/NTSC/monitor mode acceptance through `verifymode`, visible TV output after CRTC2 programming, DVI clock stability, and live control changes reflected in CVE2 registers 0x0e/0x1e, 0x20/0x22, 0x25, and 0x05. Regression tests should exercise invalid controls and unsupported output modes returning `-EINVAL`.
