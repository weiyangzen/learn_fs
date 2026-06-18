# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/sil-sii8620.c

## Purpose

`sil-sii8620.c` drives the Silicon Image SiI8620 Mobile HD Transmitter, an HDMI/MHL bridge with MHL1/2 and MHL3/eCBUS support. It handles hardware power, MHL discovery, CBUS MSC messaging, eMSC burst transfers, EDID fetch and upstream EDID priming, HPD control, video format/link setup, optional RCP input events, extcon cable detection, and DRM bridge mode validation/fixup.

## Important APIs, Types, And Functions

`struct sii8620` stores bridge/device pointers, optional RC input device, XTAL clock, reset/int GPIOs, regulators, mutex, sticky `error`, packed-pixel decision, current mode, sink type, CBUS status, MHL status/devcap/xdevcap arrays, EDID pointer, feature flags, extcon state/work, MSC transmit queue, and eMSC burst buffers. `struct sii8620_mt_msg` represents queued MSC commands with send/receive callbacks and continuations.

Core helpers include raw paged I2C access (`sii8620_read_buf()`, `readb()`, `write_buf()`, `write_seq()`, `setbits()`), message queue helpers (`sii8620_mt_*`), eMSC burst helpers (`sii8620_burst_*`), EDID helpers (`sii8620_fetch_edid()`, `set_upstream_edid()`), power/init/disconnect helpers (`hw_on()`, `hw_off()`, `disconnect()`, `mhl_init()`), mode/video helpers (`set_mode()`, `set_format()`, `set_infoframes()`, `start_video()`), IRQ subhandlers, extcon handlers, and bridge callbacks `attach()`, `detach()`, `mode_valid()`, and `mode_fixup()`.

## Control Flow

Probe allocates state, initializes mutex and message queue, gets XTAL clock, requests a disabled threaded IRQ, gets reset GPIO and regulators, initializes extcon if present, adds the DRM bridge, and either waits for extcon MHL events or powers on immediately. Cable-in enables regulators/clock, releases reset, reads chip ID, programs XTAL rate, calls `sii8620_disconnect()` to reset link state, configures CBUS drive controls, and enables IRQ.

The main IRQ thread reads `REG_FAST_INTR_STAT`, dispatches discovery, Gen2 write-burst, CoC, TDM, MSC, error, eMSC block, EDID, DDC, and SCDT handlers, then drains received bursts, advances queued MSC work, sends pending bursts, and disconnects on accumulated error. Discovery checks RGND and MHL established bits; MHL init writes local capabilities, configures peer-specific state, starts Gen2 write burst, and announces DCAP ready. MSC status/interrupt handlers react to DCAP ready, path enable, HPD changes, feature requests/completion, RCP/RAP messages, and transition to MHL3/eCBUS when supported.

Sink detection waits for both downstream HPD and devcap read, fetches EDID over the internal DDC engine, primes upstream EDID FIFO, identifies HDMI vs DVI, and enables HPD after MHL3 feature completion when required. SCDT change starts video: it selects packed-pixel mode if needed, writes TPI formats and infoframes, programs MHL1 link mode or MHL3 AV link rate/zone, and sends burst pixel-format descriptors.

## State And Persistence Behavior

State is in-memory and hardware-volatile. `mode` moves through disconnected, discovery, MHL1, MHL3, and eCBUS-S. `devcap`, `xdevcap`, `stat`, and `xstat` mirror peer-visible MHL registers and are cleared on disconnect. `edid` is dynamically allocated and replaced on new sink detection. The sticky `error` short-circuits I2C sequences until cleared, and any IRQ-time error forces MHL disconnection. Extcon `cable_state` gates cable-in/out work.

## Dependencies And Integration Points

The file depends on `sil-sii8620.h`, DRM bridge/EDID/encoder APIs, MHL protocol constants, I2C, regulator, GPIO, clock, threaded IRQ, extcon, workqueue, and optional RC core. It assumes a paged I2C map whose page addresses are in `sii8620_i2c_page[]`. The bridge integrates only mode validation/fixup; actual HPD/EDID behavior is implemented by programming upstream-visible EDID/HPD hardware.

## Risks

The driver contains many hardware magic sequences and tight state coupling between discovery, MSC queue, eMSC burst, and video start. `sii8620_fetch_edid()` performs manual DDC polling and dynamic EDID reallocation; timeout or cable drop paths must free correctly. `sii8620_detach()` unregisters then frees `rc_dev`, which is risky because `rc_unregister_device()` normally owns release. Packed-pixel mode is stored from `mode_fixup()` under lock but consumed later in IRQ/video paths. Any paged I2C address mismatch in the header breaks broad areas of the driver.

## Test Signals

Signals include chip ID read after cable-in, extcon-triggered cable state changes, RGND/MHL established/disconnect IRQs, MSC queue progress and timeout-free completions, MHL1 and MHL3/eCBUS negotiation, EDID fetch and upstream HPD assertion, HDMI vs DVI sink detection, video start on SCDT with correct packed-pixel decision, RCP key events when RC core is enabled, and error recovery returning to disconnected discovery state.
