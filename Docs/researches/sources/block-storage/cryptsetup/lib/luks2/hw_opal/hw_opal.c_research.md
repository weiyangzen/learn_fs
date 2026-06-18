# File Research: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.c

Implements cryptsetup’s Linux OPAL self-encrypting drive support behind `HAVE_HW_OPAL`, with `-ENOTSUP` stubs when OPAL support is unavailable at build time.

Core behavior:
- Wraps Linux `sed-opal` ioctls with debug logging, OPAL method-status translation, and compatibility definitions for newer Single User Mode ioctl structures if kernel headers lack them.
- Supports OPAL discovery, status, geometry, ownership, locking SP activation, user activation, password setup, locking range setup, lock/unlock, save-for-resume behavior, PSID factory reset, and locking-range reset.
- Detects and configures Single User Mode (SUM), including runtime kernel ioctl support probing and fallback behavior for non-conforming drives.
- Maintains OPAL-specific exclusive locks using cryptsetup write locks keyed by block device major/minor.

Setup flow:
- `opal_setup_ranges()` opens the device, checks SUM and existing OPAL state, activates the locking SP or reuses an active one, creates/enables the range user, sets the user password from a `volume_key`, configures range start/length, locks the range, verifies attributes and lock state, and returns the LUKS2 OPAL requirement version.
- SUM setup attempts preferred RangeStartLengthPolicy behavior, then retries without range policy, then disables SUM if the device behaves incorrectly.
- Reusing an active locking SP wipes the existing target range first via SUM erase or secure erase.

Lock/unlock flow:
- `opal_lock()` and `opal_unlock()` call a shared helper using `IOC_OPAL_LOCK_UNLOCK`.
- Unlock requires a volume key; lock does not.
- Unlock attempts `IOC_OPAL_SAVE` with `OPAL_SAVE_FOR_LOCK` for suspend/resume support. Lock attempts `IOC_OPAL_SAVE` without the flag to clear cached kernel credentials.

Validation and discovery:
- `opal_range_check_attributes_and_get_lock_state()` verifies OPAL range offset/length, RLE/WLE, and optional expected lock state, returning current read/write lock state.
- `opal_geometry()` returns OPAL logical block size, alignment granularity, and lowest aligned LBA.
- `crypt_status_hw_encryption()` uses OPAL level-0 discovery when possible, otherwise falls back to supported/SUM status probes.

Failure/security notes:
- OPAL method status is distinguished from negative errno-style ioctl failures.
- Sensitive OPAL keys are stored in `crypt_safe_alloc` buffers where practical and zeroed before return in direct stack cases.
- Factory reset intentionally does not take the OPAL serialization lock because it destroys the whole OPAL block device.
- Non-SUM and SUM paths differ in authority rules: in SUM, user credentials control RLE/WLE and lock/unlock for the range.
