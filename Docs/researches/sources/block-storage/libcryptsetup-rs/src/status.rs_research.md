# File Research: sources/block-storage/libcryptsetup-rs/src/status.rs

Implements crypt device status and metadata inspection.

Key API:
- `CryptDeviceStatusHandle::dump`
- `dump_json` behind `cryptsetup24supported`
- `get_cipher`
- `get_cipher_mode`
- `get_uuid`
- `get_device_path`
- `get_metadata_device_path`
- `get_data_offset`
- `get_iv_offset`
- `get_volume_key_size`
- `get_verity_info`
- `get_integrity_info`
- free function `status`
- free function `get_sector_size`

Behavior:
- Reads textual, JSON, cipher, UUID, path, offset, key size, verity, and integrity information from libcryptsetup.
- `dump_json` parses returned C string into `serde_json::Value` and intentionally does not free the buffer, with a comment explaining double-free/valgrind observations.
- `status` accepts optional `CryptDevice`; `None` passes null device pointer.
- `get_sector_size` returns raw `c_int`.

Research notes:
- `get_cipher`, `get_cipher_mode`, and `get_uuid` call FFI without `mutex!` around the direct pointer access in the visible code for some getters.
- Path getters return borrowed `&Path` tied to libcryptsetup-managed strings.
