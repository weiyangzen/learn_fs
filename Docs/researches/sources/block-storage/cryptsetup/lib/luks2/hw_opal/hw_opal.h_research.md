# File Research: sources/block-storage/cryptsetup/lib/luks2/hw_opal/hw_opal.h

Declares the OPAL utility API used by LUKS2 hardware encryption paths.

Exported operations:
- `opal_setup_ranges()` configures an OPAL locking range and reports the required LUKS2 OPAL requirement version.
- `opal_lock()` and `opal_unlock()` lock/unlock a segment.
- `opal_supported()` and `opal_geometry()` query device capability and geometry.
- `opal_factory_reset()` performs PSID revert of the full OPAL device.
- `opal_reset_segment()` erases/resets a specific locking range.
- `opal_range_check_attributes_and_get_lock_state()` validates range geometry and returns lock state.
- `opal_exclusive_lock()` / `opal_exclusive_unlock()` serialize OPAL operations with cryptsetup locking.

Role:
- Keeps OPAL support isolated behind a small interface so LUKS2 segment/key management can call hardware encryption functions without depending directly on Linux ioctl details.
