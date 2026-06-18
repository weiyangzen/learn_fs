# sources/distributed-fs/ceph-client/include/linux/wm97xx.h

## Purpose
`wm97xx.h` defines register bits, return codes, data structures, and driver interfaces for Wolfson WM97xx AC97 touchscreen/audio-codec auxiliary ADC support. It supports codec-specific drivers, machine acceleration hooks, touchscreen polling, GPIO access, suspend modes, and battery auxiliary data.

## Important APIs, Types, and Functions
The header defines WM97xx variants, AC97 digitizer register addresses, common digitizer bits, WM9705/WM9712/WM9713-specific bits, AUX ADC IDs, codec IDs, GPIO bit masks, AC97 frame timing, and sample return flags `RC_AGAIN`, `RC_VALID`, `RC_PENUP`, and `RC_PENDOWN`. Types include `struct wm97xx_data`, GPIO status/direction/polarity/sticky/wake enums, digitizer ioctl constants, external codec driver declarations, `struct wm97xx_codec_drv`, `struct wm97xx_mach_ops`, `struct wm97xx`, `struct wm97xx_batt_pdata`, and `struct wm97xx_pdata`. APIs include GPIO get/set/config, suspend mode set, AC97 register read/write, AUX ADC read, and machine ops register/unregister.

## Control Flow
Codec-specific operations poll samples or full touch coordinates, enable accelerated coordinate mode, initialize/restore digitizer registers, and prepare AUX reads. The core `wm97xx` object caches codec registers, owns an input device, schedules delayed polling work on a workqueue, tracks pen IRQ/state, and calls machine ops for platform-specific accelerated paths or sampling noise mitigation. Battery and touchscreen platform devices can consume AUX readings.

## State and Persistence
State is runtime codec/input state. Register caches (`dig`, `gpio`, `misc`, `dig_save`), pen state bits, delayed work, IRQ number, AC97 slot/rate, suspend mode, and platform devices persist while the codec device is bound. Hardware register state persists across runtime until reset/suspend, with cached restore paths.

## Dependencies and Integration Points
Dependencies include ALSA core/PCM/AC97, input subsystem, platform devices, mutexes, delayed work/workqueues, and codec-specific implementation files. Integration points include touchscreen input reporting, AC97 bus access, battery/aux ADC platform data, board machine operations, suspend/resume, and GPIO control.

## Risks
Register bit definitions are codec-specific and mixing variants can misprogram hardware. Polling and IRQ/accelerated modes must agree on pen state or events can be lost. AC97 register access requires `codec_mutex`. AUX sampling saves/restores digitizer registers and can disturb touch operation if sequenced incorrectly. Workqueue teardown must cancel delayed polling.

## Test Signals
Signals include codec ID detection for WM9705/9712/9713, touch coordinate and pressure reporting, pen up/down transitions, accelerated mode startup/shutdown, AUX ADC battery/temp reads, GPIO operations, suspend/resume restore, delayed-work cancellation, and platform machine hooks.
