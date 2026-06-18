# File Research: sources/block-storage/cryptsetup/src/integritysetup_arg_list.h

## Purpose
Macro list defining all `integritysetup` options. Like the cryptsetup option list, it is consumed by enum, storage, and popt table generation.

## Option Groups
- General: batch mode, verbose, debug.
- Activation/deactivation: allow discards, deferred, cancel deferred, size/device-size.
- Format geometry: buffer sectors, interleave sectors, journal size, journal watermark, journal commit time, sector size, tag size.
- Bitmap mode: bitmap mode flag, sectors per bit, flush time.
- Integrity algorithm and keys: integrity algorithm, integrity key file/size, journal integrity algorithm/key, journal encryption algorithm/key.
- Compatibility: legacy padding, legacy HMAC, legacy recalculation.
- Operational modes: no journal, recovery mode, recalculate, recalculate reset, inline integrity.
- Data placement: separate data device.
- Wipe/progress: no wipe, wipe after resize, progress frequency, progress JSON.
- Signature probing: disable blkid.

## Defaults
- `--integrity` defaults to `DEFAULT_ALG_NAME` (`crc32c`).
- `--sector-size` defaults to 512 bytes.
- Other numeric options default to zero unless specified.

## Notes
The comment omits “allowed actions” in its prose, but entries use the same eight-argument macro shape as the cryptsetup list, including action allowlists.
