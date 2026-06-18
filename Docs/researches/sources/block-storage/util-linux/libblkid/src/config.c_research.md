# File Research: sources/block-storage/util-linux/libblkid/src/config.c

## Purpose
Parses libblkid configuration from `blkid.conf`, environment-selected config files, or libeconf-backed vendor/system directories.

## Main Components
- `parse_evaluate()` parses comma-separated evaluation methods into `BLKID_EVAL_UDEV` and `BLKID_EVAL_SCAN`.
- Non-libeconf `parse_next()` parses `SEND_UEVENT=`, `CACHE_FILE=`, and `EVALUATE=` lines, skipping blanks/comments.
- `blkid_read_config()` allocates config, reads the selected config source, applies defaults, and returns a populated config object.
- libeconf path reads boolean `SEND_UEVENT`, string `CACHE_FILE`, and string `EVALUATE`.
- Defaults are evaluation order `udev,scan`, cache file `/run/blkid/blkid.tab`, and `SEND_UEVENT=yes`.
- `blkid_free_config()` releases config memory.
- `TEST_PROGRAM` main prints parsed config.

## Dependencies and Interactions
Used by cache path selection and tag/spec evaluation. It honors `BLKID_CONF` and optionally libeconf support configured at build time.

## Research Notes
The non-libeconf parser treats unknown options, long malformed lines, and invalid evaluation names as parse errors. Missing config files are not errors; they fall back to built-in defaults.
