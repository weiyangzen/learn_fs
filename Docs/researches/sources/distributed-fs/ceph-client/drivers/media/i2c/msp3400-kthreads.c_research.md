# sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-kthreads.c

## Purpose
`msp3400-kthreads.c` implements the asynchronous audio-standard detection, carrier scanning, stereo/NICAM/SAP monitoring, and audio-source selection logic for the MSP34xx TV sound processor driver. It contains separate thread flows for older manual carrier-detect devices, newer autodetect devices, and G-family autoselect devices.

## Important APIs, Types, and Functions
- `msp_stdlist[]` maps MSP standard return values to main/secondary carrier values, human-readable names, and V4L2 standard masks.
- `msp3400c_init_data[]` holds demodulator FIR, carrier, mode, source, and matrix programming for manual modes.
- Carrier-detect tables enumerate candidate main and secondary carriers for 4.5, 5.5, 6.0, and 6.5 MHz families.
- `msp_standard_std_name()` and `msp_standard_std()` translate MSP standard codes to names and V4L2 standard masks.
- `msp_set_source()` writes DSP source registers, optionally selecting I2S inputs when Dolby processing is requested.
- `msp3400c_set_carrier()` writes carrier frequency registers and triggers load.
- `msp3400c_set_mode()` programs demodulator filters, mode registers, carriers, DSP source/matrix, and prescales.
- `msp3400c_set_audmode()` chooses mono/stereo/language/NICAM/SCART source routing for manual/autodetect modes.
- `msp3400c_detect_stereo()` reads FM/NICAM detection registers and updates `rxsubchans`/`nicam_on`.
- `watch_stereo()` refreshes stereo state and reapplies audio mode; `msp_once` disables repeated monitoring.
- `msp3400c_thread()`, `msp3410d_thread()`, and `msp34xxg_thread()` are the three background control loops.
- `msp34xxg_modus()`, `msp34xxg_set_sources()`, `msp34xxg_reset()`, `msp34xxg_detect_stereo()`, and `msp34xxg_set_audmode()` implement G-family autoselect support.
- Public dispatchers `msp_set_audmode()` and `msp_detect_stereo()` call the correct implementation based on `state->opmode`.

## Control Flow
All thread functions are freezable loops sleeping on `msp_sleep()` until `restart` or stop. The manual `msp3400c_thread()` mutes output, programs AM detect, waits for tuner settle, scans main carriers, optionally scans secondary carriers, selects the best mode/carriers, unmutes, and then monitors stereo/NICAM changes. The `msp3410d_thread()` uses hardware standard autodetect where possible, falls back for radio/NTSC/AM-sound cases, programs prescales, sets audio mode, unmutes, and monitors stereo. The `msp34xxg_thread()` resets and initializes G-family devices, writes the requested/autodetect standard, waits briefly for hardware detection, unmutes, restores ACB, and monitors BTSC/SAP when relevant.

## State and Persistence Behavior
The threads mutate shared `msp_state` fields: `std`, `detected_std`, `main`, `second`, `mode`, `rxsubchans`, `nicam_on`, `scan_in_progress`, `watch_stereo`, and `restart`. The state persists in memory while the driver is bound and is re-derived from hardware scans after channel changes, routing changes, suspend/resume wakeups, and radio/standard changes. Hardware programming is direct and cumulative; reset paths must reapply mode/source/prescale state.

## Dependencies and Integration Points
The file depends on low-level helpers and state definitions from `msp3400-driver.h`, Linux kthreads/freezer/suspend support, V4L2 standard/tuner constants, and I2C client data. It is tightly integrated with the main driver's V4L2 callbacks: those callbacks set state and wake these threads, while these threads update detected standard and audio status consumed by tuner/status callbacks.

## Risks and Edge Cases
- The provided source contains a duplicated `} else {` in `msp3400c_detect_stereo()` and a duplicated `if (count)` in `msp3410d_thread()`. As written, these are likely build blockers or at least source corruption that must be fixed before compile testing.
- Shared state is not protected by a mutex; thread and ioctl paths can race on route, standard, audmode, and scan flags.
- Carrier scan decisions are threshold/best-value based and can misdetect noisy signals; module parameters (`amsound`, `stereo_threshold`, `standard`, `once`) are important test axes.
- `msp3410d_thread()` indexes `msp_stdlist[i]` after searching for a detected value. The sentinel prevents an immediate out-of-bounds read, but unknown values produce zero carriers and "unknown" behavior unless handled.
- Threads rely on `msp_sleep()` returning restart state; missed wakeups or state changes without `msp_wake_thread()` can leave hardware programmed for the previous channel.
- Hardware resets from low-level I2C errors can invalidate the assumptions of the currently running thread iteration.

## Test Signals
- Compile both MSP source files together to catch the duplicated/stray source lines.
- Simulate manual carrier scans for each main/secondary carrier table, including AM-sound SECAM override.
- Exercise `msp3410d_thread()` autodetect values for NICAM, BTSC, radio, and failed/unknown detection.
- Exercise G-family autoselect for radio, NTSC-J, NTSC-KR, SECAM-L, M/BTSC, and generic autodetect.
- Verify `rxsubchans`, `nicam_on`, `detected_std`, and DSP source registers after stereo/NICAM/SAP changes.
- Test restart behavior during each sleep point to ensure scans abort and restart cleanly.
