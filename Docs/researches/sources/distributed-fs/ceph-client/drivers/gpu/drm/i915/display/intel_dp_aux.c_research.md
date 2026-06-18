# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.c

## Purpose

`intel_dp_aux.c` implements the i915 hardware-backed DisplayPort AUX channel transport. It provides byte packing/unpacking, AUX register selection for multiple platform generations, AUX clock-divider and send-control programming, the DRM `drm_dp_aux.transfer` callback, AUX power/locking/VDD integration, AUX channel selection, init/fini, and the IRQ wakeup handler. Higher-level DP code uses this file indirectly through `intel_dp->aux` for DPCD, EDID-over-I2C, CEC, HDCP, MST, PCON, PSR, ALPM, and other AUX transactions.

## Important APIs, Types, And Functions

Public functions:

- `intel_dp_aux_pack()`: packs up to four bytes into the big-endian register format expected by DP AUX data registers.
- `intel_dp_aux_fw_sync_len()`: returns the fast-wake sync pulse length, including a DPCD quirk adjustment for a known panel/laptop combination.
- `intel_dp_aux_init()`: selects platform register accessors and timing callbacks, initializes `struct drm_dp_aux`, names it, installs the transfer callback, creates the CPU latency QoS request, and initializes DPCD probe policy.
- `intel_dp_aux_fini()`: removes the QoS request and frees the AUX name.
- `intel_dp_aux_ch()`: chooses and validates the AUX channel from VBT or platform defaults, preventing duplicate use by another digital encoder.
- `intel_dp_aux_irq_handler()`: wakes the shared GMBUS/AUX wait queue when hardware signals AUX completion.

Internal helpers:

- `intel_dp_aux_unpack()` mirrors `intel_dp_aux_pack()` for receive data.
- `intel_dp_aux_wait_done()` waits up to 10 ms for `DP_AUX_CH_CTL_SEND_BUSY` to clear and returns the final status register.
- `g4x_get_aux_clock_divider()`, `ilk_get_aux_clock_divider()`, `hsw_get_aux_clock_divider()`, and `skl_get_aux_clock_divider()` calculate platform-specific AUX clock divisors.
- `g4x_get_aux_send_ctl()` and `skl_get_aux_send_ctl()` build hardware send-control words, including message size, timeout, error bits, precharge/sync pulse lengths, Thunderbolt I/O bit, and XeLPDP power-request preservation.
- `intel_dp_aux_xfer()` performs the low-level hardware transaction.
- `intel_dp_aux_transfer()` adapts DRM AUX messages into i915 hardware transactions and decodes replies.
- Register selector families `vlv_*`, `g4x_*`, `ilk_*`, `skl_*`, `tgl_*`, and `xelpdp_*` map `enum aux_ch` and data index to the correct i915 register.

## Control Flow

Initialization starts with `intel_dp_aux_ch()` during encoder setup to choose `dig_port->aux_ch`. `intel_dp_aux_init()` then installs register-selector callbacks based on display generation and platform: XeLPDP-style for display version 14+, TGL-style for 12+, SKL-style for 9+, ILK/PCH split, VLV/CHV, or G4x. It similarly chooses the clock-divider and send-control callbacks, initializes the DRM AUX object, assigns the human-readable AUX name, sets `aux.transfer = intel_dp_aux_transfer`, adds a QoS latency request, and configures DPCD probe behavior.

A DRM AUX request enters `intel_dp_aux_transfer()`. The function builds the AUX native/I2C header, decides transmit and receive sizes from request type, copies write payloads, applies the HDCP Aksv hardware flag when needed, calls `intel_dp_aux_xfer()`, then fills `msg->reply` and returns either payload bytes transferred or an errno. Native/I2C reads expect one reply byte plus payload; writes expect one or two reply bytes and support short-write byte counts.

`intel_dp_aux_xfer()` is the critical transaction path. It locks the digital port, rejects external AUX transfers if the port is disconnected, gets the AUX power domain, optionally locks PPS for eDP or VLV/CHV, records whether VDD was already on, requests low CPU wake latency, checks panel power, waits for any previous SEND_BUSY to clear, validates the 20-byte hardware FIFO limit, then tries each clock divider and up to five transmit attempts per divider. Each attempt writes up to five data registers, starts the send, waits for completion via `intel_dp_aux_wait_done()`, clears DONE/error bits, retries on timeout or receive error with required delay, and finally reads response bytes from data registers.

Cleanup in `intel_dp_aux_xfer()` restores CPU latency QoS, turns off VDD only if this function turned it on, unlocks PPS, drops the display power reference asynchronously, and unlocks the digital port. This cleanup path is shared for normal completion and errors.

IRQ completion is minimal: `intel_dp_aux_irq_handler()` wakes the wait queue used by `intel_dp_aux_wait_done()`. The wait condition still polls the hardware register, so a missed IRQ can be covered by timeout, while an IRQ reduces latency.

## State And Persistence Behavior

The file mutates several persistent fields in `struct intel_dp`:

- Function pointers: `aux_ch_ctl_reg`, `aux_ch_data_reg`, `get_aux_clock_divider`, and `get_aux_send_ctl`.
- `intel_dp->aux`: DRM AUX device fields, transfer callback, name, DRM device, Linux device after connector registration, and I2C retry counters maintained by DRM helpers.
- `intel_dp->pm_qos`: CPU latency QoS request active for the AUX object lifetime and set to zero only during a transaction.
- `intel_dp->aux_busy_last_status`: suppresses repeated busy warnings with identical status.

It also consumes `dig_port->aux_ch`, `dig_port->base.connected`, Type-C/TBT alt-mode state, PPS/VDD state, platform generation data, and display power domains. Hardware state persists in AUX control/data registers, which are written for every transaction and cleared for DONE/error bits after each send.

## Dependencies And Integration Points

This file integrates with:

- DRM DP AUX core through `drm_dp_aux_init()` and `struct drm_dp_aux.transfer`.
- i915 register access through `intel_de_read/write`, no-trace reads, register macros from `intel_dp_aux_regs.h`, and trace helpers.
- i915 digital-port locking via `intel_digital_port_lock()` / `intel_digital_port_unlock()` implemented in `intel_dp.c`.
- Display power domains and runtime PM through `intel_display_power_get()` and `intel_display_power_put_async()`.
- eDP PPS/VDD through `intel_pps_lock()`, `intel_pps_vdd_on_unlocked()`, `intel_pps_vdd_off_unlocked()`, and `intel_pps_check_power_unlocked()`.
- Type-C/TBT state through `intel_tc_port_in_tbt_alt_mode()` and live connection callbacks.
- DPCD quirks through `intel_has_dpcd_quirk()`.

## Risks And Edge Cases

The highest-risk behavior is in transaction ordering and cleanup:

- AUX has a strict 20-byte hardware limit; callers must go through DRM helpers that segment larger transfers.
- External disconnected ports return `-ENXIO` before power setup to avoid long timeouts and satisfy DP CTS behavior.
- eDP transfers need PPS/VDD coordination. Incorrect VDD ownership handling could power off a panel-needed AUX rail or leak VDD.
- The code requests zero CPU latency during transactions because AUX is sensitive to IRQ latency; forgetting to restore QoS would affect system power.
- Some platforms require multiple clock dividers or workarounds, such as HSW non-ULT AUX divider values and XeLPDP power-request preservation.
- Timeout and receive-error retry timing is spec-sensitive. Changing retry counts or delays can break marginal sinks or compliance tests.
- `intel_dp_aux_wait_done()` uses a shared display GMBUS wait queue; wakeups are broad, so the condition must always re-read the target AUX control register.

## Test Signals

Test signals include:

- DPCD read/write success during connector detection, eDP init, MST topology probing, DSC/PSR/ALPM capability reads, and PCON controls.
- EDID-over-AUX I2C behavior, including expected NACK/defer counters for DP compliance tests.
- `kms_dp_aux_dev` and raw AUX userspace access through `/dev/drm_dp_aux*`.
- Hotplug and disconnect tests verifying `-ENXIO` avoids long AUX hangs on unplugged external ports.
- Suspend/resume and runtime PM tests verifying power domains, PPS locks, and VDD are balanced.
- Platform matrix coverage for G4x, ILK/PCH split, VLV/CHV, SKL+, TGL USB-C AUX names/registers, XeLPDP registers, and Thunderbolt alt-mode transactions.
