# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-core.c

## Purpose
`em28xx-core.c` provides shared low-level services for the em28xx media driver family. It implements USB vendor control register access, AC97 register access and analog audio routing, GPIO and mode switching, capture start/stop register programming, analog/digital URB allocation and submission, LED lookup, built-in decoder routing for EM2828X devices, and the extension registry used by ALSA, V4L2, DVB, and RC submodules.

## Important APIs, Types, and Functions
Exported register helpers are `em28xx_read_reg_req_len()`, `em28xx_read_reg_req()`, `em28xx_read_reg()`, `em28xx_write_regs_req()`, `em28xx_write_regs()`, `em28xx_write_reg()`, `em28xx_write_reg_bits()`, and `em28xx_toggle_reg_bits()`. AC97 helpers are `em28xx_read_ac97()`, `em28xx_write_ac97()`, and internal `em28xx_is_ac97_ready()`. Audio routing uses `set_ac97_input()`, `em28xx_set_audio_source()`, `em28xx_audio_analog_set()`, and `em28xx_audio_setup()`.

Capture and USB transfer helpers include `em2828X_decoder_vmux()`, `em28xx_capture_start()`, `em28xx_gpio_set()`, `em28xx_set_mode()`, `em28xx_irq_callback()`, `em28xx_uninit_usb_xfer()`, `em28xx_stop_urbs()`, `em28xx_alloc_urbs()`, and `em28xx_init_usb_xfer()`. Extension management is handled by `em28xx_register_extension()`, `em28xx_unregister_extension()`, `em28xx_init_extension()`, `em28xx_close_extension()`, `em28xx_suspend_extension()`, and `em28xx_resume_extension()` using module-global extension and device lists.

## Control Flow
Register reads and writes serialize through `dev->ctrl_urb_lock`, use `dev->urb_buf` as a shared control buffer, check `dev->disconnected`, enforce `URB_MAX_CTRL_SIZE`, call `usb_control_msg()`, translate USB errors, and optionally sleep after writes using `dev->wait_after_write`. Bit helpers read-modify-write a register over those primitives.

Audio setup reads chip configuration, classifies internal audio as none, AC97, or I2S, probes AC97 vendor/features where needed, records `dev->audio_mode.ac97`, and calls `em28xx_audio_analog_set()`. Analog audio setup writes XCLK mute/unmute bits, selects the bridge audio source, sets GPIOs for mute or input routing, mutes AC97 outputs, programs power/rate registers, writes output volume, and sets AC97 record source when requested.

Capture start handles newer EM2874/EM28174/EM28178/EM2884-style transport stream registers separately from older analog/video paths. It programs packet sizes, TS enable bits, USB suspend/video enable registers, and capture LEDs based on `dev->mode` and `dev->ts`. `em28xx_set_mode()` switches between suspend, analog, and digital mode by selecting the appropriate board GPIO sequence. `em28xx_gpio_set()` applies `struct em28xx_reg_seq` entries until the sentinel, with optional sleeps.

URB setup starts with `em28xx_alloc_urbs()`, which validates endpoint availability for analog or digital mode, tears down previous transfers, allocates URB and buffer arrays, fills bulk or isochronous URBs, and sets frame descriptors. `em28xx_init_usb_xfer()` stores the caller-provided `urb_data_copy` callback, allocates analog buffers when needed, clears bulk stalls, initializes wait queues, starts capture hardware, and submits all URBs. `em28xx_irq_callback()` invokes `urb_data_copy()` under `dev->slock`, clears isochronous frame statuses, and resubmits the URB.

The extension registry keeps a global list of live `struct em28xx` devices and registered `struct em28xx_ops`. Registering an extension immediately calls its init hook for each live device and secondary device. Adding a device calls all registered init hooks. Close/unregister/suspend/resume iterate the same lists and include `dev->dev_next` when present.

## State and Persistence Behavior
This file does not persist data beyond module lifetime. It mutates hardware registers and runtime fields in `struct em28xx`, including `int_audio_type`, `usb_audio_type`, `audio_mode.ac97`, `mode`, USB buffer state, active video/VBI buffers, and capture LEDs. `struct em28xx_usb_bufs` owns URB and buffer arrays for analog and digital transfer modes; these are allocated, stopped, and freed as streaming starts and stops. Global state consists of debug module parameters, `em28xx_devlist`, `em28xx_devlist_mutex`, and `em28xx_extension_devlist`.

Concurrency relies on `ctrl_urb_lock` for vendor control transfers, `dev->slock` for IRQ-side stream buffer copying, device locks in higher-level modules, and `em28xx_devlist_mutex` for device/extension list mutation. URB teardown uses `usb_kill_urb()` in normal context and `usb_unlink_urb()` when IRQs are disabled.

## Dependencies and Integration Points
The core depends on Linux USB APIs, AC97 codec constants, V4L2/media types through shared driver structures, board data from `em28xx-cards.c`, and URB data-copy callbacks supplied by analog V4L2 and DVB modules. It exports symbols used by em28xx audio, V4L2, DVB, RC, I2C, and camera code. It also drives board LEDs defined in the board table and configures transport-stream registers consumed by the DVB extension.

## Risks and Edge Cases
Control transfers share a fixed-size buffer, so all callers must respect the lock and length limits. `em28xx_write_regs()` uses `USB_REQ_GET_STATUS` as the vendor request wrapper, which is driver-specific and easy to misuse in new helpers. AC97 access depends on readiness polling and can fail or block setup on unreliable chips. Audio setup has conservative fallbacks but can disable vendor audio when AC97 probing fails. Capture start contains duplicated TS setup logic for several chip generations, increasing the chance of inconsistent packet-size or enable-bit changes. URB allocation sets `URB_FREE_BUFFER` while also tracking buffers in `usb_bufs->buf`; teardown relies on `usb_free_urb()` semantics and careful nulling, so ownership changes need review. The extension registry calls callbacks while holding the global list mutex, so extension callbacks must not introduce lock inversions with device registration paths.

## Test Signals
Build signals include exported-symbol consumers across em28xx submodules and no warnings in USB/media configurations. Runtime signals include successful vendor register reads/writes, reliable AC97 detection and mixer setup, correct GPIO sequence timing on mode changes, video/DVB capture start/stop without stalled URBs, clean bulk halt recovery, no resubmit storms in `em28xx_irq_callback()`, and balanced extension init/fini during module load/unload and hotplug. Suspend/resume tests should confirm extension callbacks run for both primary and secondary devices and that URBs are not active after stop or disconnect.
