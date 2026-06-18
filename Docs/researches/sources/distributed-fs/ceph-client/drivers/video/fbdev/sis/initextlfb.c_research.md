# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initextlfb.c

## Purpose

`initextlfb.c` provides Linux fbdev-specific helpers that convert SiS internal mode table data into framebuffer timing values. It is the bridge between the driver core's mode numbers/rate indexes and `struct fb_var_screeninfo` fields used by fbdev validation and reporting.

## Important APIs, Types, And Functions

- `sisfb_mode_rate_to_dclock(struct SiS_Private *SiS_Pr, unsigned char modeno, unsigned char rateindex)`: returns the pixel clock in Hz for a SiS mode/rate pair, defaulting to 65 MHz when initialization or lookup fails.
- `sisfb_mode_rate_to_ddata(struct SiS_Private *SiS_Pr, unsigned char modeno, unsigned char rateindex, struct fb_var_screeninfo *var)`: fills timing and sync fields in `var` using CRT1 timing data and returns success as `1` or failure as `0`.
- `sisfb_gettotalfrommode(struct SiS_Private *SiS_Pr, unsigned char modeno, int *htotal, int *vtotal, unsigned char rateindex)`: extracts total horizontal and vertical scan counts from CRT register table bytes.
- External dependencies include `SiSInitPtr`, `SiS_SearchModeID`, and `SiS_Generic_ConvertCRData`.

## Control Flow

Each function initializes the private table pointers with `SiSInitPtr`, normalizes fbdev-style `rateindex` by decrementing nonzero values, maps special 315 modes `0x5a` and `0x5b` to base mode IDs, and then uses `SiS_SearchModeID`. The selected mode's reference table index (`RRTI`) chooses normal, wide, or rate-offset timing entries. `sisfb_mode_rate_to_ddata` converts CRT register data into fbdev margins/syncs and then applies sync polarity, interlace, and double-scan flags. `sisfb_gettotalfrommode` reconstructs totals from packed CRTC bytes and doubles vertical total for interlaced modes.

## State And Persistence

The file is read-only with respect to hardware. It reads `SiS_Pr` tables such as `SiS_EModeIDTable`, `SiS_RefIndex`, `SiS_VCLKData`, and `SiS_CRT1Table`, and writes only caller-provided output objects (`fb_var_screeninfo`, `htotal`, and `vtotal`). No persistent state is stored by these helpers.

## Dependencies And Integration Points

- Included by the SiS fbdev build and declared in `sis.h`.
- Called by `sis_main.c` during var setup, mode validation, and display information reporting.
- Depends on `HaveWideTiming`, `InterlaceMode`, `DoubleScanMode`, `FB_SYNC_*`, and `FB_VMODE_*` constants.
- The mode/rate table shapes are defined in `vstruct.h` and populated by the init table machinery.

## Risks

- Rate indexes are not range-checked after adding to `RRTI`; callers must supply valid indexes for the mode.
- Wide-screen modes ignore refresh-rate selection when `SiS_UseWide == 1`, which is intentional but can surprise callers expecting exact rate control.
- The fallback 65 MHz clock can hide lookup failures unless the caller logs or validates separately.
- Packed CRTC extraction depends on table layout and byte positions; table format changes require synchronized updates.

## Test Signals

- For known mode/rate pairs, compare returned pixel clocks and totals against the SiS reference tables.
- Validate 315 aliases `0x5a` and `0x5b`, wide timing paths, interlaced modes, and double-scan modes.
- Exercise `sis_main.c` mode-setting paths and confirm `fb_var_screeninfo` sync polarity and `vmode` values match expected modelines.
